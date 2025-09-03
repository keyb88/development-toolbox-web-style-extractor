# Web Style Extractor

**Extract colours, fonts, and CSS from any website**

Web Style Extractor analyses websites to extract their colour palettes and typography, then generates usable files for creating matching branded internal sites, wikis, and documentation. Perfect for maintaining consistent branding across your organisation's web properties.

## What it does

Give it a website URL, and it will:
- Pull out all the colours used on the site
- Find all the fonts and typography
- Generate usable files you can actually use in your projects

Perfect for creating branded internal wikis or sites that match your organisation's main website. Extract the colours and fonts from your company's public site, then apply that theme to your internal documentation, wikis, or employee portals.

## Key Features

### 🎨 **Advanced Colour Analysis**
- Extracts colours from CSS stylesheets and computed styles
- Converts colours to modern OKLCH colour space for better perceptual uniformity
- Generates semantic colour mapping (primary, secondary, background, text)
- Creates dynamic colour variations using CSS relative colour syntax
- Provides visual colour swatches with accessibility information

### 🔤 **Intelligent Typography Detection**
- Identifies all font families from CSS rules and computed styles
- Automatically categorises fonts (serif, sans-serif, monospace, display)
- Generates fallback-aware font declarations
- Creates fluid typography scales using `clamp()` functions
- Provides live font rendering previews in HTML output

### 🚀 **Modern CSS Features**
- Detects and generates container query patterns
- Identifies CSS nesting structures
- Extracts existing CSS custom properties (variables)
- Creates systematic design token structures
- Supports cutting-edge CSS selectors (`:has()`, `:is()`, `:where()`)

### 📊 **Multi-Format Output System**
- **MediaWiki Templates**: Ready-to-use documentation for wikis
- **JSON Data**: Structured format for APIs and automation
- **Modern CSS**: Production-ready stylesheets with OKLCH colours
- **Tailwind Configuration**: Drop-in config files with extracted palettes
- **Design Tokens**: Style Dictionary-compatible JSON format
- **HTML Reports**: Interactive documentation with live previews
- **Traditional CSS**: Standard CSS variables and utility classes

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser (for computed style extraction)

### Setup
```bash
# Clone the repository
git clone https://github.com/development-toolbox/development-toolbox-web-style-extractor.git
cd development-toolbox-web-style-extractor

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- `requests` - HTTP requests for fetching web content
- `beautifulsoup4` - HTML and CSS parsing
- `cssutils` - CSS processing and manipulation
- `selenium` - Web browser automation for computed styles
- `webdriver-manager` - Automatic Chrome WebDriver management

## Quick Start

Extract styles from any website:

```bash
# Basic extraction (MediaWiki format)
python style_extractor.py https://github.com

# Generate JSON for API integration
python style_extractor.py https://github.com --output json

# Create Tailwind CSS configuration
python style_extractor.py https://github.com --output tailwind

# Generate design tokens
python style_extractor.py https://github.com --output design-tokens
```

### Project Structure
After extraction, files are organised in the `projects/` directory:

```
projects/
└── github.com/
    ├── styles.json          # Main output file (format-dependent)
    ├── metadata.txt         # Extraction metadata and statistics
    ├── README.md           # Project documentation
    └── README.html         # Interactive preview with live fonts
```

## Output Formats

### MediaWiki Template
**File**: `styles.mediawiki`  
**Purpose**: Documentation wikis and knowledge bases

```mediawiki
== Style Guide for https://github.com ==

'''Body Background:''' rgb(13, 17, 23)
'''Primary Colours:''' #1f883d, #0757ba, #197935

{| class="wikitable"
|-
! Colour !! Value !! Usage
|-
| style='background-color: #1f883d' | 
| <code>#1f883d</code>
| Primary success colour
|}
```

### JSON Data Structure
**File**: `styles.json`  
**Purpose**: API integration and programmatic access

```json
{
  "url": "https://github.com",
  "extraction_date": "2025-09-03T10:15:24Z",
  "styles": {
    "body_background": "rgb(13, 17, 23)",
    "body_font": "-apple-system, BlinkMacSystemFont, \"Segoe UI\""
  },
  "colors": ["#ffffff", "#1f883d", "#0757ba"],
  "fonts": ["SF Pro Display", "Helvetica Neue", "Arial"]
}
```

### Design Tokens
**File**: `design-tokens.json`  
**Purpose**: Cross-platform design systems

```json
{
  "designSystem": {
    "colors": {
      "semantic": {
        "primary": {
          "value": "#1f883d",
          "oklch": "oklch(32.7% 0.233 137.1deg)",
          "type": "color",
          "description": "Primary brand colour"
        }
      }
    },
    "typography": {
      "fontSizes": {
        "base": {
          "value": "clamp(1rem, 2.5vw, 1.125rem)",
          "static": "1rem",
          "type": "fontSize.fluid"
        }
      }
    }
  }
}
```

### Tailwind Configuration
**File**: `tailwind.config.js`  
**Purpose**: Tailwind CSS projects

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'github-green': '#1f883d',
        'github-blue': '#0757ba',
        'github-dark': '#0d1117'
      },
      fontFamily: {
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI']
      }
    }
  }
}
```

## Advanced Usage

### Custom Project Names
```bash
python style_extractor.py https://example.com --project-name "Company Style Guide"
```

### Modern CSS Features
```bash
# Generate cutting-edge CSS with OKLCH colours and container queries
python style_extractor.py https://example.com --output modern-css
```

### Batch Processing
```bash
# Extract from multiple sites
python style_extractor.py https://github.com --output json
python style_extractor.py https://tailwindcss.com --output tailwind  
python style_extractor.py https://figma.com --output design-tokens
```

## Use Cases

### 🏢 **Brand-Consistent Internal Sites**
Extract your company's website colours and fonts to create matching internal wikis, documentation sites, and employee portals. No more guessing at brand colours or hunting through CSS files.

### 📝 **MediaWiki Theming**
Generate ready-to-paste MediaWiki templates with your organisation's exact colour scheme. Perfect for company wikis that need to match corporate branding.

### 🛠️ **Development Workflows**  
Extract design tokens for automated build processes, generate CSS variables, and create Tailwind configurations for rapid prototyping.

### 📊 **Competitive Analysis**
Analyse competitor websites to understand their design choices, colour schemes, and typography systems.

### 🔄 **Legacy Site Updates**
Extract styles from existing sites and convert them to modern CSS formats for easier maintenance and updates.

## Technical Architecture

### Colour Processing
- **Extraction**: Parses CSS stylesheets and computes live styles using Chrome WebDriver
- **Conversion**: Transforms colours to OKLCH colour space using advanced colour theory algorithms  
- **Classification**: Categorises colours by usage context and semantic meaning
- **Optimisation**: Generates dynamic variations using CSS relative colour syntax

### Typography Analysis
- **Detection**: Identifies font families from CSS rules and rendered elements
- **Classification**: Categorises fonts by type and usage (display, body, monospace)
- **Optimisation**: Creates fallback stacks and fluid typography scales
- **Preview**: Generates live font rendering in HTML outputs

### Output Generation
- **Template System**: Uses Jinja2-style templating for consistent formatting
- **Format Adaptation**: Tailors content and instructions for each output format
- **Validation**: Ensures generated code is syntactically correct and production-ready
- **Documentation**: Creates comprehensive guides with usage examples

## Configuration

### Browser Settings
The tool uses Chrome in headless mode for computed style extraction. Ensure Chrome is installed and up-to-date.

### Custom Templates
Templates can be customised by modifying files in the `templates/` directory.

### Format Configuration
Output formats are configured in `format_configs.py` with format-specific content, capabilities, and usage instructions.

## Troubleshooting

### Common Issues

**Chrome WebDriver Errors**
```bash
# The tool automatically manages WebDriver installation
# Ensure Chrome browser is installed and accessible
```

**Network Timeouts**
```bash
# Some websites block automated requests
# The tool will fall back to basic CSS extraction when needed
```

**Permission Errors**
```bash
# Ensure write permissions for the projects/ directory
chmod 755 projects/
```

### Debug Mode
Enable detailed logging:
```bash
export PYTHONPATH=.
python -m logging.basicConfig level=DEBUG style_extractor.py
```

## Contributing

### Development Setup
```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR-USERNAME/development-toolbox-web-style-extractor.git
cd development-toolbox-web-style-extractor

# Add upstream remote
git remote add upstream https://github.com/development-toolbox/development-toolbox-web-style-extractor.git

# Install development dependencies
pip install -r requirements.txt
```

### Contributing Workflow
1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create a branch** for your feature: `git checkout -b my-new-feature`
4. **Make your changes** and test them
5. **Commit** your changes: `git commit -am 'Add some feature'`
6. **Push** to your fork: `git push origin my-new-feature`
7. **Create a Pull Request** from your fork to the main repository

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Add docstrings for public methods
- Include unit tests for new features

### Testing
```bash
# Run test suite
python -m pytest tests/

# Test specific output format
python style_extractor.py https://example.com --output json
```

## Changelog

### Version 1.2.0 (Current)
- Added comprehensive format-specific configuration system
- Improved OKLCH colour space conversion accuracy  
- Enhanced design token generation with Style Dictionary compatibility
- Added fluid typography with clamp() function support
- Implemented professional UK English documentation
- Fixed version handling and removed premature version claims

### Version 1.1.0
- Added design tokens output format
- Implemented Tailwind CSS configuration generation
- Enhanced colour extraction accuracy
- Added HTML preview with live font rendering

### Version 1.0.0
- Initial release
- Basic colour and font extraction
- MediaWiki template generation
- JSON output format

## Licence

MIT Licence. See `LICENCE` file for details.

## Support

For issues, feature requests, or questions:
- Create an issue on GitHub
- Review the troubleshooting guide above
- Check existing documentation in `docs/`

---

**Built with modern web standards and professional development practices.**