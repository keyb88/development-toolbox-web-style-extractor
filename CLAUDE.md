# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Web Style Extractor** - A Python tool that extracts colours, fonts, and CSS from websites to generate design system files in multiple formats (MediaWiki, JSON, Tailwind, Design Tokens, Modern CSS).

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Verify Chrome is installed (required for computed style extraction)
google-chrome --version || chrome --version
```

### Running the Tool
```bash
# Basic extraction (MediaWiki format)
python style_extractor.py https://example.com

# Specify output format
python style_extractor.py https://example.com --output json
python style_extractor.py https://example.com --output tailwind
python style_extractor.py https://example.com --output design-tokens
python style_extractor.py https://example.com --output modern-css

# Custom project name
python style_extractor.py https://example.com --project-name "My Style Guide"
```

### Testing and Validation
```bash
# Test extraction on a known site
python style_extractor.py https://github.com --output json

# Enable debug mode for troubleshooting
export PYTHONPATH=.
python -m logging.basicConfig level=DEBUG style_extractor.py https://example.com
```

## Architecture

### Core Components

**WebStyleExtractor** (`style_extractor.py`)
- Main extraction class that orchestrates the entire process
- Uses Selenium WebDriver for computed styles and BeautifulSoup for CSS parsing
- Handles both static CSS extraction and dynamic computed styles

**ColorConverter** (`style_extractor.py`)
- Converts colours between formats (hex, RGB, OKLCH)
- Generates semantic colour mappings and variations
- Creates modern CSS relative colour syntax

**Format Configurations** (`format_configs.py`)
- Defines output format specifications and capabilities
- Contains format-specific content, templates, and usage instructions
- Maps to file extensions and terminal messages

### Data Flow
1. **Fetch**: Downloads HTML and CSS from target URL
2. **Parse**: Extracts colours and fonts from CSS rules and computed styles
3. **Process**: Converts colours to OKLCH, categorises fonts, creates semantic mappings
4. **Generate**: Creates format-specific output files using templates
5. **Save**: Organises outputs in `projects/{domain}/` structure

### Output Directory Structure
```
projects/{domain}/
├── styles.{format}     # Main output file (format-dependent)
├── metadata.txt        # Extraction metadata and statistics
├── README.md          # Project documentation
└── README.html        # Interactive preview with live fonts
```

### Template System
Templates in `templates/` directory define output structure:
- `base_*.html` - HTML report templates
- `base_*.wiki` - MediaWiki templates
- `color_table_*` - Colour palette formatting
- `font_table_*` - Typography documentation

## Key Dependencies

- **requests**: HTTP requests for fetching web content
- **beautifulsoup4**: HTML and CSS parsing
- **cssutils**: CSS processing and manipulation
- **selenium**: WebDriver for computed styles extraction
- **webdriver-manager**: Automatic ChromeDriver management
- **pillow**: Image processing for favicon analysis

## Output Formats

### Available Formats
- `mediawiki` - Wiki documentation templates
- `json` - Structured data for APIs
- `tailwind` - Tailwind CSS configuration
- `design-tokens` - Style Dictionary compatible tokens
- `modern-css` - OKLCH colours with CSS features
- `traditional-css` - Standard CSS variables

### Format Selection Logic
Each format in `format_configs.py` defines:
- File extension and naming
- Content structure and capabilities
- Usage instructions and examples
- Terminal output messages

## Error Handling

The extractor handles common issues gracefully:
- Falls back to basic CSS extraction if WebDriver fails
- Continues with partial data if some resources fail to load
- Validates colour formats before conversion
- Creates default values for missing style properties

## File Processing Notes

- CSS extraction combines inline styles, `<style>` tags, and external stylesheets
- Font detection includes both CSS rules and computed styles
- Colour extraction deduplicates and sorts by frequency
- OKLCH conversion provides perceptually uniform colour spaces
- Template rendering uses string formatting (no Jinja2 dependency)