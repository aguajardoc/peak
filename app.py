import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# connecting to the database
db_connection = sqlite3.connect("peak.db", check_same_thread=False)
 
# cursor
crsr = db_connection.cursor()

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure username does not exist already
        elif crsr.execute("SELECT username FROM users WHERE username = ?", (request.form.get("username"),)).fetchall():
            return apology("username already in use", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted and is correct
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("confirmation doesn't match password", 400)

        # Insert values into database, generating a hash for the password
        hashedpword = generate_password_hash(
            request.form.get("password"), method="pbkdf2", salt_length=16
        )
        crsr.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            (request.form.get("username"),
            hashedpword)).fetchall()
        db_connection.commit()
        

        session["user_id"] = crsr.lastrowid

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

# Login
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
        rows = crsr.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][2], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/current")
@login_required
def current():
    return render_template("current.html")

@app.route("/past")
@login_required
def past():
    return render_template("past.html")

@app.route("/newcourse", methods=["GET", "POST"])
@login_required
def newcourse():
    #post and get methods 
    if request.method == "POST":

        pName = request.form.get("periodname")
        print("pName:", pName) 

        if pName == "newperiod":
            return render_template("newperiod.html")
        

        cName = request.form.get("coursename")
        cCredits = request.form.get("credits")

        # TODO: Get period ID
        # periods: period_id, period_name, period_start, period_end, grade, coursecount, user_id

        pID = crsr.execute("SELECT period_id FROM periods WHERE period_name = ? AND user_id = ?", (pName,session["user_id"])).fetchall()

        # TODO: Insert data into course

        crsr.execute("INSERT INTO courses (course_name, credits, grade, assignmentcount, user_id, period_id) VALUES(?, ?, 0, 0, ?, ?)", (cName, cCredits, session["user_id"], pID[0][0])).fetchall()
        db_connection.commit()
        # Update periods table accordingly, for the course count

        crsr.execute("UPDATE periods SET coursecount = coursecount + 1 WHERE period_id = ?", (pID[0][0],)).fetchall()
        db_connection.commit()

        return redirect("/current")

    else:
        periods = crsr.execute("SELECT period_name FROM periods WHERE user_id = ?", (session["user_id"],)).fetchall()
        return render_template("newcourse.html", periods=periods)

@app.route("/newperiod", methods=["GET", "POST"])
@login_required
def newperiod():
    
    if request.method == "POST":
        pName = request.form.get("periodname")
        pStart = request.form.get("periodstart")
        pEnd = request.form.get("periodend")

        # TODO: add to database
        # periods: period_id, period_name, period_start, period_end, grade, coursecount, user_id
        crsr.execute("INSERT INTO periods (period_name, period_start, period_end, grade, coursecount, user_id) VALUES(?, ?, ?, 0, 0, ?)", (pName, pStart, pEnd, session["user_id"])).fetchall()
        db_connection.commit()

        return redirect("/newcourse")

    else:
        return render_template("newperiod.html")