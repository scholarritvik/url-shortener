from flask import Flask,render_template,request,redirect
import random
import string

app = Flask(__name__)

url_db  = {} #temporary storage

def generate(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/",methods=["GET","POST"])
def home():
    short_url = None

    if request.method=="POST":
        original_url = request.form["url"]
        code = generate()
        url_db[code] = original_url
        short_url = request.host_url + code
    
    return render_template("index.html",short_url=short_url)

@app.route("/<code>")
def redirect_url(code):
    original_url = url_db.get(code)
    if original_url:
        return redirect(original_url)
    return "URL not found!"

if __name__ == "__main__":
    app.run(debug=True)
