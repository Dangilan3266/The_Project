from flask import Flask, redirect, request, render_template
import mysql.connector
from App.Routes import *




if __name__ == "__main__":
    app.run(debug=True)

#closing connection once finished with app
cursor.close()
mydb.close()