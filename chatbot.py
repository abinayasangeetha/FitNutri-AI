import os
from groq import Groq
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_response(
    user_message,
    user_context="",
    chat_history=None
):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if user_context:
        messages.append(
            {
                "role": "system",
                "content": user_context
            }
        )

    if chat_history:

        for msg in chat_history[-10:]:

            messages.append(
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
            )

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )

    return response.choices[0].message.content