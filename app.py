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

    # Fetch course data
    courses = crsr.execute("SELECT course_name, credits, assignmentcount, grade FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()

    # Fetch (while calculating) unweighted and weighted GPA for all courses
    unweighted_gpa = crsr.execute("SELECT SUM(grade) / COUNT(grade) FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()
    weighted_gpa = crsr.execute("SELECT SUM(grade * credits) / SUM(credits) FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()

    return render_template("current.html", courses=courses, unweighted_gpa=unweighted_gpa[0][0], weighted_gpa=weighted_gpa[0][0])

@app.route("/newcourse", methods=["GET", "POST"])
@login_required
def newcourse():
    #post and get methods 
    if request.method == "POST":
        
        cName = request.form.get("coursename")
        cCredits = request.form.get("credits")

        if not cName:
            return apology("must provide course name", 400)
        if not cCredits:
            return apology("must provide credits", 400)
        if not cCredits.isdigit():
            return apology("credits must be a number", 400)
        
        usednames = crsr.execute("SELECT course_name FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()

        for name in usednames:
            if cName == name[0]:
                return apology("course name already in use", 400)

        # Insert data into course
        crsr.execute("INSERT INTO courses (course_name, credits, grade, assignmentcount, user_id) VALUES(?, ?, 0, 0, ?)", (cName, cCredits, session["user_id"])).fetchall()
        db_connection.commit()

        return redirect("/current")

    else:

        return render_template("newcourse.html")

@app.route('/assignments')
@login_required
def assignments():

    # Fetch course name from URL, and ID from database
    course_name = request.args.get('course')
    cId = crsr.execute("SELECT course_id FROM courses WHERE course_name = ? AND user_id = ?", (course_name,session["user_id"])).fetchall()

    # Fetch assignments from database
    assignments = crsr.execute("SELECT assignment_name, weight, grade FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

    # Fetch (while calculating) average grade for course
    avg = crsr.execute("SELECT SUM(grade * weight) / SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()
    avg2 = crsr.execute("SELECT SUM(0.01 * grade * weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

    # Fetch the max possible grade for the course at that point
    max = crsr.execute("SELECT SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

    return render_template("assignments.html", course_name=course_name, assignments=assignments, avg=avg[0][0], avg2=avg2[0][0], max=max[0][0])
    
@app.route('/newassignment', methods=["GET", "POST"])
@login_required
def newassignment():

    if request.method == "POST":
        assignment_name = request.form.get("assignmentname")
        assignment_grade = request.form.get("grade")
        assignment_weight = request.form.get("weight")
        course_name = request.form.get("coursename")

        cId = crsr.execute("SELECT course_id FROM courses WHERE course_name = ? AND user_id = ?", (course_name,session["user_id"])).fetchall()

        totalweight = crsr.execute("SELECT SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()
        if not totalweight or totalweight[0][0] is None:
            totalweightnew = 0
        else:
            totalweightnew = totalweight[0][0]

        if float(assignment_weight) + float(totalweightnew) > 100:
            return apology("total weight of assignments exceeds 100%, try again", 400)

        crsr.execute("INSERT INTO assignments (assignment_name, grade, weight, user_id, course_id) VALUES(?, ?, ?, ?, ?)", (assignment_name, assignment_grade, assignment_weight, session["user_id"], cId[0][0])).fetchall()
        db_connection.commit()

        crsr.execute("UPDATE courses SET assignmentcount = assignmentcount + 1 WHERE course_id = ?", (cId[0][0],)).fetchall()
        db_connection.commit()

        crsr.execute("UPDATE courses SET grade = (SELECT SUM(grade * weight) / SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?) WHERE course_id = ?", (cId[0][0],session["user_id"],cId[0][0])).fetchall()
        db_connection.commit()

        assignments = crsr.execute("SELECT assignment_name, weight, grade FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

        # Fetch (while calculating) average grade for course
        avg = crsr.execute("SELECT SUM(grade * weight) / SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()
        avg2 = crsr.execute("SELECT SUM(0.01 * grade * weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

        # Fetch the max possible grade for the course at that point
        max = crsr.execute("SELECT SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

        return render_template("assignments.html", course_name=course_name, assignments=assignments, avg=avg[0][0], avg2=avg2[0][0], max=max[0][0])

    else:

        course_name = request.args.get('course_name')

        return render_template("newassignment.html", course_name=course_name)
    
@app.route('/editcourse', methods=["GET", "POST"])
@login_required
def editcourse():

    if request.method == "POST":
        course_credits = request.form.get("credits")
        course_id = request.form.get("courseid")
        course_name = request.form.get("coursename")

        crsr.execute("UPDATE courses SET course_name = ?, credits = ? WHERE course_id = ?", (course_name, course_credits, course_id)).fetchall()
        db_connection.commit()

        # Resubmit current course data

        # Fetch course data
        courses = crsr.execute("SELECT course_name, credits, assignmentcount, grade FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()

        # Fetch (while calculating) unweighted and weighted GPA for all courses
        unweighted_gpa = crsr.execute("SELECT SUM(grade) / COUNT(grade) FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()
        weighted_gpa = crsr.execute("SELECT SUM(grade * credits) / SUM(credits) FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()

        return render_template("current.html", courses=courses, unweighted_gpa=unweighted_gpa[0][0], weighted_gpa=weighted_gpa[0][0])
    else:

        course_name = request.args.get('course_name')
        cId = crsr.execute("SELECT course_id FROM courses WHERE course_name = ? AND user_id = ?", (course_name,session["user_id"])).fetchall()
        course_credits = crsr.execute("SELECT credits FROM courses WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

        return render_template("editcourse.html", course_name=course_name, course_credits=course_credits[0][0], cId=cId[0][0])
    
@app.route("/deletecourse", methods=["POST"])
@login_required
def deletecourse():
    courseid = request.form.get("courseid")

    # Delete the course from the database, along with its corresponding assignments
    
    crsr.execute("DELETE FROM courses WHERE course_id = ?", (courseid,))
    db_connection.commit()

    crsr.execute("DELETE FROM assignments WHERE course_id = ?", (courseid,))
    db_connection.commit()

    # Resubmit updated course data, without the deleted course

    # Fetch course data
    courses = crsr.execute("SELECT course_name, credits, assignmentcount, grade FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()

    # Fetch (while calculating) unweighted and weighted GPA for all courses
    unweighted_gpa = crsr.execute("SELECT SUM(grade) / COUNT(grade) FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()
    weighted_gpa = crsr.execute("SELECT SUM(grade * credits) / SUM(credits) FROM courses WHERE user_id = ?", (session["user_id"],)).fetchall()

    return render_template("current.html", courses=courses, unweighted_gpa=unweighted_gpa[0][0], weighted_gpa=weighted_gpa[0][0])

@app.route('/editassignment', methods=["GET", "POST"])
@login_required
def editassignment():

    if request.method == "POST":

        # Fetch new data from form
        assignment_name = request.form.get("assignmentname")
        assignment_grade = request.form.get("grade")
        assignment_weight = request.form.get("weight")
        assignment_id = request.form.get("assignmentid")

        # Fetch course data
        cId = crsr.execute("SELECT course_id FROM assignments WHERE assignment_id = ?", (assignment_id,)).fetchall()
        course_name = crsr.execute("SELECT course_name FROM courses WHERE course_id = ?", (cId[0][0],)).fetchall()

        # Validation of new weight
        totalweight = crsr.execute("SELECT SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()
        oldweight = crsr.execute("SELECT weight FROM assignments WHERE assignment_id = ? AND user_id = ?", (assignment_id,session["user_id"])).fetchall()
        if not totalweight or totalweight[0][0] is None:
            totalweightnew = 0
        else:
            totalweightnew = totalweight[0][0] - oldweight[0][0]

        if float(assignment_weight) + float(totalweightnew) > 100:
            return apology("total weight of assignments exceeds 100%, try again", 400)

        # Update assignment data
        crsr.execute("UPDATE assignments SET assignment_name = ?, grade = ?, weight = ? WHERE assignment_id = ?", (assignment_name, assignment_grade, assignment_weight, assignment_id)).fetchall()
        
        # Fetch assignments from database
        assignments = crsr.execute("SELECT assignment_name, weight, grade FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()
        crsr.execute("UPDATE courses SET grade = (SELECT SUM(grade * weight) / SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?) WHERE course_id = ?", (cId[0][0],session["user_id"],cId[0][0])).fetchall()
        db_connection.commit()

        # Fetch (while calculating) average grade for course with updated assignment
        avg = crsr.execute("SELECT SUM(grade * weight) / SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()
        avg2 = crsr.execute("SELECT SUM(0.01 * grade * weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

        # Fetch the max possible grade for the course at that point
        max = crsr.execute("SELECT SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

        return render_template("assignments.html", course_name=course_name[0][0], assignments=assignments, avg=avg[0][0], avg2=avg2[0][0], max=max[0][0])

    else:

        assignment_name = request.args.get('assignment')
        assignment_id = crsr.execute("SELECT assignment_id FROM assignments WHERE assignment_name = ? AND user_id = ?", (assignment_name,session["user_id"])).fetchall()
        
        assignments = crsr.execute("SELECT assignment_name, weight, grade FROM assignments WHERE assignment_id = ? AND user_id = ?", (assignment_id[0][0],session["user_id"])).fetchall()   

        return render_template("editassignment.html", assignments=assignments, assignment_id=assignment_id[0][0])
 

@app.route("/deleteassignment", methods=["POST"])
@login_required
def deleteassignment():
    assignmentid = request.form.get("assignmentid")

    # Delete the assignment from the database, update assignmentcount

    cId = crsr.execute("SELECT course_id FROM assignments WHERE assignment_id = ?", (assignmentid,)).fetchall()

    crsr.execute("UPDATE courses SET assignmentcount = assignmentcount - 1 WHERE course_id = (SELECT course_id FROM assignments WHERE assignment_id = ?)", (assignmentid,))
    db_connection.commit()
    
    crsr.execute("DELETE FROM assignments WHERE assignment_id = ?", (assignmentid,))
    db_connection.commit()

    # Resubmit updated course data, without the deleted assignment

    # Fetch assignments from database+

    course_name = crsr.execute("SELECT course_name FROM courses WHERE course_id = ?", (cId[0][0],)).fetchall()
    assignments = crsr.execute("SELECT assignment_name, weight, grade FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

    # Fetch (while calculating) average grade for course
    avg = crsr.execute("SELECT SUM(grade * weight) / SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()
    avg2 = crsr.execute("SELECT SUM(0.01 * grade * weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

    # Fetch the max possible grade for the course at that point
    max = crsr.execute("SELECT SUM(weight) FROM assignments WHERE course_id = ? AND user_id = ?", (cId[0][0],session["user_id"])).fetchall()

    return render_template("assignments.html", course_name=course_name[0][0], assignments=assignments, avg=avg[0][0], avg2=avg2[0][0], max=max[0][0])
