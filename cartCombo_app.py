from flask import Flask, render_template, request, session, send_file
import os
import sqlite3 as sql
import time
import datetime
import pdb
app = Flask(__name__)
lid = 990
global msg



@app.route('/')
def home():
   if not session.get('logged_in'):
      return render_template('login.html')
   else:
      return render_template('home.html')
app.secret_key = os.urandom(12)

@app.route('/addUser')
def new_user():
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    # if not session.get('is_power'):
    #     return render_template('home.html')
    return render_template('addUser.html')

# CREATE TABLE User(
#     UID INTEGER PRIMARY KEY,
#     Username TEXT,
#     Password TEXT,
#     Email TEXT,
#     Address TEXT,
#     FirstName TEXT,
#     LastName TEXT,
#     OID INTEGER,


@app.route('/addUserData', methods = ['POST', 'GET'])
def addUserData():
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    # if not session.get('is_power'):
    #     return render_template('home.html')
    try:
         username = request.form['username']
         password = request.form['password']
         email = request.form['email']
         aid = request.form['aid']
         firstname = request.form['firstname']
         lastname = request.form['lastname']

         with sql.connect("data/test.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO User(Username,Password,Email,Address,FirstName, LastName) VALUES (?,?,?,?,?,?)",(username,password,email,aid,firstname,lastname))
            con.commit()
            msg = "Record successfully added"
    except Exception as e:
             con.rollback()
             msg = e

    finally:
             return render_template("result.html", msg = msg)
             con.close()

@app.route('/user')
def user():

    con = sql.connect("data/test.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from User")
    rows = cur.fetchall()
    return render_template("user.html",rows = rows)

@app.route('/login', methods=['POST'])
def login():
   username = request.form['username']
   password = request.form['password']

   con = sql.connect("data/test.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   query = "select * from User where Username=\'" + username + "\'"
   cur.execute(query)

   rows = cur.fetchall()
   if len(rows) == 0:
      return home()
   elif rows[0]['Password'] == password:
      session['logged_in'] = True
      # if rows[0]['UserLevel'] == 'power':
      #    session['is_power'] = True
      # elif rows[0]['UserLevel'] == 'regular':
      #    session['is_regular'] = True
      return home()
   else:
      return home()

@app.route('/logout')
def logout():
   # if not session.get('logged_in'):
   #    return render_template('login.html')
   # session['is_power'] = False
   # session['is_regular'] = False
   session['logged_in'] = False
   # render_template("logout.html")
   return render_template("logout.html")

if __name__ == '__main__':
    app.run(debug = True, threaded=True)