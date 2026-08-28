from flask import Flask, render_template, url_for

sonricksstoreApp = Flask(__name__)

@sonricksstoreApp.route("/")
def home():
    return render_template("home.html" )


if __name__ == "__main__":
    sonricksstoreApp.run(debug=True, port=3550)
