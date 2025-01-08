from flask_sqlalchemy import SQLAlchemy


class Item:
    def __init__(self,id,quantity, name, campaign, price, image):
        self.id = #pull from DB
        self.quantity = #pull from DB
        self.name = #pull from DB
        self.campaign = #pull from DB
        self.price = #pull from DB
        self.image = #pull from Static
    def update_stock(self):
        new_quantity = #pull from DB , make sure value is INT
        self.quantity = new_quantity

    def new_item(self):
        items_dict = {}
        items_id_list = #pull from DB
        if self.id in items_id_list:
            # Raise Error in HTML
        else:
            items_dict.append(self.id,self.quantity)

    #הורדת מוצר כשמלאי=0 מתצוגה
    #הכנסת פריט
    #בדיקה אם קיים קמפיין


class User:
        # מודא קיום בטבלה
        # רישום
        # רכישה

class Cart:
    # הוספה לעגלה (מחיר,סכימה של מחירים,פריט לרשימה)
    # הורדת פריט

class Purchase:
    # בדיקת מלאי DB
    # עדכון DB

    #building DB columns

# function of init

# func of availability

# func of reducing quantity from stock



