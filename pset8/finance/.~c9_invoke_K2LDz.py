import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    userId = session["user_id"]
    rows = db.execute("SELECT cash FROM users WHERE id = :id", id=userId)

    stocks = []
    total = currentBalance
    rows = db.execute("select s.symbol, s.name, sum(p.amount) as total from stocks s inner join portfolio p on s.stockid = p.stockid group by s.symbol having p.userid = :userid", userid=userId)
    currentBalance = float(rows[0]["cash"])
    for row in rows:
        quote = lookup(rows[0]["symbol"])
        value = int(rows[0]["total"]) * float(quote["price"])
        stock = {
                "symbol": rows[0]["symbol"],
                "name": rows[0]["name"],
                "amount": int(rows[0]["total"]),
                "currentPrice": usd(float(quote["price"])),
                "value": usd(value)
            }
        total += value;
        stocks.append(stock)

    return render_template("index.html", stocks=stocks, balance=usd(currentBalance), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    if request.method == "POST":
        userId = session["user_id"]
        rows = db.execute("SELECT cash FROM users WHERE id = :id", id=userId)
        cash = rows[0]["cash"]

        symbol = request.form['symbol']
        amount = int(request.form['amount'])

        if amount <= 0:
            return apology(f"Invalid amount of {amount}. Must be > 0")

        quote = lookup(symbol)
        if not quote:
            return apology(f"Symbol {symbol} does not exist")

        price = float(quote["price"])
        if price * amount > cash:
            return apology("Insufficient funds")

        balance = cash - (price * amount)

        symbolRow = db.execute("SELECT stockid FROM stocks where symbol=:symbol", symbol=symbol)
        if len(symbolRow) == 0:
            db.execute("INSERT INTO stocks (name, symbol) VALUES (:name, :symbol)", name=quote["name"], symbol=symbol)
            symbolRow = db.execute("SELECT stockid FROM stocks where symbol=:symbol", symbol=symbol)

        stockId = symbolRow[0]["stockid"]

        db.execute("UPDATE users SET cash=:cash WHERE id=:userid", cash=balance, userid=userId)

        db.execute("INSERT INTO portfolio (userid, stockid, price, timestamp, amount) VALUES(:userid, :stockid, :price, strftime('%s','now'), :amount)",
        userid=userId, stockid=stockId, price=price, amount=amount)
        return render_template('success.html', message=f"You bought {amount} shares of {symbol}")

    return apology("Sorry, this is unavailable", code=404)


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args['username']
    rows = db.execute("select username from users where username=:username", username=username)
    return jsonify(len(rows) == 0)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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
        username = request.form['username']
        password = request.form['password']
        pwdConfirm = request.form['confirmation']
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) > 0:
            return apology("Username already exists")
        if not password  == pwdConfirm:
            return apology("Password and confirmation did not match")
        hashPwd = generate_password_hash(password)
        db.execute("INSERT INTO users ('username', 'hash') VALUES (:username, :hash)", username=username, hash=hashPwd)
        return render_template('success.html', message="You have been registered.")
    return apology("Sorry, this is unavailable", code=404)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
