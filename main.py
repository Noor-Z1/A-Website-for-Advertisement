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
        c.execute("SELECT * FROM Advertisement WHERE category = ?", selected)
        allData = c.fetchall()
        print(allData)
        c.execute("SELECT cname from CATEGORY where cid = ?", selected)
        category_name = c.fetchone()[0]  # extracting the name from the tuple
        filtered = []

        for row in allData:
            # Create a regular expression pattern for the keyword
            pattern = re.compile(keyword, re.IGNORECASE)
            # Check if the pattern matches any part of AN ACTIVE advertisement
            if (pattern.search(row[1]) or pattern.search(row[2]) or pattern.search(row[4])) and row[3]:
                filtered.append(row)

        if filtered == [] or allData == []:
            msg = "No advertisement found!"

    else:
        c.execute("SELECT * FROM Advertisement")
        allData = c.fetchall()

        # create a dictionary with all the categories as keys
        mydict = {}
        for category in categories:
            mydict[category[1]] = []

        for row in allData:
            # Create a regular expression pattern for the keyword
            pattern = re.compile(keyword, re.IGNORECASE)
            # Check if the pattern matches any part of AN ACTIVE advertisement
            if (pattern.search(row[1]) or pattern.search(row[2]) or pattern.search(row[4])) and row[3]:
                c.execute("SELECT cname from CATEGORY where cid = ?", (row[5],))
                name = c.fetchone()[0]
                mydict[name].append(row)

        conn.close()

    if selected != "all":
        return render_template("home.html", data=allData, msg=msg, type=category_name, categories=categories, session=session)
    else:
        # might add another return for the case where all categories are selected! or find a better way
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

        print(row)
        if row is not None:
            # if the username exists in our db
            session["username"] = username
            return render_template('home.html', session=session, categories=categories)
        else:
            # added this because we need to show error message just below the form as per assignment!
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


"""
THIS IS REDUNDANT I THINK
"""
# @app.route('/display')
# def display():
#     return render_template('advertisement.html')

@app.route('/advertisement', methods=['GET', 'POST'])  # to be completed: send categories for checkbox
def advertisement():

    # I COMMENTED somethings AND ONE RETURN IS ENOUGH HERE

    # if "username" in session:  # username should be in the session because this page is way after login
    conn = sqlite3.connect("adv.db")
    c = conn.cursor()
    c.execute("SELECT title, description, category, isactive  FROM Advertisement WHERE username=?",
              (session["username"],))
    records = c.fetchall()

    c.execute("Select * from Category")
    categories = c.fetchall()
    conn.close()
    #     return render_template("advertisement.html", records=records)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']   # this will give you the category id
        conn = sqlite3.connect("adv.db")
        c = conn.cursor()
        # setting the isactive as 1 which means it is active by default
        # to be completed for category -> right now assigning category as 1
        # Shemin needs to change it
        c.execute("INSERT INTO Advertisement(title, description, isactive, username,category) "
                  "VALUES(?,?,?,?,?) ", (title, description, 1, session["username"], 1))
        conn.commit()
        conn.close()

    return render_template('advertisement.html', categories= categories, records=records)


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
