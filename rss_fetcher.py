import feedparser
from datetime import datetime, timedelta
import pytz  # For timezone handling


def fetch_rss_feeds(feed_urls):
    """Fetch and filter RSS feeds."""
    feeds = []
    current_time = datetime.now(pytz.utc)  # Current UTC time
    yesterday = current_time - timedelta(days=7)  # Time threshold (last 7 days)

    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Parse published date
            published = None
            if hasattr(entry, 'published'):
                published = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc)
            elif hasattr(entry, 'updated'):
                published = datetime(*entry.updated_parsed[:6], tzinfo=pytz.utc)

            # Filter posts published in the last 24 hours
            if published and published >= yesterday:
                feeds.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": published.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "summary": entry.summary if 'summary' in entry else "No summary available."
                })

    return feeds
