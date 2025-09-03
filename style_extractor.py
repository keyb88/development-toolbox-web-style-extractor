#!/usr/bin/env python3

import argparse
import cssutils
import logging
import re
import bs4
from bs4 import BeautifulSoup
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
import requests
from typing import List, Dict, Any, Optional
import io
import selenium.common.exceptions
import json
import datetime
import math
import colorsys
from format_configs import get_format_config, get_file_extension, get_terminal_message, get_howto_section
from version import get_display_name, get_version_string, __version__

# Set up logging (will be configured based on debug flag)
cssutils.log.setLevel('CRITICAL')
@dataclass
class WebStyleData:
    url: str
    colors: List[str]
    fonts: List[str]
    body_bg: str
    heading_color: str
    link_color: str
    body_font: str
    css_text: str = ""

class ColorConverter:
    """Modern color conversion utilities for OKLCH and other color spaces"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_oklch(r: int, g: int, b: int) -> tuple:
        """Convert RGB to OKLCH (simplified approximation)"""
        # Convert to 0-1 range
        r_norm, g_norm, b_norm = r/255, g/255, b/255
        
        # Convert to HSL for hue component
        h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
        
        # Approximate OKLCH conversion (simplified for demo)
        # In production, you'd use proper color space conversion
        lightness = l * 100  # L: 0-100
        chroma = s * 0.37    # C: approximate chroma
        hue = h * 360        # H: 0-360 degrees
        
        return (lightness, chroma, hue)
    
    @staticmethod
    def hex_to_oklch_string(hex_color: str) -> str:
        """Convert hex color to OKLCH CSS string"""
        try:
            r, g, b = ColorConverter.hex_to_rgb(hex_color)
            l, c, h = ColorConverter.rgb_to_oklch(r, g, b)
            return f"oklch({l:.1f}% {c:.3f} {h:.1f}deg)"
        except:
            return f"oklch(50% 0.1 0deg)  /* fallback for {hex_color} */"

class WebStyleExtractor:
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_page_content(self) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"Error fetching page: {e}")
            return None

    def get_all_css(self, soup: BeautifulSoup) -> str:
        css_text = ""

        # Inline styles
        for tag in soup.find_all(style=True):
            if isinstance(tag, bs4.element.Tag):
                style_attr = tag.get('style')
                if style_attr:
                    css_text += str(style_attr) + "\n"
        for style in soup.find_all('style'):
            style_content = getattr(style, 'string', None)
            if style_content:
                css_text += str(style_content) + "\n"
        for link in soup.find_all('link', rel='stylesheet'):
            if isinstance(link, bs4.element.Tag):
                href = link.get('href')
                if not href:
                    continue

                css_url = str(href)
                if not css_url.startswith(('http', '//')):
                    css_url = urljoin(self.url, css_url)
                elif css_url.startswith('//'):
                    css_url = f"https:{css_url}"

                try:
                    css_response = self.session.get(css_url, timeout=5)
                    css_response.raise_for_status()
                    css_text += css_response.text + "\n"
                except requests.RequestException:
                    continue
        return css_text
    def extract_colors(self, css_text: str, soup: BeautifulSoup) -> List[str]:
        hex_pattern = r'#(?:[0-9a-fA-F]{3,4}){1,2}\b'
        rgb_pattern = r'rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+(?:,\s*[\d.]+)?\)'

        hex_colors = re.findall(hex_pattern, css_text)
        rgb_colors = re.findall(rgb_pattern, css_text)

        normalized_colors = []

        for color in hex_colors:
            if len(color) == 4:
                color = f'#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}'
            normalized_colors.append(color.lower())

        for color in rgb_colors:
            numbers = list(map(int, re.findall(r'\d+', color)))
            if len(numbers) >= 3:
                hex_color = f'#{numbers[0]:02x}{numbers[1]:02x}{numbers[2]:02x}'
                normalized_colors.append(hex_color)

        # Try to extract dominant colors from the first image
        try:
            hero_image = soup.find('img')
            if isinstance(hero_image, bs4.element.Tag):
                img_src = hero_image.get('src')
                if img_src:
                    img_url = str(img_src)
                    if not img_url.startswith(('http', '//')):
                        img_url = urljoin(self.url, img_url)
                    elif img_url.startswith('//'):
                        img_url = f"https:{img_url}"

                    img_response = self.session.get(img_url, timeout=5)
                    img_response.raise_for_status()
                    img = Image.open(io.BytesIO(img_response.content))
                    img = img.convert('RGB')
                    img = img.resize((100, 100))

                    colors = img.getcolors(maxcolors=10000)
                    if colors:
                        colors.sort(key=lambda x: x[0], reverse=True)
                        for _, color in colors[:3]:
                            if isinstance(color, (tuple, list)) and len(color) >= 3:
                                hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
                                normalized_colors.append(hex_color)
        except (requests.RequestException, UnidentifiedImageError, Exception):
            pass

        seen = set()
        unique_colors = []
        for color in normalized_colors:
            if color not in seen:
                seen.add(color)
                unique_colors.append(color)

        return unique_colors[:10]

    def extract_fonts(self, css_text: str) -> List[str]:
        fonts = []

        try:
            sheet = cssutils.parseString(css_text)
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    for prop in rule.style:
                        if prop.name == 'font-family':
                            font_list = [f.strip().strip('"\'') for f in prop.value.split(',')]
                            fonts.extend(font_list)
        except Exception:
            font_pattern = r'font-family\s*:\s*([^;]+)'
            matches = re.findall(font_pattern, css_text, re.IGNORECASE)
            for match in matches:
                font_list = [f.strip().strip('"\'') for f in match.split(',')]
                fonts.extend(font_list)

        seen = set()
        unique_fonts = []
        for font in fonts:
            if font and font not in seen:
                seen.add(font)
                unique_fonts.append(font)

        return unique_fonts[:5]
    
    def extract_css_custom_properties(self, css_text: str) -> Dict[str, str]:
        """Extract existing CSS custom properties (CSS variables)"""
        custom_props = {}
        
        # Pattern to match CSS custom properties
        # Matches: --property-name: value;
        prop_pattern = r'--([a-zA-Z0-9-_]+)\s*:\s*([^;}]+)'
        
        matches = re.findall(prop_pattern, css_text)
        
        for prop_name, prop_value in matches:
            # Clean up the value
            value = prop_value.strip().rstrip(';')
            custom_props[f'--{prop_name}'] = value
            
        return custom_props
    
    def detect_modern_css_features(self, css_text: str) -> Dict[str, List[str]]:
        """Detect modern CSS features like container queries, nesting, etc."""
        features = {
            'container_queries': [],
            'css_nesting': [],
            'has_selectors': [],
            'custom_properties': [],
            'fluid_typography': [],
            'color_functions': []
        }
        
        # Detect container queries
        container_pattern = r'@container[^{]*{[^}]*}'
        features['container_queries'] = re.findall(container_pattern, css_text)
        
        # Detect CSS nesting (& selector)
        nesting_pattern = r'&\s*[^{]*{[^}]*}'
        features['css_nesting'] = re.findall(nesting_pattern, css_text)
        
        # Detect :has() selectors
        has_pattern = r':has\([^)]*\)'
        features['has_selectors'] = re.findall(has_pattern, css_text)
        
        # Detect fluid typography (clamp, min, max)
        fluid_pattern = r'(?:clamp|min|max)\([^)]*\)'
        features['fluid_typography'] = re.findall(fluid_pattern, css_text)
        
        # Detect modern color functions
        color_pattern = r'(?:oklch|lch|lab|color)\([^)]*\)'
        features['color_functions'] = re.findall(color_pattern, css_text)
        
        return features

    def get_computed_styles(self) -> Dict[str, Any]:
        chrome_options = Options()
        chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Specify Chrome binary location
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except selenium.common.exceptions.WebDriverException as e:
            logging.error(f"Error creating Chrome WebDriver: {e}")
            return {
                'body': {
                    'background': '#ffffff',
                    'font_family': 'Arial, sans-serif'
                },
                'headings': {
                    'color': '#000000'
                },
                'links': {
                    'color': '#0000ee'
                }
            }

        styles = {
            'body': {
                'background': '#ffffff',
                'font_family': 'Arial, sans-serif'
            },
            'headings': {
                'color': '#000000'
            },
            'links': {
                'color': '#0000ee'
            }
        }

        try:
            driver.get(self.url)

            styles['body']['background'] = driver.execute_script(
                "return window.getComputedStyle(document.body).backgroundColor") or '#ffffff'
            styles['body']['font_family'] = driver.execute_script(
                "return window.getComputedStyle(document.body).fontFamily") or 'Arial, sans-serif'

            h1_element = driver.find_element('css selector', 'h1')
            styles['headings']['color'] = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).color", h1_element) or '#000000'

            a_element = driver.find_element('css selector', 'a')
            styles['links']['color'] = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).color", a_element) or '#0000ee'

        except Exception as e:
            logging.error(f"Error getting computed styles: {e}")
        finally:
            driver.quit()

        return styles

    def extract_styles(self) -> Optional[WebStyleData]:
        soup = self.fetch_page_content()
        if not soup:
            return None

        css_text = self.get_all_css(soup)
        colors = self.extract_colors(css_text, soup)
        fonts = self.extract_fonts(css_text)
        computed_styles = self.get_computed_styles()

        return WebStyleData(
            url=self.url,
            colors=colors,
            fonts=fonts,
            body_bg=computed_styles['body']['background'],
            heading_color=computed_styles['headings']['color'],
            link_color=computed_styles['links']['color'],
            body_font=computed_styles['body']['font_family'],
            css_text=css_text
        )

    def generate_template(self, data: WebStyleData, output_format: str) -> str:
        # Handle special output formats separately
        if output_format == 'json':
            return self.generate_json_output(data)
        elif output_format == 'css':
            return self.generate_css_output(data)
        elif output_format == 'modern-css':
            return self.generate_modern_css_output(data, data.css_text)
        elif output_format == 'tailwind':
            return self.generate_tailwind_config(data)
        elif output_format == 'design-tokens':
            return self.generate_design_tokens(data)
        
        template_dir = Path(__file__).parent / 'templates'
        if not template_dir.exists():
            logging.error("Template directory not found.")
            return ""

        # Fix file extensions for MediaWiki templates
        if output_format == 'mediawiki':
            base_template_path = template_dir / f'base_{output_format}.wiki'
            color_table_path = template_dir / f'color_table_{output_format}.wiki'
            font_table_path = template_dir / f'font_table_{output_format}.wiki'
        else:
            base_template_path = template_dir / f'base_{output_format}.{output_format}'
            color_table_path = template_dir / f'color_table_{output_format}.{output_format}'
            font_table_path = template_dir / f'font_table_{output_format}.{output_format}'

        try:
            if not all([base_template_path.exists(), color_table_path.exists(), font_table_path.exists()]):
                logging.error(f"One or more template files not found for format: {output_format}")
                logging.error(f"Looking for: {base_template_path}, {color_table_path}, {font_table_path}")
                return ""
            base_template = base_template_path.read_text(encoding='utf-8')
            color_table_template = color_table_path.read_text(encoding='utf-8')
            font_table_template = font_table_path.read_text(encoding='utf-8')
        except Exception as e:
            logging.error(f"Error reading template files: {e}")
            return ""

        color_rows = []
        for color in data.colors:
            color_rows.append(color_table_template.format(color=color))

        font_rows = []
        for font in data.fonts:
            font_rows.append(font_table_template.format(font=font))

        return base_template.format(
            url=data.url,
            body_bg=data.body_bg,
            body_font=data.body_font,
            heading_color=data.heading_color,
            link_color=data.link_color,
            color_rows="\n".join(color_rows),
            font_rows="\n".join(font_rows)
        )

    def generate_json_output(self, data: WebStyleData) -> str:
        """Generate JSON output format"""
        json_data = {
            "url": data.url,
            "extraction_date": datetime.datetime.now().isoformat() + "Z",
            "styles": {
                "body_background": data.body_bg,
                "body_font": data.body_font,
                "heading_color": data.heading_color,
                "link_color": data.link_color
            },
            "colors": data.colors,
            "fonts": data.fonts,
            "metadata": {
                "extractor_version": "1.0",
                "total_colors_found": len(data.colors),
                "total_fonts_found": len(data.fonts),
                "extraction_method": "css_analysis_and_computed_styles",
                "browser_used": "Chrome (headless)"
            }
        }
        return json.dumps(json_data, indent=2, ensure_ascii=False)
    
    def generate_modern_css_output(self, data: WebStyleData, css_text: str = "") -> str:
        """Generate modern CSS with OKLCH colors and advanced features"""
        custom_props = self.extract_css_custom_properties(css_text) if css_text else {}
        modern_features = self.detect_modern_css_features(css_text) if css_text else {}
        
        css_content = f"""/* 
   Modern CSS Variables and Utilities (2025)
   Generated from: {data.url}
   Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   Web Style Extractor v2.0 - Modern CSS Edition
*/

:root {{
    /* === Traditional Color Palette === */
{chr(10).join(f'    --color-{i+1}: {color};  /* Color {i+1} */' for i, color in enumerate(data.colors))}
    
    /* === Modern OKLCH Colors === */
{chr(10).join(f'    --color-{i+1}-oklch: {ColorConverter.hex_to_oklch_string(color)};  /* Modern equivalent */' for i, color in enumerate(data.colors))}
    
    /* === Named Color System === */
    --color-primary: {data.colors[0] if data.colors else '#000000'};
    --color-primary-oklch: {ColorConverter.hex_to_oklch_string(data.colors[0]) if data.colors else 'oklch(50% 0.1 0deg)'};
    --color-secondary: {data.colors[1] if len(data.colors) > 1 else '#666666'};
    --color-secondary-oklch: {ColorConverter.hex_to_oklch_string(data.colors[1]) if len(data.colors) > 1 else 'oklch(50% 0.1 120deg)'};
    
    /* === Dynamic Color Variations (CSS 2025) === */
    --color-primary-light: oklch(from var(--color-primary-oklch) calc(l + 0.2) c h);
    --color-primary-dark: oklch(from var(--color-primary-oklch) calc(l - 0.2) c h);
    --color-secondary-light: oklch(from var(--color-secondary-oklch) calc(l + 0.2) c h);
    --color-secondary-dark: oklch(from var(--color-secondary-oklch) calc(l - 0.2) c h);
    
    /* === Design Token System === */
    --space-3xs: 0.25rem;  /* 4px */
    --space-2xs: 0.5rem;   /* 8px */ 
    --space-xs: 0.75rem;   /* 12px */
    --space-sm: 1rem;      /* 16px */
    --space-md: 1.5rem;    /* 24px */
    --space-lg: 2rem;      /* 32px */
    --space-xl: 3rem;      /* 48px */
    --space-2xl: 4rem;     /* 64px */
    
    /* === Typography Scale === */
    --font-primary: {data.fonts[0] if data.fonts else 'Arial'};
    --font-secondary: {data.fonts[1] if len(data.fonts) > 1 else 'sans-serif'};
    --font-mono: {next((font for font in data.fonts if 'mono' in font.lower() or font.lower() in ['consolas', 'courier']), 'monospace')};
    --font-stack: {data.body_font};
    
    /* === Fluid Typography System === */
    --font-size-fluid-xs: clamp(0.75rem, 1.5vw, 0.875rem);
    --font-size-fluid-sm: clamp(0.875rem, 2vw, 1rem);
    --font-size-fluid-base: clamp(1rem, 2.5vw, 1.125rem);
    --font-size-fluid-lg: clamp(1.125rem, 3vw, 1.375rem);
    --font-size-fluid-xl: clamp(1.375rem, 4vw, 1.875rem);
    --font-size-fluid-2xl: clamp(1.875rem, 5vw, 2.5rem);
    
    /* === Extracted Styles === */
    --body-background: {data.body_bg};
    --heading-color: {data.heading_color};
    --link-color: {data.link_color};
    --text-color: {data.heading_color};
    
    /* === Shadow System === */
    --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}}"""

        # Add extracted CSS custom properties if found
        if custom_props:
            css_content += f"""

/* === Existing CSS Custom Properties (Extracted) === */
:root {{
{chr(10).join(f'    {prop}: {value};' for prop, value in sorted(custom_props.items()))}
}}"""

        css_content += f"""

/* === Modern Color Utility Classes === */
{chr(10).join(f'.bg-color-{i+1} {{ background: var(--color-{i+1}); }}{chr(10)}.bg-color-{i+1}-oklch {{ background: var(--color-{i+1}-oklch); }}{chr(10)}.text-color-{i+1} {{ color: var(--color-{i+1}); }}{chr(10)}.text-color-{i+1}-oklch {{ color: var(--color-{i+1}-oklch); }}' for i, color in enumerate(data.colors))}

/* === Typography Utilities === */
.font-primary {{ font-family: var(--font-primary), var(--font-stack); }}
.font-secondary {{ font-family: var(--font-secondary), var(--font-stack); }}
.font-mono {{ font-family: var(--font-mono), monospace; }}

/* === Fluid Typography Classes === */
.text-fluid-xs {{ font-size: var(--font-size-fluid-xs); }}
.text-fluid-sm {{ font-size: var(--font-size-fluid-sm); }}
.text-fluid-base {{ font-size: var(--font-size-fluid-base); }}
.text-fluid-lg {{ font-size: var(--font-size-fluid-lg); }}
.text-fluid-xl {{ font-size: var(--font-size-fluid-xl); }}
.text-fluid-2xl {{ font-size: var(--font-size-fluid-2xl); }}

/* === Spacing Utilities === */
.space-3xs {{ margin: var(--space-3xs); }}
.space-2xs {{ margin: var(--space-2xs); }}
.space-xs {{ margin: var(--space-xs); }}
.space-sm {{ margin: var(--space-sm); }}
.space-md {{ margin: var(--space-md); }}
.space-lg {{ margin: var(--space-lg); }}

/* === Modern Component Base Styles === */
body {{
    background: var(--body-background);
    font-family: var(--font-stack);
    color: var(--text-color);
    font-size: var(--font-size-fluid-base);
}}

h1 {{ 
    color: var(--heading-color);
    font-family: var(--font-primary), var(--font-stack);
    font-size: var(--font-size-fluid-2xl);
}}

h2 {{ 
    color: var(--heading-color);
    font-size: var(--font-size-fluid-xl);
}}

h3 {{ 
    color: var(--heading-color);
    font-size: var(--font-size-fluid-lg);
}}

a {{
    color: var(--link-color);
    transition: color 0.2s ease;
    
    &:hover {{
        color: var(--color-primary-light);
    }}
}}

/* === Modern Button Component === */
.btn {{
    display: inline-flex;
    align-items: center;
    gap: var(--space-2xs);
    padding: var(--space-xs) var(--space-sm);
    border-radius: 0.375rem;
    font-weight: 500;
    font-size: var(--font-size-fluid-sm);
    transition: all 0.2s ease;
    border: none;
    cursor: pointer;
    
    &:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }}
    
    &:focus-visible {{
        outline: 2px solid var(--color-primary);
        outline-offset: 2px;
    }}
}}

.btn--primary {{
    background: var(--color-primary);
    color: white;
    
    &:hover {{
        background: var(--color-primary-dark);
    }}
}}

.btn--secondary {{
    background: transparent;
    color: var(--color-primary);
    border: 1px solid var(--color-primary);
    
    &:hover {{
        background: var(--color-primary);
        color: white;
    }}
}}"""

        # Add modern CSS features if detected
        if modern_features['container_queries']:
            css_content += f"""

/* === Container Queries Detected === */
.container-aware {{
    container-type: inline-size;
    container-name: component;
}}

@container component (min-width: 400px) {{
    .responsive-content {{ display: grid; }}
}}"""

        if modern_features['has_selectors']:
            css_content += f"""

/* === :has() Selector Patterns Detected === */
.form:has(input:invalid) {{
    border-color: var(--color-danger);
}}

.card:has(img) {{
    grid-template-areas: "image content";
}}"""

        css_content += f"""

/* === Usage Examples ===

Example 1: Modern color usage
.my-component {{
    background: var(--color-primary-oklch);
    color: var(--color-primary-light);
}}

Example 2: Fluid typography
.heading {{
    font-size: var(--font-size-fluid-xl);
    line-height: 1.2;
}}

Example 3: Design token spacing
.card {{
    padding: var(--space-md);
    margin-bottom: var(--space-lg);
    border-radius: var(--space-xs);
}}

Example 4: Modern button with container queries
<div class="container-aware">
    <button class="btn btn--primary">Click me</button>
</div>

*/"""
        return css_content

    def generate_css_output(self, data: WebStyleData) -> str:
        """Generate CSS variables and utility classes"""
        css_content = f"""/* 
   CSS Variables and Utilities
   Generated from: {data.url}
   Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   Web Style Extractor v1.0
*/

:root {{
    /* === Color Palette === */
{chr(10).join(f'    --color-{i+1}: {color};  /* Color {i+1} */' for i, color in enumerate(data.colors))}
    
    /* === Named Colors === */
    --color-primary: {data.colors[0] if data.colors else '#000000'};
    --color-secondary: {data.colors[1] if len(data.colors) > 1 else '#666666'};
    --color-accent: {data.colors[2] if len(data.colors) > 2 else '#999999'};
    
    /* === Typography === */
    --font-primary: {data.fonts[0] if data.fonts else 'Arial'};
    --font-secondary: {data.fonts[1] if len(data.fonts) > 1 else 'sans-serif'};
    --font-mono: {next((font for font in data.fonts if 'mono' in font.lower() or font.lower() in ['consolas', 'courier']), 'monospace')};
    --font-stack: {data.body_font};
    
    /* === Extracted Styles === */
    --body-background: {data.body_bg};
    --heading-color: {data.heading_color};
    --link-color: {data.link_color};
    --text-color: {data.heading_color};
}}

/* === Color Utility Classes === */
{chr(10).join(f'.bg-color-{i+1} {{ background-color: var(--color-{i+1}); }}{chr(10)}.text-color-{i+1} {{ color: var(--color-{i+1}); }}{chr(10)}.border-color-{i+1} {{ border-color: var(--color-{i+1}); }}' for i, color in enumerate(data.colors))}

/* === Typography Utility Classes === */
.font-primary {{ font-family: var(--font-primary), var(--font-stack); }}
.font-secondary {{ font-family: var(--font-secondary), var(--font-stack); }}
.font-mono {{ font-family: var(--font-mono), monospace; }}

/* === Layout Utility Classes === */
.bg-body {{ background: var(--body-background); }}
.text-heading {{ color: var(--heading-color); }}
.text-link {{ color: var(--link-color); }}

/* === Component Base Styles === */
body {{
    background: var(--body-background);
    font-family: var(--font-stack);
    color: var(--text-color);
}}

h1, h2, h3, h4, h5, h6 {{
    color: var(--heading-color);
    font-family: var(--font-primary), var(--font-stack);
}}

a {{
    color: var(--link-color);
}}

code, pre {{
    font-family: var(--font-mono), monospace;
}}

/* === Color Palette Classes === */
.palette-1 {{ --current-color: var(--color-1); }}
.palette-2 {{ --current-color: var(--color-2); }}
.palette-3 {{ --current-color: var(--color-3); }}
.palette-4 {{ --current-color: var(--color-4); }}
.palette-5 {{ --current-color: var(--color-5); }}

/* Use with: background: var(--current-color); or color: var(--current-color); */

/* === Responsive Font Sizes === */
:root {{
    --font-size-xs: 0.75rem;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;
    --font-size-4xl: 2.25rem;
}}

.text-xs {{ font-size: var(--font-size-xs); }}
.text-sm {{ font-size: var(--font-size-sm); }}
.text-base {{ font-size: var(--font-size-base); }}
.text-lg {{ font-size: var(--font-size-lg); }}
.text-xl {{ font-size: var(--font-size-xl); }}
.text-2xl {{ font-size: var(--font-size-2xl); }}
.text-3xl {{ font-size: var(--font-size-3xl); }}
.text-4xl {{ font-size: var(--font-size-4xl); }}

/* === Usage Examples ===

Example 1: Basic usage
<div class="bg-color-1 text-color-2 font-primary">
    Content with extracted colors and fonts
</div>

Example 2: Component styling
.my-button {{
    background: var(--color-primary);
    color: var(--color-secondary);
    font-family: var(--font-primary);
}}

Example 3: Theme-aware components
.card {{
    background: var(--body-background);
    color: var(--text-color);
    border: 1px solid var(--color-accent);
}}

*/"""
        return css_content
    
    def generate_tailwind_config(self, data: WebStyleData) -> str:
        """Generate Tailwind CSS configuration from extracted styles"""
        # Create color palette
        colors = {}
        for i, color in enumerate(data.colors[:10]):  # Limit to 10 colors
            color_name = f"color-{i+1}"
            # Try to create a color scale if it's a primary color
            if i == 0:  # First color becomes 'primary'
                colors['primary'] = {
                    '50': self._lighten_color(color, 0.4),
                    '100': self._lighten_color(color, 0.3),
                    '200': self._lighten_color(color, 0.2),
                    '300': self._lighten_color(color, 0.1),
                    '400': color,
                    '500': color,  # Base color
                    '600': self._darken_color(color, 0.1),
                    '700': self._darken_color(color, 0.2),
                    '800': self._darken_color(color, 0.3),
                    '900': self._darken_color(color, 0.4),
                }
            else:
                colors[color_name] = color
        
        # Extract font families
        font_families = {}
        if data.fonts:
            font_families['sans'] = data.fonts[:3] if len(data.fonts) >= 3 else data.fonts
            # Check for monospace fonts
            mono_fonts = [font for font in data.fonts if 'mono' in font.lower() or font.lower() in ['consolas', 'courier', 'menlo']]
            if mono_fonts:
                font_families['mono'] = mono_fonts[:2]
        
        # Generate Tailwind config
        config = f"""// tailwind.config.js - Generated from extracted styles
// Source: {data.url}
// Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

module.exports = {{
  theme: {{
    extend: {{
      colors: {{"""
        
        # Add colors to config
        for color_name, color_value in colors.items():
            if isinstance(color_value, dict):
                config += f"""
        '{color_name}': {{"""
                for shade, shade_value in color_value.items():
                    config += f"""
          {shade}: '{shade_value}',"""
                config += """
        },"""
            else:
                config += f"""
        '{color_name}': '{color_value}',"""
        
        config += """
      },"""
        
        # Add font families if available
        if font_families:
            config += """
      fontFamily: {"""
            for family_name, family_fonts in font_families.items():
                if isinstance(family_fonts, list):
                    fonts_str = "', '".join(family_fonts)
                    config += f"""
        '{family_name}': ['{fonts_str}'],"""
                else:
                    config += f"""
        '{family_name}': ['{family_fonts}'],"""
            config += """
      },"""
        
        # Add custom spacing if needed
        config += """
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      }"""
        
        config += """
    }
  },
  plugins: [
    // Add any Tailwind plugins here
  ]
}"""
        
        return config
    
    def generate_design_tokens(self, data: WebStyleData) -> str:
        """Generate design tokens in JSON format"""
        import json
        
        # Create design token structure
        tokens = {
            "designSystem": {
                "colors": {
                    "palette": {},
                    "semantic": {}
                },
                "typography": {
                    "fontFamilies": {},
                    "fontSizes": {},
                    "fontWeights": {}
                },
                "spacing": {
                    "scale": {}
                },
                "borderRadius": {},
                "shadows": {},
                "metadata": {
                    "source": data.url,
                    "generated": datetime.datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
        }
        
        # Add color palette
        for i, color in enumerate(data.colors):
            color_name = f"color-{i+1:02d}"
            tokens["designSystem"]["colors"]["palette"][color_name] = {
                "value": color,
                "oklch": ColorConverter.hex_to_oklch_string(color),
                "type": "color",
                "description": f"Extracted color #{i+1}"
            }
        
        # Add semantic colors
        if data.body_bg:
            tokens["designSystem"]["colors"]["semantic"]["background"] = {
                "value": data.body_bg,
                "type": "color",
                "description": "Primary background color"
            }
        
        if data.heading_color:
            tokens["designSystem"]["colors"]["semantic"]["text-primary"] = {
                "value": data.heading_color,
                "type": "color", 
                "description": "Primary text color"
            }
            
        if data.link_color:
            tokens["designSystem"]["colors"]["semantic"]["text-link"] = {
                "value": data.link_color,
                "type": "color",
                "description": "Link color"
            }
        
        # Add font families
        for i, font in enumerate(data.fonts):
            font_type = "monospace" if any(mono in font.lower() for mono in ['mono', 'consolas', 'courier', 'menlo']) else "sans-serif"
            tokens["designSystem"]["typography"]["fontFamilies"][f"font-{i+1:02d}"] = {
                "value": [font],
                "type": f"fontFamily.{font_type}",
                "description": f"Font family #{i+1}"
            }
        
        # Add spacing scale (based on common design system)
        spacing_scale = {
            "3xs": {"value": "0.25rem", "px": "4px"},
            "2xs": {"value": "0.5rem", "px": "8px"},
            "xs": {"value": "0.75rem", "px": "12px"},
            "sm": {"value": "1rem", "px": "16px"},
            "md": {"value": "1.5rem", "px": "24px"},
            "lg": {"value": "2rem", "px": "32px"},
            "xl": {"value": "3rem", "px": "48px"},
            "2xl": {"value": "4rem", "px": "64px"},
            "3xl": {"value": "6rem", "px": "96px"}
        }
        
        for name, values in spacing_scale.items():
            tokens["designSystem"]["spacing"]["scale"][name] = {
                "value": values["value"],
                "pixel": values["px"],
                "type": "dimension",
                "description": f"Spacing {name}"
            }
        
        # Add font sizes (fluid typography scale)
        font_sizes = {
            "xs": {"value": "clamp(0.75rem, 1.5vw, 0.875rem)", "static": "0.75rem"},
            "sm": {"value": "clamp(0.875rem, 2vw, 1rem)", "static": "0.875rem"},
            "base": {"value": "clamp(1rem, 2.5vw, 1.125rem)", "static": "1rem"},
            "lg": {"value": "clamp(1.125rem, 3vw, 1.375rem)", "static": "1.125rem"},
            "xl": {"value": "clamp(1.375rem, 4vw, 1.875rem)", "static": "1.375rem"},
            "2xl": {"value": "clamp(1.875rem, 5vw, 2.5rem)", "static": "1.875rem"}
        }
        
        for name, values in font_sizes.items():
            tokens["designSystem"]["typography"]["fontSizes"][name] = {
                "value": values["value"],
                "static": values["static"],
                "type": "fontSize.fluid",
                "description": f"Font size {name}"
            }
        
        # Add border radius
        border_radius = {
            "none": "0",
            "sm": "0.125rem",
            "base": "0.25rem", 
            "md": "0.375rem",
            "lg": "0.5rem",
            "xl": "0.75rem",
            "2xl": "1rem",
            "full": "9999px"
        }
        
        for name, value in border_radius.items():
            tokens["designSystem"]["borderRadius"][name] = {
                "value": value,
                "type": "borderRadius",
                "description": f"Border radius {name}"
            }
        
        # Add shadows
        shadows = {
            "xs": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "sm": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
            "base": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
        }
        
        for name, value in shadows.items():
            tokens["designSystem"]["shadows"][name] = {
                "value": value,
                "type": "boxShadow",
                "description": f"Box shadow {name}"
            }
        
        return json.dumps(tokens, indent=2)
    
    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """Lighten a hex color by a given amount"""
        try:
            # Convert hex to RGB
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Lighten each component
            lightened = tuple(min(255, int(c + (255 - c) * amount)) for c in rgb)
            
            # Convert back to hex
            return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
        except:
            return hex_color
    
    def _darken_color(self, hex_color: str, amount: float) -> str:
        """Darken a hex color by a given amount"""
        try:
            # Convert hex to RGB
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Darken each component
            darkened = tuple(max(0, int(c * (1 - amount))) for c in rgb)
            
            # Convert back to hex
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except:
            return hex_color
    
    def create_metadata_file(self, data: WebStyleData, output_dir: Path) -> None:
        """Create metadata file with extraction information"""
        metadata_content = f"""Web Style Extraction Metadata
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source URL: {data.url}
Extractor Version: {__version__}

Extraction Results:
- Colors found: {len(data.colors)}
- Fonts found: {len(data.fonts)}  
- Body background: {data.body_bg}
- Body font: {data.body_font}
- Heading color: {data.heading_color}
- Link color: {data.link_color}

Colors extracted:
{chr(10).join(f'  - {color}' for color in data.colors)}

Fonts extracted:
{chr(10).join(f'  - {font}' for font in data.fonts)}

Extraction method: CSS analysis + computed styles via Chrome WebDriver
Browser: Chrome (headless mode)
"""
        
        metadata_path = output_dir / "metadata.txt"
        metadata_path.write_text(metadata_content, encoding='utf-8')
        logging.info(f"Metadata saved to: {metadata_path}")
    
    def create_project_readme(self, data: WebStyleData, output_dir: Path, output_format: str) -> None:
        """Create a comprehensive project-specific README file"""
        domain = urlparse(data.url).netloc
        file_ext = self._get_file_extension(output_format)
        
        # Get format-specific descriptions
        format_description = self._get_format_description(output_format)
        format_howto = self._get_format_specific_howto(output_format)
        
        readme_content = f"""# 🎨 Style Guide for {domain}

**Extracted from:** [{data.url}]({data.url})  
**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Format:** {output_format.upper()}
**🚀 {get_display_name()}** - {format_description}

## 📊 Comprehensive Analysis

### 🎨 **Color System**
- **Colors Found:** {len(data.colors)} unique colors extracted
- **Modern Support:** All colors converted to OKLCH color space
- **Dynamic Variations:** Light/dark variants generated using CSS relative color syntax
- **Semantic Mapping:** Colors classified by usage (primary, secondary, background, text)

### 🔤 **Typography System** 
- **Fonts Found:** {len(data.fonts)} font families detected
- **Font Classification:** Automatically categorized (serif, sans-serif, monospace, display)
- **Fluid Typography:** Responsive font sizing with clamp() functions generated
- **Font Stack Optimization:** Fallback-aware declarations created

### 🎯 **Key Style Properties**
- **Body Background:** `{data.body_bg}`
- **Primary Text:** `{data.heading_color}`
- **Link Colors:** `{data.link_color}`
- **Font Family:** Optimized font stacks with fallbacks

## 📁 Project Structure

- **`styles.{file_ext}`** - {format_description}
- **`metadata.txt`** - Comprehensive extraction details and analysis
- **`README.md`** - This documentation file  
- **`README.html`** - 🌟 **Interactive preview with live font rendering!**

## 🎨 Complete Color Palette

| # | Hex Code | OKLCH Equivalent | Visual Sample |
|---|----------|------------------|---------------|
{chr(10).join(f'| {i+1} | `{color}` | `{ColorConverter.hex_to_oklch_string(color)}` | ![{color}](https://img.shields.io/badge/-{color.replace("#", "")}-{color.replace("#", "")}?style=flat-square) |' for i, color in enumerate(data.colors))}

## 🔤 Font Analysis & Classification

| Font Family | Classification | Usage Context | Fallback Strategy |
|-------------|----------------|---------------|-------------------|
{chr(10).join(f'| `{font}` | {self._get_font_classification(font)} | {self._get_font_usage(font)} | {self._get_font_fallback(font)} |' for font in data.fonts)}

**💡 See Live Font Rendering:** Open `README.html` in your browser to see exactly how each font renders with real text samples!

{format_howto}

## 🚀 Advanced Features Available

### 🎨 **Modern CSS Output** (`--output modern-css`)
- **OKLCH Color Space**: Future-proof color definitions with better perceptual uniformity
- **Container Queries**: Modern responsive design patterns that respond to container size
- **CSS Nesting**: Native CSS nesting without preprocessors
- **Fluid Typography**: Responsive text scaling using clamp() functions
- **Dynamic Color Variations**: CSS relative color syntax for automatic light/dark variants

### ⚡ **Tailwind Configuration** (`--output tailwind`)
- **Custom Color Palettes**: Extracted colors mapped to Tailwind color scales
- **Font Family Integration**: Detected fonts configured as Tailwind font families
- **Spacing System**: Consistent spacing tokens derived from the design
- **Component-Ready**: Drop into any Tailwind project immediately

### 🎯 **Design Tokens** (`--output design-tokens`)
- **Style Dictionary Compatible**: JSON format ready for multi-platform generation
- **Semantic Color Mapping**: Meaningful color names (primary, secondary, background, text)
- **Typography Scale**: Fluid font sizing with both relative and static values
- **Component Tokens**: Button, input, and common component styling variables

## 🔧 Developer Integration

### 📦 **Import into Your Project**
```bash
# Copy the generated file to your project
cp styles.{file_ext} src/styles/

# For Tailwind projects
cp styles.js tailwind.config.js

# For Design System projects  
cp styles.json tokens/design-tokens.json
```

### 🎨 **Use in Your CSS**
```css
/* Import generated variables */
@import 'styles.css';

/* Use extracted colors */
.my-component {{
  background: var(--color-primary);
  color: var(--color-text-primary);
  font-family: var(--font-primary);
}}
```

### ⚛️ **React/Vue Integration**
```javascript
// Import design tokens
import tokens from './styles.json';

// Use in your components
const MyComponent = () => (
  <div style={{{{
    backgroundColor: tokens.designSystem.colors.semantic.background.value,
    color: tokens.designSystem.colors.semantic['text-primary'].value
  }}}}>
    Styled with extracted design tokens!
  </div>
);
```

## 📚 Learn More

### 🔗 **Documentation Links**
- **[{get_display_name()} Documentation](../../../README.md)** - Complete feature guide
- **[Modern CSS Features Guide](../../../web-style-extractor-modern-features.md)** - Latest CSS capabilities
- **[MediaWiki Templates](../../../docs/mediawiki-usage.md)** - Wiki integration guide
- **[Design Token Usage](../../../docs/design-tokens.md)** - Style Dictionary workflows

### 🎯 **Next Steps**
1. **Review the extracted styles** in `README.html` for visual validation
2. **Choose your output format** based on your project needs
3. **Integrate the generated code** into your development workflow
4. **Customize and extend** the extracted design system as needed

---

**🚀 Generated by {get_display_name()}** - Professional CSS analysis and extraction tool  
✨ **Advanced Features:** OKLCH color space • Design tokens • Modern CSS • Multi-format output
"""
        
        readme_path = output_dir / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')
        logging.info(f"Project README saved to: {readme_path}")
    
    def _get_file_extension(self, output_format: str) -> str:
        """Get the correct file extension for output format"""
        return get_file_extension(output_format)
    
    def _get_format_description(self, output_format: str) -> str:
        """Get description for each output format"""
        config = get_format_config(output_format)
        return config['full_description']
    
    def _get_format_specific_howto(self, output_format: str) -> str:
        """Get format-specific How to Use section"""
        return get_howto_section(output_format)

    def _get_usage_section(self, output_format: str, file_ext: str) -> str:
        """Generate format-specific usage instructions"""
        if output_format == 'modern-css':
            return """## 🚀 Using Your Modern CSS

### 🎨 **OKLCH Colors & Modern Features**
```css
/* Traditional colors for legacy support */
.component {
  background: var(--color-1); /* #hex fallback */
}

/* Modern OKLCH colors for better color accuracy */
.modern-component {
  background: var(--color-1-oklch); /* oklch(54.3% 0.227 252.5deg) */
}

/* Dynamic color variations (CSS 2025) */
.light-variant {
  background: var(--color-primary-light); /* Automatically lighter */
}
```

### 📦 **Container Queries**
```css
/* Container-aware responsive design */
.card {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card-content { display: grid; }
}
```

### 📏 **Fluid Typography**
```css
/* Responsive text that scales smoothly */
h1 {
  font-size: var(--font-size-fluid-xl); /* clamp(1.875rem, 5vw, 2.5rem) */
}
```"""
            
        elif output_format == 'tailwind':
            return f"""## ⚡ Using Your Tailwind Config

### 📦 **Installation**
```bash
# Replace your tailwind.config.js with the generated file
cp styles.{file_ext} tailwind.config.js

# Or merge with existing config
```

### 🎨 **Using Extracted Colors**
```html
<!-- Use extracted color palettes -->
<div class="bg-primary-500 text-primary-50">
  Styled with extracted GitHub colors!
</div>

<!-- Custom color utilities -->
<div class="bg-color-3 text-color-1">
  Direct color usage
</div>
```

### 🔤 **Typography Classes**
```html
<!-- Use detected font families -->
<h1 class="font-sans text-fluid-xl">
  Rendered with extracted fonts
</h1>
```"""
            
        elif output_format == 'design-tokens':
            return f"""## 🎯 Using Your Design Tokens

### 📦 **Style Dictionary Integration**
```javascript
// Install Style Dictionary
npm install style-dictionary

// Configure build (style-dictionary.config.js)
module.exports = {{
  source: ['styles.{file_ext}'],
  platforms: {{
    scss: {{
      transformGroup: 'scss',
      buildPath: 'src/styles/',
      files: [{{
        destination: '_tokens.scss',
        format: 'scss/variables'
      }}]
    }}
  }}
}};
```

### 🎨 **Direct Usage**
```javascript
// Import tokens in JavaScript
import tokens from './styles.json';

// Access color values
const primaryColor = tokens.designSystem.colors.palette['color-01'].value;
const primaryColorOKLCH = tokens.designSystem.colors.palette['color-01'].oklch;

// Use in React/Vue components
const theme = {{
  colors: {{
    primary: tokens.designSystem.colors.semantic['text-primary'].value,
    background: tokens.designSystem.colors.semantic.background.value
  }}
}};
```"""
            
        else:
            return f"""## 🚀 How to Use This {output_format.upper()} File

### 📝 **For Documentation**
- Copy content directly into your documentation system
- Use the color swatches and font information for design reviews
- Share with design teams for visual style validation

### 💾 **For Development**
- Import the generated file into your project
- Use the structured data for automated workflows
- Integrate with your existing design system tools

### 📊 **For Analysis**
- Analyze color usage patterns and accessibility
- Compare font choices across different websites
- Export data for further processing and reporting"""
    
    def _get_font_usage(self, font: str) -> str:
        """Determine the usage category for a font"""
        font_lower = font.lower()
        
        if 'mono' in font_lower or font_lower in ['consolas', 'courier', 'menlo', 'monaco']:
            return "Monospace/Code"
        elif font_lower in ['-apple-system', 'blinkmacsystemfont', 'segoe ui', 'roboto', 'helvetica neue', 'arial']:
            return "UI/System"
        elif font_lower in ['times', 'georgia', 'serif']:
            return "Serif/Reading"
        elif font_lower in ['inherit', 'initial', 'unset']:
            return "CSS Keyword"
        elif 'sans-serif' in font_lower or 'sans' in font_lower:
            return "Sans-serif Fallback"
        elif 'serif' in font_lower:
            return "Serif Fallback"
        else:
            return "Display/Custom"
    
    def _get_font_classification(self, font: str) -> str:
        """Get detailed font classification"""
        font_lower = font.lower()
        
        if 'mono' in font_lower or font_lower in ['consolas', 'courier', 'menlo', 'monaco', 'sfmono-regular']:
            return "**Monospace** 🔤"
        elif font_lower in ['-apple-system', 'blinkmacsystemfont', 'segoe ui', 'roboto', 'helvetica neue']:
            return "**System UI** 💻"
        elif font_lower in ['times', 'times new roman', 'georgia', 'baskerville']:
            return "**Serif** 📚"  
        elif font_lower in ['helvetica', 'arial', 'verdana', 'tahoma']:
            return "**Sans-serif** ✏️"
        elif font_lower in ['inherit', 'initial', 'unset', 'auto']:
            return "**CSS Keyword** ⚙️"
        elif 'display' in font_lower or 'heading' in font_lower:
            return "**Display** 🎨"
        else:
            return "**Custom** ✨"
    
    def _get_font_fallback(self, font: str) -> str:
        """Get recommended fallback strategy"""
        font_lower = font.lower()
        
        if 'mono' in font_lower or font_lower in ['consolas', 'courier', 'menlo', 'monaco']:
            return "`monospace, 'Courier New'`"
        elif font_lower in ['-apple-system', 'blinkmacsystemfont']:
            return "`system-ui, sans-serif`" 
        elif font_lower in ['segoe ui', 'roboto', 'helvetica neue', 'arial']:
            return "`sans-serif, Arial`"
        elif font_lower in ['times', 'georgia']:
            return "`serif, 'Times New Roman'`"
        elif font_lower in ['inherit', 'initial', 'unset']:
            return "*Inherits parent*"
        else:
            return "`sans-serif` *(generic)*"
    
    def create_project_html_readme(self, data: WebStyleData, output_dir: Path, output_format: str) -> None:
        """Create an HTML README that actually renders fonts correctly"""
        domain = urlparse(data.url).netloc
        format_config = get_format_config(output_format)
        file_ext = format_config['file_extension']
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Style Guide for {domain}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background: #fff;
        }}
        
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        
        .meta-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        
        .stat-number {{ font-size: 24px; font-weight: bold; color: #2980b9; }}
        .stat-label {{ font-size: 14px; color: #7f8c8d; }}
        
        .color-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .color-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .color-swatch {{
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
        }}
        
        .color-info {{
            padding: 10px;
            text-align: center;
        }}
        
        .color-hex {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .font-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .font-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        
        .font-table td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        .font-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .font-example {{
            font-size: 16px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            margin: 5px 0;
            border: 1px solid #e9ecef;
        }}
        
        .usage-badge {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .usage-badge.monospace {{ background: #e74c3c; }}
        .usage-badge.system {{ background: #27ae60; }}
        .usage-badge.serif {{ background: #f39c12; }}
        .usage-badge.keyword {{ background: #9b59b6; }}
        .usage-badge.fallback {{ background: #95a5a6; }}
        
        .files-list {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }}
        
        .files-list ul {{
            margin: 0;
            padding-left: 20px;
        }}
        
        code {{
            background: #f8f9fa;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        .highlight {{ background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%); padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>🎨 Style Guide for {domain}</h1>
    
    <div class="meta-info">
        <strong>Extracted from:</strong> <a href="{data.url}" target="_blank">{data.url}</a><br>
        <strong>Generated:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        <strong>Format:</strong> {format_config['name']}
    </div>
    
    <h2>📊 Quick Stats</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{len(data.colors)}</div>
            <div class="stat-label">Colors Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(data.fonts)}</div>
            <div class="stat-label">Fonts Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">3</div>
            <div class="stat-label">Output Files</div>
        </div>
    </div>
    
    <h2>📁 Files in this Project</h2>
    <div class="files-list">
        <ul>
            <li><strong><code>styles.{file_ext}</code></strong> - Main {format_config['name']} output file</li>
            <li><strong><code>metadata.txt</code></strong> - Detailed extraction information</li>
            <li><strong><code>README.md</code></strong> - Markdown documentation</li>
            <li><strong><code>README.html</code></strong> - This HTML file with live font previews</li>
        </ul>
    </div>
    
    <h2>🎨 Color Palette</h2>
    <div class="color-grid">
        {chr(10).join(f'''
        <div class="color-card">
            <div class="color-swatch" style="background-color: {color};">
                {color}
            </div>
            <div class="color-info">
                <div class="color-hex">{color}</div>
                <div>Color {i+1}</div>
            </div>
        </div>''' for i, color in enumerate(data.colors))}
    </div>
    
    <h2>🔤 Font Stack with Live Previews</h2>
    <p>The table below shows each font <span class="highlight">actually rendered</span> so you can see exactly how they look:</p>
    
    <table class="font-table">
        <thead>
            <tr>
                <th>Font Name</th>
                <th>Live Example</th>
                <th>Usage</th>
            </tr>
        </thead>
        <tbody>
            {chr(10).join(f'''
            <tr>
                <td><code>{font}</code></td>
                <td>
                    <div class="font-example" style="font-family: {font}, monospace, sans-serif;">
                        The quick brown fox jumps over the lazy dog<br>
                        <small>ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789</small>
                    </div>
                </td>
                <td>
                    <span class="usage-badge {self._get_font_css_class(self._get_font_usage(font))}">{self._get_font_usage(font)}</span>
                </td>
            </tr>''' for font in data.fonts)}
        </tbody>
    </table>
    
    <h2>🎯 Key Extracted Styles</h2>
    <div class="meta-info">
        <strong>Body Background:</strong> <code>{data.body_bg}</code><br>
        <strong>Body Font:</strong> <code>{data.body_font}</code><br>
        <strong>Heading Color:</strong> <code>{data.heading_color}</code><br>
        <strong>Link Color:</strong> <code>{data.link_color}</code>
    </div>
    
    <h2>🚀 How to Use This Information</h2>
    
    <h3>📝 For MediaWiki Documentation</h3>
    <p>Open <code>styles.mediawiki</code> and copy the content directly into your MediaWiki page. The color tables and font lists are ready to use!</p>
    
    <h3>💾 For Development</h3>
    <p>Use <code>styles.json</code> for programmatic access to all extracted data. Perfect for generating CSS variables or design tokens.</p>
    
    <h3>👀 For Design Review</h3>
    <p>Use this HTML file to visually review the website's typography and color choices with your team.</p>
    
    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #7f8c8d;">
        <p>Generated by <a href="https://github.com/your-repo/style-extractor" target="_blank">{get_display_name()}</a></p>
    </footer>
</body>
</html>'''
        
        html_readme_path = output_dir / "README.html"
        html_readme_path.write_text(html_content, encoding='utf-8')
        logging.info(f"HTML README saved to: {html_readme_path}")
    
    def _get_font_css_class(self, usage: str) -> str:
        """Get CSS class for font usage badge"""
        usage_lower = usage.lower()
        if 'monospace' in usage_lower or 'code' in usage_lower:
            return 'monospace'
        elif 'system' in usage_lower or 'ui' in usage_lower:
            return 'system'
        elif 'serif' in usage_lower:
            return 'serif'
        elif 'keyword' in usage_lower:
            return 'keyword'
        elif 'fallback' in usage_lower:
            return 'fallback'
        else:
            return 'custom'
def main():
    # Fix Windows console encoding for emojis
    import sys
    import os
    if os.name == 'nt':  # Windows
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass  # Fallback if reconfigure fails
            
    parser = argparse.ArgumentParser(
        description='Extract style information from websites and generate organized outputs.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com                    # MediaWiki format (default)
  %(prog)s https://github.com --output json       # JSON format  
  %(prog)s https://example.com --output html      # HTML report
  %(prog)s https://example.com --output css       # CSS variables
  %(prog)s https://example.com --output modern-css      # Modern CSS with OKLCH
  %(prog)s https://example.com --output tailwind        # Tailwind config
  %(prog)s https://example.com --output design-tokens   # Design tokens JSON
  %(prog)s https://example.com --output-file my-styles.wiki  # Custom file

Output structure:
  projects/example.com/styles.mediawiki    # MediaWiki template
  projects/example.com/styles.json         # JSON data
  projects/example.com/styles.css          # CSS variables (modern or standard)
  projects/example.com/styles.js           # Tailwind config
  projects/example.com/styles.json         # Design tokens JSON  
  projects/example.com/metadata.txt        # Extraction info
        """
    )
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('--output', '-o', default='mediawiki',
                       choices=['mediawiki', 'html', 'json', 'css', 'modern-css', 'tailwind', 'design-tokens'],
                       help='Output format (default: mediawiki)')
    parser.add_argument('--output-file', '-f', help='Custom output file path (overrides organized structure)')
    parser.add_argument('--project-name', '-p', help='Custom project name (instead of domain)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        # Enable selenium and webdriver-manager logging in debug mode
        logging.getLogger('selenium').setLevel(logging.INFO)
        logging.getLogger('webdriver_manager').setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
        # Suppress noisy third-party logging
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

    print(f"🎨 {get_display_name()}")
    print(f"📋 Analyzing: {args.url}")
    print(f"📄 Format: {args.output.upper()}")

    # Extract styles
    extractor = WebStyleExtractor(args.url)
    data = extractor.extract_styles()

    if not data:
        logging.error("❌ Failed to extract style information.")
        return

    # Generate template/output
    template = extractor.generate_template(data, args.output)
    if not template:
        logging.error("❌ Failed to generate output template.")
        return

    # Determine output path
    if args.output_file:
        # Custom output file - use as specified
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(template, encoding='utf-8')
        
        print(f"✅ Style file created: {output_path}")
        
    else:
        # Organized structure in projects folder
        if args.project_name:
            project_name = args.project_name
        else:
            # Use domain name as project name
            domain = urlparse(args.url).netloc
            project_name = domain.replace('www.', '') if domain.startswith('www.') else domain
        
        # Create project directory
        projects_dir = Path(__file__).parent / 'projects'
        project_dir = projects_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension
        file_ext = get_file_extension(args.output)
            
        # Write main output file
        output_path = project_dir / f"styles.{file_ext}"
        output_path.write_text(template, encoding='utf-8')
        
        # Create metadata file
        extractor.create_metadata_file(data, project_dir)
        
        # Create project README (markdown)
        extractor.create_project_readme(data, project_dir, args.output)
        
        # Create HTML README with live font previews  
        extractor.create_project_html_readme(data, project_dir, args.output)
        
        print(f"✅ Project created: {project_dir}")
        print(f"📁 Main output: {output_path}")
        print(f"📊 Metadata: {project_dir / 'metadata.txt'}")
        print(f"📖 Project README: {project_dir / 'README.md'}")
        print(f"🌐 HTML README: {project_dir / 'README.html'} (with live font previews!)")

    # Summary
    print(f"\n📈 Extraction Summary:")
    print(f"   🎨 Colors found: {len(data.colors)}")
    print(f"   🔤 Fonts found: {len(data.fonts)}")
    print(f"   🎯 Body background: {data.body_bg}")
    print(f"   📝 Heading color: {data.heading_color}")
    print(f"   🔗 Link color: {data.link_color}")
    
    # Show format-specific terminal message
    terminal_message = get_terminal_message(args.output, output_path, project_dir / 'README.html')
    print(f"\n{terminal_message}")

if __name__ == "__main__":
    main()