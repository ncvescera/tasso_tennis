from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from app import *
from models import User
from forms import *
import requests


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html' , title='About')

@app.route('/register', methods=["GET", "POST"])
def register():
    # controlla se l'utente e' gia' autenticato
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))   # redirige alla pagina dashboard

    form = RegistrationForm()   # prepara il form di registrazione
    
    if form.validate_on_submit():
        # prende i dati del form
        user    = form.username.data
        pwd     = form.password.data
        name    = form.name.data
        surname = form.surname.data
        email   = form.email.data
        landowner = form.landowner.data
        confirm_pwd = form.confirm_password.data

        # vedo se esistono utenti con la stessa email o stesso username
        existing_user = User.query.filter_by(username=user).first()
        existing_email = User.query.filter_by(email=email).first()

        if not existing_user and not existing_email:
            if pwd == confirm_pwd:  # controlla che la password sia giusta
                hashed_password = bcrypt.generate_password_hash(pwd)    # creo la hash della password
                new_user = User(username=user, password=hashed_password, name=name, surname=surname, email=email,landowner=landowner) # creo il nuovo utente

                # aggiungo l'utente al database
                db.session.add(new_user)
                db.session.commit()

                flash(f'Account created for {form.username.data}!', 'success')  # crea il messaggio da stampare
                return redirect(url_for('home'))
            else:
                flash(f'Password and Confirm Password doesn\'t match !', 'danger')
        else:        
            if existing_user:
                flash(f'Username {form.username.data} alredy in use !', 'danger')

            if existing_email:
                flash(f'Email {form.email.data} alredy in use !', 'danger')

    return render_template('registration.html', title="Register", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()  # prepara il form di login

    # controlla se l'utente e' gia' autenticato
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))   # redirige alla pagina dashboard

    if form.validate_on_submit():
        # prende i dati del form
        email = form.email.data
        pwd   = form.password.data

        user = User.query.filter_by(email=email).first()    # cerca l'utente con la data email
        if user:
            # se trova l'utente controlla la password
            if bcrypt.check_password_hash(user.password, pwd):
                login_user(user)    # effettua il login
                flash('You have been logged in!', 'success')
                
                return redirect(url_for('dashboard'))
    
        flash('Login Unsucessful. Please check username and password', 'danger')
            
    return render_template('login.html', title="Login", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()   # effettua il logout
    flash('You have been logged out!', 'success')
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    # in base al tipo di utente fa vedere una dashboard diversa
    if current_user.landowner:
        return render_template('dashboard_lat.html', title="Dashboard")
    else:
        return render_template('dashboard_user.html', title="Dashboard")


@app.route('/addfield', methods=["GET", "POST"])
@login_required
def addfield():
    # controlla che l'utente sia un latifondista
    if current_user.landowner:
        form = AddFieldForm()   # prepara il form

        return render_template('addfield.html', title="Dashboard", form=form)
    else:
        return url_for('dashboard')


@app.route('/prenota', methods=["GET", "POST"])
@login_required
def prenota():
    # controlla che l'utente sia un utente normale
    if current_user.landowner == False:
        return render_template('prenota.html', title="Prenota")
    else:
        return url_for('dashboard')