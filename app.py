from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://blog_user:123456789@localhost:5432/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Инициализация Flask-Migrate
migrate = Migrate(app, db)


# Модели
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


# Формы
class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    submit = SubmitField('Добавить')


# Роуты
@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    form = CommentForm()
    return render_template('view_post.html', post=post, comments=comments, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=form.author.data)
        db.session.add(post)
        db.session.commit()
        flash('Статья успешно создана!', 'success')
        return redirect(url_for('index'))
    return render_template('new_post.html', form=form)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.author = form.author.data
        db.session.commit()
        flash('Статья успешно обновлена!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    return render_template('edit_post.html', form=form)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Статья успешно удалена!', 'success')
    return redirect(url_for('index'))


@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=form.author.data, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен!', 'success')
    else:
        flash('Ошибка при добавлении комментария.', 'danger')
    return redirect(url_for('view_post', post_id=post_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Создание таблиц в PostgreSQL
    app.run(debug=True)
