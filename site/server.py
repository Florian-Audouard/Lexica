from flask import Flask, jsonify, render_template, request
import os
import json
from database import search, modif_data


os.chdir(os.path.dirname(__file__))


app = Flask(__name__)


@app.route("/search", methods=["POST"])
def fetch():
    result = json.loads(request.get_data())
    keyword = result["keyword"]
    langueBase = result["langueBase"]
    langueResult = result["langueResult"]
    res = search(keyword, langue=langueResult, langue_base=langueBase)
    return jsonify(res)


@app.route("/edit", methods=["POST"])
def edit():
    for change in json.loads(request.get_data()):
        modif_data(change[0], change[1], change[2])
        pass
    return "ok"


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    app.run()
