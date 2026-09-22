import json
import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")


def load_params():
    """يقرأ المعاملات (r, PSH, تكاليف, ...) من data.json في كل طلب،
    حتى لو الشخص 1 عدّل الملف وهو الخادم شغال، تنعكس التعديلات مباشرة."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/params")
def api_params():
    return jsonify(load_params())


if __name__ == "__main__":
    app.run(debug=True, port=5000)