from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "This is a secret string"
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'newuser'
app.config['MYSQL_DATABASE_PASSWORD'] = 'awesomeblog'
app.config['MYSQL_DATABASE_DB'] = 'hosportal'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
app.permanent_session_lifetime = timedelta(minutes=10)

db = MySQL(app)


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
        cur = mysql.connect.cursor()
        cur.execute("INSERT INTO hosuser(username, email, password, type) VALUES (%s, %s, %s, %s)", (username, email, password, type))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("login"))

    else:
        if "user" in session:
            return redirect(url_for("user"))
    return render_template("signup.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("index.html", content=user)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
