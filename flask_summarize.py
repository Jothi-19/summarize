import os
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# ---------------- HOME PAGE (ASK INPUTS) ----------------
@app.route("/", methods=["GET"])
def home():
    return """
    <html>
        <head>
            <title>Website Summary Generator</title>
        </head>
        <body>
            <h2>Website Summary Generator</h2>
            <form method="post" action="/summarize">
                <label>Website URL:</label><br>
                <input type="text" name="url" required><br><br>

                <label>Word Count:</label><br>
                <input type="number" name="word_limit" required><br><br>

                <button type="submit">Generate Summary</button>
            </form>
        </body>
    </html>
    """


# ---------------- SUMMARY PROCESS ----------------
@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        url = request.form.get("url")
        word_limit = int(request.form.get("word_limit"))

        if word_limit <= 0:
            return "<h3>Word limit must be greater than zero</h3>"

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "<h3>API key not found</h3>"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = " ".join(soup.stripped_strings)
        if not text:
            return "<h3>No readable content found</h3>"

        client = Groq(api_key=api_key)

        prompt = f"""
        Summarize the following website content in {word_limit} words.

        {text[:6000]}
        """

        result = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        summary_text = result.choices[0].message.content.strip()

        return f"""
        <html>
            <body>
                <h2>Summary Output</h2>
                <p>{summary_text}</p>
                <br>
                <a href="/">Generate Another Summary</a>
            </body>
        </html>
        """

    except Exception as e:
        return f"<h3>Error: {e}</h3>"


if __name__ == "__main__":
    app.run(debug=True)

    