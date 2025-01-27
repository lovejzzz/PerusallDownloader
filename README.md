# Perusall Article Downloader

A web application that helps download articles from Perusall as PDF files. This tool provides a user-friendly interface to download articles while maintaining their quality and organization.

## Features

- Easy-to-use web interface
- Real-time progress tracking
- Automatic PDF generation
- Clean and modern UI
- Cross-browser compatibility

## How to Use

1. Open your Perusall article in Chrome/Firefox
2. Press F12 to open Developer Tools
3. Click on the Console tab
4. Copy and paste the provided JavaScript code into the console
5. Copy the output from the console
6. Paste it into the web interface
7. Click "Download Article"
8. Wait for the process to complete
9. Click "Download PDF" when ready

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/perusall-downloader.git
cd perusall-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python web_app.py
```

4. Open http://localhost:5001 in your browser

## Requirements

- Python 3.x
- Flask
- ImageMagick
- img2pdf

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
