from datetime import datetime, timedelta, date

class Transaction:
    # initializing a new borrow object
    def __init__(self,Order_ID,Timestamp,User_Email):
        self.Order_ID = Order_ID
        self.Timestamp = Timestamp
        self.User_Email= User_Email
