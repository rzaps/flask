from flask import render_template,request, redirect, url_for
from app import app

users = []


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/blog/")
def blog():
    return render_template("blog.html")

@app.route("/contacts/")
def contacts():
    return render_template("contacts.html")

@app.route("/form/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        city = request.form.get("city")
        age = request.form.get("age")
        hobby = request.form.get("hobby")
        if name and city and age:
            users.append({"name": name, "city": city, "age": age, "hobby": hobby})
            return redirect(url_for("form"))
    return render_template("form.html", users=users)