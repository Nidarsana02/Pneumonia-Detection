from flask import Flask, render_template, url_for, request, redirect, session
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError, EqualTo
import bcrypt
import MySQLdb.cursors
import re
import mysql.connector

app= Flask(__name__)#, template_folder='E:\Lung-Disease-Detection-Team4\Front-end\Templates')
app.secret_key = 'your_secret_key'

db_config = {
    'host': "localhost",
    'user': "root",
    'password': "d@tBAs#55",
    'database': "pneumonia",
}


mysql = MySQL(app)

class RegisterForm(FlaskForm):
     user_name= StringField("Username",validators=[DataRequired()],render_kw={"placeholder": "Username"})
     user_id= StringField("id",validators=[DataRequired()],render_kw={"placeholder": "id"})
     user_pass= PasswordField("Password",validators=[DataRequired()],render_kw={"placeholder": "Password"})
     user_conf_pass= PasswordField("Confirm Password",validators=[DataRequired(),
                         EqualTo('user_pass', message='Passwords must match.')],render_kw={"placeholder": "Confirm Password"})
     user_role= RadioField("Role", choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')], validators=[DataRequired()])
     submit= SubmitField("Register")

     def validate_user_id(self,field):
          cursor = mysql.connection,cursor()
          cursor.execute("SELECT * FROM user WHERE id=%s",(field.data))
          user = cursor.fetchone()
          cursor.close()
          if user:
               raise ValidationError('id already taken')

class LoginForm(FlaskForm):
     user_id= StringField("id",validators=[DataRequired()],render_kw={"placeholder": "Username"})
     user_pass= PasswordField("Password",validators=[DataRequired()],render_kw={"placeholder": "id"})
     submit = SubmitField("Login")

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
         user_name = form.user_name.data
         user_id = form.user_id.data
         user_pass = form.user_pass.data
         user_role = form.user_role.data

         hashed_user_pass = bcrypt.hashpw(user_pass.encode('utf-8'),bcrypt.gensalt())

         cursor = mysql.connection.cursor()
         cursor.execute("INSERT INTO users (user_name,user_id,user_pass,user_role) VALUES (%s,%s,%s,%s)",(user_name,user_id,hashed_user_pass,user_role))
         mysql.connection.commit()
         cursor.close()

         return redirect(url_for('plogreg'))
    
    if 'user_pass' in form.errors:
        return render_template('register.html', form=form, error="passwords donot match. Please try again")
    if 'user_id' in form.errors:
        return render_template('register.html', form=form, error="id already exist. Please choose a different one.")


    
    return render_template('register.html',form=form)
    

@app.route('/login', methods= ['GET', 'POST'])
def login():
     form = LoginForm()
     if form.validate_on_submit():
        user_id = form.user_id.data
        user_pass = form.user_pass.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s",(user_id))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(user_pass.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('plogreg'))
        else:
            return render_template('login.html', form=form, error="incorrect id or password")

            

     return render_template('login.html',form=form)

@app.route('/plogreg', methods=['GET', 'POST'])
def postlogreg():
     if 'user_id' in session:
        user_id = session['user_id']
        user_name = session['user_name']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where user_id=%s and user_name=%s ",(user_id,user_name))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('plogreg.html',user=user)
            
     return redirect(url_for('login'))

     
@app.route('/NurseUpdate')
def NurseUpdate():
    return render_template('NurseUpdate.html')

@app.route('/Receptionist')
def Receptionist():
    return render_template('Receptionist.html')

@app.route('/add', methods=['POST'])
def add():
    pt_id = request.form.get('pt_id')
    pt_age = request.form.get('pt_age')
    pt_gender = request.form.get('pt_gender')
    at_name = request.form.get('at_name')
    at_mob = request.form.get('at_mob')

    print(f"Received: pt_id={pt_id}, pt_age={pt_age}, pt_gender={pt_gender}, at_name={at_name}, at_mob={at_mob}")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO patient (pt_id, pt_age, pt_gender, at_name, at_mob) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (pt_id, pt_age, pt_gender, at_name, at_mob))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
            print(f"Error: {err}")
            return "Error storing data"

    return redirect(url_for('NurseUpdate'))

@app.route('/submit', methods=['POST'])
def submit():
    treat_doc_id = request.form.get('treat_doc_id')
    room_no = request.form.get('room_no')
    bed_no = request.form.get('bed_no')
    rythm = request.form.get('rythm')
    heart_rate = request.form.get('heart_rate')
    temp = request.form.get('temp')
    sbp = request.form.get('sbp')
    dbp = request.form.get('dbp')
    resp_rate = request.form.get('resp_rate')
    oxy_sat = request.form.get('oxy_sat')

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO NurseUpdate (treat_doc_id, room_no, bed_no, rythm, heart_rate, temp, sbp, dbp, resp_rate,oxy_sat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (treat_doc_id, room_no, bed_no, rythm, heart_rate, temp, sbp, dbp, resp_rate,oxy_sat))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
            print(f"Error: {err}")
            return "Error storing data"

    return redirect(url_for('NurseUpdate'))

if __name__ == '__main__':
    app.run(debug=True)