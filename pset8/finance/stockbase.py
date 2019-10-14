class StockBase:

    def __init__(self, db):
        self.db = db

    def getBalance(self, userId):
        # returns current cash balance of user
        rows = self.db.execute("SELECT cash FROM users WHERE id = :id", id=userId)
        if len(rows) > 0:
            return float(rows[0]["cash"])
        return 0.0

    def updateBalance(self, userId, newBalance):
        # updates cash balance of user
        return self.db.execute("UPDATE users SET cash=:newBalance WHERE id=:userid", newBalance=newBalance, userid=userId)

    def getPortfolio(self, userId):
        # returns stock portfolio rows
        return self.db.execute("SELECT s.symbol, s.name, s.stockid, p.amount FROM stocks s INNER JOIN portfolio p ON s.stockid = p.stockid WHERE p.userid=:userid AND p.amount > 0 ORDER BY s.name", userid=userId)

    def getStockIdBySymbol(self, symbol):
        # returns id of stock
        rows = self.db.execute("SELECT stockid FROM stocks where symbol=:symbol", symbol=symbol)
        if len(rows) == 0:
            return -1
        return int(rows[0]["stockid"])

    def addStock(self, name, symbol):
        # adds stock to db
        return self.db.execute("INSERT INTO stocks (name, symbol) VALUES (:name, :symbol)", name=name, symbol=symbol)

    def getAmountOfStocks(self, userId, stockId):
        # returns how many stocks the user has in his portfolio
        portfolioRows = self.db.execute(
            "SELECT amount FROM portfolio WHERE userid=:userid AND stockid=:stockid", userid=userId, stockid=stockId)
        if len(portfolioRows) == 0:
            return -1
        return int(portfolioRows[0]["amount"])

    def updateAmountInPortfolio(self, userId, stockId, newAmount):
        # updates amount of stocks
        return self.db.execute("UPDATE portfolio SET amount=:newAmount WHERE userid=:userid AND stockid=:stockid", userid=userId, stockid=stockId, newAmount=newAmount)

    def addToPortfolio(self, userId, stockId, amount):
        # adds stock and amount to portfolio
        return self.db.execute("INSERT INTO portfolio (userid, stockid, amount) VALUES (:userid, :stockid, :amount)", userid=userId, stockid=stockId, amount=amount)

    def updateOrInsertToPortfolio(self, userId, stockId, amount):
        # updates or inserts the given amount
        currentStockAmount = self.getAmountOfStocks(userId, stockId)
        if currentStockAmount < 0:
            return self.addToPortfolio(userId, stockId, amount)
        newAmount = currentStockAmount + amount
        return self.updateAmountInPortfolio(userId, stockId, newAmount)

    def getHistory(self, userId):
        # returns history of user
        return self.db.execute("SELECT s.name, s.symbol, h.price, h.amount, h.'transaction', h.timestamp FROM stocks s INNER JOIN history h ON s.stockid = h.stockid WHERE h.userid=:userid ORDER BY h.timestamp DESC", userid=userId)

    def addToHistory(self, userId, stockId, price, amount, transaction):
        # transaction is a keyword in sqlite3, hence we need quotes
        return self.db.execute("INSERT INTO history ('userid', 'stockid', 'price', 'amount', 'transaction') VALUES (:userid, :stockid, :price, :amount, :transaction)",
                               userid=userId, stockid=stockId, price=price, amount=amount, transaction=transaction)

    def addUser(self, userName, hashedPw):
        return self.db.execute("INSERT INTO users ('username', 'hash') VALUES (:username, :hashedPw)", username=userName, hashedPw=hashedPw)

    def getUserByName(self, userName):
        return self.db.execute("select * from users where username=:username", username=userName)

    def userNameExists(self, userName):
        rows = self.db.execute("select username from users where username=:username", username=userName)
        return len(rows) > 0