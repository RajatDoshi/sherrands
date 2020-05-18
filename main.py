#command to run the server
#FLASK_APP=main.py FLASK_ENV=development flask run --port 4071

from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import nexmo

client = nexmo.Client(key='332168c1', secret='IYB7GNSXl8HNtEMc')

app = Flask(__name__)
app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x81\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shoppingList.db' #change test.db name in the future
app.config['SQLALCHEMY_BINDS'] = {'logins': 'sqlite:///logins.db', 'productDataBase': 'sqlite:///productDataBase.db'}
db = SQLAlchemy(app)

approvedStoreList = ["Walmart", "Target", "Kroger"]

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	prodID = db.Column(db.Integer, default=0)
	user = db.Column(db.String(200))
	neighborhood = db.Column(db.String(200))
	content = db.Column(db.String(200))
	item = db.Column(db.String(200))
	desiredAmount = db.Column(db.String(200))
	pricePerUnit = db.Column(db.String(200))
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Task %r>' % self.id

class Logins(db.Model):
	__bind_key__ = 'logins'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(200))
	name = db.Column(db.String(200))
	email = db.Column(db.String(200))
	address = db.Column(db.String(200))
	neighborhood = db.Column(db.String(200))
	password = db.Column(db.String(200))

class Products(db.Model):
	__bind_key__ = 'productDataBase'
	id = db.Column(db.Integer, primary_key=True)
	prodStore = db.Column(db.String(200))
	prodName = db.Column(db.String(200))
	prodPrice = db.Column(db.Float, default=0.0)
	prodSize = db.Column(db.String(200))
	prodQuantity = db.Column(db.Integer, default=0)

# Shopping List Main Code
@app.route('/', methods=['POST', 'GET']) 
def index(): 
	if request.method == 'POST':
		if 'user' in session:
			curr_user = session['user']
			neighborhoodVal = int(session['neighborhood'][0])
		else:
			curr_user = 'Anonymous'
			neighborhoodVal = 00000
		store_info = request.form['content']
		item_info = request.form['item_info']
		quantity_info = request.form['quantity']
		price_info = 3.1

		new_entry = Todo(user=curr_user, content=store_info, neighborhood=neighborhoodVal, item=item_info, desiredAmount=quantity_info, pricePerUnit=price_info)
		try:
			db.session.add(new_entry)
			db.session.commit()
			return redirect('/')
		except Exception as e:
			return str(e)

	else:
		tasks = Todo.query.order_by(Todo.date_created).all()
		if 'user' in session:
			curr_user = session['user']
			return render_template('index.html', tasks=tasks, signInStatus="Sign Out", signUpStatus = "", neigh=session['neighborhood'][0], userNameForFilter=session['user'], approvedStoreList=approvedStoreList)
		else:
			return render_template('index.html', tasks=tasks, signInStatus="Sign In", signUpStatus = "Sign Up", neigh=0, userNameForFilter='Anonymous', approvedStoreList=approvedStoreList)


#Local Inventory Management Code
@app.route('/addItems', methods=['POST', 'GET']) 
def addItems():
	if request.method == 'POST':
		prodStore = request.form['store']
		prodName = request.form['name']
		prodPrice = request.form['price']
		prodSize = request.form['size']
		prodQuantity = request.form['quantity']
		prod_var = Products(prodStore=prodStore, prodName=prodName, prodPrice=float(prodPrice), prodSize=prodSize, prodQuantity=int(prodQuantity))
		try:
			db.session.add(prod_var)
			db.session.commit()
			return redirect('/addItems')
		except Exception as e:
			return str(e)

	if request.method == 'GET':
		tasks = Products.query.order_by(Products.prodStore).all()
		if 'user' in session:
			curr_user = session['user']
			return render_template('addItem.html', tasks=tasks, signInStatus="Sign Out", signUpStatus = "", neigh=session['neighborhood'][0], userNameForFilter=session['user'], approvedStoreList=approvedStoreList)
		else:
			return render_template('addItem.html', tasks=tasks, signInStatus="Sign In", signUpStatus = "Sign Up", neigh=0, userNameForFilter='Anonymous', approvedStoreList=approvedStoreList)


@app.route('/lookUpItem', methods=['POST', 'GET']) 
def lookUpItem():
	if request.method == 'POST':
		tasks = Products.query.order_by(Products.prodStore).all()
		searchStore = request.form['content']
		qntyWanted = int(request.form['quantity'])
		initItem = request.form['item_info']
		if 'user' in session:
			curr_user = session['user']
			return render_template('lookUp.html', tasks=tasks, signInStatus="Sign Out", signUpStatus = "", approvedStoreList=approvedStoreList, searchStore=searchStore, qntyWanted=qntyWanted, initItem=initItem)
		else:
			return render_template('lookUp.html', tasks=tasks, signInStatus="Sign In", signUpStatus = "Sign Up", approvedStoreList=approvedStoreList, searchStore=searchStore, qntyWanted=qntyWanted, initItem=initItem)
	else:
		return "GET REQ"

@app.route('/addToList/<int:id>/<int:qnty>')
def addToList(id, qnty):
	if 'user' in session:
		curr_user = session['user']
		neighborhoodVal = int(session['neighborhood'][0])
	else:
		curr_user = 'Anonymous'
		neighborhoodVal = 00000

	prod = Products.query.get_or_404(id)
	prod.prodQuantity -= qnty
	db.session.commit()
	prod_var = Todo(prodID=id, user=curr_user, content=prod.prodStore, neighborhood=neighborhoodVal, item=prod.prodName, desiredAmount=qnty, pricePerUnit=prod.prodPrice)
	try:
		db.session.add(prod_var)
		db.session.commit()
		return redirect('/')
	except Exception as e:
		return str(e)


#Delete Product Inventory and Shopping List Item
@app.route('/deleteProd/<int:id>')
def deleteProd(id):
	prod = Products.query.get_or_404(id)

	try:
		db.session.delete(prod)
		db.session.commit()
		return redirect('/addItems')
	except:
		return "There was a problem in deleting that item"


@app.route('/delete/<int:id>')
def delete(id):
	task = Todo.query.get_or_404(id)

	try:
		db.session.delete(task)
		db.session.commit()
	except:
		return "There was a problem in deleting that item"
	
	task2 = Products.query.get_or_404(task.prodID)
	task2.prodQuantity = task2.prodQuantity + int(task.desiredAmount)
	try:
		db.session.commit()
		return redirect('/')
	except:
		return 'There was an issue with your update'

	return redirect('/')


#Update Product Inventory or Shopping List Code
@app.route('/updateProd', methods=["POST"])
def updateProd():
	idVAL = int(request.form['taskID'])
	task = Products.query.get_or_404(idVAL)
	# task.prodStore =  request.form['store']
	task.prodName = request.form['name']
	task.prodPrice = float(request.form['price'])
	task.prodSize = request.form['size']
	task.prodQuantity = int(request.form['quantity'])
	try:
		db.session.commit()
		return redirect('/addItems')
	except:
		return 'There was an issue with your update'



@app.route('/update', methods=["POST"])
def update():
	idVAL = int(request.form['taskID'])
	origQty=int(request.form['origQty'])
	task = Todo.query.get_or_404(idVAL)

	# task.content =  request.form['content']
	# task.item = request.form['item_info']
	task.desiredAmount = request.form['quantity']
	try:
		db.session.commit()
	except:
		return 'There was an issue with your update'

	task2 = Products.query.get_or_404(task.prodID)
	task2.prodQuantity = task2.prodQuantity + origQty - int(task.desiredAmount)
	try:
		db.session.commit()
		return redirect('/')
	except:
		return 'There was an issue with your update'
	# else:
	# 	return render_template('update.html', tasks=task, approvedStoreList=approvedStoreList)


#Sign In/ Sign Up Pipeline Code
@app.route('/process_signup', methods=['POST', 'GET']) 
def process_signup():
	if request.method == 'POST':
		uname = request.form['username']
		name = request.form['name']
		email_info = request.form['email']
		addy = request.form['address']
		zip_code = request.form['zipcode']
		password_info = request.form['password']
		repeat_pass = request.form['psw-repeat']
		if not password_info == repeat_pass:
			return "passwords don't match"
		login_var = Logins(username=uname, name=name, email=email_info, address=addy, neighborhood=zip_code, password=password_info)
		try:
			db.session.add(login_var)
			db.session.commit()
		except Exception as e:
			return str(e)
		return redirect('/signin')
	else:
		return "GET REQUEST TO PROCESS SIGNUP"


@app.route('/signup', methods=['POST', 'GET']) 
def signup():
	if request.method == 'POST':
		return "POST COMMAND TO signup"
	else:
		return render_template('createAccount.html')

@app.route('/signin', methods=['POST', 'GET']) 
def signin():
	if request.method == 'POST':
		if 'user' in session:
			del session['user']
			del session['address']
		uname = request.form['uname']
		password_info = request.form['psw']
		related_password = db.session.query(Logins.password).filter_by(username=uname).first()
		if (not related_password == None) and password_info == related_password[0]:
			related_address = db.session.query(Logins.address).filter_by(username=uname).first()
			session['user'] = uname
			session['address'] = related_address
			related_neighborhood = db.session.query(Logins.neighborhood).filter_by(username=uname).first()
			session['neighborhood'] = related_neighborhood
			return redirect('/')
		return render_template('signin.html', errorMessage="Wrong Password or Username")
	else:
		return render_template('signin.html')

@app.route('/signout', methods=['GET']) 
def sign_out():
	if 'user' not in session:
		return redirect('/')
	del session['user']
	del session['address']
	del session['neighborhood']
	return redirect('/')


#Send Message to User
@app.route('/sendMessage', methods=['POST', 'GET']) 
def sendMessage():
	print("bro")
	if 'user' not in session:
		return redirect('/signin')
	curr_user = session['user']
	jsdata = request.form['javascript_data']
	going_to_store = str(jsdata)
	# going_to_store = "Walmart"
	curr_neighborhood = session['neighborhood'][0]
	usersInNeighborhood = db.session.query(Logins).filter_by(neighborhood=curr_neighborhood).all()
	res = {}
	for login in usersInNeighborhood:
		itemList = db.session.query(Todo).filter_by(user=login.username).all()
		for item in itemList:
			if item.content == going_to_store:
				temp = "Buy " + item.desiredAmount + " " + item.item + " @ $" + item.pricePerUnit
				if not login.username in res:
					res[login.username] = [temp]
				else:
					res[login.username].append(temp)
	#twilio
	# response = client.send_message({'from': '17324199309','to': '14046637639','text': str(res)})
	return res

# main driver function 
if __name__ == '__main__':   
	app.run(debug=True) 