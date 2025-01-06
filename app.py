import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from rss_fetcher import fetch_rss_feeds
from summarizer import summarize_content
from risk_score import generate_risk_score_and_explanation, assign_severity_tag

# Streamlit app title
st.set_page_config(page_title="ThreatLens",
    page_icon="ThreatLens_logo.ico",
    layout="wide" 
    )
st.sidebar.image('ThreatLens_logo.webp', width=100)
st.title("ThreatLens - Threat Intelligence Dashboard")
st.sidebar.header("ThreatLens \n\n",divider="orange")
st.sidebar.header("Settings \n\n")
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            
            width: 400px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

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

def display_severity_bar(risk_score):
    """Displays a fixed color spectrum severity bar with a label and severity type based on risk score."""
    # Normalize the risk_score to a percentage
    severity_percent = (risk_score / 10) * 100
    
    if severity_percent >= 80:
        severity_type = "Critical"

    elif severity_percent >= 60 :
        severity_type = "High"

    elif severity_percent >= 40:
        severity_type = "Medium"

    else:
        severity_type = "Low"

    # Display the severity label and percentage next to the bar
    #st.markdown(f"**Severity:** {severity_type} ({severity_percent:.0f}%)")

    # Create a Streamlit progress bar widget (to avoid layout shifting)
    progress_bar = st.progress(0)  
    st.markdown(f"""
    <style>
        div.stProgress > div > div > div > div {{
            background-color: red;
        }}
    </style>
    """, unsafe_allow_html=True)
    # Update the progress bar based on risk score (severity percentage)
    progress_bar.progress(severity_percent / 100)
    
    # Display the severity as a label
    st.markdown(f"<div style='text-align: center; font-size: 15px; font-weight: bold;'> Severity: {severity_type} ({severity_percent:.0f}%)</div>", unsafe_allow_html=True)



if st.sidebar.button("Fetch Threat Feeds"):
    with st.spinner("Fetching and summarizing feeds..."):
        feeds = fetch_rss_feeds(rss_urls)

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

            if not filtered_feeds:
                st.write("No articles from the last 7 days.")
            else:
                # Sort the filtered feeds by the publication date (most recent first)
                sorted_feeds = sorted(filtered_feeds, key=lambda x: datetime.strptime(x['published'].replace(' UTC', ''), "%Y-%m-%d %H:%M:%S"), reverse=True)

                # Limit the number of articles to display
                sorted_feeds = sorted_feeds[:num_articles]

                # Process each feed: summarize, display, and store in ChromaDB
                for feed in sorted_feeds:
                    # Generate summary
                    summary = summarize_content(feed["summary"])
                    risk_score, keywords, explanation = generate_risk_score_and_explanation(feed["summary"])

                    # Ensure risk_score is an integer
                    try:
                        risk_score = int(risk_score)  # Explicitly convert to integer
                    except ValueError:
                        st.write(f"Invalid risk score for article: {feed['title']}")
                        risk_score = 0  # Default value in case of invalid risk score

                    severity = assign_severity_tag(risk_score)
                    st.subheader(feed["title"])
                    st.write(f"**Published:** {feed['published']}")
                    st.write(f"**Link:** [Read More]({feed['link']})")
                    st.write(f"**Summary:** {summary}")
                    st.write(f"**Risk Score:** {risk_score} / 10")
                    st.write(f"{explanation}")  
                    st.write(f"**Keywords:** {', '.join(keywords)}")  
                    #st.write(f"**Severity:** {severity}")
                    
                    # Display severity visually as a progress bar
                    display_severity_bar(risk_score)
                    st.write("---")

