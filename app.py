from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape
import re
import datetime
import csv

app = Flask(__name__)
app.secret_key = '123456789abcde'

# Class definition for User
class User:
    def __init__(self, name, account_id):
        self.name = name
        self.account_id = account_id

    def show(self): # Method to display user information
        return f"Name: {self.name}\nAccount ID: {self.account_id}"

# Class definition for Bank, inheriting from User
class Bank(User):
    def __init__(self, name, account_id):
        super().__init__(name, account_id)
        self.balance = 0  # Initializing balance, transactions, and transaction ID
        self.transactions = []
        self.transaction_id = 0
        self.date = datetime.datetime.now()  # Getting current date and time / will be used to know when transaction was performed

    def deposit(self, amount):  # Method to handle deposit transaction
        try:
            amount = int(amount)
            if amount > 0:
                self.balance += amount
                self.transaction_id += 1
                self.transactions.append({"Date,Time": self.date.strftime("%X %x"), "Transaction ID": f"D{self.transaction_id}", "Transaction Type": "Deposit", "Amount": amount})
                return f"You have deposited {amount}$ successfully"
            else:
                return "Amount must be a positive number"
        except ValueError:
            return "Invalid input. Amount must be a number"

    def withdraw(self, amount):  # Method to handle withdrawal transaction
        try:
            amount = int(amount)
            if amount > 0:
                if amount <= self.balance:
                    self.balance -= amount
                    self.transaction_id += 1
                    self.transactions.append({"Date,Time": self.date.strftime("%X %x"), "Transaction ID": f"W{self.transaction_id}", "Transaction Type": "Withdraw", "Amount": amount})
                    return f"You have withdrawn {amount}$ successfully"
                else:
                    return "Amount isn't available in your account"
            else:
                return "Amount must be a positive number"
        except ValueError:
            return "Invalid input. Amount must be a number"

    def show_balance(self):  # Method to display account balance
        return f"Account balance is {self.balance}$"

    def show_transactions(self):  # Method to display transaction history
        transactions_str = ""
        for transaction in self.transactions:
            transactions_str += f"{transaction['Date,Time']} {transaction['Transaction ID']} {transaction['Transaction Type']} {transaction['Amount']}$\n"
        return transactions_str
    
    def save_to_session(self):  # Method to save user data to session
        session['user'] = {
            'name': self.name,
            'account_id': self.account_id,
            'balance': self.balance,
            'transactions': self.transactions,
            'transaction_id': self.transaction_id
        }
    
    @classmethod
    def load_from_session(cls):  # Class method to load user data from session
        user_data = session.get('user')
        if user_data:
            # Creating a new instance of Bank class with session data / initialize a new bank instance with data retrieved
            user = cls(user_data['name'], user_data['account_id'])
            user.balance = user_data['balance']
            user.transactions = user_data['transactions']
            user.transaction_id = user_data['transaction_id']
            return user
        return None


# Function to check user credentials from a database
def database_check(name, id_num):
    with open("bkdata.csv", newline="") as csvfile:
        accreader = csv.DictReader(csvfile)
        for row in accreader:
            if row["Name"] == name and row["ID"] == id_num:
                return True
    return False


# Route for the index page
@app.route("/")
def index():
    return render_template("index.html")

# Route for the homepage
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        id_num = request.form["id"]
        if database_check(name, id_num):
            return redirect(url_for("bank_interface", name=name, id=id_num))
        else:
            return render_template("login.html", error="Credentials are not correct")
    return render_template("login.html")

# Route for bank interface with user-specific URL
@app.route("/bank_interface/<name>/<id>", methods=["GET", "POST"])
def bank_interface(name, id):
    user = Bank.load_from_session()
    if not user:
        user = Bank(name, id)

    if request.method == "POST":
        choice = request.form["choice"]
        if choice == "1":
            amount = request.form.get("amount")
            message = user.deposit(amount)
        elif choice == "2":
            amount = request.form.get("amount")
            message = user.withdraw(amount)
        elif choice == "3":
            message = user.show_balance()
        elif choice == "4":
            message = user.show_transactions()
        else:
            message = "Choice isn't available"

        user.save_to_session()  # Saving user data back to session
        return render_template("bank_interface.html", user=user, choice=choice, message=message)
    return render_template("bank_interface.html", user=user)

@app.route("/logout")
def logout():
    session.clear()  # Clear session data
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
