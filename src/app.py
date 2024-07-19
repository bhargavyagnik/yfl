from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
  search_query = ""
  if request.method == "POST":
    search_query = request.form["search"]
  return render_template("index.html", search_query=search_query)

if __name__ == "__main__":
  app.run(debug=True)
