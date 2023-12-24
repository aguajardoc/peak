# Peak [WIP]

Peak is a simple and rudimentary gradebook, created using Python to link all the required files through Flask, a SQL database connection, and HTML for the layout of the pages, which in itself involved the usage of CSS, Bootstrap, and Jinja. Users can register and log in to this webapp, add new courses, set credit values, add assignments with corresponding grades and weights, see their average for a given course, their cumulative average for the course, and weighted and unweighted GPA's for the entire course list!

## app.py

Establishes the connection to the database (peak.db) through SQL, configures the Flask application, and includes all the code relevant to the corresponding SQL queries when a user performs any given action (registering, logging in/out, edit/add course and assignment data).

## helpers.py

Allows for the calling of the apology function as an error message and for the decoration of routes in app.py to require user login (@login_required). Code adapted from the CS50x Problem Set 9, 2023.

# static

Contains all external assets used, designed and created using Photopea, along with the styles.css file.

## styles.css

Details relevant styles for the navbar, along with the positioning and animations of elements when required.

# templates

Contains all HTML files used for each page.

## layout.html

Sets up the general layout to be used in every other page of the webapp.

## apology.html

Shows the user an error message whenever an action cannot be completed. Code adapted from the CS50x Problem Set 9, 2023.

## register.html

Allows a new user to create an account. Data validation in app.py, hashing the password for security. 

Design choices: aimed for something simple but functional, could be better if I spent more time on it.

## login.html

Allows a registered user to log in. Data validation in app.py.

Design choices: same as for register.html, could also be better if I spent more time on it.

## index.html

Main page of the app, shows the overall purpose. 

Design choices: aimed to use animations simply to learn how to involve them, not meant to be super clean.

## current.html

Shows a user's course list taking advantage of Bootstrap. Allows the addition of new courses, their editing, and their deletion.

Design choices: I first wanted the add button to be the image within the button and that's it, but it did not work out as expected and ended up placing the image within the button so that the user sees it more easily. I wanted to use the table as an opportunity to acquaint myself with some Bootstrap features.

## assignments.html

Shows a user's course's assignment list, taking advantage of Bootstrap. Allows the addition of new assignments, their editing, and their deletion.

Design choices: copy that of current.html, with minor alterations where needed.

## newcourse.html

Allows a user to add a new course.

Design choices: same as login.html and register.html, could also be better if I spent more time on it.

## newassignment.html

Allows a user to add a new assignment.

Design choices: same as newcourse.html, but with the addition of the percentage sign appended at the end of the input box for user readability. Turned out better than I expected, but it could still look cleaner.

## editcourse.html

Allows a user to edit an existing course.

Design choices: same as newcourse.html, while reminding users of their initially inputted data, which worked nicely.

## editassignment.html

Allows a user to edit an existing assignment.

Design choices: same as editcourse.html.

## What did I learn?

A lot. As this is my first webapp I've built, Flask, Bootstrap and SQL were completely foreign to me, and I'm glad I was able to implement them for this project that I will continue to use for myself during my academic career.

As of now, I *do not* consider the project as finished. There are multiple holes in the logic that I hope I can fix, alongside features that I would like to implement, like separating courses into distinct periods/semesters. I'm not too proud of the design choices made, particularly with index.html, so I could expand over that in the future. Once I do this, I'd be glad to release this to the public eye so that they too can benefit from my project.

Also, I somewhat learned the basics of Markdown for this very file.

ツ

### Current State: Many issues are still present, and features are missing, as detailed above.
