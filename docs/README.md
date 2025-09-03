# 🎨 Web Style Extractor

A Python tool that extracts color schemes, fonts, and styling information from websites and generates output in multiple formats (MediaWiki templates, HTML reports, JSON data).

## ✨ Features

- ✅ Extract color palettes from CSS and images
- ✅ Identify font families used on websites
- ✅ Capture computed styles (backgrounds, headings, links)
- ✅ Generate MediaWiki templates for documentation
- ✅ Create HTML reports with visual previews
- ✅ Export structured JSON data
- ✅ Organized output in domain-specific project folders

## 📦 Installation

1. Install Python 3.7+ and pip
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure Chrome browser is installed (for computed style extraction)

## 🚀 Quick Start

```bash
# Extract styles in MediaWiki format (default)
python style_extractor.py https://example.com

# Generate JSON output
python style_extractor.py https://github.com --output json

# Create HTML report
python style_extractor.py https://stackoverflow.com --output html

# Custom output file
python style_extractor.py https://example.com --output-file my-custom-styles.wiki
```

## Output Structure

The tool creates organized project folders:

```
projects/
├── example.com/
│   ├── styles.mediawiki     # MediaWiki template
│   ├── styles.html          # HTML report  
│   ├── styles.json          # JSON data
│   └── metadata.txt         # Extraction info
├── github.com/
│   └── styles.mediawiki
└── stackoverflow.com/
    └── styles.html
```

## 📋 Output Formats

### 📝 MediaWiki Template (`--output mediawiki`)
Creates wiki markup that can be copied directly into MediaWiki pages. Perfect for documentation wikis and style guides.
- 📋 [How to use MediaWiki templates →](mediawiki-usage.md)

### 📊 HTML Report (`--output html`)  
Generates a visual HTML report with color swatches and font previews. Great for presentations and design reviews.

### 💾 JSON Data (`--output json`)
Structured data format perfect for integrating with other tools, APIs, or automated workflows.

## ⚙️ Command Line Options

```bash
python style_extractor.py [URL] [OPTIONS]

Arguments:
  url                    Website URL to analyze

Options:
  --output, -o          Output format: mediawiki, html, json (default: mediawiki)
  --output-file, -f     Custom output file path
  --help, -h            Show help message
```

## 📝 Examples

### Extract GitHub's Color Scheme
```bash
python style_extractor.py https://github.com --output json
# Creates: projects/github.com/styles.json
```

### Generate MediaWiki Template for Documentation
```bash
python style_extractor.py https://docs.python.org --output mediawiki
# Creates: projects/docs.python.org/styles.mediawiki
```

### Create Visual HTML Report
```bash
python style_extractor.py https://stackoverflow.com --output html  
# Creates: projects/stackoverflow.com/styles.html
```

## What Gets Extracted

- **Colors**: Hex colors from CSS, RGB values, dominant image colors
- **Fonts**: Font families from CSS rules and computed styles
- **Background**: Body background color/image
- **Headings**: H1-H6 text colors and styling
- **Links**: Link colors and hover states
- **Images**: Dominant colors from hero/featured images

## Troubleshooting

### Chrome Driver Issues
If you get WebDriver errors:
1. Make sure Chrome is installed
2. Check that Chrome path is correct in the script
3. Try updating Chrome to latest version

### Missing Dependencies
```bash
pip install beautifulsoup4 cssutils Pillow selenium webdriver-manager requests
```

### Network Issues
- Some sites block automated requests
- Try different user agents or headers
- Check if the site requires authentication

## Project Structure

```
style-extractor/
├── style_extractor.py       # Main script
├── requirements.txt         # Dependencies
├── templates/              # Output templates
│   ├── base_mediawiki.wiki
│   ├── base_html.html
│   └── color_table_*.* 
├── projects/               # Generated outputs
├── docs/                   # Documentation
│   ├── README.md          # This file
│   ├── mediawiki-usage.md # MediaWiki guide
│   └── examples/          # Sample outputs
```

## Contributing

Feel free to submit issues and pull requests to improve the tool!

## License

This project is open source. Use it however you'd like!