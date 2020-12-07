from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
import mysql.connector

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

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        type = request.form["type"]
        cur = db.cursor()
        cur.execute("INSERT INTO hosuser(username, email, password, type) VALUES (%s, %s, %s, %s)", (username, email, password, type))
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
        query = "SELECT username, email, password, type from hosuser where username = '" + username + "'"
        cur.execute(query)
        usr = cur.fetchone()
        cur.close()
        if usr:
            if pw == usr[2]:
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
        return render_template("index.html", role=user[3], content=user[0])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if "user" in session:
        user = session["user"]
        return render_template("profile.html", role=user[3], content=user[0])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/appointment")
def appointment():
    if "user" in session:
        user = session["user"]
        return render_template("Appointment.html", role=user[3], content=user[0])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/prescription", methods=["POST", "GET"])
def prescription():
    cur = db.cursor(buffered=True)
    cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
    cur.execute("START TRANSACTION;")
    resultRows = cur.execute("SELECT * FROM Prescription;")
    preDetails = cur.fetchall()
    return render_template("Prescription.html", preDetails=preDetails)
    #button redirect to /pre_select


@app.route("/pre_select", methods=["POST", "GET"])
def pre_select():
    if request.method == 'POST':
        preDetails = request.form
        pre_id = preDetails['pre_id']
        amount_toassign = preDetails['amount']
        pat_id = preDetails['pat_id']
        doc_id = preDetails['doc_id']
        cur = db.cursor()
        cur.execute("SELECT amount_left FROM Prescription WHERE Pre_id = %s;", pre_id)
        amount_left = cur.fetchall()
        if amount_toassign <= amount_left[0]:
            cur.execute("UPDATE Prescription"
                        "SET amount_left = amount_left - %s"
                        "WHERE Pre_id = %s;", (amount_toassign, pre_id))
            cur.execute("UPDATE Report"
                        "SET Report.Pre_id = %s"
                        "WHERE Report.Report_num = (SELECT MAX(Appointment.Report_num)"
                        "FROM Appointment"
                        "WHERE Appointment.Patient_id = %s AND Appointment.Doctor_id = %s);", (pre_id, pat_id, doc_id))
            cur.execute("UPDATE Doctor SET Doctor.state = 'available' WHERE Doctor_id = %s;", (doc_id))
            db.commit()
            return render_template("Pre_select.html")
        else:
            db.commit()
            return render_template("Pre_select.html")
    else:
        return render_template("Pre_select.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/delete")
def delete():
    if "user" in session:
        user = session["user"]
        cur = db.cursor()
        print(user[0])
        sql = "DELETE FROM hosuser WHERE username = '" + user[0] + "'"
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
