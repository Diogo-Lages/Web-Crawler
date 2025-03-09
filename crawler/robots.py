import urllib.robotparser
import urllib.parse
import requests
from urllib.parse import urljoin
import logging
from typing import Optional, Dict

class RobotsParser:
    def __init__(self, user_agent: str = "PythonWebCrawler/1.0"):
        self.user_agent = user_agent
        self.parsers: Dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def can_fetch(self, url: str) -> bool:
        try:
            self.logger.debug(f"Checking if can fetch URL: {url}")

            # Parse URL
            try:
                parsed_url = urllib.parse.urlparse(url)
                domain = parsed_url.netloc
                if not domain:
                    self.logger.warning(f"Invalid URL format: {url}")
                    return False
            except Exception as e:
                self.logger.error(f"Error parsing URL {url}: {str(e)}")
                return False

            self.logger.debug(f"Parsed domain: {domain}")

            # Initialize parser if needed
            if domain not in self.parsers:
                self.logger.debug(f"Initializing parser for domain: {domain}")
                self._init_parser(domain, url)

            # Get parser instance
            parser = self.parsers.get(domain)
            if parser is None:
                self.logger.debug(f"No parser available for {domain}, allowing crawl")
                return True

            # Check if URL can be fetched
            try:
                can_fetch = parser.can_fetch(self.user_agent, url)
                self.logger.debug(f"Robots.txt decision for {url}: {can_fetch}")
                return can_fetch
            except Exception as e:
                self.logger.error(f"Error checking can_fetch for {url}: {str(e)}")
                return True

        except Exception as e:
            self.logger.error(f"Error in can_fetch for {url}: {str(e)}")
            self.logger.exception("Full traceback:")
            return True

    def _init_parser(self, domain: str, url: str) -> None:
        try:
            self.logger.debug(f"Initializing robots parser for domain: {domain}")

            # Create robots.txt URL
            robots_url = urljoin(f"https://{domain}", "/robots.txt")
            self.logger.debug(f"Fetching robots.txt from: {robots_url}")

            # Create parser instance
            parser = urllib.robotparser.RobotFileParser(robots_url)

            try:
                # Fetch robots.txt
                response = requests.get(robots_url, timeout=10)
                if response.status_code == 200:
                    self.logger.debug("Successfully fetched robots.txt")
                    parser.parse(response.text.splitlines())
                    self.parsers[domain] = parser
                else:
                    self.logger.debug(f"No robots.txt found (status code: {response.status_code})")
                    self.parsers[domain] = None
            except requests.RequestException as e:
                self.logger.warning(f"Error fetching robots.txt from {robots_url}: {str(e)}")
                self.parsers[domain] = None

        except Exception as e:
            self.logger.error(f"Error initializing parser for {domain}: {str(e)}")
            self.logger.exception("Full traceback:")
            self.parsers[domain] = None

    def get_crawl_delay(self, url: str) -> float:
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc

            if domain not in self.parsers:
                self._init_parser(domain, url)

            parser = self.parsers.get(domain)
            if not parser:
                return 0

            delay = parser.crawl_delay(self.user_agent)
            return delay if delay is not None else 0

        except Exception as e:
            self.logger.error(f"Error getting crawl delay for {url}: {str(e)}")
            self.logger.exception("Full traceback for crawl delay error:")
            return 0