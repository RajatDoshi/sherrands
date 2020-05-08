#command to run the server
#FLASK_APP=main.py FLASK_ENV=development flask run --port 4050

from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import nexmo

client = nexmo.Client(key='332168c1', secret='IYB7GNSXl8HNtEMc')

app = Flask(__name__)
app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x81\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_BINDS'] = {'logins': 'sqlite:///logins.db'}
db = SQLAlchemy(app)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
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

# @app.route('/', defaults={'user': 'Anonymous'})
@app.route('/', methods=['POST', 'GET']) 
def index(): 
	if request.method == 'POST':
		if 'user' in session:
			curr_user = session['user']
			neighborhoodVal = int(session['neighborhood'][0])
			print("bro", neighborhoodVal)
		else:
			curr_user = 'Anonymous'
			neighborhoodVal = 00000
		store_info = request.form['content']
		item_info = request.form['item_info']
		quantity_info = request.form['quantity']
		price_info = request.form['price']

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
			return render_template('index.html', tasks=tasks, signInStatus="Sign Out", signUpStatus = "", neigh=session['neighborhood'][0], userNameForFilter=session['user'])
		else:
			return render_template('index.html', tasks=tasks, signInStatus="Sign In", signUpStatus = "Sign Up", neigh=0, userNameForFilter='Anonymous')

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

@app.route('/sendMessage', methods=['POST', 'GET']) 
def sendMessage():
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
	response = client.send_message({'from': '17324199309','to': '14046637639','text': str(res)})
	return res

@app.route('/delete/<int:id>')
def delete(id):
	task_to_delete = Todo.query.get_or_404(id)

	try:
		db.session.delete(task_to_delete)
		db.session.commit()
		return redirect('/')
	except:
		return "There was a problem in deleting that item"

@app.route('/update/<int:id>', methods=["POST", "GET"])
def update(id):
	task = Todo.query.get_or_404(id)
	if request.method == 'POST':
		task.content =  request.form['content']
		task.item = request.form['item_info']
		task.desiredAmount = request.form['quantity']
		task.pricePerUnit = request.form['price']
		try:
			db.session.commit()
			return redirect('/')
		except:
			return 'There was an issue with your update'
	else:
		return render_template('update.html', tasks=task)

# main driver function 
if __name__ == '__main__':   
	app.run(debug=True) 