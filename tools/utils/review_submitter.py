import requests


def submit_review(slug: str, token: str, user_id: int, review_text: str, ratings: list) -> dict:
    url = f"https://api.horizon-dev.ezyschooling.com/api/v1/analatics/{slug}/parent-review/"

    payload = {
        "user_id": str(user_id),
        "review": review_text,
        "ratings": str(ratings)  # must be sent as stringified JSON inside multipart
    }

    headers = {
        "Authorization": f"Token {token}"
    }
    print(f"Submitting review for {slug} with payload: {payload}")
    # response = requests.post(url, headers=headers, files=payload)
    # return {
    #     "status": response.status_code,
    #     "success": response.status_code == 201,
    #     "response": response.json()
    # }
    return
