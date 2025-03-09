import time
from typing import Dict, Any
import psutil
import threading
from collections import deque
import logging


class CrawlerStats:
    def __init__(self):
        self.start_time = None
        self.pages_crawled = 0
        self.bytes_downloaded = 0
        self.errors = 0
        self.current_depth = 0
        self.urls_in_queue = 0
        self.memory_usage = deque(maxlen=100)  # Store last 100 measurements
        self.crawl_speed = deque(maxlen=10)  # Pages per minute, last 10 measurements
        self.active = False
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def start_session(self) -> None:
        self.start_time = time.time()
        self.pages_crawled = 0
        self.bytes_downloaded = 0
        self.errors = 0
        self.active = True
        self._start_monitoring()

    def stop_session(self) -> None:
        self.active = False

    def _start_monitoring(self) -> None:

        def monitor():
            while self.active:
                try:
                    # Monitor memory usage
                    process = psutil.Process()
                    mem_info = process.memory_info()
                    with self.lock:
                        self.memory_usage.append(mem_info.rss / 1024 / 1024)  # MB

                    # Calculate crawl speed
                    if self.start_time and self.pages_crawled > 0:
                        elapsed_minutes = (time.time() - self.start_time) / 60
                        speed = self.pages_crawled / elapsed_minutes if elapsed_minutes > 0 else 0
                        with self.lock:
                            self.crawl_speed.append(speed)

                    time.sleep(1)  # Update every second
                except Exception as e:
                    self.logger.error(f"Error in monitoring: {str(e)}")

        threading.Thread(target=monitor, daemon=True).start()

    def increment_pages(self) -> None:
        with self.lock:
            self.pages_crawled += 1

    def add_bytes_downloaded(self, bytes_count: int) -> None:
        with self.lock:
            self.bytes_downloaded += bytes_count

    def increment_errors(self) -> None:
        with self.lock:
            self.errors += 1

    def update_queue_size(self, size: int) -> None:
        with self.lock:
            self.urls_in_queue = size

    def update_depth(self, depth: int) -> None:
        with self.lock:
            self.current_depth = depth

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            avg_speed = sum(self.crawl_speed) / len(self.crawl_speed) if self.crawl_speed else 0
            current_memory = self.memory_usage[-1] if self.memory_usage else 0

            return {
                "pages_crawled": self.pages_crawled,
                "errors": self.errors,
                "elapsed_time": elapsed_time,
                "bytes_downloaded": self.bytes_downloaded,
                "current_depth": self.current_depth,
                "urls_in_queue": self.urls_in_queue,
                "crawl_speed": avg_speed,
                "memory_usage": current_memory
            }
