import os
from flask import Flask, render_template,flash,session,redirect,logging,url_for,request,send_from_directory
from flaskext.mysql import MySQL
from functools import wraps
from wtforms import Form, StringField,TextAreaField,PasswordField, validators
from wtforms.fields.html5 import EmailField
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, IMAGES
import time
#from flask_wtf.file import FileField, FileRequired, FileAllowed
#from werkzeug.utils import secure_filename

#from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQL()


photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/account'
configure_uploads(app, photos)


app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'Dnjeri'
app.config['MYSQL_DATABASE_PASSWORD'] = 'adan'
app.config['MYSQL_DATABASE_DB'] = 'overflow'
#app.config['MYSQL_DATABASE_CHARSET'] = 'utf-8'

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

#db = SQLAlchemy(app)

mysql.init_app(app)
conn=mysql.connect()
cursor = conn.cursor()

@app.route('/')
def index():
	return redirect( '/all_questions' )


class RegisterForm(Form):
	fname = StringField('first Name',[validators.Length(min=1, max=50)])
	lname = StringField('last Name',[validators.Length(min=1, max=50)])
	username = StringField('username',[validators.Length(min=5, max=50)])
	email = EmailField('email',[validators.Length(min=1, max=50)])
	#image = FileField(validators=[FileAllowed(u'Image Only!'), FileRequired(u'Choose a file!')])
	password  = PasswordField('password',[
		validators.DataRequired(),
		validators.EqualTo('confirm',message="password mismatch")
		])
	confirm = PasswordField('confirm password')

	
# signup
@app.route( '/auth/signup', methods=['GET','POST'] )
def signup():
	form =RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		fname= form.fname.data 
		lname= form.lname.data
		username = form.username.data
		email = form.email.data
		accountimage = request.files['accountimage']
		filename = photos.save( accountimage )
		password= bcrypt.generate_password_hash(form.password.data)
		
		image='account/'+filename
		

		cursor.execute("INSERT INTO users (username,fname,lname,email,image,password) values(%s,%s,%s,%s,%s,%s)",(username,fname,lname,email, image,password)) 
		print('there')
		conn.commit()
		flash("Registered successfully","Success")
		return redirect( url_for('signin') )
		#cursor.close()

		# END : if - request-method post -- form valid

	return render_template('register.html',form=form)
	

class LoginForm(Form):
	email = EmailField('email',[validators.Length(min=7, max=50)])
	password  = PasswordField('password',[validators.DataRequired()])
	

# signin
@app.route( '/auth/login',methods=['GET','POST'] )
def signin():
	form = LoginForm(request.form) 
	if request.method == 'POST' and form.validate():
		email = form.email.data
		password= form.password.data

		result = cursor.execute("SELECT * FROM  users WHERE email= %s",(email))
		if result > 0:
			data = cursor.fetchone()
			print( data )
			passwordc = data[7]
			print( '\nFrom database :: %s' % passwordc)
			print( 'From form :: %s' % password)
			newpwd = password.encode('utf-8')
			if bcrypt.check_password_hash(passwordc, newpwd ) :
				print( 'Password check SUCCESS\n' )
				session['logged_in'] = True
				session['username'] = data[1]
				session['user_id'] = data[0]
				print('true')
				return redirect(url_for('index'))
			else:
				error='Password does not match username'
				print('FAILED - invalid password')
		else:
				error='The email does not exist. Register'
				print('false missing')
    #cursor.close()
	return render_template('login.html',form=form)


def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unathorized, Please login','danger')
			return redirect(url_for('signin'))
	return wrap

class QuestionForm(Form):
	question = TextAreaField('question',[validators.DataRequired()])
	question_title = StringField(' question title',[validators.Length(min=7, max=100)])
	tags = StringField('Tags',[validators.Length(min=10, max=150)])

@app.route('/questions',methods=['GET', 'POST'])
@is_logged_in
def postQn():
	form = QuestionForm(request.form) 
	if request.method == 'POST' and form.validate():
		question = form.question.data
		title = form.question_title.data
		tags = form.tags.data
		user_id = 13
		timestr = time.strftime("%Y%m%d-%H%M%S")
		image =request.files['image']
		#os.rename(image,timestr+image)
		filename = photos.save(image)
		imagery = 'templates/account/'+filename


		cursor.execute("INSERT INTO questions (title,question,tags,image,user_id) values(%s,%s,%s,%s,%s)",(title,question,tags,imagery,user_id)) 
		conn.commit()
		flash("Question Posted successfully","Success")

		return redirect(url_for('allQn'))
	return render_template( 'post_question.html',form=form )

# allQn - view all questions 
@app.route('/all_questions')
def allQn():
	result = cursor.execute("SELECT * FROM  questions")
	if result > 0:
			data = cursor.fetchall()
	return render_template( 'view_all_questions.html',datas=data )


class AnswerForm(Form):
	answer = TextAreaField('Answer',[validators.DataRequired()])

# oneQn - view one questions 
@app.route( '/view_question/<quiz_id>', methods=['GET','POST'] )
@is_logged_in
def viewQn(quiz_id):
	print( '\n\tprocessing question data.\n' )
	print( '...received question-id :: %s .\n' % quiz_id )
	
	quiz_id = quiz_id
	form = AnswerForm(request.form)

	answersquery = cursor.execute( "SELECT * FROM  answer WHERE question_id=%s",(quiz_id) )
	 # answer,user_id
	if answersquery:
		print( 'SUCCESS [cursor.excute--select *]' )
		fetchedAnswers = cursor.fetchall()

		answerData = {}

		for answer in fetchedAnswers:
			#print( answer )
			answerId = answer[0]
			answerBody = answer[1]
			answerQnId = answer[2]
			answerBy = answer[3]
			answerUpVotes = answer[4]
			answerDownVotes = answer[5]
			answerStatus = answer[6]
			#print( 'ID[ %s ]-body[ %s ]-QnId[ %s ]-ById[ %s ]-UpV[ %s ]-DownV[ %s ]-Status[ %s ]' % ( answerId,answerBody,answerQnId,answerBy,answerUpVotes,answerDownVotes,answerStatus ) )
			answerData[ answerId ] = []
			answerData[ answerId ].append( answerBody )
			answerData[ answerId ].append( answerStatus )

			# get data of user who answered the question
			userdata = cursor.execute( "SELECT id,username,image FROM  users WHERE id= %s", ( answerBy ) )
			if userdata:
				print( 'userdata SUCCESS [cursor.excute--select *]' )
				userRecord = cursor.fetchone()
				for det in userRecord:
					answerData[ answerId ].append( det )
					# END : for
			else:
				print( 'userdata [cursor.excute--select *] FAILED' )
				# END : if - userdata
			# END : for
	else:
		answerData = {}
		# END : if - answersquery
	print( '\n' )
	print( answerData )
	current_user = session['user_id']


	"""
	dict_ans = {}
	questiondata = {}
	current_user = session['user_id']
	allanswers = cursor.execute("SELECT answer,user_id FROM  answer ") # answer,user_id
	if allanswers > 0:
		majibu = cursor.fetchall()
		dict_ans['answers'] = majibu
		users =[]

		for jibu in majibu:
			answered_by = jibu[1]
			theanswer = jibu[0]
			print( '\tanswered_by :: %s .' % answered_by )
			print( '\tfield :: %s .' % theanswer )

			questiondata[ theanswer ] = []

			# get data of user who answered the question
			userdata = cursor.execute( "SELECT username,image FROM  users WHERE id= %s", ( answered_by ) )
			if userdata > 0:
				ans = cursor.fetchone()
				for det in ans:
					questiondata[ theanswer ].append( det )
					# END : for
				users.append(ans)
			else:
				print( 'data of user(the answerer) not found' )


			# end: for

		print( '\n' )
		print( questiondata )
				
		#print(users)
	else:
		print( 'answer data not found' )
		# END : if
	print( '\n' )

	dict_ans['users'] = users
	"""



	result = cursor.execute("SELECT * FROM  questions WHERE id= %s",(quiz_id))
	if result > 0:
		datas = cursor.fetchone()
		use_id = datas[5]
	users = cursor.execute("SELECT * FROM  users WHERE id= %s",(use_id))
	if users > 0:
		user = cursor.fetchone()


	if request.method == 'POST' and form.validate():
		curr_user = session['user_id']
		quiz_id =datas[0]
		status = "not_accepted"
		answerd=form.answer.data

		cursor.execute("INSERT INTO answer (answer,question_id,user_id,status) values(%s,%s,%s,%s)",(answerd,quiz_id,curr_user,status)) 
		conn.commit()
		flash("Answer Posted successfully","Success")

	return render_template( 'question.html', **locals() )





@app.route('/question/<quiz_id>/answer/<anw_id>')
def acceptanswer(quiz_id, anw_id):
	pass

@app.route('/answer/<answer_id>/<quiz_id>', methods=['GET','POST'] )
def delUser(answer_id=None, quiz_id=None):
	status="accepted"
	cursor.execute("UPDATE answer  SET status=%s WHERE id=%s",(status,answer_id))
	conn.commit()
	return redirect('view_question/'+quiz_id)
	#pass
@app.route('/delete/<quiz_id>')
def delete(quiz_id):
	cursor.execute("DELETE FROM questions WHERE id=%s",(quiz_id))
	conn.commit()
	return redirect(url_for('allQn'))

@app.route('/logout')
def logout():
	session.clear()
	flash("You are now logged out","Success")
	return redirect(url_for('signin'))

if __name__=='__main__':
	app.secret_key ='secret123'
	app.run( debug=True )