from ast import keyword
from flask import Flask, jsonify, render_template, request
import os
import json
from database import search


os.chdir(os.path.dirname(os.path.abspath(__file__)))


app = Flask(__name__)
if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    app.run()


@app.route("/search", methods=["GET", "POST"])
def fetch():
    keyword = json.loads(request.get_data())["keyword"]
    res = search(keyword)
    return jsonify(res)


@app.route("/")
def index():
    return render_template("index.html")
