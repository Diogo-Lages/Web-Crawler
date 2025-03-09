import re
from typing import List, Pattern
from urllib.parse import urlparse
import logging


class URLFilter:
    def __init__(self):
        self.include_patterns: List[Pattern] = []
        self.exclude_patterns: List[Pattern] = []
        self.allowed_domains: List[str] = []
        self.logger = logging.getLogger(__name__)

    def add_include_pattern(self, pattern: str) -> None:
        try:
            self.include_patterns.append(re.compile(pattern))
        except re.error as e:
            self.logger.error(f"Invalid include pattern '{pattern}': {str(e)}")

    def add_exclude_pattern(self, pattern: str) -> None:
        try:
            self.exclude_patterns.append(re.compile(pattern))
        except re.error as e:
            self.logger.error(f"Invalid exclude pattern '{pattern}': {str(e)}")

    def add_allowed_domain(self, domain: str) -> None:
        self.allowed_domains.append(domain.lower())

    def should_crawl(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc.lower()
            if self.allowed_domains and domain not in self.allowed_domains:
                return False

            for pattern in self.exclude_patterns:
                if pattern.search(url):
                    return False

            if self.include_patterns:
                return any(pattern.search(url) for pattern in self.include_patterns)

            return True

        except Exception as e:
            self.logger.error(f"Error filtering URL {url}: {str(e)}")
            return False

    def clear_filters(self) -> None:
        self.include_patterns = []
        self.exclude_patterns = []
        self.allowed_domains = []
