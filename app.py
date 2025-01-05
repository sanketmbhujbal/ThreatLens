import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from rss_fetcher import fetch_rss_feeds
from summarizer import summarize_content
from risk_score import generate_risk_score, assign_severity_tag

# Streamlit app title
st.set_page_config(page_title="ThreatLens", page_icon="ThreatLens_logo.ico",layout="wide")
st.sidebar.image('ThreatLens_logo.webp', width=150)
st.title("ThreatLens - Threat Intelligence Dashboard")
st.sidebar.header("ThreatLens \n\n",divider="orange")
st.sidebar.header("Settings \n\n")


# Input RSS feed URLs
rss_urls = st.sidebar.text_area(
    "Enter RSS Feed URLs (one per line)",
    "https://feeds.feedburner.com/TheHackersNews\nhttps://blog.malwarebytes.com/feed/"
).splitlines()

# Input for number of articles to display
num_articles = st.sidebar.number_input("Number of articles to display", min_value=1, max_value=30, value=5)

# Get the current date and the date 7 days ago
current_date = datetime.utcnow()
seven_days_ago = current_date - timedelta(days=7)

if st.sidebar.button("Fetch Threat Feeds"):
    with st.spinner("Fetching and summarizing feeds..."):
        feeds = fetch_rss_feeds(rss_urls)
        #st.write(f"Total articles fetched: {len(feeds)}")  # Debug: Show the total number of fetched articles

        if not feeds:
            st.write("No recent feeds found.")
        else:
            # Filter articles from the last 7 days
            filtered_feeds = []
            for feed in feeds:
                try:
                    # Parse the published date and remove 'UTC' from the string
                    published_date_str = feed['published'].replace(' UTC', '')  # Remove ' UTC'
                    published_date = datetime.strptime(published_date_str, "%Y-%m-%d %H:%M:%S")

                    if published_date > seven_days_ago:
                        filtered_feeds.append(feed)
                except ValueError as e:
                    st.write(f"Error parsing date for article {feed['title']}: {e}")

            #st.write(f"Total articles in last 7 days: {len(filtered_feeds)}")  # Debug: Show the number of filtered articles

            if not filtered_feeds:
                st.write("No articles from the last 7 days.")
            else:
                # Sort the filtered feeds by the publication date (most recent first)
                sorted_feeds = sorted(filtered_feeds, key=lambda x: datetime.strptime(x['published'].replace(' UTC', ''), "%Y-%m-%d %H:%M:%S"), reverse=True)

                # Limit the number of articles to display
                sorted_feeds = sorted_feeds[:num_articles]

                st.write(f"Total articles displayed: {len(sorted_feeds)}")  # Debug: Show the number of displayed articles

                # Process each feed: summarize, display, and store in ChromaDB
                for feed in sorted_feeds:
                    # Generate summary
                    summary = summarize_content(feed["summary"])
                    risk_score = generate_risk_score(feed["summary"])
                    severity_tag = assign_severity_tag(risk_score)
                    st.subheader(feed["title"])
                    st.write(f"**Published:** {feed['published']}")
                    st.write(f"**Link:** [Read More]({feed['link']})")
                    st.write(f"**Summary:** {summary}")
                    st.write(f"**Risk Score:** {risk_score}")
                    st.write(f"**Severity:** {severity_tag}")
                    st.write("---")

