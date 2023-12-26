from flask import *
import sqlite3

app = Flask(__name__)
app.secret_key = "123"


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        fullname = request.form["Full name"]
        email = request.form["Email address"]
        tel = request.form["Telephone number"]

        # to be completed: Update database
        conn = sqlite3.connect("adv.db")
        c = conn.cursor()
        c.execute("INSERT INTO User VALUES(?,?,?,?,?)",(username, password, fullname, email, tel))
        conn.commit()
        conn.close()
        return redirect(url_for('register_success'))
    else:
        return render_template('register.html')

@app.route("/register_success")
def register_success():
    return render_template('register_success.html')

@app.route("/loginform")
def index():
    if "username" in session: # dictionary in python flask, username as a key in this dict
        return render_template("login.html", username=session["username"]) # if username available: send username to the index.html
    else:
        return render_template("login.html")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # now connect to db and check username and password and update the session dictionary
        conn = sqlite3.connect("adv.db")
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE username = ? AND password = ?",
                  (username, password))
        row = c.fetchone()
        conn.close()

        if row is not None:
            # if the username exists in our db
            session["username"] = username
        return redirect(url_for('loginform'))
    else: # skip this part (GET method)
        pass
@app.route('/logout')
def logout():
    # remove the username from our session
    session.pop("username", None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()