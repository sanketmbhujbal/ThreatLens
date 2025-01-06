from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API keys from environment
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE_URL"))

def generate_risk_score_and_explanation(content):
    """Use OpenAI's GPT model to assess the risk score and explanation of an article based on its content."""
    try:
        # Prompt to assess risk score and explain reasoning
        prompt = f"""
        Based on the following article, analyze its content and:
        1. Assign a risk score between 1 and 10, where 1 is the lowest risk and 10 is the highest risk. 
        2. Provide keywords or phrases related to cybersecurity threats that influenced the score.
        3. Offer a brief two sentence explanation of why this score was assigned.

        Article:
        {content}

        Format your response strictly as:
        Score: [integer between 1 and 10]
        Keywords: [comma-separated keywords or phrases]
        Explanation: [brief explanation]
        """

        # OpenAI API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Analyze risk and explain severity based on content."},
                      {"role": "user", "content": prompt}]
        )
        # print(f"Raw API response: {response}") #debugging responses
        # Parse the output
        result = response.choices[0].message.content.strip()
        lines = result.split("\n")

        # Extract Score, Keywords, and Explanation
        risk_score_str = lines[0].split(":")[1].strip()
        if risk_score_str.isdigit():
            risk_score = int(risk_score_str)
        else:
            raise ValueError("Invalid risk score value.")

        keywords = lines[1].split(":")[1].strip().split(", ")
        explanation = lines[2].split(":")[1].strip() 

        return risk_score, keywords, explanation

    except Exception as e:
        return f"Error: {e}", [], ""


def assign_severity_tag(risk_score):
    """Assign a severity tag based on the risk score."""
    try:
        # Ensure risk_score is an integer
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
