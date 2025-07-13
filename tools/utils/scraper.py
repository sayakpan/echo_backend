import requests
from bs4 import BeautifulSoup


SECTION_SELECTORS = {
    "Quick Facts": "quick-facts",
    "Admission Process": "admission-process",
    "Facilities": "facilities",
    "Why you should consider this school": "why-you-should-consider-this-school",
    "Scholarship": "scholarship",
    "About Us": "about-us",
    "Food Details": "food-details",
    "Awards & Recognition": "awards-recognition",
    "Fees Structure": "fees-structure"
}


def extract_school_sections(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    extracted = {}

    for section_title, section_id in SECTION_SELECTORS.items():
        section_div = soup.find("div", {"id": section_id})
        if section_div:
            text = section_div.get_text(separator="\n", strip=True)
            if text:
                extracted[section_title] = text

    if not extracted:
        raise ValueError("Failed to extract any section content from the school page.")

    return extracted
