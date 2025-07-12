import os
import google.generativeai as genai
from dotenv import load_dotenv
import random


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def build_review_prompt(school_name: str, section_text: str) -> str:
    prompts = [
        f"""
You're a parent writing a brief review about your experience with **{school_name}**.
Based on the official profile information below, share your honest thoughts in 5–7 sentences.
Mention what stood out (positive or negative) — academics, infrastructure, food, or admissions.
Be specific, natural, and real. Start conversationally, no robotic phrases.

{section_text}
""",

        f"""
Pretend you're giving quick feedback to another parent about **{school_name}**.
Using the following school profile data, write a short, unique, and honest review (5–7 sentences).
Highlight both strengths and any shortcomings (e.g., missing facilities, food quality, fees).
Avoid template-like tone. Sound like a real parent reflecting on your child’s experience.

{section_text}
""",

        f"""
Using the details below, write a short parent review for **{school_name}**.
Keep it natural and honest — like a WhatsApp message to a fellow parent.
Mention important aspects: teachers, facilities, meals, value, or safety.
Avoid generic intros like “So, we joined…” or “It’s been a journey.”

{section_text}
""",

        f"""
Imagine you’ve just completed a parent survey for **{school_name}**.
Write a brief review (5–7 lines) summarizing what you liked and what felt lacking.
Use an honest tone — mention academics, facilities, food, or communication clearly.
Keep it varied and personal, not formal or repetitive.

{section_text}
""",

        f"""
Write a short, casual, and honest review for **{school_name}**, based on the info below.
Share real pros and cons like a friend would — about academics, staff, meals, or pricing.
Be unique in tone and expression. Limit to 5–7 sentences max.
Start naturally, no copy-paste structure.

{section_text}
"""
    ]

    return random.choice(prompts)


def generate_parent_review(school_name: str, section_data: dict) -> str:
    section_text = ""
    for title, content in section_data.items():
        section_text += f"\n\n## {title}\n{content.strip()}"

    prompt = build_review_prompt(school_name, section_text)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Review generation failed."
