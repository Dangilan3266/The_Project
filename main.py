from flask import Flask, render_template, request, redirect, session
import mysql.connector
from flask_session.__init__ import Session
import App.Item
from datetime import date, datetime
from werkzeug.utils import secure_filename, os


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
def welcome_page():
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
                return redirect("/M_Home_Page")

            # Check if email exists in users
            cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()  # Fetch a single result instead of all
            if result and result[0] == password:
                session['email'] = email
                return redirect("/Home_Page")  # Correct template name

            # If no match found
            else:
                message = 'Incorrect Login Details.'
                return render_template("Login.html",message=message)

        finally:
            # Ensure connection is closed even if there's an error
            close_connection(connection, cursor)

    else:
        return render_template("Login.html")  # Correct redirection for GET request

@app.route("/SignUp" ,methods=["POST", "GET"])
def signup():
    today = date.today().strftime("%Y-%m-%d")
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

            cursor.execute("INSERT INTO users(Email,Name, Password, DOB,Gender,Faculty) Values(%s,%s,%s,%s,%s,%s)",(email,Name,Password,DOB,Gender,Faculty))
            connection.commit()
            return render_template("login.html", message="Registration successful! Please log in.")
        finally:
            close_connection(connection, cursor)
    else:
        return render_template("SignUp.html", today=today)


@app.route("/Home_Page", methods=["POST", "GET"])
def Home_Page():
    if 'email' not in session:
        return redirect("/")  # Redirect to log in if no session exists

    connection, cursor = open_connection()

    try:
        if request.method == "POST":
            # Fetch items in stock
            cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
            items = cursor.fetchall()

            # Handle Transaction Logic
            email = session["email"]
            transaction_date = datetime.now()
            cursor.execute("SELECT MAX(order_id) FROM transactions")
            result = cursor.fetchone()
            last_transaction_number = result[0] if result[0] is not None else 0
            new_transaction_number = last_transaction_number + 1

            # Insert the transaction into `transactions` table
            cursor.execute("""
                INSERT INTO transactions (Order_id, Date, Users_Email)
                VALUES (%s, %s, %s)
            """, (new_transaction_number, transaction_date, email))

            for item in items:
                item_id = int(item[0])  # G_ID
                desired_quantity = int(request.form.get(f'quantity_{item_id}', 0))  # Handle missing quantities gracefully
                new_quantity = int(item[1]) - desired_quantity

                if desired_quantity > 0:  # Only update for valid purchases
                    # Update garment stock
                    cursor.execute("UPDATE garment SET Quantity_in_stock = %s WHERE G_id = %s", (new_quantity, item_id))

                    # Insert the garment transaction into `transactions_garment` table
                    cursor.execute("""
                        INSERT INTO transactions_garment (Quantity, Transactions_Order_ID, Garment_G_ID)
                        VALUES (%s, %s, %s)
                    """, (desired_quantity, new_transaction_number, item_id))

            message = "Thank You for Your Purchase!"

            # Fetch updated items for display
            cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
            updated_items = cursor.fetchall()

            # Commit all changes
            connection.commit()
        else:
            # Fetch items for GET request
            cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
            updated_items = cursor.fetchall()
            message = request.args.get("message", None)

    except Exception as e:
        connection.rollback()
        message = f"Error: {e}"
        updated_items = []
    finally:
        close_connection(connection, cursor)

    return render_template("Home_Page.html", message=message, products=updated_items)


# @app.route("/M_Home_Page")
# def M_Home_Page(): ## need to be
#     if 'email' not in session:
#         return redirect("/")  # Redirect to log in if no session exists
#
#     connection, cursor = open_connection()
#
#     try:
#         if request.method == "POST":
#             cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
#             items = cursor.fetchall()
#
#             for item in items:
#                 item_id = int(item[0])  # G_ID
#                 desired_quantity = int(
#                     request.form.get(f'quantity_{item_id}', 0))  # Handle missing quantities gracefully
#                 new_quantity = int(item[1]) - desired_quantity
#                 if desired_quantity > 0:  # Only update for valid purchases
#                     cursor.execute("UPDATE garment SET Quantity_in_stock = %s WHERE G_id = %s",
#                                    (new_quantity, item_id))
#
#             message = "Thank You for Your Purchase!"
#
#             # Fetch updated items for display
#             cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
#             updated_items = cursor.fetchall()
#
#             # Handle Transaction Logic
#             email = session["email"]
#             transaction_date = datetime.now()  # Correctly set date
#             cursor.execute("SELECT MAX(order_id) FROM transactions")
#             result = cursor.fetchone()
#             last_transaction_number = result[0] if result[0] is not None else 0
#             new_transaction_number = last_transaction_number + 1
#
#             # insert transaction to DB
#             cursor.execute("""
#                 INSERT INTO transactions (Order_id, Date, Users_Email)
#                 VALUES (%s, %s, %s)
#             """, (new_transaction_number, transaction_date, email))
#             # insert transaction garments to DB by pull from html
#             # cursor.execute("""
#             #     INSERT INTO transactions_garment (Order_id, Date, Users_Email)
#             #     VALUES (%s, %s, %s)
#             # """, (new_transaction_number, transaction_date, email))
#             connection.commit()
#         else:
#             cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
#             updated_items = cursor.fetchall()
#             message = request.args.get("message", None)
#     except Exception as e:
#         connection.rollback()
#         message = f"Error: {e}"
#         updated_items = []
#     finally:
#         close_connection(connection, cursor)
#
#     return render_template("M_Home_Page.html", message=message, products=updated_items)


@app.route('/Inventory_Update', methods=['GET', 'POST'])
def inventory_update():
    connection, cursor = open_connection()
    current_time = datetime.now()
    if request.method == 'POST':
        try:
            # Fetch all items from the database
            cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
            items = cursor.fetchall()

            # Loop through the items and process only updated quantities
            for item in items:
                item_id = item[0]  # G_ID
                previous_quantity = item[1]  # Current stock quantity
                new_quantity = request.form.get(f'quantity_{item_id}')  # Get new quantity from the form

                if new_quantity is not None:  # Check if a value was provided
                    new_quantity = int(new_quantity)

                    if new_quantity != previous_quantity:  # Only process if the quantity has changed
                        # Update the Quantity_in_stock in the garment table
                        cursor.execute(
                            "UPDATE garment SET Quantity_in_stock = %s WHERE G_ID = %s",
                            (new_quantity, item_id)
                        )

                        # Log the update in the stock_update table
                        cursor.execute(
                            "INSERT INTO stock_update (Add_Quantity, Garment_G_ID, Update_Date) VALUES (%s, %s, %s)",
                            (new_quantity, item_id, current_time)
                        )

            # Commit the transaction to save all changes
            connection.commit()
            message = "Inventory successfully updated!"

            # Fetch the updated items to display in the table
            cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
            updated_items = cursor.fetchall()
        except Exception as e:
            # Roll back in case of error
            connection.rollback()
            message = f"Error updating inventory: {e}"
            updated_items = []  # Return an empty list if an error occurs
        finally:
            close_connection(connection, cursor)

        # Render the template with the updated items
        return render_template('Inventory_Update.html', message=message, items=updated_items)

    else:  # For GET requests, fetch items to display in the form
        cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
        items = cursor.fetchall()
        close_connection(connection, cursor)
        return render_template('Inventory_Update.html',items=items)



# @app.route('/Inventory_Update', methods=['GET', 'POST'])
# def inventory_update():
#     connection, cursor = open_connection()
#
#     if request.method == 'POST':
#         try:
#             # Fetch all items from the database
#             cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
#             items = cursor.fetchall()
#
#             # Loop through the items and update their quantities based on the form input
#             for item in items:
#                 item_id = item[0]  # G_ID
#                 new_quantity = request.form.get(f'quantity_{item_id}')  # Get new quantity from the form
#
#                 if new_quantity is not None:  # Check if a value was provided
#                     new_quantity = int(new_quantity)
#                     # Update the stock in the database
#                     cursor.execute(
#                         "UPDATE garment SET Quantity_in_stock = %s WHERE G_ID = %s",
#                         (new_quantity, item_id)
#                     )
#
#             # Commit the transaction
#             connection.commit()
#             message = "Inventory successfully updated!"
#
#             # Fetch the updated items to reflect changes
#             cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
#             updated_items = cursor.fetchall()
#         except Exception as e:
#             # Roll back in case of error
#             connection.rollback()
#             message = f"Error updating inventory: {e}"
#             updated_items = []  # Return an empty list if an error occurs
#         finally:
#             close_connection(connection, cursor)
#
#         # Render the template with the updated items
#         return render_template('Inventory_Update.html', message=message, items=updated_items)
#
#     else:  # For GET requests, fetch items to display in the form
#         cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
#         items = cursor.fetchall()
#         close_connection(connection, cursor)
#         return render_template('Inventory_Update.html', items=items)


@app.route("/New_Item", methods=["POST", "GET"])
def new_item():
    if request.method == "POST":
        # Form inputs
        item_name = request.form.get("Item_Name")
        quantity = request.form.get("Quantity_in_stock")
        campaign = request.form.get("Marketing_Campaign")
        price = request.form.get("price")
        file = request.files.get("image")

        # Validate input
        if not item_name or not quantity or not price or not file:
            return render_template("New_Item.html", message="Please fill in all required fields.")

        # Validate file type
        allowed_extentions = {'png', 'jpg', 'jpeg', 'gif'}

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extentions

        if not allowed_file(file.filename):
            return render_template("New_Item.html",
                                   message="Invalid image format. Please upload PNG, JPG, JPEG, or GIF.")

        # Save the file to /static/Images
        UPLOAD_FOLDER = './static/Images'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Database operations
        connection, cursor = open_connection()

        try:
            # Check if the product already exists
            cursor.execute("SELECT * FROM garment WHERE Name = %s", (item_name,))
            result = cursor.fetchone()
            if result:
                return render_template(
                    "New_Item.html",
                    message="Product already exists! But hey, you can always update quantity or add a different one.",
                )

            # Get the last garment ID
            cursor.execute("SELECT MAX(G_ID) FROM garment")
            result = cursor.fetchone()
            last_garment_id = result[0] if result and result[0] is not None else 0
            new_garment_id = last_garment_id + 1

            # Insert the new product with the image path
            cursor.execute(
                "INSERT INTO garment (G_ID, Name, Quantity_in_stock, Marketing_Campaign, price, Picture) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (new_garment_id, item_name, quantity, campaign, price, f'{filename}'),
            )
            connection.commit()
            return render_template("New_Item.html", message="Product added successfully! You can add another one here:")
        except Exception as e:
            print(f"Error adding product: {e}")
            return render_template(
                "New_Item.html", message="An error occurred while adding the product, please try again."
            )
        finally:
            close_connection(connection, cursor)

    return render_template("New_Item.html")

@app.route("/Goodbye", methods=["POST", "GET"])
def Goodbye():
    return render_template("Goodbye.html")

@app.route('/logout')
def logout():
    session.clear()
    return render_template("Welcome_Page.html")

@app.errorhandler(404)
def invalid_route(e):
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)




