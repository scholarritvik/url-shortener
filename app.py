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
        expiry = request.form.get("expiry")

        try:
            code = create_short_url(original_url, expiry)
            short_url = url_for("redirect_url", code=code, _external=True)
            return render_template("index.html", short_url=short_url)

        except ValueError as e:
            return render_template(
                "index.html",
                error=str(e),
                input_url=original_url,
                input_expiry=expiry
            )

    return render_template("index.html")


@app.route("/result/<code>")
def result(code):
    short_url = url_for("redirect_url", code=code, _external=True)
    return render_template("index.html", short_url=short_url)


@app.route("/<code>")
def redirect_url(code):
    url, status = resolve_short_code(code)

    if status == "not_found":
        abort(404)

    if status == "expired":
        abort(410)

    return redirect(url)


@app.route("/stats")
def stats():
    # optional: move this to database.py later
    from database import get_all_urls
    data = get_all_urls()
    return render_template("stats.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)