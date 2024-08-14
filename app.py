from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Message
from datetime import datetime, timedelta
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)

online_users = set()


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def index():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and user.blocked_until and user.blocked_until > datetime.now():
            return redirect(url_for('blocked', username=user.username))
        messages = Message.query.order_by(Message.timestamp).all()
        return render_template('index.html', messages=messages)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter((User.email == login) | (User.username == login)).first()
        if user and user.check_password(password):
            session['username'] = user.username
            session['email'] = user.email
            session['is_admin'] = user.is_admin
            online_users.add(user.username)
            emit('online_count', len(online_users), broadcast=True, namespace='/')
            return redirect(url_for('index'))
        else:
            flash('Invalid login or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        online_users.discard(session['username'])
        emit('online_count', len(online_users), broadcast=True, namespace='/')
    session.pop('username', None)
    session.pop('email', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        join_room(session['username'])
        online_users.add(session['username'])
        emit('online_count', len(online_users), broadcast=True, namespace='/')

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session:
        leave_room(session['username'])
        online_users.discard(session['username'])
        emit('online_count', len(online_users), broadcast=True, namespace='/')

@socketio.on('message')
def handle_message(msg):
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and user.blocked_until and user.blocked_until > datetime.now():
            return
        new_message = Message(sender_id=user.id, content=msg)
        db.session.add(new_message)
        db.session.commit()
        emit('message', {'username': session['username'], 'message': msg}, broadcast=True, namespace='/')

@app.route('/admin')
def admin():
    if 'username' in session and session['is_admin']:
        users = User.query.all()
        messages = Message.query.order_by(Message.timestamp).all()
        return render_template('admin_chat.html', users=users, messages=messages)
    return redirect(url_for('index'))

@app.route('/block_user', methods=['POST'])
def block_user():
    if 'username' in session and session['is_admin']:
        user_id = request.form['user_id']
        hours = request.form['hours']
        reason = request.form['reason']
        user = User.query.get(user_id)
        if user:
            user.blocked_until = datetime.now() + timedelta(hours=int(hours))
            user.block_reason = reason
            db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    if 'username' in session and session['is_admin']:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
    return redirect(url_for('admin'))

@app.route('/make_admin/<int:user_id>')
def make_admin(user_id):
    if 'username' in session and session['is_admin']:
        user = User.query.get(user_id)
        if user:
            user.is_admin = True
            db.session.commit()
    return redirect(url_for('admin'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'username' in session and session['is_admin']:
        user = User.query.get(user_id)
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            if request.form['password']:
                user.set_password(request.form['password'])
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template('edit_user.html', user=user)
    return redirect(url_for('index'))

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'username' in session and session['is_admin']:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter((User.email == email) | (User.username == username)).first()
        if user:
            flash('Email or username already registered')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully')
    return redirect(url_for('admin'))

@app.route('/blocked/<username>')
def blocked(username):
    user = User.query.filter_by(username=username).first()
    if user and user.blocked_until and user.blocked_until > datetime.now():
        remaining_time = user.blocked_until - datetime.now()
        return render_template('blocked.html', user=user, remaining_time=remaining_time)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template('profile.html', user=user)
    return redirect(url_for('login'))

@app.route('/admin/chat')
def admin_chat():
    if 'username' in session and session['is_admin']:
        messages = Message.query.order_by(Message.timestamp).all()
        return render_template('admin_chat.html', messages=messages)
    return redirect(url_for('index'))

@app.route('/admin/users')
def admin_users():
    if 'username' in session and session['is_admin']:
        users = User.query.all()
        return render_template('admin_users.html', users=users)
    return redirect(url_for('index'))

if __name__ == '__main__':
    socketio.run(app, debug=True)