import requests
from typing import Optional, Dict, List
import random
import logging
from queue import Queue
import time


class ProxyManager:
    def __init__(self):
        self.proxies: List[Dict[str, str]] = []
        self.active_proxies = Queue()
        self.logger = logging.getLogger(__name__)

    def add_proxy(self, proxy: str, proxy_type: str = "http") -> None:
        proxy_dict = {
            "http": f"{proxy_type}://{proxy}",
            "https": f"{proxy_type}://{proxy}"
        }
        self.proxies.append(proxy_dict)
        self.active_proxies.put(proxy_dict)

    def get_proxy(self) -> Optional[Dict[str, str]]:
        if self.active_proxies.empty():
            # Refill the queue if empty
            for proxy in self.proxies:
                self.active_proxies.put(proxy)

        if not self.active_proxies.empty():
            return self.active_proxies.get()
        return None

    def return_proxy(self, proxy: Dict[str, str]) -> None:
        self.active_proxies.put(proxy)

    def test_proxy(self, proxy: Dict[str, str]) -> bool:
        try:
            response = requests.get(
                "http://www.google.com",
                proxies=proxy,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Proxy test failed: {str(e)}")
            return False

    def remove_proxy(self, proxy: Dict[str, str]) -> None:
        if proxy in self.proxies:
            self.proxies.remove(proxy)
