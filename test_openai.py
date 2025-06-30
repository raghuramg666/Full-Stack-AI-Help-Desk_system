from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Sample user prompt
prompt = "today date please"

def test_openai_call():
    """Sends a prompt to OpenAI and prints the response."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        print("OpenAI Response:", response.choices[0].message.content.strip())
    except Exception as e:
        print("OpenAI API Error:", str(e))

if __name__ == "__main__":
    test_openai_call()
