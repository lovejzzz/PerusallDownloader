# Perusall Article Downloader

A web application that helps download articles from Perusall as PDF files. This tool provides a user-friendly interface to download articles while maintaining their quality and organization.

## Features

- Easy-to-use web interface
- Real-time progress tracking
- Automatic PDF generation
- Clean and modern UI
- Cross-browser compatibility

## Project Structure

```
.
├── docs/               # Frontend files (GitHub Pages)
│   └── index.html     # Main web interface
├── backend/           # Backend server
│   ├── web_app.py    # Flask application
│   ├── app.py        # Legacy desktop app
│   └── requirements.txt
└── README.md
```

## How to Use

1. Visit [https://yourusername.github.io/perusall-downloader](https://yourusername.github.io/perusall-downloader)
2. Open your Perusall article in Chrome/Firefox
3. Press F12 to open Developer Tools
4. Click on the Console tab
5. Copy and paste the provided JavaScript code into the console
6. Copy the output from the console
7. Paste it into the web interface
8. Click "Download Article"
9. Wait for the process to complete
10. Click "Download PDF" when ready

## Development

### Frontend
The frontend is hosted on GitHub Pages from the `docs` directory. After making changes to the frontend:
1. Commit and push your changes
2. Go to repository Settings > Pages
3. Select the `docs` folder as the source

### Backend
The backend needs to be hosted separately (e.g., on Heroku, DigitalOcean, or AWS).

1. Clone the repository:
```bash
git clone https://github.com/yourusername/perusall-downloader.git
cd perusall-downloader/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python web_app.py
```

4. The server will run on http://localhost:5001

## Requirements

- Python 3.x
- Flask
- ImageMagick
- img2pdf

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
