from flask import *
import sqlite3

app = Flask(__name__)
app.secret_key = "123"

@app.route("/register")
def index():
    if "username" and "password" in session:
        # dictionary in python flask, username and password as a key in this dict
        return render_template("login.html",
                               username=session["username"], password=session["password"])
        # if username available: send username to the login.html
    else:
        return render_template("register.html")
        # register screen will be displayed if no username is available

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # now connect to db and check username and password and update the session dictionary
        conn = sqlite3.connect("adv.db")
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE username = ? AND password = ?", (username, password))
        row = c.fetchone()
        conn.close()
        if row != None:
            # if the username exists in our db
            session["username"] = username
            session["password"] = password
        # else:
        #     # redirect
        #OR do this instead
        return redirect(url_for('login'))
        # go to login function

    else: # skip this part (GET method)
        pass
@app.route('/logout')
def logout():
    # remove the username and password from our session
    session.pop("username", None)
    session.pop("password", None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()