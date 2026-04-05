import os
import json
import re
import requests
import nltk
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from google import genai

# ------------------ SETUP ------------------
load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

client = genai.Client(api_key=API_KEY)
app = Flask(__name__, template_folder="templates")

# Download tokenizer once
nltk.download("punkt")

vader = SentimentIntensityAnalyzer()

# ------------------ SCRAPER ------------------
def extract_text_from_url(url, max_chars=40000):
    headers = {"User-Agent": "NewsBiasDetector/1.0"}
    resp = requests.get(url, headers=headers, timeout=12)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    article_tag = soup.find("article")
    if article_tag:
        text = " ".join(p.get_text(" ", strip=True) for p in article_tag.find_all("p"))
        if len(text) > 200:
            return text[:max_chars]

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = "\n\n".join(paragraphs)

    if len(text) < 100:
        raise RuntimeError("Extracted content too short")

    return text[:max_chars]

# ------------------ BASIC NLP ------------------
def analyze_basic_nlp(text):
    short_text = text[:2000]

    blob = TextBlob(short_text)
    vader_scores = vader.polarity_scores(short_text)

    return {
        "polarity": round(blob.sentiment.polarity, 3),
        "subjectivity": round(blob.sentiment.subjectivity, 3),
        "vader": vader_scores,
        "tones": {
            "emotional": int(abs(vader_scores["compound"]) * 100),
            "subjective": int(blob.sentiment.subjectivity * 100),
            "positive": int(vader_scores["pos"] * 100),
            "negative": int(vader_scores["neg"] * 100)
        }
    }

# ------------------ PROMPT ------------------
def build_prompt(article_text, tone, basic_nlp):
    tone_map = {
        "neutral": "balanced and neutral",
        "facts": "fact-only (no opinions)",
        "simple": "simple explanation for a 10-year-old"
    }

    return f"""
Respond ONLY with valid JSON.

Keys:
- summary (3–6 sentences, {tone_map.get(tone)})
- keyPoints (5 items)
- biasScore (-50 to +50)
- biasText (short explanation)
- biasPosition (0-100)
- tones (emotional, subjective, positive, negative)

Pre-analysis:
Polarity: {basic_nlp['polarity']}
Subjectivity: {basic_nlp['subjectivity']}
VADER: {basic_nlp['vader']}

Article:
\"\"\"{article_text}\"\"\"
"""

# ------------------ JSON CLEANER ------------------
def clean_json(raw):
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    return json.loads(raw)

# ------------------ ROUTES ------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)

    content = data.get("content", "").strip()
    is_url = data.get("isUrl", False)
    tone = data.get("tone", "neutral")

    if not content:
        return jsonify({"error": "No content provided"}), 400

    try:
        article_text = extract_text_from_url(content) if is_url else content
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # 🔹 Step 1: Fast NLP
    basic_nlp = analyze_basic_nlp(article_text)

    # 🔹 Step 2: Gemini reasoning
    prompt = build_prompt(article_text, tone, basic_nlp)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        parsed = clean_json(response.text)

        bias_score = float(parsed.get("biasScore", 0))
        bias_position = max(0.0, min(100.0, bias_score + 50.0))

        result = {
            "summary": parsed.get("summary", ""),
            "keyPoints": parsed.get("keyPoints", []),
            "biasScore": bias_score,
            "biasText": parsed.get("biasText", ""),
            "biasPosition": bias_position,
            "tones": basic_nlp.get("tones", {}),

            # 🔥 Combined NLP
            "basicNLP": basic_nlp
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)