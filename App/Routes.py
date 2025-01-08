from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)

#setting up SQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="group_008"
)
cursor = mydb.cursor()



@app.route('/')
def homepage():
    return render_template("Home_Page.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if 'temp_db'.get(username) == password:       # connection between db and the login method
            session['username'] = username
            return redirect("/")
        else:
            return render_template("login.html", massage='Incorrect Login Details.')
    return render_template("Login.html")


@app.route("/SignUp")
def signup():
    return render_template("SignUp.html")


@app.errorhandler(404)
def invalid_route(e):
    return redirect("/")






