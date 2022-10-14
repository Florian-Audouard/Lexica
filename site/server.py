import os
import json
from flask import Flask, jsonify, render_template, request
from database import search, modif_data, list_langue


os.chdir(os.path.dirname(__file__))


app = Flask(__name__)


@app.route("/search", methods=["POST"])
def fetch_search():
    result = json.loads(request.get_data())
    keyword = result["keyword"]
    langue_base = result["langueBase"]
    langue_result = result["langueResult"]
    res = search(keyword, langue=langue_result, langue_base=langue_base)
    return jsonify(res)


@app.route("/listLangue", methods=["GET"])
def fetch_langue():
    res = list_langue()
    return jsonify(res)


@app.route("/edit", methods=["POST"])
def edit():
    for change in json.loads(request.get_data()):
        modif_data(change[0], change[1], change[2])
    return "ok"


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    app.run()
