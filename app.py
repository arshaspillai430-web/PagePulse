from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/audit", methods=["POST"])
def audit():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "URL is required"}), 400

    url = data["url"]

    # Check valid URL
    parsed_url = urlparse(url)

    if not parsed_url.scheme or not parsed_url.netloc:
        return jsonify({"error": "Invalid URL"}), 400

    try:
        start_time = time.time()

        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response_time = round(time.time() - start_time, 3)

        # Check HTML response
        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            return jsonify({
                "error": "URL does not contain an HTML page"
            }), 400

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract details
        title = soup.title.text.strip() if soup.title else "No title"

        meta = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        meta_description = (
            meta["content"].strip()
            if meta and meta.get("content")
            else "No description"
        )

        h1_count = len(soup.find_all("h1"))

        images = soup.find_all("img")

        missing_alt = 0

        for img in images:
            if not img.get("alt"):
                missing_alt += 1

        words = soup.get_text(
            separator=" "
        ).split()

        word_count = len(words)

        return jsonify({
            "status_code": response.status_code,
            "response_time": response_time,
            "title": title,
            "meta_description": meta_description,
            "h1_count": h1_count,
            "images_missing_alt": missing_alt,
            "word_count": word_count
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Request timed out"
        }), 408

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Unable to fetch URL"
        }), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)