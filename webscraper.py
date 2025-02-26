import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import random


class WebsiteCrawler:
    def __init__(self, base_url, output_dir="downloaded_site", max_depth=3, rate_limit=1):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.output_dir = output_dir
        self.visited_urls = set()
        self.rate_limit = rate_limit
        self.max_depth = max_depth
        self.stop_requested = False
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def stop(self):
        self.stop_requested = True
        print("\n[INFO] Stop requested. Finishing current page...")

    def is_valid_url(self, url):
        try:
            parsed = urlparse(url)

            # Skip any image files or unsupported formats
            invalid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico', '.pdf', '.zip', '.doc', '.docx')
            if url.lower().endswith(invalid_extensions):
                print(f"[SKIP] Invalid file type: {url}")
                return False

            # Skip special pages (e.g., Wikipedia)
            skip_patterns = [
                '/wiki/Wikipedia:', '/wiki/File:', '/wiki/Help:', '/wiki/Special:', '/wiki/Talk:',
                '/wiki/User:', '/wiki/Template:', '/wiki/Category:', '/wiki/Portal:',
                'action=', 'oldid=', 'diff=', 'printable=', 'mobileaction='
            ]
            if any(pattern in url for pattern in skip_patterns):
                print(f"[SKIP] Special page: {url}")
                return False

            # Ensure the URL belongs to the same domain
            is_valid = (
                parsed.netloc == self.domain and
                parsed.scheme in ['http', 'https']
            )

            if not is_valid:
                print(f"[SKIP] URL rejected: {url}")

            return is_valid

        except Exception as e:
            print(f"[ERROR] Error parsing URL {url}: {str(e)}")
            return False

    def clean_filename(self, url):
        # Remove the domain and scheme
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path.endswith('.html'):
            path += '.html'

        # Clean the filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', path)
        filepath = os.path.join(self.output_dir, filename)

        # Create subdirectories if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        return filepath

    def download_page(self, url):
        headers = {"User-Agent": random.choice(self.user_agents)}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"[SUCCESS] Downloaded: {url}")
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] Failed to download {url}: {str(e)}")
            return None

    def save_page(self, content, url):
        try:
            filepath = self.clean_filename(url)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[SUCCESS] Saved: {filepath}")
        except Exception as e:
            print(f"[ERROR] Error saving {url}: {str(e)}")

    def extract_links(self, content, url):
        soup = BeautifulSoup(content, 'html.parser')
        links = set()

        print(f"\n[INFO] Extracting links from {url}")
        link_count = 0

        for anchor in soup.find_all('a', href=True):
            link = urljoin(url, anchor['href'])
            if self.is_valid_url(link):
                links.add(link)
                link_count += 1

        print(f"[INFO] Found {link_count} valid links on this page")
        return links

    def crawl(self):
        queue = [(self.base_url, 0)]
        pages_processed = 0
        start_time = time.time()

        print(f"\n[INFO] Starting crawl of {self.base_url}")
        print(f"[INFO] Maximum depth: {self.max_depth}")

        while queue and not self.stop_requested:
            url, depth = queue.pop(0)

            if url in self.visited_urls or depth >= self.max_depth:
                continue

            pages_processed += 1
            print(f"\n[INFO] Processing page {pages_processed} at depth {depth}/{self.max_depth}")
            print(f"[INFO] URL: {url}")
            print(f"[INFO] Queue size: {len(queue)}")

            self.visited_urls.add(url)

            # Download the page
            content = self.download_page(url)
            if content:
                # Save the page
                self.save_page(content, url)

                # Extract and add new links to the queue
                if depth < self.max_depth - 1:
                    new_links = self.extract_links(content, url)
                    queue.extend([(link, depth + 1) for link in new_links if link not in self.visited_urls])

                # Rate limiting
                if queue and not self.stop_requested:
                    print(f"[INFO] Waiting {self.rate_limit} seconds before next page...")
                    time.sleep(self.rate_limit)

        elapsed_time = time.time() - start_time
        print(f"\n[INFO] Crawling completed!")
        if self.stop_requested:
            print("[INFO] Crawling was stopped by user")
        print(f"[INFO] Total pages processed: {pages_processed}")
        print(f"[INFO] Total unique URLs visited: {len(self.visited_urls)}")
        print(f"[INFO] Total time: {elapsed_time:.2f} seconds")


class WebCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler")
        self.root.geometry("600x500")
        self.crawler = None

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL input
        ttk.Label(main_frame, text="URL to crawl:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Output directory
        ttk.Label(main_frame, text="Output directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloaded_site"))
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)

        # Depth input
        ttk.Label(main_frame, text="Maximum depth:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.depth_var = tk.StringVar(value="3")
        depth_entry = ttk.Entry(main_frame, textvariable=self.depth_var, width=10)
        depth_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Rate limit input
        ttk.Label(main_frame, text="Rate limit (seconds):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.rate_limit_var = tk.StringVar(value="1")
        rate_limit_entry = ttk.Entry(main_frame, textvariable=self.rate_limit_var, width=10)
        rate_limit_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)

        # Log text area
        self.log_text = tk.Text(main_frame, height=15, width=60, wrap=tk.WORD)
        self.log_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Scrollbar for log
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Crawling", command=self.start_crawling)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop button (initially disabled)
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_crawling, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Redirect stdout to our log
        sys.stdout = self

    def write(self, text):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {text}")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def flush(self):
        pass

    def browse_output(self):
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)

    def stop_crawling(self):
        self.stop_button.configure(state='disabled')
        self.progress_var.set("Stopping...")
        if self.crawler:
            self.crawler.stop()

    def start_crawling(self):
        # Validate inputs
        url = self.url_var.get().strip()
        output_dir = self.output_var.get().strip()

        try:
            depth = int(self.depth_var.get())
            if depth < 1:
                raise ValueError("Depth must be at least 1")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid depth value. Please enter a positive number.")
            return

        try:
            rate_limit = float(self.rate_limit_var.get())
            if rate_limit < 0:
                raise ValueError("Rate limit must be non-negative")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid rate limit value. Please enter a non-negative number.")
            return

        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "URL must start with http:// or https://")
            return

        # Disable inputs while crawling
        self.start_button.configure(state='disabled')
        self.url_entry.configure(state='disabled')
        self.output_entry.configure(state='disabled')
        self.progress_var.set("Crawling...")

        # Clear log
        self.log_text.delete(1.0, tk.END)

        # Start crawling in a separate thread
        def crawl_thread():
            try:
                self.crawler = WebsiteCrawler(url, output_dir, depth, rate_limit)
                self.stop_button.configure(state='normal')  # Enable stop button
                self.crawler.crawl()
                if self.crawler.stop_requested:
                    self.root.after(0, self.crawling_finished, True, "Crawling stopped by user")
                else:
                    self.root.after(0, self.crawling_finished, True)
            except Exception as e:
                self.root.after(0, self.crawling_finished, False, str(e))

        threading.Thread(target=crawl_thread, daemon=True).start()

    def crawling_finished(self, success, error_message=None):
        # Re-enable inputs
        self.start_button.configure(state='normal')
        self.url_entry.configure(state='normal')
        self.output_entry.configure(state='normal')

        # Disable stop button
        self.stop_button.configure(state='disabled')

        if success:
            if error_message and "stopped by user" in error_message:
                self.progress_var.set("Crawling stopped")
                messagebox.showinfo("Stopped", "Website crawling was stopped by user")
            else:
                self.progress_var.set("Crawling completed!")
                messagebox.showinfo("Success", "Website crawling completed successfully!")
        else:
            self.progress_var.set("Error occurred!")
            messagebox.showerror("Error", f"An error occurred while crawling:\n{error_message}")


def main():
    root = tk.Tk()
    app = WebCrawlerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
