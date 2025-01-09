from flask_sqlalchemy import SQLAlchemy
from pymysql.cursors import Cursor


class Item:
    def __init__(self, id, quantity, name, campaign, price, image):
        self.id = id
        self.quantity = quantity
        self.name = name
        self.campaign = campaign
        self.price = price
        self.image = image

    def new_item(self, cursor, connection):
        try:
            # Check if the item already exists
            cursor.execute("SELECT G_ID FROM garment WHERE G_ID = %s", (self.id,))
            result = cursor.fetchone()
            if result:
                return False
            # Insert new item into the database
            cursor.execute(
                "INSERT INTO garment (G_ID, Quantity, Name, Campaign, Price, Image) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (self.id, self.quantity, self.name, self.campaign, self.price, self.image)
            )
            connection.commit()
            return True
        except Exception as e:
            print(f"Error while adding new item: {e}")
            return False

    def update_stock(self, new_quantity, cursor, connection):
        try:
            # Update stock in the database
            cursor.execute(
                "UPDATE garment SET Quantity = %s WHERE G_ID = %s",
                (new_quantity, self.id)
            )
            connection.commit()
            self.quantity = new_quantity
        except Exception as e:
            print(f"Error while updating stock: {e}")

    def in_stock(self):
        return self.quantity > 0

    def in_campaign(self):
        return bool(self.campaign)

    def buy_item(self, desired_quantity, cursor, connection):
        try:
            if desired_quantity <= self.quantity:
                # Update the quantity in the database
                new_quantity = self.quantity - desired_quantity
                cursor.execute(
                    "UPDATE garment SET Quantity = %s WHERE G_ID = %s",
                    (new_quantity, self.id)
                )
                connection.commit()
                self.quantity = new_quantity
                return True
            else:
                return False
        except Exception as e:
            print(f"Error while buying item: {e}")
            return False




    #הורדת מוצר כשמלאי=0 מתצוגה
    #הכנסת פריט
    #בדיקה אם קיים קמפיין


class User:
        # מודא קיום בטבלה
        # רישום
        # רכישה


class Purchase:
    # בדיקת מלאי DB
    # עדכון DB

    #building DB columns

# function of init

# func of availability

# func of reducing quantity from stock



