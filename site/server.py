import os
import json
from flask import Flask, jsonify, render_template, request
from database import search, modif_data, list_langue, history, get_page_db


os.chdir(os.path.dirname(__file__))


app = Flask(__name__)


@app.route("/search", methods=["POST"])
def fetch_search():
    result = json.loads(request.get_data())
    keyword = result["keyword"]
    langue_base = result["langueBase"]
    langue_result = result["langueResult"]
    offset = result["offset"]
    res = search(keyword, langue=langue_result, langue_base=langue_base, offset=offset)
    return jsonify({"table": res[0], "count": res[1]})


@app.route("/listLangue", methods=["POST"])
def fetch_langue():
    result = json.loads(request.get_data())
    res = list_langue(result["livre"])
    return jsonify(res)


@app.route("/edit", methods=["POST"])
def edit():
    for change in json.loads(request.get_data()):
        modif_data(change[0], change[1], change[2])
    return "ok"


@app.route("/historyRequest", methods=["POST"])
def history_request():
    result = json.loads(request.get_data())
    langue = result["langue"]
    sens = result["sens"]
    return jsonify(history(langue=langue, sens=sens))


@app.route("/getPage", methods=["POST"])
def get_page():
    result = json.loads(request.get_data())
    livre = result["livre"]
    num_page = result["page"]
    return jsonify(get_page_db(livre, num_page))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/historique")
def historique():
    return render_template("historique.html")


@app.route("/correction-page")
def correction_page():
    return render_template("correction-page.html")


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    app.run()
