from flask import Flask, request, jsonify, send_file
import requests
import os
import subprocess
from threading import Thread
import time
import shutil
from flask_cors import CORS
import tempfile
from pathlib import Path

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Store download progress and file paths
downloads = {}

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/download', methods=['POST'])
def start_download():
    try:
        data = request.json
        if not data or 'urls' not in data or 'title' not in data:
            return jsonify({'error': 'Invalid input format'}), 400

        # Generate unique download ID
        download_id = str(int(time.time()))
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        downloads[download_id] = {
            'progress': 0,
            'status': 'starting',
            'messages': [],
            'error': None,
            'temp_dir': temp_dir,
            'pdf_path': None
        }

        # Start download in background
        Thread(target=process_download, args=(download_id, data['urls'], data['title'])).start()

        return jsonify({'download_id': download_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<download_id>')
def get_status(download_id):
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    status_data = {
        'progress': downloads[download_id]['progress'],
        'status': downloads[download_id]['status'],
        'messages': downloads[download_id]['messages'],
        'error': downloads[download_id]['error']
    }
    
    # Add download URL if PDF is ready
    if downloads[download_id]['status'] == 'completed' and downloads[download_id]['pdf_path']:
        status_data['download_url'] = f'/api/pdf/{download_id}'
    
    return jsonify(status_data)

@app.route('/api/pdf/<download_id>')
def get_pdf(download_id):
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    download_info = downloads[download_id]
    if not download_info['pdf_path'] or not os.path.exists(download_info['pdf_path']):
        return jsonify({'error': 'PDF not found'}), 404

    try:
        return send_file(
            download_info['pdf_path'],
            as_attachment=True,
            download_name=os.path.basename(download_info['pdf_path'])
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def log_message(download_id, message):
    downloads[download_id]['messages'].append(message)

def update_progress(download_id, progress, status=None):
    downloads[download_id]['progress'] = progress
    if status:
        downloads[download_id]['status'] = status

def process_download(download_id, urls_str, title):
    try:
        temp_dir = downloads[download_id]['temp_dir']
        folder = title.replace(' ', '-')
        work_dir = os.path.join(temp_dir, folder)
        
        # Create folder
        os.makedirs(work_dir)

        # Download images
        urls = [u for u in urls_str.splitlines() if u]
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            log_message(download_id, f'Downloading chunk {i+1} of {total_urls}')
            with open(os.path.join(work_dir, f'{i:0>2}.png'), 'wb') as f:
                f.write(requests.get(url.strip()).content)
            progress = ((i + 1) / total_urls) * 50
            update_progress(download_id, progress, 'downloading')

        # Change to work directory
        original_dir = os.getcwd()
        os.chdir(work_dir)

        # Convert images to pages
        log_message(download_id, 'Converting images to pages...')
        pgno = 1
        i = len([f for f in os.listdir() if f.endswith('.png') and f[:2].isdigit()])
        total_pages = (i + 5) // 6

        for j in range(0, i, 6):
            f = ' '.join([f'{k:0>2}.png' for k in range(j, min(i, j + 6))])
            log_message(download_id, f'Converting page {pgno} of {total_pages}')
            command = f'/opt/homebrew/bin/magick convert -append {f} page_{pgno}.png'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f'Error during conversion: {result.stderr}')
            pgno += 1
            progress = 50 + (pgno / (total_pages + 1)) * 40
            update_progress(download_id, progress, 'converting')

        # Create PDF
        log_message(download_id, 'Creating final PDF...')
        pdf_filename = f'{folder}.pdf'
        pages = ' '.join([f'page_{k}.png' for k in range(1, pgno)])
        command = f'/Library/Frameworks/Python.framework/Versions/3.12/bin/img2pdf {pages} -o "{pdf_filename}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f'Error during PDF creation: {result.stderr}')

        # Store PDF path
        downloads[download_id]['pdf_path'] = os.path.abspath(pdf_filename)

        # Clean up
        update_progress(download_id, 95, 'cleaning')
        log_message(download_id, 'Cleaning up temporary files...')
        for f in os.listdir():
            if f.endswith('.png'):
                os.remove(f)

        os.chdir(original_dir)
        update_progress(download_id, 100, 'completed')
        log_message(download_id, f'Done! Click the download button to get your PDF.')

    except Exception as e:
        downloads[download_id]['error'] = str(e)
        downloads[download_id]['status'] = 'error'
        log_message(download_id, f'Error: {str(e)}')
    finally:
        # Schedule cleanup of temporary directory after some time
        def cleanup_temp():
            time.sleep(3600)  # Keep files for 1 hour
            try:
                shutil.rmtree(downloads[download_id]['temp_dir'])
                del downloads[download_id]
            except:
                pass
        Thread(target=cleanup_temp, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
