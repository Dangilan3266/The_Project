from main import *




if __name__ == "__main__":
    app.run(debug=True)

#closing connection once finished with app
cursor.close()
mydb.close()