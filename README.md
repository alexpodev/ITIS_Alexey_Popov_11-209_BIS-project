# Web Crawler for KPFU Media News

A Python-based web crawler designed to extract and save news articles from the KPFU Media portal (media.kpfu.ru), with text processing and lemmatization capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
    - [Crawler](#crawler)
    - [Lemmatizator](#lemmatizator)
- [Configuration](#configuration)
- [Output Structure](#output-structure)
- [Project Information](#project-information)

---

## Overview

This crawler automatically navigates through the KPFU Media news section, collects article URLs, and saves the HTML content of each page for offline analysis. It supports pagination and includes intelligent filtering to ensure only relevant text-heavy pages are stored.

## Features

### Crawler

- **Automatic Pagination**: Traverses multiple pages of the news archive
- **Content Filtering**: Skips non-text pages (images, PDFs, documents, etc.)
- **Language Detection**: Prioritizes pages with Cyrillic or Latin text content
- **Rate Limiting**: Built-in delay between requests to respect server resources
- **Index Generation**: Creates an index file mapping saved pages to their source URLs
- **Configurable Limits**: Set minimum number of pages to collect

### Lemmatizator

- **Tokenization**: Extracts individual words from HTML documents
- **Noise Filtering**: Removes duplicates, stop words, numbers, and non-Russian words
- **Lemmatization**: Groups tokens by their dictionary form (lemma) using pymorphy3
- **Per-page Processing**: Generates separate token and lemma files for each crawled page

## Requirements

- Python 3.6 or higher
- Required packages:
    - `requests`
    - `beautifulsoup4`
    - `pymorphy3` (for lemmatization)

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

### Crawler

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

### Lemmatizator

Run the lemmatizator:

```bash
python3 lemmatizator.py
```

The lemmatizator will:

1. Read all HTML files from `crawl_output/`
2. Extract and filter tokens (remove noise, duplicates, stop words)
3. Lemmatize tokens using pymorphy3
4. Generate per-page output files in `tokens_lemmas/`

**Output files:**

- `tokens_page_XXXX.txt` — unique tokens, one per line
- `lemmas_page_XXXX.txt` — lemma groups in format: `<lemma> <token1> <token2> ...`

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

After running the crawler and lemmatizator:

```
project/
├── crawl_output/              # Directory containing saved HTML pages
│   ├── page_0001.txt
│   ├── page_0002.txt
│   └── ...
├── tokens_lemmas/             # Directory containing processed tokens and lemmas
│   ├── tokens_page_0001.txt
│   ├── lemmas_page_0001.txt
│   ├── tokens_page_0002.txt
│   ├── lemmas_page_0002.txt
│   └── ...
├── index.txt                  # Index mapping page numbers to URLs
├── crawler.py                 # Main crawler script
└── lemmatizator.py            # Text processing and lemmatization script
```

### Index File Format

The `index.txt` file contains tab-separated entries:

```
# File Number    URL
#====================================
1    https://media.kpfu.ru/news/article-1
2    https://media.kpfu.ru/news/article-2
```

### Tokens File Format

Each `tokens_page_XXXX.txt` contains one token per line (lowercase, no duplicates):

```
объявлен
конкурс
гранты
президента
```

### Lemmas File Format

Each `lemmas_page_XXXX.txt` contains lemma groups:

```
объявить объявлен
конкурс конкурс
гранты грантов
президент президента президенту
```

## Project Information

- **Author**: Alexey Popov
- **Group**: 11-209
- **Institution**: ITIS, Kazan Federal University (KFU)
- **License**: For educational purposes only

---

_Last Updated: March 4, 2026_
