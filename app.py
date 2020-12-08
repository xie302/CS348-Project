from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
import mysql.connector
from random import seed
from random import randint
db = mysql.connector.connect(
    host="34.72.99.39",
    user="root",
    password="CS348",
    database="CS348Proj"
)

app = Flask(__name__)
app.secret_key = "This is a secret string"

app.config['MYSQL_DATABASE_USER'] = 'newuser'
app.config['MYSQL_DATABASE_PASSWORD'] = 'awesomeblog'
app.config['MYSQL_DATABASE_DB'] = 'hosportal'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

app.permanent_session_lifetime = timedelta(minutes=10)


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == "POST":

        username = request.form["UserName"]
        email = request.form["Email"]
        password = request.form["Password"]
        type = request.form["type"]
        cur = db.cursor()
        seed(1)
        while True:
            UID = randint(10000000, 99999999)
            query = "SELECT UID from User where UID="+str(UID)
            cur.execute(query)
            data = cur.fetchall()
            if not data:
                break
            seed(UID)
        cur.execute("INSERT INTO User(UID,UserName, Email, Password, Type) VALUES (%s, %s, %s, %s, %s)", (str(UID),username, email, password, type))
        db.commit()
        cur.close()
        flash("User " + username + " created!")
        return redirect(url_for("login"))

    else:
        if "user" in session:
            return redirect(url_for("user"))
    return render_template("signup.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pw = request.form["password"]
        cur = db.cursor()
        query = "SELECT UID, UserName, Email, Password, Type from User where UserName = '" + username + "'"
        cur.execute(query)
        usr = cur.fetchone()
        cur.close()
        if usr:
            if pw == usr[3]:
                session.permanent = True
                session["user"] = usr
                return redirect(url_for("user"))
            else:
                flash("Wrong Password!")
                return render_template("login.html")
        else:
            flash("Invalid User!")
            return render_template("login.html")
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("index.html", role=user[4], content=user[1])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if "user" in session:
        user = session["user"]
        return render_template("profile.html", role=user[4], content=user[1])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/appointment")
def appointment():
    if "user" in session:
        user = session["user"]
        return render_template("Appointment.html", role=user[4], content=user[1])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/prescription")
def prescription():
    if "user" in session:
        user = session["user"]
        return render_template("Prescription.html", role=user[4], content=user[1])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/delete")
def delete():
    if "user" in session:
        user = session["user"]
        cur = db.cursor()
        print(user[1])
        sql = "DELETE FROM User WHERE UserName = '" + user[1] + "'"
        cur.execute(sql)
        db.commit()
        cur.close()
        session.pop("user", None)
        flash("User Deleted!")
        return redirect(url_for("login"))
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
