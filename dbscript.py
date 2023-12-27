import sqlite3


def createTable(dbname):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = 1")  # check the validity of foreign keys

    c.execute("CREATE TABLE IF NOT EXISTS User("
              "username TEXT PRIMARY KEY,"
              "password TEXT,"
              "fullname TEXT,"
              "email TEXT,"
              "telno TEXT)")

    c.execute("CREATE TABLE IF NOT EXISTS Category("
              "cid INTEGER PRIMARY KEY,"
              "cname TEXT)")

    c.execute("CREATE TABLE IF NOT EXISTS Advertisement("
              "aid INTEGER PRIMARY KEY AUTOINCREMENT,"
              "title TEXT,"
              "description TEXT,"
              "isactive INTEGER,"
              "username TEXT,"
              "category INTEGER,"
              "FOREIGN KEY (username) REFERENCES User(username),"
              "FOREIGN KEY (category) REFERENCES Category(cid))")

    conn.commit()
    conn.close()


def insert(dbname):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    category = [(1,"Clothes"), (2,"Technology"), (3, "Cars"), (4, "Food"), (5, "Drink")]
    c.executemany("INSERT INTO Category VALUES(?,?)", category)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    createTable("adv.db")
    insert("adv.db")
