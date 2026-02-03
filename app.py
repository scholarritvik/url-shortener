from flask import Flask, render_template, request, redirect, url_for
import random
import string

app = Flask(__name__)

url_db = {}  # temporary storage


def generate(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        original_url = request.form["url"]
        code = generate()
        url_db[code] = original_url
        return redirect(url_for("result", code=code))

    return render_template("index.html")


@app.route("/result/<code>")
def result(code):
    short_url = url_for("redirect_url", code=code, _external=True)
    return render_template("index.html", short_url=short_url)


@app.route("/<code>")
def redirect_url(code):
    original_url = url_db.get(code)
    if original_url:
        return redirect(original_url)
    return "URL not found!"


if __name__ == "__main__":
    app.run(debug=True)
