import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import os
import subprocess
from textwrap import dedent
import threading
import queue

class PerusallDownloader(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Perusall Article Downloader")
        self.geometry("800x900")  # Increased height to ensure button visibility
        self.minsize(800, 900)    # Set minimum size to prevent window from being too small

        # Instructions
        instructions_frame = ttk.LabelFrame(self, text="Instructions", padding="10")
        instructions_frame.pack(fill="x", padx=10, pady=5)

        instructions_text = """1. Open your Perusall article in Chrome/Firefox
2. Press F12 to open Developer Tools
3. Click on Console tab
4. Copy and paste the code below into the console
5. Copy the output from the console and paste it in the input area below"""

        # Make instructions selectable
        instructions_area = tk.Text(instructions_frame, height=5, wrap=tk.WORD)
        instructions_area.insert("1.0", instructions_text)
        instructions_area.configure(state='disabled')
        instructions_area.pack(fill="x")

        # Code frame with copy button
        code_frame = ttk.LabelFrame(self, text="JavaScript Code", padding="10")
        code_frame.pack(fill="x", padx=10, pady=5)

        self.js_code = '''var len = 0; 
var times = 0;
var i = setInterval(() => { 
    var img = document.querySelectorAll("img.chunk"); 
    img[img.length-1].scrollIntoView(); 
    if (len < img.length) {
        len = img.length;
    } else if (times > 3) {
        var urls = [];
        img.forEach((e) => urls.push(e.src));
        var spl = location.pathname.split('/');
        console.info('urls = """\\n' + urls.join('\\n') + '\\n"""\\n\\ntitle="' + spl[spl.length-1] + '"');
        clearInterval(i);
    } else {
        times++;
    }
}, 2000);'''

        # Code text area
        self.code_area = tk.Text(code_frame, height=15, wrap=tk.NONE)
        self.code_area.insert("1.0", self.js_code)
        self.code_area.configure(state='disabled')
        
        # Add horizontal scrollbar for code
        code_scroll_x = ttk.Scrollbar(code_frame, orient="horizontal", command=self.code_area.xview)
        self.code_area.configure(xscrollcommand=code_scroll_x.set)
        
        # Copy button
        copy_button = ttk.Button(code_frame, text="Copy Code", command=self.copy_code)
        
        # Pack code widgets
        self.code_area.pack(fill="x", expand=True)
        code_scroll_x.pack(fill="x")
        copy_button.pack(pady=5)

        # Combined console frame
        self.console_frame = ttk.LabelFrame(self, text="Console", padding="10")
        self.console_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Input label
        ttk.Label(self.console_frame, text="Paste console output here:").pack(anchor="w")

        # Input area
        self.text_area = scrolledtext.ScrolledText(self.console_frame, height=8, wrap=tk.WORD)
        self.text_area.pack(fill="x", pady=(0, 10))

        # Separator
        ttk.Separator(self.console_frame, orient='horizontal').pack(fill='x', pady=5)

        # Console output label
        ttk.Label(self.console_frame, text="Download progress:").pack(anchor="w")

        # Console output
        self.console = scrolledtext.ScrolledText(self.console_frame, height=15, wrap=tk.WORD, bg='black', fg='white')
        self.console.pack(fill="both", expand=True)

        # Progress bar (hidden initially)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.console_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.pack_forget()  # Hide initially

        # Download button (below console)
        ttk.Button(self, text="Download Article", command=self.start_download).pack(pady=(0, 10))

        # Queue for thread communication
        self.queue = queue.Queue()
        self.is_downloading = False

    def copy_code(self):
        """Copy the JavaScript code to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.js_code)
        messagebox.showinfo("Success", "Code copied to clipboard!")

    def log(self, message):
        """Add message to console"""
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.update_idletasks()

    def start_download(self):
        """Start download in a separate thread"""
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress!")
            return

        self.is_downloading = True
        self.progress_var.set(0)
        self.console.delete(1.0, tk.END)
        self.progress_bar.pack(fill="x", pady=(5, 0))  # Show progress bar
        self.log("Starting download...")
        
        # Start download thread
        thread = threading.Thread(target=self.download_article)
        thread.daemon = True
        thread.start()

        # Start checking queue
        self.after(100, self.check_queue)

    def check_queue(self):
        """Check queue for messages from download thread"""
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg.get('type') == 'progress':
                    self.progress_var.set(msg['value'])
                elif msg.get('type') == 'log':
                    self.log(msg['message'])
                elif msg.get('type') == 'error':
                    messagebox.showerror("Error", msg['message'])
                    self.is_downloading = False
                    self.progress_bar.pack_forget()  # Hide progress bar on error
                    return
                elif msg.get('type') == 'done':
                    messagebox.showinfo("Success", msg['message'])
                    self.is_downloading = False
                    self.progress_bar.pack_forget()  # Hide progress bar when done
                    return
        except queue.Empty:
            if self.is_downloading:
                self.after(100, self.check_queue)

    def download_article(self):
        """Download article in background thread"""
        try:
            # Extract urls and title from input
            content = self.text_area.get("1.0", tk.END).strip()
            
            # Parse the content
            exec(content, globals())
            
            if 'urls' not in globals() or 'title' not in globals():
                self.queue.put({'type': 'error', 'message': "Invalid input format. Make sure you copied the entire console output."})
                return

            folder = title.replace(' ', '-')

            # Create a folder for the downloaded images
            if not os.path.exists(folder):
                os.mkdir(folder)

            # Count total URLs for progress
            total_urls = len([u for u in urls.splitlines() if u])
            downloaded = 0

            # Download each image from the URLs provided
            for u in urls.splitlines():
                if u:
                    self.queue.put({'type': 'log', 'message': f'Downloading chunk {downloaded} of {total_urls}'})
                    with open(f'{folder}/{downloaded:0>2}.png', 'wb') as f:
                        f.write(requests.get(u.strip()).content)
                    downloaded += 1
                    progress = (downloaded / total_urls) * 50  # First 50% for downloads
                    self.queue.put({'type': 'progress', 'value': progress})

            # Change to the folder where images were downloaded
            os.chdir(folder)

            self.queue.put({'type': 'log', 'message': 'Converting images to pages...'})
            
            pgno = 1
            # Count number of PNG files
            i = len([f for f in os.listdir() if f.endswith('.png') and f[:2].isdigit()])
            total_pages = (i + 5) // 6  # Round up division by 6

            # Combine every 6 images into a single page
            for j in range(0, i, 6):
                f = ' '.join([f'{k:0>2}.png' for k in range(j, min(i, j + 6))])
                self.queue.put({'type': 'log', 'message': f'Converting page {pgno} of {total_pages}'})
                command = f'/opt/homebrew/bin/magick convert -append {f} page_{pgno}.png'
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    self.queue.put({'type': 'error', 'message': f'Error during conversion: {result.stderr}'})
                    return
                pgno += 1
                progress = 50 + (pgno / (total_pages + 1)) * 40  # Next 40% for conversion

            # Convert all combined pages into a single PDF
            self.queue.put({'type': 'log', 'message': 'Creating final PDF...'})
            pages = ' '.join([f'page_{k}.png' for k in range(1, pgno)])
            command = f'/Library/Frameworks/Python.framework/Versions/3.12/bin/img2pdf {pages} -o "{folder}.pdf"'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                self.queue.put({'type': 'error', 'message': f'Error during PDF creation: {result.stderr}'})
                return

            self.queue.put({'type': 'progress', 'value': 95})
            self.queue.put({'type': 'log', 'message': 'Cleaning up temporary files...'})

            # Delete all PNG files after PDF is created
            for f in os.listdir():
                if f.endswith('.png'):
                    os.remove(f)

            os.chdir('..')
            self.queue.put({'type': 'progress', 'value': 100})
            self.queue.put({'type': 'done', 'message': f'Done! PDF saved as: {folder}.pdf'})

        except Exception as e:
            self.queue.put({'type': 'error', 'message': str(e)})

if __name__ == "__main__":
    app = PerusallDownloader()
    app.mainloop()
