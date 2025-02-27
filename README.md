# WebScraper.py

**WebScraper.py** is a Python-based web scraping and crawling tool with a **graphical user interface (GUI)**. It allows users to crawl websites, download pages, and save them locally with features like depth control, rate limiting, and real-time logging.

---

## Features

- **GUI Interface**: Built with `tkinter` for ease of use.
- **Depth Control**: Set the maximum depth for crawling.
- **Local Saving**: Downloads and saves web pages locally.
- **Rate Limiting**: Configurable delay between requests.
- **Stop Functionality**: Stop the crawling process at any time.
- **Real-Time Logging**: Live updates in the GUI.

---

## Requirements

- Python 3.x
- Libraries: `tkinter`, `requests`, `beautifulsoup4`

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Diogo-Lages/Web-Scraper.git
   cd Web_Scraper.py
   ```

2. Install the required libraries:
   ```bash
   pip install requests beautifulsoup4
   ```

3. Run the program:
   ```bash
   python webscraper.py
   ```

---

## Usage

1. Enter the **URL** to crawl in the GUI.
2. Specify the **output directory**.
3. Set the **maximum depth**.
4. Click **Start Crawling** to begin.
5. Use the **Stop** button to halt the process.

---

## Code Structure

- **`WebsiteCrawler` Class**: Core crawling logic.
- **`WebCrawlerGUI` Class**: Manages the GUI and threading.
- **Main Function**: Initializes the GUI.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.


