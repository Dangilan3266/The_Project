# all imports
from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from flask_session.__init__ import Session
from datetime import date, datetime, timedelta
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
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_FILE_THRESHOLD"] = 100
Session(app)

# welcome page - log in or sign up as manager / user
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

            # Track if any items were purchased by creating list and condition on emptiness
            selected_items = []

            # Generate Order ID before checking quantities
            email = session["email"]
            transaction_date = datetime.now()
            cursor.execute("SELECT MAX(order_id) FROM transactions")
            result = cursor.fetchone()
            last_transaction_number = result[0] if result[0] is not None else 0
            new_transaction_number = last_transaction_number + 1

            # Track the selected items and their quantities
            for item in items:
                item_id = int(item[0])  # G_ID
                try:
                    desired_quantity = int(request.form.get(f'quantity_{item_id}', 0))  # Handle missing quantities gracefully
                except ValueError:
                    desired_quantity = 0

                # If any item has a desired quantity greater than 0, add it to the selected_items list
                if desired_quantity > 0:
                    selected_items.append((item_id, desired_quantity, item[1]))  # Item ID, Quantity, Stock Quantity

            if selected_items:
                # Insert the transaction into `transactions` table
                cursor.execute("""
                    INSERT INTO transactions (Order_id, Date, Users_Email)
                    VALUES (%s, %s, %s)
                """, (new_transaction_number, transaction_date, email))

                # Now insert into `transactions_garment` for each selected item
                for item_id, desired_quantity, current_stock in selected_items:
                    new_quantity = current_stock - desired_quantity

                    # Insert the garment transaction into `transactions_garment` table
                    cursor.execute("""
                        INSERT INTO transactions_garment (Quantity, Transactions_Order_ID, Garment_G_ID)
                        VALUES (%s, %s, %s)
                    """, (desired_quantity, new_transaction_number, item_id))

                    # Update the stock in the garment table
                    cursor.execute("UPDATE garment SET Quantity_in_stock = %s WHERE G_id = %s", (new_quantity, item_id))
                    connection.commit()
                message = "Thank You for Your Purchase!"
                return redirect(url_for("Goodbye", message=message))

            else:
                message = "No items were purchased."  # This will be shown if all quantities are zero
                connection.commit()
                return redirect(url_for("Home_Page", message=message))

        else:  # GET request
            # Fetch items for display
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


@app.route("/M_Home_Page", methods=["POST", "GET"])
def M_Home_Page():
    # Check if user is logged in
    if 'email' not in session:
        return redirect("/")

    connection, cursor = open_connection()

    try:
        # Verify if log in user is a manager
        cursor.execute("SELECT Email FROM Managers WHERE Email = %s", (session['email'],))
        manager = cursor.fetchone()

        if not manager:
            return redirect("/")  # Redirect non-managers

        if request.method == "POST":
            # Fetch items in stock
            cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
            items = cursor.fetchall()

            # Track if any items were purchased by creating list and condition on emptiness
            selected_items = []

            # Generate Order ID before checking quantities
            email = session["email"]
            transaction_date = datetime.now()
            cursor.execute("SELECT MAX(order_id) FROM transactions")
            result = cursor.fetchone()
            last_transaction_number = result[0] if result[0] is not None else 0
            new_transaction_number = last_transaction_number + 1

            # Track the selected items and their quantities
            for item in items:
                item_id = int(item[0])  # G_ID
                try:
                    desired_quantity = int(request.form.get(f'quantity_{item_id}', 0))
                    # Handle missing quantities gracefully
                except ValueError:
                    desired_quantity = 0

                # If any item has a desired quantity greater than 0, add it to the selected_items list
                if desired_quantity > 0:
                    selected_items.append((item_id, desired_quantity, item[1]))  # Item ID, Quantity, Stock Quantity

            if selected_items:
                # Insert the transaction into `transactions` table
                cursor.execute("""
                    INSERT INTO transactions (Order_id, Date, Users_Email)
                    VALUES (%s, %s, %s)
                """, (new_transaction_number, transaction_date, email))

                # Now insert into `transactions_garment` for each selected item
                for item_id, desired_quantity, current_stock in selected_items:
                    new_quantity = current_stock - desired_quantity

                    # Insert the garment transaction into `transactions_garment` table
                    cursor.execute("""
                        INSERT INTO transactions_garment (Quantity, Transactions_Order_ID, Garment_G_ID)
                        VALUES (%s, %s, %s)
                    """, (desired_quantity, new_transaction_number, item_id))

                    # Update the stock in the garment table
                    cursor.execute("UPDATE garment SET Quantity_in_stock = %s WHERE G_id = %s", (new_quantity, item_id))
                    connection.commit()
                message = "Thank You for Your Purchase!"
                return redirect(url_for("M_Goodbye", message=message))
            else:
                message = "No items were purchased."  # This will be shown if all quantities are zero
                connection.commit()
                return redirect(url_for("M_Home_Page", message=message))
            # Commit all changes only if there were purchases

        else:  # GET request
            # Fetch items for display
            cursor.execute("SELECT * FROM garment WHERE Quantity_in_stock > 0 ORDER BY Marketing_Campaign DESC")
            updated_items = cursor.fetchall()
            message = request.args.get("message", None)

    except Exception as e:
        connection.rollback()
        message = f"Error: {e}"
        updated_items = []
    finally:
        close_connection(connection, cursor)

    return render_template("M_Home_Page.html", message=message, products=updated_items)


@app.route('/Inventory_Update', methods=['GET', 'POST'])
def Inventory_Update():
    current_time = datetime.now()
    if 'email' not in session:
        return redirect("/")

    connection, cursor = open_connection()
    try:
        cursor.execute("SELECT Email FROM Managers WHERE Email = %s", (session['email'],))
        manager = cursor.fetchone()
        if not manager:
            return redirect("/")

        if request.method == 'POST':
            cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
            items = cursor.fetchall()

            for item in items:
                item_id = item[0]
                previous_quantity = item[1]
                new_quantity = request.form.get(f'quantity_{item_id}')

                if new_quantity is not None:
                    new_quantity = int(new_quantity)
                    if new_quantity != previous_quantity:
                        cursor.execute(
                            "UPDATE garment SET Quantity_in_stock = %s WHERE G_ID = %s",
                            (new_quantity, item_id)
                        )
                        cursor.execute(
                            "INSERT INTO stock_update (New_Quantity, Garment_G_ID, Update_Date) VALUES (%s, %s, %s)",
                            (new_quantity, item_id, current_time)
                        )

            connection.commit()
            message = "Inventory successfully updated!"
            cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
            updated_items = cursor.fetchall()
            return render_template('Inventory_Update.html', message=message, items=updated_items)

        else:  # GET request
            cursor.execute("SELECT G_ID, Quantity_in_stock, Name FROM garment")
            items = cursor.fetchall()
            return render_template('Inventory_Update.html', items=items)

    except Exception as e:
        connection.rollback()
        message = f"Error updating inventory: {e}"
        return render_template('Inventory_Update.html', message=message, items=[])

    finally:
        close_connection(connection,cursor)


@app.route("/New_Item", methods=["POST", "GET"])
def New_Item():
    if 'email' not in session:
        return redirect("/")

    connection, cursor = open_connection()
    try:
        cursor.execute("SELECT Email FROM Managers WHERE Email = %s", (session['email'],))
        manager = cursor.fetchone()
        if not manager:
            return redirect("/")

        if request.method == "POST":
            # Form inputs
            item_name = request.form.get("Item_Name")
            quantity = request.form.get("Quantity_in_stock")
            campaign = request.form.get("Marketing_Campaign")
            price = request.form.get("price")
            file = request.files.get("image")

            # Validate input
            if not all([item_name, quantity, price, file]):
                return render_template("New_Item.html", message="Please fill in all required fields.")

            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return render_template("New_Item.html",
                                       message="Invalid image format. Please upload PNG, JPG, JPEG, or GIF.")

            # Save file
            UPLOAD_FOLDER = './static/Images'
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Check if product exists
            cursor.execute("SELECT * FROM garment WHERE Name = %s", (item_name,))
            if cursor.fetchone():
                return render_template("New_Item.html",
                                       message="Product already exists! But hey, you can always update quantity or add a different one.")

            # Get new garment ID
            cursor.execute("SELECT MAX(G_ID) FROM garment")
            result = cursor.fetchone()
            new_garment_id = (result[0] if result and result[0] is not None else 0) + 1

            # Insert new product
            cursor.execute(
                """INSERT INTO garment 
                   (G_ID, Name, Quantity_in_stock, Marketing_Campaign, price, Picture)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (new_garment_id, item_name, quantity, campaign, price, filename)
            )
            connection.commit()
            return render_template("New_Item.html",
                                   message="Product added successfully! You can add another one here:")

        # GET request
        return render_template("New_Item.html")

    except Exception as e:
        connection.rollback()
        return render_template("New_Item.html",
                               message=f"Error: {e}")

    finally:
        close_connection(connection,cursor)


# redirect after purchase is made
@app.route("/Goodbye", methods=["POST", "GET"])
def Goodbye():
    return render_template("Goodbye.html")


# redirect after purchase is made
@app.route("/M_Goodbye", methods=["POST", "GET"])
def M_Goodbye():
    return render_template("M_Goodbye.html")

# log out method to clear session and log the user out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("welcome_page"))


# error handler of page not found
@app.errorhandler(404)
def invalid_route(e):
    return redirect("/")

# RUN
if __name__ == "__main__":
    app.run(debug=True)




