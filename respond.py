from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool
from logs.logger_utils import get_logger

# Load environment variables and initialize OpenAI client and logger
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = get_logger(__name__)

async def generate_response(chat_context, context_chunks, category, username):
    """
    Generates a professional response using OpenAI based on the user query,
    historical chat context, and relevant document chunks.
    """
    context = "\n\n".join(context_chunks)

    prompt = f"""
Dear user,

You are a highly experienced IT Helpdesk assistant with over 15 years of enterprise support expertise.
Based on the user’s request and the following documentation context, generate a precise and helpful response.

Requirements:
- Use clear, calm, and professional tone.
- Apply company-approved phrasing.
- Escalate the issue if appropriate.
- End the response with: "Regards, Raghu".

Context:
{context}

Chat History:
{chat_context}

Generate the best possible reply.
""".strip()

    def call_openai():
        try:
            logger.info("Generating response using OpenAI API")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("OpenAI API error", exc_info=True)
            return "We’re unable to generate a response at this moment. Please contact support."

    return await run_in_threadpool(call_openai)
