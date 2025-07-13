import json
import requests


def submit_review(slug: str, token: str, user_id: int, review_text: str, ratings: list) -> dict:
    url = f"https://api.horizon-dev.ezyschooling.com/api/v1/analatics/{slug}/parent-review/"

    # Validate ratings structure
    if not isinstance(ratings, list) or not all(
        isinstance(r, dict)
        and "name" in r
        and "rating" in r
        and isinstance(r["name"], str)
        and isinstance(r["rating"], int)
        and 1 <= r["rating"] <= 5
        for r in ratings
    ):
        raise ValueError("Invalid ratings format. Expected list of dicts with 'name' (str) and 'rating' (int 1–5).")

    payload = {
        "user_id": str(user_id),
        "review": review_text,
        "ratings": str(ratings)  # must be sent as stringified JSON inside multipart
    }

    headers = {
        "Authorization": f"Token {token}"
    }

    files = {
        "user_id": (None, str(user_id)),
        "review": (None, review_text),
        "ratings": (None, json.dumps(ratings))
    }
    print(files)
    response = requests.post(url, headers=headers, files=files)
    print("Response status:", response.status_code)
    print("Response content:", response.content.decode())

    try:
        response_data = response.json()
    except Exception:
        response_data = {"raw": response.content.decode()}

    return {
        "status": response.status_code,
        "success": response.status_code == 200,
        "response": response_data
    }
