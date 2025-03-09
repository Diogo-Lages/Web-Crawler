import tkinter as tk
from tkinter import ttk, scrolledtext
import time
from typing import Dict, Any
import logging

class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)

class Dashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.update_interval = 1000

    def setup_ui(self):
        self.paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.stats_frame = ttk.LabelFrame(self.paned, text="Crawling Statistics", padding="5")
        self.paned.add(self.stats_frame, weight=1)

        self.labels: Dict[str, tk.StringVar] = {
            "Pages Crawled": tk.StringVar(value="0"),
            "Crawl Speed": tk.StringVar(value="0 pages/min"),
            "Memory Usage": tk.StringVar(value="0 MB"),
            "Queue Size": tk.StringVar(value="0"),
            "Current Depth": tk.StringVar(value="0"),
            "Errors": tk.StringVar(value="0"),
            "Elapsed Time": tk.StringVar(value="00:00:00"),
            "Downloaded": tk.StringVar(value="0 KB")
        }

        for i, (label_text, var) in enumerate(self.labels.items()):
            ttk.Label(self.stats_frame, text=f"{label_text}:").grid(
                row=i//2, column=i%2*2, sticky="w", padx=5, pady=2
            )
            ttk.Label(self.stats_frame, textvariable=var).grid(
                row=i//2, column=i%2*2+1, sticky="w", padx=5, pady=2
            )

        self.log_frame = ttk.LabelFrame(self.paned, text="Crawler Logs", padding="5")
        self.paned.add(self.log_frame, weight=2)

        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_handler = LogHandler(self.log_text)
        self.log_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(self.log_handler)

        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("INFO", foreground="black")
        self.log_text.tag_configure("DEBUG", foreground="gray")

    def update_stats(self, stats: Dict[str, Any]) -> None:
        self.labels["Pages Crawled"].set(str(stats["pages_crawled"]))
        self.labels["Crawl Speed"].set(f"{stats['crawl_speed']:.1f} pages/min")
        self.labels["Memory Usage"].set(f"{stats['memory_usage']:.1f} MB")
        self.labels["Queue Size"].set(str(stats["urls_in_queue"]))
        self.labels["Current Depth"].set(str(stats["current_depth"]))
        self.labels["Errors"].set(str(stats["errors"]))

        elapsed = stats["elapsed_time"]
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        self.labels["Elapsed Time"].set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        bytes_downloaded = stats["bytes_downloaded"]
        if bytes_downloaded < 1024:
            size_str = f"{bytes_downloaded} B"
        elif bytes_downloaded < 1024 * 1024:
            size_str = f"{bytes_downloaded/1024:.1f} KB"
        else:
            size_str = f"{bytes_downloaded/1024/1024:.1f} MB"
        self.labels["Downloaded"].set(size_str)