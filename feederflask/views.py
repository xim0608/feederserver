from flask import request, redirect, url_for, render_template, flash, abort, jsonify, session
from feederflask import app, db
from feederflask.models import User, Cataction, Waiting
from datetime import datetime, timedelta


# セッションの有効時間は５分
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


# ユーザーを表示（デバッグ用）
@app.route('/users/')
def user_list():
    users = User.query.all()
    return render_template('user/list.html', users=users)


# ユーザーの情報を表示
@app.route('/users/<int:user_id>/')
def user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('user/detail.html', user=user)


# ユーザーの情報を変更
@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
def user_edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'POST':
        user.name = request.form['name']
        user.catname = request.form['catname']
        user.email = request.form['email']
        user.password = request.form['password']
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user_id))
    return render_template('user/edit.html', user=user)


# ユーザーを作成
@app.route('/users/create/', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        user = User(name=request.form['name'], catname=request.form['catname'],
                    email=request.form['email'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('home'))
    return render_template('user/edit.html')


# ユーザーを削除
@app.route('/users/<int:user_id>/delete/', methods=['DELETE'])
def user_delete(user_id):
    user = User.query.get(user_id)
    if user is None:
        # アクセスしたユーザーidがデータベースに存在しなかった場合
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    elif session['user_id'] != user_id:
        # セッションがないor消そうとしているユーザーとアクセスしているユーザーが異なる場合
        response = jsonify({'status': 'You do not have permissions'})
        response.status_code = 403
        return response
    else:
        # セッション認証＆ユーザー存在
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'OK'})


# 全ユーザーのアクションを表示
@app.route('/action/')
def show_action():
    actions = Cataction.query.order_by(Cataction.actionid.desc()).all()
    return render_template('action/timeline.html', actions=actions)


# ユーザーIDで指定されたユーザーのアクションを表示
@app.route('/action/<int:user_id>/')
def show_action_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        # アクセスしたユーザーidがデータベースに存在しなかった場合
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    actions = Cataction.query.filter(Cataction.ownerid == user_id).order_by(Cataction.actionid.desc()).all()
    return render_template('action/timeline.html', actions=actions)


@app.route('/action/add/', methods=["GET", "POST"])
def add_action():
    if 'user_id' not in session:
        response = jsonify({'status': 'You do not have permissions'})
        response.status_code = 403
        return response
    owner_id = session['user_id']
    if request.method == "POST":
        cataction = Cataction(ownerid=owner_id, actiontime=(datetime.utcnow()+timedelta(hours=9)).strftime('%Y/%m/%d %H:%M:%S'))
        db.session.add(cataction)
        db.session.commit()
        return redirect(url_for('show_action'))
    return "You cannot add actions from this page...\nYou can only add from client app automatically."


@app.route('/feed/')
def feed():
    if 'user_id' not in session:
        response = jsonify({'status': 'You do not have permissions'})
        response.status_code = 403
        return response
    user_id = session['user_id']
    waited = Waiting.query.get(user_id)
    if not waited:
        waiting = Waiting(id=user_id)
        db.session.add(waiting)
        db.session.commit()
    else:
        return "すでにデータを送信済みです"
    return render_template('feed.html')


@app.route('/feed/delete/', methods=["DELETE"])
def delete_feed():
    if 'user_id' not in session:
        response = jsonify({'status': 'You do not have permissions'})
        response.status_code = 403
        return response
    user_id = session['user_id']
    waiting = Waiting.query.get(user_id)
    db.session.delete(waiting)
    db.session.commit()
    return "You cannot delete data from this page"


@app.route('/feed/check/')
def check_feed():
    if 'user_id' not in session:
        response = jsonify({'status': 'FORBIDDEN'})
        response.status_code = 403
        return response
    user_id = session['user_id']
    waiting = Waiting.query.get(user_id)
    if waiting:
        response = jsonify({'status': 'FOUND'})
        response.status_code = 302
        return response
    else:
        response = jsonify({'status': 'NOT FOUND'})
        response.status_code = 404
        return response


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user, authenticated = User.authenticate(db.session.query, request.form['email'], request.form['password'])
        if authenticated:
            session['user_id'] = user.id
            flash('You were logged in')
            return redirect(url_for('user_list'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('user_list'))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/howto')
def howto():
    return render_template('howto.html')