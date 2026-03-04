# Web Crawler for KPFU Media News

A Python-based web crawler designed to extract and save news articles from the KPFU Media portal (media.kpfu.ru).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output Structure](#output-structure)
- [Project Information](#project-information)

---

## Overview

This crawler automatically navigates through the KPFU Media news section, collects article URLs, and saves the HTML content of each page for offline analysis. It supports pagination and includes intelligent filtering to ensure only relevant text-heavy pages are stored.

## Features

- **Automatic Pagination**: Traverses multiple pages of the news archive
- **Content Filtering**: Skips non-text pages (images, PDFs, documents, etc.)
- **Language Detection**: Prioritizes pages with Cyrillic or Latin text content
- **Rate Limiting**: Built-in delay between requests to respect server resources
- **Index Generation**: Creates an index file mapping saved pages to their source URLs
- **Configurable Limits**: Set minimum number of pages to collect

## Requirements

- Python 3.6 or higher
- Required packages:
    - `requests`
    - `beautifulsoup4`

## Installation

1. Clone or download this repository:

    ```bash
    cd /home/butterfp/Documents/ITIS_Alexey_Popov_11-209_BIS-project
    ```

2. Create virtual environment:

    ```bash
    python3 -m venv venv
    ```

3. Open virtual environment:

    ```bash
    source venv/bin/activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    Or install manually:

    ```bash
    pip install requests beautifulsoup4
    ```

## Usage

Run the crawler:

```bash
python3 crawler.py
```

The crawler will:

1. Fetch the main news page
2. Paginate through available news pages
3. Extract article URLs
4. Download and save article content
5. Generate an index file

## Configuration

Edit the constants at the top of `crawler.py` to customize behavior:

| Parameter       | Default                      | Description                         |
| --------------- | ---------------------------- | ----------------------------------- |
| `BASE_URL`      | `https://media.kpfu.ru`      | Base URL of the target website      |
| `NEWS_URL`      | `https://media.kpfu.ru/news` | Starting URL for crawling           |
| `OUTPUT_DIR`    | `crawl_output`               | Directory for saved pages           |
| `INDEX_FILE`    | `index.txt`                  | Name of the index file              |
| `MIN_PAGES`     | `100`                        | Minimum number of pages to download |
| `REQUEST_DELAY` | `0.5`                        | Delay between requests (seconds)    |

## Output Structure

After execution, the following will be created:

```
project/
├── crawl_output/          # Directory containing saved pages
│   ├── page_0001.txt
│   ├── page_0002.txt
│   └── ...
├── index.txt              # Index mapping page numbers to URLs
└── crawler.py             # Main script
```

### Index File Format

The `index.txt` file contains tab-separated entries:

```
# File Number    URL
#====================================
1    https://media.kpfu.ru/news/article-1
2    https://media.kpfu.ru/news/article-2
```

## Project Information

- **Author**: Alexey Popov
- **Group**: 11-209
- **Institution**: ITIS, Kazan Federal University (KFU)
- **License**: For educational purposes only

---

_Last Updated: March 4, 2026_
