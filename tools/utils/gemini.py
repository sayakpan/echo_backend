import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
import random
import json
import random
import re



load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")




def extract_json_block(text):
    match = re.search(r'{.*}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON block found")
    return json.loads(match.group(0))


def build_review_prompt(school_name: str, section_text: str) -> str:
    prompts = [
        f"""
You're a parent writing a short review about your experience with **{school_name}**.
Based on the school info below, share your honest thoughts in 5–7 sentences — good or bad.
Mention academics, infrastructure, food, safety, and overall satisfaction.
Then give ratings (1–5) for each aspect.

Return your response in this JSON format:
OUTPUT = STRICTLY JSON otherwise you will be disqualified.
{{
  "review": "<your review>",
  "ratings": [
    {{"name": "overall-rating", "rating": <1-5>}},
    {{"name": "sports", "rating": <1-5>}},
    {{"name": "infrastructure", "rating": <1-5>}},
    {{"name": "value-for-money", "rating": <1-5>}},
    {{"name": "admission-process", "rating": <1-5>}},
    {{"name": "extra-curricular", "rating": <1-5>}}
  ]
}}

{section_text}
""",

        f"""
Imagine you're texting another parent about **{school_name}** after enrolling your child.
Write a short, honest review (5–7 lines) using the school info below.
Mention anything noteworthy — teaching quality, campus, meals, fees, or support.
Then share your ratings from 1 to 5 for academics, facilities, food, safety, and overall.


Return your response in this JSON format:
OUTPUT = STRICTLY JSON otherwise you will be disqualified.
{{
  "review": "<your review>",
  "ratings": [
    {{"name": "overall-rating", "rating": <1-5>}},
    {{"name": "sports", "rating": <1-5>}},
    {{"name": "infrastructure", "rating": <1-5>}},
    {{"name": "value-for-money", "rating": <1-5>}},
    {{"name": "admission-process", "rating": <1-5>}},
    {{"name": "extra-curricular", "rating": <1-5>}}
  ]
}}
{section_text}
""",

        f"""
You’ve just submitted a parent review survey for **{school_name}**.
Now write a brief summary (5–7 sentences) capturing what you liked and what needs work.
Discuss things like academics, food, value for money, or infrastructure.
Then rate each key aspect from 1 to 5.


Return your response in this JSON format:
OUTPUT = STRICTLY JSON otherwise you will be disqualified.
{{
  "review": "<your review>",
  "ratings": [
    {{"name": "overall-rating", "rating": <1-5>}},
    {{"name": "sports", "rating": <1-5>}},
    {{"name": "infrastructure", "rating": <1-5>}},
    {{"name": "value-for-money", "rating": <1-5>}},
    {{"name": "admission-process", "rating": <1-5>}},
    {{"name": "extra-curricular", "rating": <1-5>}}
  ]
}}

{section_text}
""",

        f"""
Pretend you're on a school discussion forum sharing feedback on **{school_name}**.
Write a quick review (5–7 sentences) reflecting what stood out — both pros and cons.
Then provide ratings for academics, facilities, food, safety, and overall (1–5 scale).


Return your response in this JSON format:
OUTPUT = STRICTLY JSON otherwise you will be disqualified.
{{
  "review": "<your review>",
  "ratings": [
    {{"name": "overall-rating", "rating": <1-5>}},
    {{"name": "sports", "rating": <1-5>}},
    {{"name": "infrastructure", "rating": <1-5>}},
    {{"name": "value-for-money", "rating": <1-5>}},
    {{"name": "admission-process", "rating": <1-5>}},
    {{"name": "extra-curricular", "rating": <1-5>}}
  ]
}}

{section_text}
""",

        f"""
You're a parent recommending (or warning about) **{school_name}** to others.
Use the school info below to write a casual and truthful review in 5–7 sentences.
After the review, give ratings out of 5 for academics, facilities, food, safety, and overall experience.


Return your response in this JSON format:
OUTPUT = STRICTLY JSON otherwise you will be disqualified.
{{
  "review": "<your review>",
  "ratings": [
    {{"name": "overall-rating", "rating": <1-5>}},
    {{"name": "sports", "rating": <1-5>}},
    {{"name": "infrastructure", "rating": <1-5>}},
    {{"name": "value-for-money", "rating": <1-5>}},
    {{"name": "admission-process", "rating": <1-5>}},
    {{"name": "extra-curricular", "rating": <1-5>}}
  ]
}}
{section_text}
"""
    ]

    return random.choice(prompts)


def generate_parent_review(school_name: str, section_data: dict) -> dict:
    section_text = ""
    for title, content in section_data.items():
        section_text += f"\n\n## {title}\n{content.strip()}"

    prompt = build_review_prompt(school_name, section_text)

    try:
        response = model.generate_content(prompt)
        print(f"Gemini response: {response.text.strip()}")
        text = response.text.strip()

        json_data = extract_json_block(text)

        review = json_data.get("review", "").strip()
        ratings = json_data.get("ratings", [])

        if not review or not isinstance(ratings, list):
            raise ValueError("Incomplete review or ratings")

        return {
            "review": review,
            "ratings": ratings
        }

    except Exception as e:
        print(f"Gemini response parse error: {e}")
        return {
            "review": "Review generation failed.",
            "ratings": {
                "academics": 3,
                "facilities": 3,
                "food": 3,
                "safety": 3,
                "overall": 3
            }
        }


def generate_static_review(school_name: str, section_data: dict) -> dict:
    # Simulate Gemini-like thinking time
    time.sleep(random.uniform(1.0, 2.5))

    review = f"""We recently enrolled our child at {school_name}, and it's been a positive start. The admission process was smooth, and the facilities seem well-maintained. The teachers are approachable, and extracurricular activities are encouraged. However, the lack of a cafeteria is a small drawback. Overall, we’re satisfied with the school so far."""

    ratings = [
        {"name": "overall-rating", "rating": 4},
        {"name": "sports", "rating": 3},
        {"name": "infrastructure", "rating": 4},
        {"name": "value-for-money", "rating": 4},
        {"name": "admission-process", "rating": 5},
        {"name": "extra-curricular", "rating": 4}
    ]

    return {
        "review": review,
        "ratings": ratings
    }