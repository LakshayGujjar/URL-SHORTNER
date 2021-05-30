#python function to convert given number into base62
from math import floor

def return_base_62(num):
	encoded = ""
	base62_charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

	#we want be having primary key value == 0 and less so we dont want program to  return value 
	#on such i/p
	while num > 0 :
		i = num%62
		num = floor(num/62)
		encoded = base62_charset[i] + encoded 

	return encoded

def return_base_10(str):
	encoded = 0
	base62_charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

	temp = len(str) - 1

	for i in str:
		index = base62_charset.find(i);
		encoded = encoded + (index*(62**temp))
		temp = temp - 1

	return encoded

# return_base_62(3)
# return_base_62(3337770)

# return_base_10("r")
# return_base_10("1H")

#IMPLMENTING DATABASE
import sqlite3

#connects to a created database else creates one
#con = sqlite3.connect('url_shortner_db.db')

#cursor obje. helps to run sql query 
#cursor_obj  = con.cursor()

#execute method of cursor obj runs our query
#cursor_obj.execute("CREATE TABLE urls(id integer PRIMARY KEY,url text,short_url text)")

#helper function to insert into database
def insert_row(con,url):
	cursor_obj = con.cursor()
	cursor_obj.execute("SELECT MAX(id) from urls")
	length = cursor_obj.fetchall()[0][0]
	print(length)
	short = return_base_62(length+1)
	row = (length+1,url,short)
	
	cursor_obj.execute("INSERT INTO urls VALUES (?,?,?)",row)
	con.commit()
	return short

#helper function to delete the database rows
#if delete is implemented you need to remember that deleting an entry
#will make its id useless as we will be inserting into db from last 
def delete_row(con,delete_id):
	cursor_obj  = con.cursor()
	my_query = "DELETE FROM urls where id = " + str(delete_id)
	cursor_obj.execute(my_query)
	con.commit()

def insert_user_urls(con,url):
	cursor_obj = con.cursor()
	my_query = "SELECT short_url from urls where url = " + "\"" + url + "\""
	cursor_obj.execute(my_query)
	
	# to work with sql select we need to use fetchall
	row = cursor_obj.fetchall()
	len = 0
	for r in row:
		len = len+1
	
	if len == 0: 
		temp = insert_row(con,url)
		return temp
	else : 
		return row[0][0]

#given a short url return actual url
def url_for_redirect(con,small_url):
	temp = return_base_10(small_url)

	cursor_obj = con.cursor()
	my_query = "SELECT url from urls where id = "+ str(temp)
	cursor_obj.execute(my_query)
	
	row = cursor_obj.fetchall()[0][0]   # return list of tuples that is why [0][0]
	print(row)
	return row

#implementing fn testing

#deleting a row
#delete_row(con,id)

#inserting a url 
# insert_user_urls(con,"www.facebook.com")
# insert_user_urls(con,"www.youtube.com")

#actual url for a corresponding short url
#url_for_redirect(con,"3")

#CONFIGURING FLASK APP
from flask import Flask,request,render_template,redirect,url_for
app = Flask(__name__)

@app.route('/',methods = ['POST','GET'])
def home_page():
	#if method was get that means user just came to
	#form so let him most to us
	short_url = None
	if request.method == 'POST':
		url = request.form["url"]
		with sqlite3.connect("url_shortner_db.db") as con:
			short_url = insert_user_urls(con,url)
			short_url = "http://127.0.0.1:5000/" + short_url

		con.close()
		return render_template("index.html",short_url = short_url)

	return render_template("index.html",short_url = short_url)

@app.route('/<base62_str>/')
def redirect_user(base62_str):
	with sqlite3.connect("url_shortner_db.db") as con:
		main_url = url_for_redirect(con,base62_str)
	
	main_url = "http://" + main_url
	con.close()
	return redirect(main_url)

app.debug = True
app.run()


