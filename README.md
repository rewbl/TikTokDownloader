# TikTok Downloader

A TikTok/Douyin video downloader and bookmark manager built with Python.

## Features

- Download TikTok/Douyin videos
- Bookmark management
- MongoDB integration
- Slack notifications
- File download services

## Installation

This project uses Poetry for dependency management.

### Prerequisites

- Python 3.10+
- Poetry

### Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Usage

Run the main downloader:
```bash
python main_downloader.py
```

Run the Douyin following monitor:
```bash
python main_douyin_following.py
```

Run the Douyin discovers:
```bash
python main_douyin_discovers.py
```

## Project Structure

- `app/` - Main application code
- `DouyinEndpoints/` - API endpoints for Douyin
- `FileDownload/` - File download services
- `StudioY/` - StudioY integration
- `Slack/` - Slack notification services

## Configuration

Configure your settings in `Parameter.py`.

## License

This project is for educational purposes only.
