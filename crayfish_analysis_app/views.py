from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db, Post, Comment, Like

main_bp = Blueprint('views', __name__)

@main_bp.route('/')
@main_bp.route("/home")
# @login_required
def home():
    """Returns home page """
    posts = Post.query.all()
    return render_template('home.html', user=current_user, posts=posts)

@main_bp.route("/signup", methods=['GET','POST'])
def signup():
    """Render signup page and handle signup form submission"""
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short', category='error')
        elif len(password1)< 6:
            flash('Password is too short', category='error')
        elif len(email) <4:
            flash('email is invalid', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template('signup.html', user=current_user)

@main_bp.route("/login", methods=['GET','POST'])
def login():
    """Returns login page"""
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@main_bp.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty.', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.forum'))

    return render_template('create_post.html', user=current_user)

@main_bp.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category="error")
    elif current_user.id != post.user.id:
        flash("You do not have permission to delete this post.", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.", category="success")
    return redirect(url_for('views.forum'))

@main_bp.route("/posts/<username>")
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username exists.", category="error")
        return redirect(url_for("views.forum"))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)

@main_bp.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash("Comment cannot be empty.", category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash("Comment added.", category="success")
    
    return redirect(url_for("views.forum"))

@main_bp.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash("Comment does not exist.", category="error")
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash("You do not have permission to delete this comment.", category="error")
    else:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted.", category="success")
    
    return redirect(url_for("views.forum"))

@main_bp.route("/like-post/<post_id>", methods=["GET"])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id)
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        flash("Post does not exist.", category="error")
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for("views.forum"))

@main_bp.route("/about")
def about():
    """Returns about page """
    return render_template('about.html', user=current_user)

@main_bp.route("/account-management")
@login_required
def account_management():
    """Returns account management page """
    return render_template('account_management.html', user=current_user)

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Returns crayfish dashboard """
    return render_template('dashboard.html', user=current_user)

@main_bp.route("/forum")
def forum():
    """Returns forum page """
    posts = Post.query.all()
    return render_template('forum.html', user=current_user, posts=posts)