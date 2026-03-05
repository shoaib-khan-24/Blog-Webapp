from datetime import date, datetime
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm
from flask_gravatar import Gravatar
from twilio.rest import Client
from dotenv import load_dotenv
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

#flask login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'   #for posts
db = SQLAlchemy(model_class=Base)
db.init_app(app)

#gravatar step
gravatar = Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)


#twilio credentials
load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE")
admin_phone = os.getenv("ADMIN_PHONE")


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "registered_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

    #parent relationship
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="commenter")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    #child relationship
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("registered_users.id"), nullable=False)
    author = relationship("User", back_populates="posts")

    #parent relationship
    all_comments = relationship("Comment", back_populates="post")


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)

    #child relationship
    commenter_id: Mapped[int] = mapped_column(Integer, ForeignKey("registered_users.id"), nullable=False)
    commenter = relationship("User", back_populates="comments")

    #child relationship
    post = relationship("BlogPost", back_populates="all_comments")
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_posts.id"), nullable=False)


with app.app_context():
    db.create_all()

#creating decorator
def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id == 1:
            return func(*args, **kwargs)
        else:
            return abort(403)
    return wrapper


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        user_to_check = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user_to_check:
            #user already exists, go for login
            flash("User already exists! Try login.")
            return redirect(url_for("login"))

        new_user = User(
            name = form.name.data,
            email = form.email.data,
            password = generate_password_hash(
                form.password.data,
                "pbkdf2:sha256",
                8
            )
        )
        db.session.add(new_user)
        db.session.commit()
        print("User added")
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    curr_year = datetime.today().year
    return render_template("register.html", form=form, curr_year=curr_year)


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_password = form.password.data
        #obtain the user
        user_to_check = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user_to_check:
            print('user exists')
            same_or_not = check_password_hash(user_to_check.password, user_password)
            if same_or_not:
                print("user authenticated!")
                login_user(user_to_check)
                return redirect(url_for('get_all_posts'))
            else:
                flash("Wrong password! Please try again.")
        else:
            flash("Wrong email! Please try again.")
    curr_year = datetime.today().year
    return render_template("login.html", form=form, curr_year=curr_year)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    curr_year = datetime.today().year
    return render_template("index.html", all_posts=posts, current_user=current_user, curr_year=curr_year)



@app.route("/post/<int:post_id>", methods=['GET','POST'])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Login required to comment!")
            return redirect(url_for("login"))
        new_comment = Comment(
            text=form.text.data,
            commenter=current_user,
            post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))
    curr_year = datetime.today().year
    return render_template("post.html", post=requested_post, form=form, current_user=current_user, curr_year=curr_year)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    curr_year = datetime.today().year
    return render_template("make-post.html", form=form, curr_year=curr_year)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    curr_year = datetime.today().year
    return render_template("make-post.html", form=edit_form, is_edit=True, curr_year=curr_year)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    curr_year = datetime.today().year
    return render_template("about.html", curr_year=curr_year)


@app.route("/contact", methods=['GET','POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        #using twilio to send message to owner
        user_name = form.name.data
        user_email = form.email.data
        user_phone = form.phone.data
        user_message = form.message.data

        user_complete_message = f"User {user_name} ({user_phone},{user_email}) has contacted you!\n{user_message}"

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body = user_complete_message,
            from_ = twilio_phone,
            to = admin_phone,
        )
        print(message.body)

        return redirect(url_for("get_all_posts"))
    curr_year = datetime.today().year
    return render_template("contact.html", form=form, curr_year=curr_year)



if __name__ == "__main__":
    app.run(debug=True, port=5002)
