"""
Format-specific configuration for Web Style Extractor
Contains all text variations for different output formats
"""

FORMAT_CONFIGS = {
    'mediawiki': {
        'name': 'MediaWiki',
        'file_extension': 'mediawiki',
        'emoji': '📝',
        'short_description': 'MediaWiki template with color tables and font documentation',
        'full_description': 'Ready-to-use MediaWiki template with color tables and font documentation',
        'terminal_message': """💡 Next steps:
   1. Open {output_path}
   2. Copy content to your MediaWiki page
   3. View {html_path} to see fonts rendered!
   4. See docs/mediawiki-usage.md for detailed instructions""",
        'howto_title': '📝 For MediaWiki Documentation',
        'howto_instructions': [
            '1. Open `styles.mediawiki`',
            '2. Copy all the content',
            '3. Paste into your MediaWiki page',
            '4. Save and view the formatted style guide'
        ],
        'howto_description': 'The MediaWiki template includes color palette tables with visual swatches, font lists with proper formatting, and key style information ready for documentation.',
        'capabilities': [
            'Color palette tables with visual swatches',
            'Font lists with classifications',
            'Wiki-formatted documentation',
            'Copy-paste ready templates'
        ],
        'use_cases': [
            'Wiki documentation',
            'Style guides',
            'Design system docs',
            'Team knowledge bases'
        ],
        'import_example': """```bash
# Copy the generated file to your wiki
cp styles.mediawiki /path/to/wiki/
```"""
    },
    
    'json': {
        'name': 'JSON',
        'file_extension': 'json',
        'emoji': '💾',
        'short_description': 'Structured data for APIs and automation',
        'full_description': 'Structured data format perfect for APIs, automation, and data analysis',
        'terminal_message': """💡 JSON data ready for:
   • API integration
   • Automated workflows
   • Data analysis""",
        'howto_title': '💾 For Development & APIs',
        'howto_instructions': [
            '1. Import `styles.json` into your application',
            '2. Access structured color and font data',
            '3. Use for automated workflows and API integration',
            '4. Generate CSS/SCSS variables programmatically'
        ],
        'howto_description': 'The JSON format is perfect for API integration, automated workflows, design token systems, and data analysis and processing.',
        'capabilities': [
            'Structured data format',
            'API-ready output',
            'Programmatic access',
            'Cross-platform compatibility'
        ],
        'use_cases': [
            'API integration',
            'Build tool automation',
            'Data analysis',
            'CI/CD pipelines'
        ],
        'import_example': """```javascript
// Import in JavaScript/TypeScript
import styles from './styles.json';

// Use in your application
const colors = styles.colors;
const fonts = styles.fonts;
```"""
    },
    
    'modern-css': {
        'name': 'Modern CSS',
        'file_extension': 'css',
        'emoji': '🚀',
        'short_description': 'Cutting-edge CSS with OKLCH and container queries',
        'full_description': 'Cutting-edge CSS with OKLCH colors, container queries, fluid typography, and design tokens',
        'terminal_message': """🚀 Modern CSS with cutting-edge features:
   • OKLCH color space support
   • Container query patterns
   • Fluid typography with clamp()
   • Design token variables""",
        'howto_title': '🚀 For Modern CSS Development',
        'howto_instructions': [
            '1. Import `styles.css` with cutting-edge CSS features',
            '2. Use OKLCH colors for better color accuracy',
            '3. Implement container queries and fluid typography',
            '4. Leverage dynamic color variations with CSS 2025 syntax'
        ],
        'howto_description': 'Modern CSS with OKLCH color space, container queries, fluid typography, and CSS relative color syntax for future-proof styling.',
        'capabilities': [
            'OKLCH color space',
            'Container queries',
            'Fluid typography with clamp()',
            'CSS custom properties',
            'Relative color syntax',
            'Modern selectors (:has, :is, :where)'
        ],
        'use_cases': [
            'Modern web applications',
            'Progressive enhancement',
            'Future-proof styling',
            'Component libraries'
        ],
        'import_example': """```css
/* Import modern CSS */
@import 'styles.css';

/* Use OKLCH colors */
.component {
  background: var(--color-primary-oklch);
  color: var(--color-text-oklch);
}

/* Container queries */
@container (min-width: 400px) {
  .card { display: grid; }
}
```"""
    },
    
    'css': {
        'name': 'CSS',
        'file_extension': 'css',
        'emoji': '🎨',
        'short_description': 'Standard CSS with variables and utility classes',
        'full_description': 'Standard CSS file with custom properties and utility classes',
        'terminal_message': """🎨 CSS generated with:
   • Custom properties (variables)
   • Utility classes
   • Responsive helpers""",
        'howto_title': '🎨 For CSS Integration',
        'howto_instructions': [
            '1. Import `styles.css` into your project',
            '2. Use CSS custom properties for theming',
            '3. Apply utility classes for quick styling',
            '4. Customize variables as needed'
        ],
        'howto_description': 'Standard CSS with custom properties for easy theming and utility classes for rapid development.',
        'capabilities': [
            'CSS custom properties',
            'Utility classes',
            'Cross-browser compatible',
            'Easy customization'
        ],
        'use_cases': [
            'Traditional websites',
            'WordPress themes',
            'Static sites',
            'Legacy browser support'
        ],
        'import_example': """```html
<!-- Link in HTML -->
<link rel="stylesheet" href="styles.css">

<!-- Or import in CSS -->
@import url('styles.css');
```"""
    },
    
    'tailwind': {
        'name': 'Tailwind CSS',
        'file_extension': 'js',
        'emoji': '⚡',
        'short_description': 'Tailwind configuration with custom colors and fonts',
        'full_description': 'Complete Tailwind CSS configuration with extracted color palettes and font families',
        'terminal_message': """⚡ Tailwind configuration ready:
   • Custom color palette
   • Font family setup
   • Ready to use with your Tailwind project""",
        'howto_title': '⚡ For Tailwind CSS Projects',
        'howto_instructions': [
            '1. Copy `tailwind.config.js` to your project root',
            '2. Merge with existing Tailwind configuration',
            '3. Use extracted colors as Tailwind utilities',
            '4. Apply custom font families in your components'
        ],
        'howto_description': 'Tailwind CSS configuration with extracted design system ready for immediate use in your Tailwind projects.',
        'capabilities': [
            'Custom color palettes',
            'Font family configuration',
            'Spacing scales',
            'Component classes',
            'Dark mode variants'
        ],
        'use_cases': [
            'Tailwind CSS projects',
            'Rapid prototyping',
            'Component libraries',
            'Design system implementation'
        ],
        'import_example': """```javascript
// tailwind.config.js
module.exports = require('./styles.js');

// Use in HTML
<div class="bg-extracted-primary text-extracted-light">
  Styled with extracted colors!
</div>
```"""
    },
    
    'design-tokens': {
        'name': 'Design Tokens',
        'file_extension': 'json',
        'emoji': '🎯',
        'short_description': 'Style Dictionary compatible design tokens',
        'full_description': 'Comprehensive design tokens in Style Dictionary format for multi-platform generation',
        'terminal_message': """🎯 Design tokens generated:
   • Style Dictionary compatible
   • Multi-platform ready
   • Semantic naming""",
        'howto_title': '🎯 For Design Systems',
        'howto_instructions': [
            '1. Import `design-tokens.json` into Style Dictionary',
            '2. Configure platform-specific outputs',
            '3. Generate tokens for iOS, Android, Web',
            '4. Use semantic color and typography scales'
        ],
        'howto_description': 'Design tokens following industry standards, ready for Style Dictionary or other token transformation tools.',
        'capabilities': [
            'Style Dictionary format',
            'Semantic naming',
            'Platform-agnostic',
            'Typography scales',
            'Spacing systems',
            'Component tokens'
        ],
        'use_cases': [
            'Cross-platform apps',
            'Design system libraries',
            'Multi-brand theming',
            'Component documentation'
        ],
        'import_example': """```javascript
// Use with Style Dictionary
const StyleDictionary = require('style-dictionary');

StyleDictionary.extend({
  source: ['design-tokens.json'],
  platforms: {
    scss: {
      transformGroup: 'scss',
      files: [{
        destination: 'variables.scss',
        format: 'scss/variables'
      }]
    }
  }
}).buildAllPlatforms();
```"""
    },
    
    'html': {
        'name': 'HTML Report',
        'file_extension': 'html',
        'emoji': '📊',
        'short_description': 'Interactive HTML report with visual previews',
        'full_description': 'Interactive HTML report with live previews and visual analysis',
        'terminal_message': """📊 HTML report generated:
   • Visual color swatches
   • Interactive previews
   • Shareable documentation""",
        'howto_title': '📊 For Visual Documentation',
        'howto_instructions': [
            '1. Open `styles.html` in your browser',
            '2. Review visual color swatches',
            '3. Check font rendering previews',
            '4. Share with design team for review'
        ],
        'howto_description': 'Interactive HTML report perfect for design reviews, documentation, and team collaboration.',
        'capabilities': [
            'Visual color previews',
            'Live font rendering',
            'Interactive elements',
            'Print-friendly layout'
        ],
        'use_cases': [
            'Design reviews',
            'Client presentations',
            'Documentation',
            'Style guide reference'
        ],
        'import_example': """```html
<!-- Open directly in browser -->
<a href="styles.html">View Style Guide</a>

<!-- Or embed in iframe -->
<iframe src="styles.html" width="100%" height="600"></iframe>
```"""
    }
}

def get_format_config(format_name: str) -> dict:
    """Get configuration for a specific format"""
    return FORMAT_CONFIGS.get(format_name, FORMAT_CONFIGS['json'])

def get_file_extension(format_name: str) -> str:
    """Get file extension for a format"""
    config = get_format_config(format_name)
    return config['file_extension']

def get_terminal_message(format_name: str, output_path: str = None, html_path: str = None) -> str:
    """Get formatted terminal message for a format"""
    config = get_format_config(format_name)
    message = config['terminal_message']
    
    if output_path and '{output_path}' in message:
        message = message.replace('{output_path}', str(output_path))
    if html_path and '{html_path}' in message:
        message = message.replace('{html_path}', str(html_path))
    
    return message

def get_howto_section(format_name: str) -> str:
    """Get the How To Use section for a format"""
    config = get_format_config(format_name)
    
    instructions = '\n'.join(config['howto_instructions'])
    
    return f"""## 🚀 How to Use This Information

### {config['howto_title']}
{instructions}

{config['howto_description']}"""

def get_capabilities_section(format_name: str) -> str:
    """Get capabilities list for a format"""
    config = get_format_config(format_name)
    capabilities = '\n'.join(f'- {cap}' for cap in config['capabilities'])
    return f"""### ✨ Capabilities
{capabilities}"""

def get_use_cases_section(format_name: str) -> str:
    """Get use cases for a format"""
    config = get_format_config(format_name)
    use_cases = '\n'.join(f'- {case}' for case in config['use_cases'])
    return f"""### 🎯 Use Cases
{use_cases}"""

def get_import_example(format_name: str) -> str:
    """Get import example for a format"""
    config = get_format_config(format_name)
    return config['import_example']