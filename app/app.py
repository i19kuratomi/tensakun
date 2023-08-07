from flask import Flask, render_template, request
from tensakun import main, error
import diff

app = Flask(__name__, template_folder='./public')


@app.route("/")
def index():
    return render_template('tensaku.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/api", methods=['POST'])
def post():
    args = request.args
    input = args.get("input")
    isKeigo = int(args.get("isKeigo"))
    isHankaku = int(args.get("isHankaku"))
    result = main(input, isKeigo, isHankaku)
    error_result = error(input, result)
    diff_result= diff.compare(input, result)
    return {"result": result, "diff": diff_result}


if __name__ == "__main__":
    app.run(debug=True)
