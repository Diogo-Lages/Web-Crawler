# Web Crawler

Web Crawler is a user-friendly desktop application designed to crawl websites while respecting `robots.txt` rules, managing proxies, and providing real-time statistics and visualizations.

## Features

- **GUI Interface**: Easy-to-use graphical interface for configuring and controlling the crawler.
- **Robots.txt Compliance**: Automatically checks and respects website crawling rules defined in `robots.txt`.
- **Proxy Management**: Supports proxy rotation to avoid IP blocking during large-scale crawls.
- **URL Filtering**: Includes and excludes URLs based on customizable patterns and domain restrictions.
- **Real-Time Statistics**: Displays live metrics such as pages crawled, memory usage, queue size, and errors.
- **Data Visualization**: Provides dynamic graphs for crawl speed, memory usage, and URLs in the queue.
- **Export Options**: Export crawled data in HTML, JSON, or CSV formats for further analysis.
- **Pause/Resume/Stop**: Full control over the crawling process with pause, resume, and stop functionality.
- **Concurrency**: Configurable number of concurrent workers for efficient crawling.

## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `matplotlib`
  - `pandas`
  - `psutil`
  - `urllib3`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Diogo-Lages/Web-Crawler.git
   cd Web-Crawler
   ```

2. Install the required Python libraries manually using pip:
   ```bash
   pip install requests beautifulsoup4 matplotlib pandas psutil urllib3
   ```

3. Run the application:
   ```bash
   python webcrawler.py
   ```

## Usage

1. **Start the Application**: Launch the program by running `webcrawler.py`. A GUI window will appear.
2. **Configure Settings**:
   - Enter the starting URL.
   - Set the maximum depth for crawling.
   - Adjust the number of concurrent workers and rate limit.
   - Add include/exclude URL patterns if needed.
3. **Start Crawling**: Click the "Start" button to begin crawling. The status and statistics will update in real-time.
4. **Pause/Resume/Stop**: Use the respective buttons to control the crawling process.
5. **Export Data**: Once crawling is complete, export the results in HTML, JSON, or CSV format using the "Export Report" button.

## Code Structure

The project is organized into the following modules:

- **`crawler/`**: Contains core functionality for crawling, proxy management, robots.txt parsing, and statistics tracking.
  - `proxy_manager.py`: Manages proxy rotation.
  - `robots.py`: Handles robots.txt compliance.
  - `stats.py`: Tracks crawling statistics.
  - `url_filter.py`: Filters URLs based on patterns and domains.
- **`gui/`**: Implements the graphical user interface.
  - `dashboard.py`: Displays real-time statistics and logs.
  - `visualization.py`: Provides dynamic graphs for monitoring the crawl process.
- **`webcrawler.py`**: Entry point of the application, initializes the GUI and starts the crawler.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
