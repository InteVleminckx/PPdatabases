# TUTORIAL Len Feremans, Sandy Moens and Joey De Pauw
# see tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
from flask import Flask, request, session, jsonify, flash, redirect, url_for
from flask.templating import render_template

from config import config_data
from db_connection import DBConnection
from user_data_acces import DataScientist, UserDataAcces

from werkzeug.security import generate_password_hash, check_password_hash

# INITIALIZE SINGLETON SERVICES
app = Flask('Tutorial ')
app.secret_key = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'
app_data = dict()
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
user_data_access = UserDataAcces(connection)

DEBUG = False
HOST = "127.0.0.1" if DEBUG else "0.0.0.0"


# REST API
# See https://www.ibm.com/developerworks/library/ws-restful/index.html
# @app.route('/quotes', methods=['GET'])
# def get_quotes():
#     # Lookup row in table Quote, e.g. 'SELECT ID,TEXT FROM Quote'
#     quote_objects = quote_data_access.get_quotes()
#     # Translate to json
#     return jsonify([obj.to_dct() for obj in quote_objects])
#
#
# @app.route('/quotes/<int:id>', methods=['GET'])
# def get_quote(id):
#     # ID of quote must be passed as parameter, e.g. http://localhost:5000/quotes?id=101
#     # Lookup row in table Quote, e.g. 'SELECT ID,TEXT FROM Quote WHERE ID=?' and ?=101
#     quote_obj = quote_data_access.get_quote(id)
#     return jsonify(quote_obj.to_dct())
#
#
# # To create resource use HTTP POST
# @app.route('/quotes', methods=['POST'])
# def add_quote():
#     # Text value of <input type="text" id="text"> was posted by form.submit
#     quote_text = request.form.get('text')
#     quote_author = request.form.get('author')
#     # Insert this value into table Quote(ID,TEXT)
#     quote_obj = Quote(iden=None, text=quote_text, author=quote_author)
#     print('Adding {}'.format(quote_obj.to_dct()))
#     quote_obj = quote_data_access.add_quote(quote_obj)
#     return jsonify(quote_obj.to_dct())


#----------------- VIEW -----------------#
@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html', app_data=app_data)

@app.route("/contact")
def contact():
    return render_template('contact.html', app_data=app_data)

@app.route("/services")
def services():
    return render_template('services.html', app_data=app_data)

@app.route("/datasets")
def datasets():
    return render_template('datasets.html', app_data=app_data)

@app.route("/visualizations")
def visualizations():
    return render_template('visualizations.html', app_data=app_data)

#----------------- User_DB -----------------#
@app.route("/login", methods=['GET'])
def login():

    user_objects = user_data_access.get_users()
    return render_template('login.html', app_data=app_data)


@app.route("/login/<string:email>", methods=['GET'])
def get_user(username):
    user_object = user_data_access.get_user(username)

    return jsonify([user_object.to_dct()])


@app.route("/register", methods=['POST'])
def add_user():
    user_firstname = request.form.get('firstname')
    user_lastname = request.form.get('lastname')
    user_username = request.form.get('username')
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    user = DataScientist.query.filter_by(email=user_email).first

    # some basic checks (if they trigger, they 'flash' a message on the page (see the login.html doc))
    if user: # check to see if user with the email already exists in the database
        flash('This email already exists.', category='error')
    elif len(user_firstname) < 1:
        flash('First name cannot be empty.', category='error')
    elif len(user_lastname) < 1:
        flash('Last name cannot be empty.', category='error')
    elif len(user_username) < 1:
        flash('Username cannot be empty.', category='error')
    elif len(user_email) < 1:
        flash('E-mail cannot be empty.', category='error')
    elif len(user_password) < 1:
        flash('Password cannot be empty.', category='error')
    else:
        user_obj = DataScientist(firstname=user_firstname, lastname=user_lastname, username=user_username, email=user_email, password=generate_password_hash(user_password, method='sha256'))
        print('Adding {}'.format(user_obj.to_dct()))
        user_obj = user_data_access.add_user(user_obj)

        flash('Account succesfully registered!', category='success')

        return redirect(url_for('main'))

    return render_template('login.html', app_data=app_data)

@app.route("/login", methods=['POST'])
def login_user():
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    user = DataScientist.query.filter_by(email=user_email).first
    if user:
        if check_password_hash(user.password, user_password):
            flash('Logged in successfully!', category='success')
            return redirect(url_for('main'))
        else:
            flash('Incorrect password, try again.', category='error')
    else:
        flash('Email does not exist.', category='error')

    # user_obj = DataScientist(firstname=user_firstname, lastname=user_lastname, username=user_username, email=user_email, password=generate_password_hash(user_password, method='sha256'))
    # print('Adding {}'.format(user_obj.to_dct()))
    # user_obj = user_data_access.add_user(user_obj)

    # return redirect(url_for('home'))

    return render_template('login.html', app_data=app_data)

# @app.route("/show_quotes")
# def show_quotes():
#     quote_objects = quote_data_access.get_quotes()
#     # Render quote_objects "server-side" using Jinja 2 template system
#     return render_template('quotes.html', app_data=app_data, quote_objects=quote_objects)
#
#
# @app.route("/show_quotes_ajax")
# def show_quotes_ajax():
#     # Render quote_objects "server-side" using Jinja 2 template system
#     return render_template('quotes_ajax.html', app_data=app_data)


# RUN DEV SERVER
if __name__ == "__main__":
    app.run(HOST, debug=True)
