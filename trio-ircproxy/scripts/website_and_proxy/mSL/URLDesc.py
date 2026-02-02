import os
import re
import tempfile
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from langdetect import detect
from nsfw_image_detector import NSFWDetector
from PIL import Image

"""
Written mostly by ChatGPT

Works like this:

from  mSL.URLDesc import inspect_url
import json

url = "https://www.google.ca"
result = inspect_url(url)

# Pretty print the JSON output
print(json.dumps(result, indent=2))

"""
cache = {}
VIOLENCE_KEYWORDS = {
    "kill",
    "murder",
    "shot",
    "stab",
    "assault",
    "attack",
    "blood",
    "death",
    "corpse",
    "torture",
    "war",
    "assassin",
    "assassinate",
}
GORE_KEYWORDS = {"gore", "dismembered", "decapitated", "organs", "guts", "mutilation"}
SEXUAL_KEYWORDS = {
    "sex",
    "porn",
    "nude",
    "nudity",
    "xxx",
    "explicit",
    "fuck",
    "fucking",
    "fucks",
    "lesbian",
    "cum",
    "cumming",
    "pussy",
    "cock",
    "creampie",
    "deep throat",
}


# text cleaning
def _clean_text(text):
    return re.sub(r"\s+", " ", text).lower()


# extract image URLs
def _extract_image_urls(soup, base_url):
    return [
        urljoin(base_url, img.get("src"))
        for img in soup.find_all("img")
        if img.get("src")
    ]


# download an image, return local path
def _download_image(url):
    try:
        r = requests.get(url, timeout=10, stream=True)
        if r.status_code != 200:
            return None
        fd, path = tempfile.mkstemp(".jpg")
        with os.fdopen(fd, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return path
    except Exception:
        return None


# text-based violence/gore/sexual scoring
def _analyze_text(text, meta_description=None, meta_keywords=None):
    words = set(text.split())

    # Include meta description/keywords
    if meta_description:
        words |= set(meta_description.lower().split())
    if meta_keywords:
        for kw in meta_keywords:
            words |= set(kw.lower().split())

    return {
        "violence_score": len(words & VIOLENCE_KEYWORDS),
        "gore_score": len(words & GORE_KEYWORDS),
        "sexual_keywords_count": len(words & SEXUAL_KEYWORDS),
    }


# modern NSFW image scoring
def _analyze_images(image_urls):
    detector = NSFWDetector()
    max_score = 0.0

    for url in image_urls[:8]:
        path = _download_image(url)
        if not path:
            continue
        try:
            img = Image.open(path).convert("RGB")
            # returns dict of class -> probability
            probs = detector.predict_proba(img)
            # "nsfw" class prob or highest non-safe probability
            score = max(v for v in probs.values())
            max_score = max(max_score, score)
        except Exception:
            pass
        finally:
            os.remove(path)

    return round(max_score, 3)


# determine PG / PG13 / R / Adult rating
def _determine_rating(violence, gore, sexual_count, nsfw_score):
    if nsfw_score > 0.85 or sexual_count > 5:
        return "Adult"
    if gore > 0 or violence > 6 or nsfw_score > 0.6:
        return "R"
    if violence > 0 or sexual_count > 0 or nsfw_score > 0.3:
        return "PG13"
    return "PG"


# combined score for sorting / thresholds
def _calculate_content_score(violence, gore, sexual_count, nsfw_score):
    nsfw_scaled = nsfw_score * 10
    score = (violence * 2) + (gore * 3) + (sexual_count * 1.5) + nsfw_scaled
    return round(score, 2)


# map rating + content_score to an IRC‑friendly flag
def _irc_flag(rating, content_score):
    if rating == "Adult" or content_score > 10:
        return "ADULT"
    if rating == "R" or content_score > 5:
        return "RATED-R"
    if rating == "PG13" or content_score > 2:
        return "WARNING"
    return "SAFE"


# main API
def inspect_url(url: str) -> dict:
    global cache
    if url in cache.keys():
        return cache[url]

    response = requests.get(url, timeout=15, headers={"User-Agent": "URLInspector/1.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = _clean_text(soup.get_text(" "))

    # extract meta
    meta_description = next(
        (
            meta.get("content")
            for meta in soup.find_all("meta")
            if meta.get("name", "").lower() == "description"
        ),
        None,
    )
    meta_keywords = next(
        (
            meta.get("content").split(",")
            for meta in soup.find_all("meta")
            if meta.get("name", "").lower() == "keywords"
        ),
        [],
    )

    # analyze text + meta
    text_scores = _analyze_text(page_text, meta_description, meta_keywords)

    # analyze images
    image_urls = _extract_image_urls(soup, url)
    max_nsfw_score = _analyze_images(image_urls)

    # boost score if sexual keywords + NSFW images missing
    if max_nsfw_score < 0.1 and text_scores["sexual_keywords_count"] >= 2:
        max_nsfw_score = 0.9  # treat as adult

    rating = _determine_rating(
        text_scores["violence_score"],
        text_scores["gore_score"],
        text_scores["sexual_keywords_count"],
        max_nsfw_score,
    )

    content_score = _calculate_content_score(
        text_scores["violence_score"],
        text_scores["gore_score"],
        text_scores["sexual_keywords_count"],
        max_nsfw_score,
    )

    irc_flag = _irc_flag(rating, content_score)

    data = {
        "url": url,
        "title": soup.title.string.strip() if soup.title else None,
        "description": meta_description,
        "keywords": meta_keywords,
        "language": detect(page_text) if page_text else None,
        "text_analysis": text_scores,
        "max_nsfw_image_score": max_nsfw_score,
        "rating": rating,
        "content_score": content_score,
        "irc_flag": irc_flag,
        "image_count": len(image_urls),
    }
    cache[url] = data
    return data
