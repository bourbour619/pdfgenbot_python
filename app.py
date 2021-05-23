from flask import Flask
from os import path

app = Flask(__name__)

@app.route('/')
def index():
    return path.join(path.dirname(__file__),'bot')


if __name__ == "__main__":
    app.run(debug=True)