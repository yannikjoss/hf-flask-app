from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
#from urllib.parse import url_parse, urlunparse # wird nicht genutzt
from app import db
from models import User, Post, Comment
from datetime import datetime
import secrets
from functools import wraps
from forms import CommentForm

routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/')
@routes_blueprint.route('/index')
@login_required
def index():
    posts = current_user.followed_posts().paginate(page=request.args.get('page', 1), per_page=10)
    return render_template('index.html', title='Startseite', posts=posts)


@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Ungültiger Benutzername oder Passwort', 'danger') # Kategorie hinzugefügt
            return redirect(url_for('routes.login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        # request.host_url to check if next_page is a relative URL => fix für relogin bug
        if next_page and next_page.startswith(('http://', 'https://')):
            return redirect(next_page)
        else:
            return redirect(url_for('routes.index'))
    return render_template('login.html', title='Anmelden')


@routes_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))


@routes_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Benutzername bereits vergeben.', 'warning') # Kategorie hinzugefügt
            return redirect(url_for('routes.register'))
        if User.query.filter_by(email=email).first():
            flash('Email bereits registriert.', 'warning') # Kategorie hinzugefügt
            return redirect(url_for('routes.register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Herzlichen Glückwunsch, Sie sind nun registriert!', 'success') # Kategorie hinzugefügt
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Registrieren')


@routes_blueprint.route('/user/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page=request.args.get('page', 1), per_page=5)
    return render_template('profile.html', user=user, posts=posts)


@routes_blueprint.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.profile_bio = request.form['bio']
        db.session.commit()
        flash('Ihr Profil wurde aktualisiert.', 'info') # Kategorie hinzugefügt
        return redirect(url_for('routes.edit_profile'))
    return render_template('edit_profile.html', title='Profil bearbeiten')


@routes_blueprint.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('Sie können sich nicht selbst folgen!', 'warning') # Kategorie hinzugefügt
        return redirect(url_for('routes.user_profile', username=username))
    if current_user.is_following(user):
        flash(f'Sie folgen {username} bereits.', 'info') # Kategorie hinzugefügt
        return redirect(url_for('routes.user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'Sie folgen nun {username}!', 'success') # Kategorie hinzugefügt
    return redirect(url_for('routes.user_profile', username=username))


@routes_blueprint.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('Sie können sich nicht selbst entfolgen!', 'warning') # Kategorie hinzugefügt
        return redirect(url_for('routes.user_profile', username=username))
    if not current_user.is_following(user):
        flash(f'Sie folgen {username} nicht.', 'info') # Kategorie hinzugefügt
        return redirect(url_for('routes.user_profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'Sie folgen {username} nun nicht mehr.', 'info') # Kategorie hinzugefügt
    return redirect(url_for('routes.user_profile', username=username))


@routes_blueprint.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        post = Post(body=request.form['post'], author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Ihr Post wurde veröffentlicht!', 'success') # Kategorie hinzugefügt
        return redirect(url_for('routes.index'))
    return render_template('new_post.html', title='Neuer Post')

@routes_blueprint.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Ihr Kommentar wurde veröffentlicht!', 'success') # Kategorie hinzugefügt
        return redirect(url_for('routes.post_detail', post_id=post_id))

    comments = post.comments.order_by(Comment.timestamp.desc()).all()
    return render_template('post_detail.html', post=post, form=form, comments=comments, title="Post Details")


@routes_blueprint.route('/users')
@login_required
def users_list():
    users = User.query.filter(User.id != current_user.id).order_by(User.username).paginate(
        page=request.args.get('page', 1), per_page=10
    )
    return render_template('users.html', title='Benutzer finden', users=users)


# API Key Funktionalität und Endpunkte (unverändert)
def generate_api_key():
    return secrets.token_hex(32)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({"error": "Invalid API key"}), 403
        return f(current_user=user, *args, **kwargs)
    return decorated_function


@routes_blueprint.route('/api/get_api_key')
@login_required
def get_api_key():
    """API Endpunkt, um einen API Key für den angemeldeten Benutzer zu generieren (Web-Interface)"""
    if not current_user.api_key: # Prüfen, ob der Benutzer bereits einen Key hat
        current_user.api_key = generate_api_key() # Neuen Key generieren
        db.session.commit() # Key in der Datenbank speichern
    return render_template('api_key.html', api_key=current_user.api_key) # Key im Template anzeigen


@routes_blueprint.route('/api/posts')
@require_api_key
def api_get_posts(current_user):
    """API Endpunkt, um Posts von Benutzern zu erhalten, denen der aktuelle Benutzer folgt"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    posts_pagination = current_user.followed_posts().paginate(page=page, per_page=per_page)
    posts_data = [{
        'id': post.id,
        'body': post.body,
        'timestamp': post.timestamp.isoformat(),
        'author': post.author.username
    } for post in posts_pagination.items]
    return jsonify({
        'posts': posts_data,
        'total_pages': posts_pagination.pages,
        'current_page': posts_pagination.page,
        'per_page': posts_pagination.per_page,
        'total_posts': posts_pagination.total
    })


@routes_blueprint.route('/api/user/<username>/posts')
@require_api_key
def api_get_user_posts(username, current_user):
    """API Endpunkt, um Posts eines bestimmten Benutzers zu erhalten"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    posts_pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    posts_data = [{
        'id': post.id,
        'body': post.body,
        'timestamp': post.timestamp.isoformat(),
        'author': post.author.username
    } for post in posts_pagination.items]
    return jsonify({
        'posts': posts_data,
        'total_pages': posts_pagination.pages,
        'current_page': posts_pagination.page,
        'per_page': posts_pagination.per_page,
        'total_posts': posts_pagination.total
    })