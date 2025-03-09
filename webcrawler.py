import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import os
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from datetime import datetime
import pandas as pd
import html


from crawler.robots import RobotsParser
from crawler.proxy_manager import ProxyManager
from crawler.url_filter import URLFilter
from crawler.stats import CrawlerStats
from gui.dashboard import Dashboard
from gui.visualization import CrawlerVisualization

class EnhancedWebCrawler:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler")
        self.root.geometry("1200x800")

        self.user_agent_var = tk.StringVar(value="WebCrawler/1.0")
        self.crawled_data = []

        self.setup_logging()

        self.robots_parser = RobotsParser(user_agent=self.user_agent_var.get())
        self.proxy_manager = ProxyManager()
        self.url_filter = URLFilter()
        self.stats = CrawlerStats()

        self.crawl_queue = queue.Queue()
        self.visited_urls = set()
        self.stop_requested = False
        self.pause_requested = False
        self.thread_pool = None
        self.max_workers = 5

        self.setup_ui()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Crawler")

        self.setup_url_frame()

        self.setup_settings_frame()

        self.setup_filter_frame()

        self.setup_control_frame()

        self.setup_status_frame()

        self.dashboard = Dashboard(self.notebook)
        self.notebook.add(self.dashboard, text="Dashboard")

        self.visualization = CrawlerVisualization(self.notebook)
        self.notebook.add(self.visualization, text="Visualization")

    def setup_url_frame(self):
        url_frame = ttk.LabelFrame(self.main_frame, text="URL Configuration", padding="5")
        url_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(url_frame, text="Start URL:").grid(row=0, column=0, sticky="w", padx=5)
        self.url_var = tk.StringVar()
        ttk.Entry(url_frame, textvariable=self.url_var, width=80).grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)

    def setup_settings_frame(self):
        settings_frame = ttk.LabelFrame(self.main_frame, text="Crawler Settings", padding="5")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(settings_frame, text="Max Depth:").grid(row=0, column=0, sticky="w", padx=5)
        self.depth_var = tk.StringVar(value="3")
        ttk.Entry(settings_frame, textvariable=self.depth_var, width=10).grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(settings_frame, text="Concurrent Workers:").grid(row=0, column=2, sticky="w", padx=5)
        self.workers_var = tk.StringVar(value="5")
        ttk.Entry(settings_frame, textvariable=self.workers_var, width=10).grid(row=0, column=3, sticky="w", padx=5)

        ttk.Label(settings_frame, text="Rate Limit (seconds):").grid(row=1, column=0, sticky="w", padx=5)
        self.rate_limit_var = tk.StringVar(value="1")
        ttk.Entry(settings_frame, textvariable=self.rate_limit_var, width=10).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(settings_frame, text="User Agent:").grid(row=1, column=2, sticky="w", padx=5)
        self.user_agent_var = tk.StringVar(value="EnhancedWebCrawler/1.0")
        ttk.Entry(settings_frame, textvariable=self.user_agent_var, width=40).grid(row=1, column=3, columnspan=2, sticky="w", padx=5)

    def setup_filter_frame(self):
        filter_frame = ttk.LabelFrame(self.main_frame, text="URL Filters", padding="5")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Include Pattern:").grid(row=0, column=0, sticky="w", padx=5)
        self.include_pattern_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.include_pattern_var, width=40).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(filter_frame, text="Add Include", command=self.add_include_pattern).grid(row=0, column=2, padx=5)

        ttk.Label(filter_frame, text="Exclude Pattern:").grid(row=1, column=0, sticky="w", padx=5)
        self.exclude_pattern_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.exclude_pattern_var, width=40).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(filter_frame, text="Add Exclude", command=self.add_exclude_pattern).grid(row=1, column=2, padx=5)

    def setup_control_frame(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_crawling)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_crawling, state="disabled")
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_crawling, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.export_button = ttk.Button(control_frame, text="Export Report", command=self.show_export_dialog, state="disabled")
        self.export_button.pack(side=tk.LEFT, padx=5)

    def setup_status_frame(self):
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="5")
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(fill=tk.X)

    def add_include_pattern(self):
        pattern = self.include_pattern_var.get().strip()
        if pattern:
            self.url_filter.add_include_pattern(pattern)
            self.include_pattern_var.set("")
            messagebox.showinfo("Success", f"Added include pattern: {pattern}")

    def add_exclude_pattern(self):
        pattern = self.exclude_pattern_var.get().strip()
        if pattern:
            self.url_filter.add_exclude_pattern(pattern)
            self.exclude_pattern_var.set("")
            messagebox.showinfo("Success", f"Added exclude pattern: {pattern}")

    def validate_inputs(self) -> bool:
        try:
            max_depth = int(self.depth_var.get())
            max_workers = int(self.workers_var.get())
            rate_limit = float(self.rate_limit_var.get())

            if max_depth < 1 or max_workers < 1 or rate_limit < 0:
                raise ValueError("Invalid input values")

            return True
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for depth, workers, and rate limit")
            return False

    def start_crawling(self):
        if not self.validate_inputs():
            return

        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a start URL")
            return

        self.stop_requested = False
        self.pause_requested = False
        self.visited_urls.clear()
        while not self.crawl_queue.empty():
            self.crawl_queue.get()

        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        self.status_var.set("Crawling...")


        self.stats.start_session()
        self.visualization.reset()

        self.thread_pool = ThreadPoolExecutor(max_workers=int(self.workers_var.get()))
        threading.Thread(target=self.crawl_worker, args=(url,), daemon=True).start()

        self.update_stats()

    def pause_crawling(self):
        if self.pause_requested:
            self.pause_requested = False
            self.pause_button.configure(text="Pause")
            self.status_var.set("Crawling...")
        else:
            self.pause_requested = True
            self.pause_button.configure(text="Resume")
            self.status_var.set("Paused")

    def stop_crawling(self):
        self.stop_requested = True
        self.status_var.set("Stopping...")
        self.pause_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")

    def crawl_worker(self, start_url: str):
        try:
            self.crawl_queue.put((start_url, 0))
            max_depth = int(self.depth_var.get())
            rate_limit = float(self.rate_limit_var.get())

            while not self.stop_requested and not self.crawl_queue.empty():
                if self.pause_requested:
                    time.sleep(1)
                    continue

                url, depth = self.crawl_queue.get()
                if depth > max_depth or url in self.visited_urls:
                    continue

                if not self.url_filter.should_crawl(url):
                    continue

                self.process_url(url, depth)
                time.sleep(rate_limit)

            self.crawl_completed()

        except Exception as e:
            self.logger.error(f"Crawl worker error: {str(e)}")
            self.crawl_completed(error=str(e))

    def process_url(self, url: str, depth: int):
        try:
            self.logger.info(f"Starting to process URL: {url} at depth {depth}")

            if not self.robots_parser.can_fetch(url):
                self.logger.info(f"Skipping {url} - not allowed by robots.txt")
                return

            self.logger.debug(f"Current queue size: {self.crawl_queue.qsize()}")
            self.logger.debug(f"Visited URLs count: {len(self.visited_urls)}")

            headers = {"User-Agent": self.user_agent_var.get()}
            self.logger.debug(f"Using headers: {headers}")

            self.logger.info(f"Making request to {url}")
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
            except requests.RequestException as e:
                self.logger.error(f"Request error for {url}: {str(e)}")
                self.stats.increment_errors()
                return

            self.logger.info(f"Successfully downloaded {url}, status code: {response.status_code}")

            self.visited_urls.add(url)
            self.stats.increment_pages()
            self.stats.add_bytes_downloaded(len(response.content))
            self.stats.update_depth(depth)

            self.logger.debug("Parsing page content with BeautifulSoup")
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            self.logger.info(f"Found {len(links)} links on page {url}")

            data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'timestamp': datetime.now().isoformat(),
                'depth': depth,
                'links': [{'text': link.get_text(strip=True), 'href': urljoin(url, link['href'])}
                         for link in links if link.get('href')]
            }
            self.crawled_data.append(data)


            for link in links:
                try:
                    href = link['href']
                    self.logger.debug(f"Processing link: {href}")
                    next_url = urljoin(url, href)
                    self.logger.debug(f"Joined URL: {next_url}")

                    if self.url_filter.should_crawl(next_url):
                        self.logger.debug(f"Adding URL to queue: {next_url}")
                        self.crawl_queue.put((next_url, depth + 1))
                except Exception as link_error:
                    self.logger.error(f"Error processing link {link.get('href', '')}: {str(link_error)}")
                    continue

            self.stats.update_queue_size(self.crawl_queue.qsize())

        except Exception as e:
            self.logger.error(f"Error processing {url}: {str(e)}")
            self.logger.exception("Full traceback for processing error:")
            self.stats.increment_errors()

    def crawl_completed(self, error: Optional[str] = None):
        self.thread_pool.shutdown(wait=True)
        self.stats.stop_session()

        if not error:
            self.export_button.configure(state="normal")

        self.root.after(0, self.update_ui_on_completion, error)

    def update_ui_on_completion(self, error: Optional[str]):
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")

        if error:
            self.status_var.set(f"Error: {error}")
            messagebox.showerror("Error", f"Crawling failed: {error}")
        else:
            self.status_var.set("Crawling completed")
            messagebox.showinfo("Success", "Crawling completed successfully")

    def update_stats(self):
        if not self.stop_requested:
            stats = self.stats.get_stats()
            self.dashboard.update_stats(stats)
            self.visualization.update_plots(stats)
            self.root.after(1000, self.update_stats)

    def export_data(self, format_type: str = 'html'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            if format_type == 'html':
                filename = f'crawl_report_{timestamp}.html'
                self._export_html(filename)
            elif format_type == 'json':
                filename = f'crawl_data_{timestamp}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.crawled_data, f, indent=2, ensure_ascii=False)
            elif format_type == 'csv':
                filename = f'crawl_data_{timestamp}.csv'
                df = pd.DataFrame([
                    {
                        'url': d['url'],
                        'title': d['title'],
                        'timestamp': d['timestamp'],
                        'depth': d['depth'],
                        'num_links': len(d['links'])
                    }
                    for d in self.crawled_data
                ])
                df.to_csv(filename, index=False)

            self.logger.info(f"Data exported to {filename}")
            return filename

        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            raise

    def _export_html(self, filename: str):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crawler Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .page {{ margin: 15px 0; padding: 10px; border: 1px solid #ddd; }}
                .links {{ margin-left: 20px; }}
                pre {{ background: #f8f8f8; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Web Crawler Report</h1>

            <div class="stats">
                <h2>Crawling Statistics</h2>
                <p>Pages Crawled: {len(self.crawled_data)}</p>
                <p>Start Time: {self.stats.start_time}</p>
                <p>Total Time: {time.time() - self.stats.start_time:.2f} seconds</p>
            </div>

            <h2>Crawled Pages</h2>
        """

        for data in self.crawled_data:
            html_content += f"""
            <div class="page">
                <h3><a href="{html.escape(data['url'])}">{html.escape(data['title'] or data['url'])}</a></h3>
                <p>Depth: {data['depth']}</p>
                <p>Crawled at: {data['timestamp']}</p>

                <div class="links">
                    <h4>Found Links ({len(data['links'])})</h4>
                    <ul>
            """

            for link in data['links'][:10]:
                html_content += f"""
                    <li><a href="{html.escape(link['href'])}">{html.escape(link['text'] or link['href'])}</a></li>
                """

            if len(data['links']) > 10:
                html_content += f"<li>... and {len(data['links']) - 10} more links</li>"

            html_content += """
                    </ul>
                </div>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def show_export_dialog(self):
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Crawler Data")
        export_window.geometry("300x150")

        ttk.Label(export_window, text="Choose export format:").pack(pady=10)

        format_var = tk.StringVar(value="html")

        ttk.Radiobutton(export_window, text="HTML Report", variable=format_var, value="html").pack()
        ttk.Radiobutton(export_window, text="JSON Data", variable=format_var, value="json").pack()
        ttk.Radiobutton(export_window, text="CSV Data", variable=format_var, value="csv").pack()

        def do_export():
            try:
                filename = self.export_data(format_var.get())
                messagebox.showinfo("Success", f"Data exported to {filename}")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

        ttk.Button(export_window, text="Export", command=do_export).pack(pady=10)


def main():
    root = tk.Tk()
    app = EnhancedWebCrawler(root)
    root.mainloop()

if __name__ == "__main__":
    main()