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



def email_check(username,password):
    cursor.execute("SELECT Email FROM users")
    emails_list = cursor.fetchall()
    if username in emails_list:
        cursor.execute((f"select password from password where username={username}"))
        password_value = cursor.fetchone()
        if password = password_value:
            return render_template("Home_Page.html")
        else:/









#closing connection once finished with app
# cursor.close()
# mydb.close()