import json
import os

from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")
ANALYSIS_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "data.json")


def load_params():
    """يقرأ المعاملات (r, PSH, تكاليف, ...) من data.json في كل طلب،
    حتى لو الشخص 1 عدّل الملف وهو الخادم شغال، تنعكس التعديلات مباشرة."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("analysis.html")


@app.route("/decision")
def decision():
    return render_template("index.html")


@app.route("/api/params")
def api_params():
    return jsonify(load_params())


@app.route("/api/analysis")
def api_analysis():
    with open(ANALYSIS_DATA_PATH, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))


@app.route("/assets/particles.js")
def particles_asset():
    return send_from_directory(os.path.join(os.path.dirname(__file__), "src", "assets"), "particles.js")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)