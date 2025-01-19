from pymysql.cursors import Cursor


class Item:
    def __init__(self, id, quantity, name, campaign, price, image):
        """
        Initialize a new Item instance.

        Parameters:
        - id (int): The unique ID of the item.
        - quantity (int): The quantity of the item in stock.
        - name (str): The name of the item.
        - campaign (bool): Whether the item is part of a campaign.
        - price (float): The price of the item.
        - image (str): The file path or URL of the item's image.

        Initializes the item with the given attributes.
        """
        self.id = id
        self.quantity = quantity
        self.name = name
        self.campaign = campaign
        self.price = price
        self.image = image

    def new_item(self, id, quantity, name, campaign, price, image, cursor, connection):
        """
        Add a new item to the database.

        Parameters:
        - cursor (Cursor): The database cursor to execute SQL queries.
        - connection: The database connection for committing changes.

        Returns:
        - bool: True if the item was successfully added, False if the item already exists.

        Checks if the item exists in the `garment` table. If not, it inserts the item into the database.
        """
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
                (id, quantity, name, campaign, price, image)
            )
            connection.commit()
            return True ## maybe we should return what was added or print on main
        except Exception as e:
            print(f"Error while adding new item: {e}")
            return False

    def update_stock(self, id, new_quantity, cursor, connection):
        """
        Update the stock quantity of the item.

        Parameters:
        - new_quantity (int): The new stock quantity for the item.
        - cursor (Cursor): The database cursor to execute SQL queries.
        - connection: The database connection for committing changes.

        Updates the `Quantity` column in the `garment` table for the given item.
        """
        try:
            # Update stock in the database
            cursor.execute(
                "UPDATE garment SET Quantity = %s WHERE G_ID = %s",
                (new_quantity, id)
            )
            connection.commit()
            self.quantity = new_quantity
        except Exception as e:
            print(f"Error while updating stock: {e}")

    def in_stock(self):
        """
        Check if the item is in stock.

        Returns:
        - bool: True if the item's quantity is greater than 0, False otherwise.
        """
        return self.quantity > 0

    def in_campaign(self):
        """
        Check if the item is part of a campaign.

        Returns:
        - bool: True if the item is part of a campaign, False otherwise.
        """
        return bool(self.campaign)

    def buy_item(self, desired_quantity, cursor, connection):
        """
        Purchase a specified quantity of the item.

        Parameters:
        - desired_quantity (int): The quantity of the item to purchase.
        - cursor (Cursor): The database cursor to execute SQL queries.
        - connection: The database connection for committing changes.

        Returns:
        - bool: True if the purchase was successful, False if there is insufficient stock.

        Reduces the item's stock by the desired quantity if enough stock is available and updates the database.
        """
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
    pass

class Purchase:
    # בדיקת מלאי DB
    # עדכון DB
    pass
    #building DB columns

# function of init

# func of availability

# func of reducing quantity from stock



