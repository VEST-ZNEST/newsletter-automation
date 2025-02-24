from flask import Flask, request, jsonify
from fetch_ai_news import fetch_ai_news_with_params, format_article

app = Flask(__name__)

@app.route("/api/ai-news", methods=["GET"])
def get_ai_news():
    # Get query parameters
    date = request.args.get("date")
    num_headlines = request.args.get("numHeadlines", 5)
    try:
        num_headlines = int(num_headlines)
    except ValueError:
        num_headlines = 5

    try:
        articles = fetch_ai_news_with_params(date, num_headlines)
        # Format each article using your format_article function.
        headlines = [format_article(article) for article in articles]
        return jsonify({"headlines": headlines})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
