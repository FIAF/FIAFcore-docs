
from flask import Flask, render_template
import json
import pathlib

with open(pathlib.Path.cwd() / 'static' / 'summary.json') as data:
    data = json.load(data)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home_page():

    return render_template(
        'index.html', 
        data=data
        )

if __name__ == "__main__":
    app.run(debug=True, port=5027)