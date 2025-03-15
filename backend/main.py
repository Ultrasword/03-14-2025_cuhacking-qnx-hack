import flask


app = flask.Flask(__name__)


# ============================================ #
"""
Define purpose of this backend server


Flask backend runs 



"""
# ============================================ #


@app.route("/")
def home():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)
