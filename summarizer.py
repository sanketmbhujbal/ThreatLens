from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"), base_url = os.getenv("OPENAI_API_BASE_URL"))
def summarize_content(content):
    """Summarize content using OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize articles to provide most important details."},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
