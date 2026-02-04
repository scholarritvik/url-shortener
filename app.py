from flask import Flask, render_template, request, redirect, url_for, abort
from services import create_short_url, resolve_short_code
from database import init_db

app = Flask(__name__)

# Initialize DB once at startup
init_db()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        original_url = request.form.get("url")

        try:
            code = create_short_url(original_url)
        except ValueError:
            return render_template("index.html", error="Invalid URL")

        return redirect(url_for("result", code=code))

    return render_template("index.html")


@app.route("/result/<code>")
def result(code):
    short_url = url_for("redirect_url", code=code, _external=True)
    return render_template("index.html", short_url=short_url)


@app.route("/<code>")
def redirect_url(code):
    original_url = resolve_short_code(code)

    if not original_url:
        abort(404)

    return redirect(original_url)


@app.route("/stats")
def stats():
    # optional: move this to database.py later
    from database import get_all_urls
    data = get_all_urls()
    return render_template("stats.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)