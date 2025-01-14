from flask import Flask, render_template, request, redirect, session
import mysql.connector
from flask_session.__init__ import Session
import App.Item

app = Flask(__name__)


def open_connection():
    connection = mysql.connector.connect(host='localhost',
                                         user='root',
                                         password='root',
                                         database='group_008')    # Creating connection & Connect to the MySQL server:
    cursor = connection.cursor()                                # Creating cursor:
    return connection, cursor


def close_connection(connection, cursor):
    connection.commit()                                         # commit the transaction
    cursor.close()                                              # close cursor
    connection.close()                                          # close connection


# Secret key for session management
app.secret_key = 'your_secret_key'

# Flask-Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_FILE_THRESHOLD"] = 100
Session(app)

# welcome page. here you can login and register as librarian/member


@app.route('/', methods=["GET"])
def welcomepage():
    return render_template("Welcome_Page.html")



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        connection, cursor = open_connection()

        try:
            # Check if email exists in managers
            cursor.execute("SELECT password FROM managers WHERE email = %s", (email,))
            result = cursor.fetchone()  # Fetch a single result instead of all
            if result and result[0] == password:
                session['email'] = email
                return render_template("M_Home_Page.html")  # Correct template name

            # Check if email exists in users
            cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()  # Fetch a single result instead of all
            if result and result[0] == password:
                session['email'] = email
                return render_template("Home_Page.html")  # Correct template name

            # If no match found
            message = 'Incorrect Login Details.'
            return render_template("Login.html",message=message)

        finally:
            # Ensure connection is closed even if there's an error
            close_connection(connection, cursor)

    else:
        return render_template("Login.html")  # Correct redirection for GET request

@app.route("/SignUp" ,methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        Name = request.form["Name"]
        Password = request.form["Password"]
        DOB = request.form["DOB"]
        Gender = request.form["Gender"]
        Faculty = request.form["Faculty"]
        connection, cursor = open_connection()
        try:
            cursor.execute("select email from users WHERE email = %s", (email,))
            result = cursor.fetchone()  # Fetch a single result instead of all
            if result:
                message = "This email has already registered"
                return render_template('SignUp.html',message=message)

            cursor.execute("INSERT INTO users(Email,User_Name, Password, DOB,Gender,Faculty) Values(%s,%s,%s,%s,%s,%s)",(email,Name,Password,DOB,Gender,Faculty))
            connection.commit()
            return render_template("login.html", message="Registration successful! Please log in.")
        finally:
            close_connection(connection, cursor)
    else:
        return render_template("SignUp.html")

@app.route("/M_Home_Page")
def M_Home_Page():
    return render_template("M_Home_Page.html")

@app.route("/Home_Page")
def Home_Page():
    return render_template("Home_Page.html")

@app.errorhandler(404)
def invalid_route(e):
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)




