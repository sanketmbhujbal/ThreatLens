from rss_fetcher import fetch_rss_feeds

test_urls = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://blog.malwarebytes.com/feed/",
    "https://blog.talosintelligence.com/feeds/posts/default"
]

feeds = fetch_rss_feeds(test_urls)
for feed in feeds:
    print(f"Title: {feed['title']}")
    print(f"Published: {feed['published']}")
    print(f"Link: {feed['link']}")
    print(f"Summary: {feed['summary']}\n")
