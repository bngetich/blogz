from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.UnicodeText())
    body = db.Column(db.UnicodeText())
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<Blog {0}>'.format(self.title)


@app.route('/blog')
def display_blog():
    blog_id = request.args.get('id')
    if blog_id is not None:
        #print('ID: ' + str(blog_id), file=sys.stderr)
        blog = Blog.query.filter_by(id=blog_id).first()
        #print('BLOG: ' + str(blog), file=sys.stderr)
        return render_template('blog-entry.html', blog=blog)

    blogs = Blog.query.order_by(Blog.pub_date.desc()).all()
    return render_template('main-blog.html', blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error = ''
    body_error = ''
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        # validate user's data
        if not title:
            title_error = 'Please fill in the title.'

        if not body:
            body_error = 'Please fill in the body.'

        if not title_error and not body_error:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('add-blog.html', title_error=title_error, body_error=body_error)


if __name__ == '__main__':
    app.run()
