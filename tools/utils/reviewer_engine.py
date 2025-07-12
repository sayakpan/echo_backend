from tools.utils.scraper import extract_school_sections
from tools.utils.gemini import generate_parent_review
from tools.utils.ratings import get_default_ratings
from tools.utils.review_submitter import submit_review


def generate_and_submit_review(school_slug: str, school_name: str, token: str, user_id: int) -> dict:
    profile_url = f"https://ezyschooling.com/school/{school_slug}"

    try:
        section_data = extract_school_sections(profile_url)
        review_text = generate_parent_review(school_name, section_data)
        ratings = get_default_ratings()
        result = submit_review(school_slug, token, user_id, review_text, ratings)

        return {
            "slug": school_slug,
            "review": review_text,
            "submitted": result["success"],
            "api_response": result["response"]
        }

    except Exception as e:
        return {
            "slug": school_slug,
            "submitted": False,
            "error": str(e)
        }