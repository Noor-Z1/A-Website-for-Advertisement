from flask import *
import sqlite3
import re


app = Flask(__name__)
app.secret_key = "123"


@app.route("/")
@app.route("/home")
def home():
    session.pop("username",None)         # to make sure username is not in session keys yet!
    return render_template("home.html", session=session)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["pwd"]
        fullname = request.form["Full name"]
        email = request.form["Email address"]
        tel = request.form["Telephone number"]

        # Check the duplication of the username
        # if there is the same username in the database as she/he (not their own username) inputs:
        if is_username_duplicated(username):
            msg = "Username is already taken! please choose something else"
            return render_template('register.html', msg=msg)

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

@app.post("/showadvertisements")
def showadvertisements():
    selected = request.form.get('category')
    keyword = request.form.get('search')

    conn = sqlite3.connect("adv.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATEGORY")
    categories = c.fetchall()

    msg = ""
    if selected != "all":
        # search for a match The advertisement whose titles, descriptions or contact full name includes at least one of the
        # keywords will be listed. Please note that it does not have to be a full match, so if the keyword is
        # "abc", and the title is "xyabcz", then it should be listed as well

        c.execute("SELECT * FROM Advertisement WHERE isactive = 1 and category = ?", selected)
        allData = c.fetchall()
        c.execute("SELECT cname from CATEGORY where cid = ?", selected)
        category_name = c.fetchone()[0]  # extracting the name from the tuple
        filtered = []

        # Create a regular expression pattern for the keyword
        pattern = re.compile(keyword, re.IGNORECASE)
        # Check if the pattern matches any part of AN ACTIVE advertisement
        for row in allData:
            # Check if the pattern matches any part of AN ACTIVE advertisement
            if (pattern.search(row[1]) or pattern.search(row[2]) or pattern.search(row[4])):
                filtered.append(row)

        if filtered == [] or allData == []:
            msg = "No advertisement found!"
        return render_template("home.html", data=filtered, msg=msg, type=category_name, categories=categories, session=session)

    else:
        c.execute("SELECT * FROM Advertisement where isactive = 1")
        allData = c.fetchall()

        # create a dictionary with all the categories as keys
        mydict = {}
        for category in categories:
            mydict[category[1]] = []

        # Create a regular expression pattern for the keyword
        pattern = re.compile(keyword, re.IGNORECASE)

        for row in allData:
            # Check if the pattern matches any part of AN ACTIVE advertisement
            if (pattern.search(row[1]) or pattern.search(row[2]) or pattern.search(row[4])):
                c.execute("SELECT cname from CATEGORY where cid = ?", (row[5],))
                name = c.fetchone()[0]
                mydict[name].append(row)

        conn.close()
        return render_template("home.html", data_dict=mydict, msg=msg, categories=categories, session=session)


@app.route("/SeeMore/<id>")
def showMore(id):
    aid = id

    conn = sqlite3.connect("adv.db")
    c = conn.cursor()
    c.execute("SELECT * from Advertisement where aid = ?", aid)
    row = c.fetchall()
    uname= row[0][4]

    c.execute("SELECT fullname, email, telno from User WHERE username = ?", (uname,))
    contact = c.fetchall()
    c.close()
    return render_template("details.html", adData=row[0], contactData=contact[0])


@app.get("/loginform")
@app.route("/dologin", methods=['GET', 'POST'])
def login():
    conn = sqlite3.connect("adv.db")
    c = conn.cursor()
    c.execute("SELECT * FROM Category")
    categories = c.fetchall()
    conn.close()
    if request.method == "POST" and "username" not in session:
        username = request.form["username"]
        password = request.form["pwd"]
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
            return render_template('home.html', session=session, categories=categories)
        else:
            return render_template('login.html', msg="Wrong username or password!")

    elif "username" not in session:
        return render_template('login.html')

    elif "username" in session:
        return render_template('home.html', session=session, categories=categories)


@app.route('/logout')
def logout():
    # remove the username from our session
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/advertisement', methods=['GET', 'POST'])
def advertisement():
    # establish database connection
    conn = sqlite3.connect("adv.db")
    c = conn.cursor()

    # fetch these for displaying the current records
    # joining advertisement and category table to get the  name of the category to be displayed in the table (not the id)
    c.execute("SELECT aid, title, description, cname, isactive  FROM Advertisement JOIN Category "
              "ON category=cid WHERE username=?", (session["username"],))
    records = c.fetchall()

    # need to display categories in a combo box so need to send these
    c.execute("Select * from Category")
    categories = c.fetchall()
    conn.close()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']   # this will give you the category id
        conn = sqlite3.connect("adv.db")
        c = conn.cursor()

        # setting the isactive as 1 which means it is active by default
        # it autoincremenets the aid when inserting
        c.execute("INSERT INTO Advertisement(title, description, isactive, username,category) "
                  "VALUES(?,?,?,?,?) ", (title, description, 1, session["username"], category))
        conn.commit()

        # get updated records after inserting
        # joining advertisement and category table to get the  name of the category to be displayed in the table (not the id)
        c.execute("SELECT aid, title, description, cname, isactive  FROM Advertisement JOIN Category "
                  "ON category=cid WHERE username=?", (session["username"],))
        records = c.fetchall()
        conn.close()

    return render_template('advertisement.html', categories= categories, records=records)


@app.get('/activate')
@app.get('/deactivate')
def toggle():

    # get the id of the advertisement to be updated
    id = request.args.get('id')
    # establish database connection to update the status of the record
    conn = sqlite3.connect("adv.db")
    c = conn.cursor()

    if "deactivate" in request.url:
        c.execute("UPDATE Advertisement SET isactive=0 WHERE aid=?", (id,))
    else:
        c.execute("UPDATE Advertisement SET isactive=1 WHERE aid=?", (id,))

    conn.commit()
    conn.close()

    # redirect to advertisement page to refresh it with updated status of the advertisement
    return redirect(url_for('advertisement'))


@app.route('/loadprofile')
def loadprofile():
    conn = sqlite3.connect("adv.db")
    c = conn.cursor()
    c.execute("SELECT * FROM User WHERE username = ?", (session["username"],))
    profile = c.fetchall()
    conn.close()
    msg = ""
    session["profile"] = profile[0]
    return render_template('profile.html',  details=profile[0], msg=msg)

@app.post("/editprofile")
def editprofile():

    # update the database with the new details
    username = request.form["username"]
    password = request.form["pwd"]
    fullname = request.form["Full name"]
    email = request.form["Email address"]
    tel = request.form["Telephone number"]

    # Check the duplication of the username
    # if the username that user inputs is not the same as the previous one
    # and there is the same username in the database as she/he (not their own username) inputs:
    if username != session["username"] and is_username_duplicated(username):
        msg = "Username is already taken! please choose something else"
        return render_template("profile.html", details=session["profile"], msg=msg)
    # else there is no problem, we update the database accordingly
    conn = sqlite3.connect("adv.db")
    c = conn.cursor()
    c.execute("UPDATE User SET username = ?, password = ?, fullname = ?, email = ?, telno = ? WHERE username = ?",
              (username, password, fullname, email, tel, session["username"]))
    conn.commit()
    conn.close()

    session["username"] = username
    return redirect(url_for('loadprofile'))


def is_username_duplicated(username):
    conn = sqlite3.connect("adv.db")
    c = conn.cursor()
    # here we count the number of users having the same username as the user inputs in the form (profile page)
    c.execute("SELECT COUNT(*) FROM User WHERE username=?",(username,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0


if __name__ == '__main__':
    app.run()
