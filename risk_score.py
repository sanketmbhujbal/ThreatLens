from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API keys from environment
load_dotenv()


def generate_risk_score(content):
    """Use OpenAI's GPT model to assess the risk score of an article based on its content."""
    try:
        # Generate prompt asking the model to assess the risk of the content
        client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"), base_url = os.getenv("OPENAI_API_BASE_URL"))
        prompt = f"""
        Based on the following article, assign a risk score between 1 and 10, where 1 is the lowest risk and 10 is the highest risk. The risk score should be based on factors such as the severity of the threat, the potential impact on systems, and the urgency of addressing the issue. Only return a single integer value as output, do not add a string with it.

        Article:
        {content}

        
        """
        
        # Call OpenAI API to get the risk score
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can choose other models like gpt-3.5-turbo too
            messages=[
                {"role": "system", "content": "Summarize articles to provide most important details."},
                {"role": "user", "content":prompt}
            ]
        )

        risk_score = response.choices[0].message.content.strip()  # Get the text response (risk score)

        return risk_score
    
    except Exception as e:
        return f"Error: {e}"  # Handle errors

def assign_severity_tag(risk_score):
    """Assign a severity tag based on the risk score."""
    try:
        risk_score = int(risk_score)
        if risk_score >= 8:
            return "Critical"
        elif risk_score >= 6:
            return "High"
        elif risk_score >= 4:
            return "Medium"
        else:
            return "Low"
    except ValueError:
        return "Unknown"
