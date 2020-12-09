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


@app.route("/")
def null():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("index.html", role=user[2], content=user[1])
    else:
        return redirect(url_for("login"))


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
        cur.execute("INSERT INTO User(UID,UserName, Email, Password, User_type) VALUES (%s, %s, %s, %s, %s)", (str(UID), username, email, password, type))
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
        query = "SELECT * from User where UserName = '" + username + "'"
        cur.execute(query)
        usr = cur.fetchone()
        cur.close()
        if usr:
            if pw == usr[4]:
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
        return render_template("index.html", role=user[2], content=user[1])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/profile", methods=["POST", "GET"])
def profile():
    if "user" in session:
        if request.method == "POST":
            username = request.form["UserName"]
            email = request.form["Email"]
            password = request.form["Password"]
            type = request.form["type"]
            cur = db.cursor()
            user = session["user"]
            query = "UPDATE User SET UserName = '"+username+"', Email = '"+email+"', Password = '"+password+"', User_type='"+type+"'WHERE UID ='"+user[0]+"'"
            cur.execute(query)
            db.commit()
            flash("User " + username + " modified!")
            cur.execute("SELECT * FROM User WHERE UID ='" + user[0] + "'")
            usr = cur.fetchone()
            session["user"]=usr
            cur.close()
            return redirect(url_for("user"))
        else:
            user = session["user"]
            return render_template("profile.html", role=user[2], content=user[1])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))



@app.route("/appointment")
def appointment():
    if "user" in session:
        user = session["user"]
        return render_template("Appointment.html", role=user[2], content=user[1])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/prescription", methods=["POST", "GET"])
def prescription():
    if "user" in session:
        user = session["user"]
        user_type = user[2]
        user_id = user[0]
        print(user_type)
        if user_type == 'doctor' or user_type == 'Doctor':
            cur = db.cursor(buffered=True)
            cur.execute("SELECT Doctor_id FROM Doctor WHERE UID = " + user_id + ";")
            doc_result = cur.fetchall()
            doc_id = str(doc_result[0][0])
            cur.execute("SELECT Pre_id, Pre_name, Pre_amount, Patient_id, Name"
                        " FROM Report NATURAL JOIN Prescription NATURAL JOIN Appointment NATURAL JOIN Patient"
                        " WHERE Doctor_id = " + doc_id + ";")
            pat_pre_details = cur.fetchall()
            db.commit()
            cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
            cur.execute("START TRANSACTION;")
            cur.execute("SELECT * FROM Prescription;")
            preDetails = cur.fetchall()
            return render_template("Prescription_doctor.html", preDetails=preDetails, pat_pre_details=pat_pre_details)

        elif user_type == 'patient' or user_type == 'Patient':
            cur = db.cursor(buffered=True)
            cur.execute("SELECT Patient_id FROM Patient WHERE UID = " + user_id + ";")
            pat_result = cur.fetchall()
            pat_id = str(pat_result[0][0])
            cur.execute("SELECT Pre_id, Pre_name, Pre_amount"
                        " FROM Report NATURAL JOIN Prescription"
                        " WHERE Report_num IN (SELECT A.Report_num"
                        " FROM Appointment A"
                        " WHERE A.Patient_id =" + pat_id + ");")
            preDetails = cur.fetchall()
            return render_template("Prescription_patient.html", preDetails=preDetails)
            #button redirect to /pre_select
        else:
            return("unknown user")
            return render_template("login.html", role=user[3], content=user[0])
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/pre_select", methods=["POST", "GET"])
def pre_select():
    if "user" in session:
        user = session["user"]
        if request.method == 'POST':
            #get pre_id, amount_toassign, pat_id
            preDetails = request.form
            pre_id = preDetails['pre_id']
            amount_toassign = int(preDetails['amount'])
            pat_id = preDetails['pat_id']
            cur = db.cursor()
            #get doc_id from user
            cur.execute("SELECT Doctor_id FROM Doctor WHERE UID = " + user[4] + ";")
            doc_result = cur.fetchall()
            doc_id = str(doc_result[0][0])
            #get amount_left
            query = "SELECT amount_left FROM Prescription WHERE Pre_id =" + pre_id + ";"
            cur.execute(query)
            result = cur.fetchall()
            amount_left = result[0][0]
            if amount_toassign <= amount_left:
                query = ("UPDATE Prescription"
                         " SET amount_left = amount_left - " + str(amount_toassign) + ""
                         " WHERE Pre_id = " + pre_id + ";")
                cur.execute(query)
                query = ("UPDATE Report"
                         " SET Report.Pre_id =" + pre_id + ""
                         " WHERE Report.Report_num = (SELECT MAX(Appointment.Report_num)"
                         " FROM Appointment"
                         " WHERE Appointment.Patient_id =" + pat_id + " AND Appointment.Doctor_id =" + doc_id + ");")
                cur.execute(query)
                query = ("UPDATE Report"
                         " SET Report.Pre_amount =" + str(amount_toassign) + ""
                         " WHERE Report.Report_num = (SELECT MAX(Appointment.Report_num)"
                         " FROM Appointment"
                         " WHERE Appointment.Patient_id =" + pat_id + " AND Appointment.Doctor_id =" + doc_id + ");")
                cur.execute(query)
                cur.execute("UPDATE Doctor SET Doctor.state = 'available' WHERE Doctor_id =" + doc_id + ";")
                db.commit()
                # need to be shown as small side titles
                return("Prescription request successful")
            else:
                db.commit()
                return ("Prescription request unsuccessful")
        else:
            return render_template("pre_select.html")
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out")
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
