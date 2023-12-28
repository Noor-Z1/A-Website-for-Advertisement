from flask import *
import sqlite3

app = Flask(__name__)
app.secret_key = "123"

@app.route("/")
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

        conn = sqlite3.connect("adv.db")
        c = conn.cursor()
        c.execute("INSERT INTO User VALUES(?,?,?,?,?)",
                  (username, password, fullname, email, tel))
        conn.commit()
        conn.close()

        return redirect(url_for('register_success'))
    else:
        return render_template('register.html')


@app.route("/register_success")
def register_success():
    return render_template('register_success.html')


@app.route("/loginform")
def loginform():
    if "username" in session:  # dictionary in python flask, username as a key in this dict
        return render_template("login.html", username=session["username"])
        # if username available: send username to the index.html
    else:
        return render_template("login.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST" and "username" not in session:
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
    elif 'username' in session:
        # Check which page the user should be redirected to based on session information
        if request.path == '/':
            return redirect(url_for('home'))
        elif request.path == '/advertisement':
            return redirect(url_for('advertisement'))
        elif request.path == '/profile':
            return redirect(url_for('profile'))
        elif request.path == '/logout':
            return redirect(url_for('logout'))

#     add if statements for home page, adv page, profile page, logout


@app.route('/logout')
def logout():
    # remove the username from our session
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/display')
def display():
    return render_template('advertisement.html')

@app.route('/advertisement', methods=['GET', 'POST']) # to be completed: send categories for checkbox
def advertisement():
    if "username" in session:
        conn = sqlite3.connect("adv.db")
        c = conn.cursor()
        c.execute("SELECT title, description, category, isactive  FROM Advertisement WHERE username=?",
                  (session["username"],))
        conn.commit()
        records = c.fetchall()
        conn.close()
        return render_template("advertisement.html", records=records)
    if request.method == 'POST' and "username" in session:
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        conn = sqlite3.connect("adv.db")
        c = conn.cursor()
        # setting the isactive as 1 which means it is active by default
        # to be completed for category
        c.execute("INSERT INTO Advertisement(title, description, isactive, username) "
                  "VALUES(?,?,?,?) ", (title, description, 1, session["username"]))
        conn.commit()
        conn.close()
        return redirect(url_for('display'))
    return redirect(url_for('/display'))

# @app.route('/advertisement')
# @app.get('/display')
# def display():
#     if "username" in session:
#         conn = sqlite3.connect("adv.db")
#         c = conn.cursor()
#         c.execute("SELECT title, description, category, isactive  FROM Advertisement WHERE username=?",
#                   (session["username"],))
#         conn.commit()
#         records = c.fetchall()
#         conn.close()
#         return render_template("advertisement.html", records=records)
#     else:
#         return render_template('advertisement.html')


if __name__ == '__main__':
    app.run()