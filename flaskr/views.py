# flaskr/views.py

from flask import request, redirect, url_for, render_template, flash, abort, jsonify, session
from flaskr import app, db
from flaskr.models import User

@app.route('/users/')
def user_list():
    users = User.query.all()
    return render_template('user/list.html', users=users)

@app.route('/users/<int:user_id>/')
def user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('user/detail.html', user=user)

@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
def user_edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = request.form['password']
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user_id))
    return render_template('user/edit.html', user=user)

@app.route('/users/create/', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        user = User(name=request.form['name'], email=request.form['email'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_list'))
    return render_template('user/edit.html')

@app.route('/users/<int:user_id>/delete/', methods=['DELETE'])
def user_delete(user_id):
    user = User.query.get(user_id)
    if user is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'OK'})

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == 'POST':
        user, authenticated = User.authenticate(db.session.query, request.form['email'], request.form['password'])
        if authenticated:
            session['user_id'] = user.id
            flash('You were logged in')
            return redirect(url_for('show_feed'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('show_feed'))

# @app.route('/login', methods=["GET", "POST"])
# def login():
#     form = EmailPasswordForm()
#     if form.validate_on_submit():
#         #Check Password and login
#         user = User(
#             email=form.email.data,
#             password=form.password.data
#         )
#         return redirect(url_for('index'))
#     return render_template('login.html', form=form)
#
#
# @app.route('/signin', methods=["GET", "POST"])
# def signin():
#     form = UsernamePasswordForm()
#
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first_or_404()
#         if user.is_collect_password(form.password.data):
#             login_user(user)
#
#
# @app.route('/signout')
# def signout():
#     logout_user()


@app.route('/')
def home():
    return render_template('index.html')