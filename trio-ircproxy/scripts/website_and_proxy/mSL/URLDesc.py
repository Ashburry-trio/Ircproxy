"""Utilities for analyzing web pages for safety, content category, and SEO metadata.

This module fetches a URL, extracts and normalizes the page text, and applies
heuristics plus a pre-trained NSFW classifier to estimate whether the content
is sexual, violent, or gory. It also computes basic SEO information such as
page title, meta description, and TF–IDF-based keywords, and returns a
structured JSON-like result that can be cached on disk.
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from langdetect import detect
from nsfw_detector import predict as nsfw_predict
from PIL import Image
import torch

# --------------------------
# Config
# --------------------------
CACHE_FILE = os.path.join(os.path.dirname(__file__), "settings", "url_cache.json")

TEMP_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "settings", "tmp_images")

if not os.path.exists(TEMP_IMAGE_DIR):
    os.makedirs(TEMP_IMAGE_DIR)

# Load NSFW model
NSFW_MODEL = nsfw_predict.load_model('nsfw_model.h5')

# Violence/Gore model placeholder (use a proper model here)
VIOLENCE_MODEL = None  # Replace with real classifier if available

# Multilingual categories
MULTI_LANG_CATEGORIES = {
    "en": {
        "sexual": {
            "weight": 1.0,
            "keywords": {
                "porn", "xxx", "sex", "escort", "nude", "nsfw",
                "fetish", "hentai", "camgirl", "onlyfans",
                "nudity", "sexually explicit content"
            },
            "phrases": {
                "hardcore sex",
                "adult video",
                "live cam sex",
                "explicit depictions of sexual activity",
                "this is an adult website"
            }
        },
        "violence": {
            "weight": 1.2,
            "keywords": {"kill", "murder", "shooting", "assault"},
            "phrases": {"how to kill", "school shooting"}
        },
        "gore": {
            "weight": 1.5,
            "keywords": {"gore", "blood", "beheading"},
            "phrases": {"graphic violence"}
        }
    }
}

NEGATIONS = {"no", "not", "never", "without", "anti", "prevent", "stop", "against"}


# --------------------------
# Helper Functions
# --------------------------
def load_cache():
    """Load the cached URL analysis results from disk.

    The cache is stored as a JSON file at :data:`CACHE_FILE` and maps absolute
    URL strings to their previously computed analysis results.

    Returns:
        dict: Mapping of URL strings to previously computed analysis result
        objects. If the cache file does not exist or cannot be read, an empty
        dictionary is returned.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Persist the URL analysis cache to disk.

    Args:
        cache (dict): Mapping from URL string to analysis result
            dictionaries that should be serialized to ``CACHE_FILE``.
    """
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def is_false_positive(text, keyword, window=5):
    """Heuristically flag a keyword match as a likely false positive.

    This helper looks for negation terms (for example, "no", "not", "never",
    "without") in a window of tokens immediately preceding the keyword. If any
    negation token is present, the match is treated as describing the absence of
    the concept rather than the concept itself.

    Args:
        text (str): Full page text that is being analyzed.
        keyword (str): Keyword that was matched in the text.
        window (int, optional): Number of tokens before ``keyword`` to search for
            negation markers. Defaults to 5.

    Returns:
        bool: ``True`` if the match is likely a false positive due to local
        negation context, otherwise ``False``.
    """
    words = text.split()
    for i, w in enumerate(words):
        if w == keyword:
            start = max(0, i - window)
            context = words[start:i]
            if any(n in context for n in NEGATIONS):
                return True
    return False


# --------------------------
# Image Analysis
# --------------------------
def analyze_image(img_path):
    """Fetch and analyze a URL for safety, content category, and SEO signals.

    This is the main entry point for the URL description helper. It optionally
    returns cached results if the URL has been analyzed before, otherwise it:

    * Downloads the page HTML.
    * Strips non-content tags such as ``<script>``, ``<style>``, and ``<noscript>``.
    * Normalizes and truncates the visible text content.
    * Detects the page language and selects language-specific category
      definitions.
    * Computes category scores (for example, sexual, violence, gore) based on
      keyword and phrase hits, including a simple negation-aware false-positive
      filter.
    * Derives an overall content rating (Everyone / Teen / Adult) from the
      weighted scores.
    * Extracts basic SEO information (page title, meta description, meta
      keywords, and TF–IDF-based keywords).
    * Downloads, classifies, and then deletes images referenced by ``<img>``
      tags using :func:`analyze_image`.
    * Caches the final result on disk for future calls.

    Args:
        url (str): Absolute URL to fetch and analyze.

    Returns:
        dict | None: A structured result dictionary containing the following
        top-level keys when analysis succeeds::

            {
                "url": str,
                "rating": str,
                "confidence_percent": float,
                "language": str,
                "mobile_friendly": bool,
                "seo": {
                    "title": str | None,
                    "description": str | None,
                    "meta_keywords": str | None,
                    "extracted_keywords": list[str],
                },
                "content_analysis": dict,
                "images": list[dict],
            }

        If the request fails or cannot be completed, ``None`` may be returned
        depending on how network exceptions are handled in the caller.

    Raises:
        requests.RequestException: If the HTTP request fails and exceptions are
            not suppressed.
        langdetect.lang_detect_exception.LangDetectException: If language
            detection fails before being caught.
    """
    adult_score = 0.0
    violence_score = 0.0

    try:
        scores = nsfw_predict.classify(NSFW_MODEL, img_path)
        adult_score = scores[img_path].get('porn', 0) + scores[img_path].get('hentai', 0) + scores[img_path].get('sexy',
                                                                                                                 0)
        adult_score = round(adult_score, 4)
    except:
        adult_score = 0.0

    # Placeholder violence detection
    # Replace with real model inference for actual violence/gore detection
    violence_score = 0.0

    return adult_score, violence_score


# --------------------------
# Main Analyzer
# --------------------------
def analyze_url(url):
    # Load cache
    cache = load_cache()
    if url in cache:
        print(f"[CACHE HIT] {url}")
        return cache[url]

    print(f"[PROCESSING] {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception
        return

    ```python


soup = BeautifulSoup(r.text, "html.parser")

# Remove unwanted tags
for tag in soup(["script", "style", "noscript"]):
    tag.decompose()

# Extract and process text
text = " ".join(soup.stripped_strings).lower()[:40000]

# Language detection
try:
    language = detect(text)
except:
    language = "en"

lang_categories = MULTI_LANG_CATEGORIES.get(language, {})
if not lang_categories:
    lang_categories = MULTI_LANG_CATEGORIES.get("en", {})

# Check for mobile-friendliness
mobile_friendly = bool(soup.find("meta", attrs={"name": "viewport"}))

# Content analysis
category_results = {}
total_weighted = 0
total_possible = 0

for category, cfg in lang_categories.items():
    matched_keywords = [kw for kw in cfg["keywords"] if kw in text and not is_false_positive(text, kw)]
    matched_phrases = [ph for ph in cfg["phrases"] if ph in text]
    raw_hits = len(matched_keywords) + len(matched_phrases) * 2
    raw_score = min(100, raw_hits * 15)
    weighted_score = raw_score * cfg["weight"]

    category_results[category] = {
        "raw_score": raw_score,
        "weighted_score": round(weighted_score, 2),
        "matched_keywords": matched_keywords,
        "matched_phrases": matched_phrases
    }

    total_weighted += weighted_score
    total_possible += 100 * cfg["weight"]

confidence = round((total_weighted / total_possible) * 100, 2)
rating = "Adult / R" if confidence >= 60 else "Teen / PG-13" if confidence >= 30 else "Everyone"

# SEO and keywords extraction
title = soup.title.string.strip() if soup.title else None


def meta(name):
    tag = soup.find("meta", attrs={"name": name})
    return tag.get("content", "").strip() if tag else None


vectorizer = TfidfVectorizer(stop_words="english", max_features=12)
vectorizer.fit([text])
extracted_keywords = vectorizer.get_feature_names_out().tolist()

# Image processing
images = []
for img_tag in soup.find_all("img"):
    img_url = img_tag.get("src")
    if not img_url:
        continue
    try:
        # Download image
        img_data = requests.get(img_url, headers=headers, timeout=5).content
        img_name = os.path.basename(img_url) or "temp.jpg"
        new_img_file, img_ext = os.path.splitext(os.path.basename(img_path))
        new_img_file += str(randint(1000, 9999)) + img_ext
        img_path = os.path.join(TEMP_IMAGE_DIR, img_name)
        with open(img_path, "wb") as f:
            f.write(img_data)

        # Analyze image
        adult_score, violence_score = analyze_image(img_path)
        combined_score = max(adult_score, violence_score)

        images.append({
            "url": img_url,
            "adult_score": adult_score,
            "violence_score": violence_score,
            "combined_score": combined_score
        })

        # Delete image
        os.remove(img_path)
    except:
        continue

# Final JSON result
result = {
    "url": url,
    "rating": rating,
    "confidence_percent": confidence,
    "language": language,
    "mobile_friendly": mobile_friendly,
    "seo": {
        "title": title,
        "description": meta("description"),
        "meta_keywords": meta("keywords"),
        "extracted_keywords": extracted_keywords
    },
    "content_analysis": category_results,
    "images": images
}

# Save cache
cache[url] = result
save_cache(cache)

return result
```