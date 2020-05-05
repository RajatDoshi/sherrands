#FLASK_APP=main.py FLASK_ENV=development flask run --port 4047
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_BINDS'] = {'logins': 'sqlite:///logins.db'}
db = SQLAlchemy(app)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
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
	first_name = db.Column(db.String(200))
	last_name = db.Column(db.String(200))
	email = db.Column(db.String(200))
	address = db.Column(db.String(200))
	password = db.Column(db.String(200))

@app.route('/', methods=['POST', 'GET']) 
def index(): 
    if request.method == 'POST':
        store_info = request.form['content']
        item_info = request.form['item_info']
        quantity_info = request.form['quantity']
        price_info = request.form['price']

        new_entry = Todo(content=store_info, item=item_info, desiredAmount=quantity_info, pricePerUnit=price_info)
        try:
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/')
        except Exception as e:
        	return str(e)

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/process_signup', methods=['POST', 'GET']) 
def process_signup():
	if request.method == 'POST':
		uname = request.form['username']
		fname = request.form['first_name']
		lname = request.form['last_name']
		email_info = request.form['email']
		addy = request.form['address']
		password_info = request.form['password']
		repeat_pass = request.form['psw-repeat']
		if not password_info == repeat_pass:
			return "passwords don't match"
		login_var = Logins(username=uname, first_name=fname, last_name=lname, email=email_info, address=addy, password=password_info)
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
		uname = request.form['uname']
		password_info = request.form['psw']
		related_password = db.session.query(Logins.password).filter_by(username=uname).first()
		if (not related_password == None) and password_info == related_password[0]:
			return redirect('/')
		return render_template('signin.html')
	else:
		return render_template('signin.html')

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