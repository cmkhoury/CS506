from flask import Flask, render_template, request, session, send_file
import os
import sqlite3 as sql
import time
import datetime
import pdb
import json
import helper_function
import json
import json
import requests
app = Flask(__name__)
lid = 990
global msg
db = "data/test.db"

@app.route('/', methods=['POST', 'GET'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    if session.get('is_power'):
        return render_template('powerHome.html')
    else:
        return render_template('home.html')
       #if session.get('is_regular'):
        #   return render_template('home.html')
       #if session.get('is_power'):
        #   return render_template('powerHome.html')

app.secret_key = os.urandom(12)

@app.route('/map')
def map():
    if not session.get('logged_in'):
       return render_template('login.html')

    con = sql.connect(db)
    con.row_factory = sql.Row
    cur = con.cursor()
    query = "SELECT * FROM User WHERE UID=\'" + str(UID) + "\'"
    cur.execute(query)
    rows = cur.fetchall()

    if len(rows) == 0:
       return home()

    return render_template('browse.html', lat = rows[0]['Lat'], lon = rows[0]['Lon'], state = rows[0]['State'], uid = rows[0]['UID'])

@app.route('/api/nearbyShoppers')

def nearbyShoppers():
    con = sql.connect(db)
    con.row_factory = sql.Row
    cur = con.cursor()
    state = request.args.get('state');
    uid = request.args.get('uid');
    query1 = "SELECT * FROM User WHERE State = \'" + str(state) + "\'"
    query2 = "SELECT * FROM User WHERE UID = \'" + str(uid) + "\'"
    cur.execute(query1 + " EXCEPT " + query2)
    rows = cur.fetchall()
    results = list()
    for x in range(0, len(rows)):
        user = dict()
        user["username"] = rows[x]['Username'];
        user["firstname"] = rows[x]['FirstName'];
        user["lastname"] = rows[x]['LastName'];
        user["email"] = rows[x]['Email'];
        user['streetaddress'] = rows[x]['Address']
        user["city"] = rows[x]['City'];
        user["state"] = rows[x]['State'];
        user["zip"] = rows[x]['Zip'];
        user["lat"] = rows[x]['Lat'];
        user["lon"] = rows[x]['Lon'];
        user['uid'] = rows[x]['UID'];
        results.append(user)

    return json.dumps(results)

@app.route('/profile')
def profile():
    if not session.get('logged_in'):
       return render_template('login.html')

    con = sql.connect(db)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from User where UID=\'" + str(UID) + "\'")
    rows = cur.fetchall()

    # (Username,Password,Email,Address,City,State,Zip,FirstName,LastName)

    if len(rows) == 0:
       return home()

    profile = dict();
    profile['username']= rows[0]['Username']
    profile['firstname']= rows[0]['FirstName']
    profile['lastname'] = rows[0]['LastName']
    profile['email'] = rows[0]['Email']
    profile['address'] = rows[0]['Address']
    profile['city'] = rows[0]['City']
    profile['state'] = rows[0]['State']
    profile['zip'] = rows[0]['zip']

    query = "SELECT Cart.CID AS 'CartID',Cart.Total AS 'Total',Item.Description AS 'Description',Item.IID AS 'ItemID',Item.Price AS 'Price', Item.Quantity AS 'Quantity' FROM Cart INNER JOIN CartItem ON Cart.CID = CartItem.CID INNER JOIN Item ON CartItem.IID = Item.IID WHERE UID = \'" + str(UID) + "\'"
    cur.execute(query)
    rows = cur.fetchall()

    listOfCarts = [];
    listofItems = [];

    for x in range(0, len(rows)):
      cart = dict()
      cart['cartID'] = rows[x]['CartID']
      cart['total'] = rows[x]['total']
      if(cart not in listOfCarts): listOfCarts.append(cart)
      item = dict()
      item['cartID'] = rows[x]['CartID']
      item['itemID'] = rows[x]['ItemID']
      item['price'] = rows[x]['Price']
      item['description'] = rows[x]['Description']
      item['quantity'] = rows[x]['Quantity']
      if(item not in listofItems): listofItems.append(item)

    return render_template('profile.html', profile = profile, listOfItems = listofItems, listOfCarts = listOfCarts, numItemss = len(listofItems))


@app.route('/addUser', methods = ['POST', 'GET'])
def new_user():
    # if not session.get('logged_in'):
    #     return render_template('login.html')

    return render_template('addUser.html')

#CREATE TABLE User(
#  UID INTEGER PRIMARY KEY,
# Username TEXT,
#   Password TEXT,
#   Email TEXT,
#   Address TEXT,
#   Address2 TEXT,
#   City Text,
#   State Text,
#   Zip Text,
#  FirstName TEXT,
#  LastName TEXT,
#  OID INTEGER);


@app.route('/addUserData', methods = ['POST', 'GET'])
def addUserData():
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    # if not session.get('is_power'):
    #     return render_template('home.html')
    try:
         username = request.form['username']
         password = helper_function.encryptPassword(request.form['password'])
         email = request.form['email']
         address = request.form['inputAddress']
         city = request.form['inputCity']
         state = request.form['inputState']
         zipActual = request.form['inputZip']
         firstname = request.form['firstname']
         lastname = request.form['lastname']

         addressFormatted = "".join([address, ",+", city, ",+", state, ",+", zipActual])
         apiKEY = "AIzaSyBRx7Cu0K1yT5nS9qZFiSbRaQZpPxz_9wk"
         call = "".join(["https://maps.googleapis.com/maps/api/geocode/json?address=", addressFormatted, "&key=", apiKEY])
         # print(call)
         response = requests.get(call)
         json_data = response.json()

        # # If google can't get a lat lon from the address, it's one of the fake ones
        #  if (json_data['status'] == "ZERO_RESULTS"):
        #      print("Fake Address Found")
        #      continue;

         lat = str(json_data['results'][0]['geometry']['location']['lat'])
         lon = str(json_data['results'][0]['geometry']['location']['lng'])

         with sql.connect(db) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO User(Username,Password,Email,Address,City,State,Zip,FirstName,LastName,Lat,Lon) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (username,password,email,address,city,state,zipActual,firstname,lastname,lat,lon))
            con.commit()
            msg = "Record successfully added"

    except Exception as e:
             con.rollback()
             if (str(e) == "UNIQUE constraint failed: User.Username"):
                msg = "Username already used, go back to try another username"
             else: msg = e

    finally:
             return render_template("result.html", msg = msg)
             con.close()

@app.route('/user')
def user():

    con = sql.connect(db)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from User")
    rows = cur.fetchall()
    return render_template("user.html", rows = rows)

@app.route('/carts')
def carts():

    con = sql.connect(db)
    con.row_factory = sql.Row
    cur = con.cursor()
    currentUser = session.get('username')
    query = "SELECT * FROM Cart INNER JOIN User ON Cart.UID=User.UID WHERE Username = \'" + currentUser + "\'"
    cur.execute(query)
    rows = cur.fetchall()
    return render_template("carts.html", rows = rows)

@app.route('/login', methods=['POST', 'GET'])
def login():
   global UID
   username = request.form['username']
   print(username)
   password = request.form['password']
   print(password)
   con = sql.connect(db)
   con.row_factory = sql.Row
   cur = con.cursor()

   query = "SELECT * FROM User WHERE Username=\'" + username + "\'"
   cur.execute(query)
   rows = cur.fetchall()

   if len(rows) == 0:
      return home()

   elif helper_function.checkPassword(password.encode(), rows[0]['Password'].encode()):
       if rows[0]['UserLevel'] == 'power':
          session['is_power'] = True
       elif rows[0]['UserLevel'] == '':
          session['is_regular'] = True
       session['logged_in'] = True
       session['username'] = username
       UID = rows[0]['UID']
      #print("UID: ", UID)

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

@app.route('/searchPartner')
def searchPartner():
  return render_template("searchPartner.html")

@app.route('/api/searchPartner') #?name = "XXX"
def searchPartner_api():

  con = sql.connect(db)
  con.row_factory = sql.Row
  cur = con.cursor()
  name = request.args.get('name');
  query = "select * from User WHERE Username LIKE \'%" + str(name) + "%\' OR FirstName LIKE \'%" + str(name) + "%\' OR LastName LIKE \'%" + str(name) + "%\'"
  cur.execute(query)
  rows = cur.fetchall()
  results = list()
  for x in range(0, len(rows)):
    user = dict()
    user["email"] = rows[x]['email'];
    user["username"] = rows[x]['username'];
    user["address"] = rows[x]['address'];
    user["city"] = rows[x]['city'];
    user["state"] = rows[x]['state'];
    user["zip"] = rows[x]['zip'];
    user["firstname"] = rows[x]['firstname'];
    user["lastname"] = rows[x]['lastname'];
    results.append(user)


  #if len(rows) == 0:

  return json.dumps(results);

@app.route('/api/hasUsername') #?username = "XXX"
def hasUsername_api():
  con = sql.connect(db)
  con.row_factory = sql.Row
  cur = con.cursor()
  name = request.args.get('username');
  query = "select * from User WHERE Username = \'"+ str(name) + "\'"
  cur.execute(query)
  rows = cur.fetchall()
  return json.dumps(len(rows) != 0);

if __name__ == '__main__':
    app.run(debug = True, threaded=True)
