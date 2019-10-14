import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from stockbase import StockBase

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
stockbase = StockBase(db)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


def renderIndex(message, userId):
    currentBalance = stockbase.getBalance(userId)
    total = currentBalance
    rows = stockbase.getPortfolio(userId)

    stocks = []
    for row in rows:
        quote = lookup(row["symbol"])
        value = int(row["amount"]) * float(quote["price"])
        stock = {
            "symbol": row["symbol"],
            "name": row["name"],
            "amount": int(row['amount']),
            "currentPrice": usd(float(quote["price"])),
            "value": usd(value)
        }
        total += value
        stocks.append(stock)
    return render_template("index.html", message=message, stocks=stocks, balance=usd(currentBalance), total=usd(total))


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return renderIndex("", session["user_id"])


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    if request.method == "GET":
        return render_template("cash.html")
    if request.method == "POST":
        userId = session["user_id"]
        balance = stockbase.getBalance(userId)
        amount = float(request.form['amount'])
        if amount < 0:
            return apology("Can't add negative amount")
        newBalance = float(amount) + balance
        stockbase.updateBalance(userId, newBalance)
        return renderIndex(f"You added {usd(amount)} cash to your account", userId)
    return apology("Sorry, this is unavailable", code=404)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    if request.method == "POST":
        try:
            fshares = int(request.form["shares"])
        except:
            return apology("Please provide a valid shares amount")

        if not request.form["symbol"] or fshares <= 0:
            return apology("Please provide symbol and shares amount")
        userId = session["user_id"]
        symbol = request.form['symbol']
        quote = lookup(symbol)
        if not quote:
            return apology(f"Symbol {symbol} does not exist")

        balance = stockbase.getBalance(userId)
        price = float(quote["price"])
        amountToBuy = fshares

        # check for sufficient funds
        if price * amountToBuy > balance:
            return apology("Insufficient funds")

        balance = balance - (price * amountToBuy)
        stockbase.updateBalance(userId, balance)

        stockId = stockbase.getStockIdBySymbol(symbol)
        if stockId <= 0:
            stockbase.addStock(quote["name"], symbol)
            stockId = stockbase.getStockIdBySymbol(symbol)

        stockbase.updateOrInsertToPortfolio(userId, stockId, amountToBuy)
        stockbase.addToHistory(userId, stockId, price, amountToBuy, "BUY")

        return renderIndex(f"You bought {amountToBuy} share(s) of {symbol}", userId)

    return apology("Sorry, this is unavailable", code=404)


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    userName = request.args['username']
    if not userName:
        return apology("Username has to be given")

    return jsonify(not stockbase.userNameExists(userName))


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    userId = session["user_id"]
    rows = stockbase.getHistory(userId)

    transactions = []
    for row in rows:
        transaction = {
            "symbol": row["symbol"],
            "name": row["name"],
            "amount": int(row["amount"]),
            "price": usd(float(row["price"])),
            "transaction": row["transaction"],
            "timestamp": row["timestamp"]
        }
        transactions.append(transaction)
    return render_template("history.html", rows=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        userName = request.form.get("username")
        rows = stockbase.getUserByName(userName)

        # Ensure username does not already exist and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == 'GET':
        return render_template('quote.html')
    if request.method == 'POST':
        symbol = request.form['symbol']
        if not symbol:
            return apology("Please provide valid symbol")
        quote = lookup(symbol)
        if not quote:
            return apology(f"Nothing found for {symbol}")
        quote['price'] = usd(quote['price'])
        return render_template('quoted.html', quote=quote)
    return apology("Sorry, this is unavailable", code=404)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        userName = request.form['username']
        password = request.form['password']
        pwdConfirm = request.form['confirmation']

        if not userName or not password or not pwdConfirm:
            return apology("Please provide values for userName password and confirmation")
        if stockbase.userNameExists(userName):
            return apology("Username already exists")
        if not password == pwdConfirm:
            return apology("Password and confirmation did not match")

        hashedPw = generate_password_hash(password)
        stockbase.addUser(userName, hashedPw)
        userRows = stockbase.getUserByName(userName)

        session.clear()
        userId = userRows[0]["id"]
        session["user_id"] = userId

        return renderIndex("Registered!", userId)
    return apology("Sorry, this is unavailable", code=404)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    userId = session["user_id"]
    currentBalance = stockbase.getBalance(userId)
    rows = stockbase.getPortfolio(userId)

    if request.method == 'GET':
        stocks = []
        for row in rows:
            stock = {
                "symbol": row["symbol"],
                "name": row["name"]
            }
            stocks.append(stock)
        return render_template("sell.html", stocks=stocks)

    if request.method == 'POST':
        try:
            fshares = int(request.form["shares"])
        except:
            return apology("Please provide a valid shares amount")

        if not request.form["symbol"] or fshares <= 0:
            return apology("Please provide symbol and shares amount")
        symbol = request.form["symbol"]
        toSellAmount = fshares

        for row in rows:
            if row["symbol"] == symbol:
                stockId = row['stockid']
                quote = lookup(symbol)
                price = float(quote["price"])
                value = toSellAmount * price

                currentAmount = stockbase.getAmountOfStocks(userId, stockId)
                newAmount = currentAmount - toSellAmount
                if newAmount < 0:
                    return apology(f"You don't have enough stocks to sell {toSellAmount} share(s)")

                currentBalance = stockbase.getBalance(userId)
                newBalance = currentBalance + value
                stockbase.updateBalance(userId, newBalance)

                stockbase.updateAmountInPortfolio(userId, stockId, newAmount)
                stockbase.addToHistory(userId, stockId, price, toSellAmount, "SELL")
                return renderIndex(f"You sold {toSellAmount} share(s) of {symbol} for {usd(value)}", userId)
        return apology("Please provide symbol and shares amount")
    return apology("Sorry, this is unavailable", code=404)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
