from app import *
from models import User, Blog
from hashutils import check_pw_hash


@app.before_request
def require_login():
    allowed_routes = ['login', 'display_blogs', 'index', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', defaults={'page_num': 1})
@app.route('/<int:page_num>')
def index(page_num):
    user_id = request.args.get('user')
    if user_id is not None:
        return redirect('/blog?user=' + str(user_id))
    users = User.query.order_by(User.username.asc()).paginate(
        per_page=20, page=page_num, error_out=True)
    return render_template('index.html', users=users)


@app.route('/blog/', defaults={'page_num': 1})
@app.route('/blog/<int:page_num>')
def display_blogs(page_num):
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    blogs = []

    if blog_id is not None:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog-entry.html', blog=blog)

    if user_id is not None:
        blogs = Blog.query.filter_by(owner_id=user_id).order_by(
            Blog.pub_date.desc()).paginate(per_page=5, page=page_num, error_out=True)
    else:
        blogs = Blog.query.order_by(Blog.pub_date.desc()).paginate(
            per_page=5, page=page_num, error_out=True)

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
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('add-blog.html', title_error=title_error, body_error=body_error)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ''
    password_error = ''
    verify_password_error = ''
    username_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']

        if not re.match(r'^[A-Za-z0-9_-]{3,}$', username):
            username_error = 'Not a valid username'

        if not re.match(r'[A-Za-z0-9@#$%^&+=]{3,}', password):
            password_error = 'Not a valid password'

        if password != verify_password and not password_error:
            verify_password_error = 'Passwords do not match.'
            password = ''
            verify_password = ''

        existing_user = User.query.filter_by(username=username).first()

        if not username_error and not password_error and not verify_password_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = 'Username already exists.'

    return render_template('signup.html', username=username, password_error=password_error,
                           verify_password_error=verify_password_error, username_error=username_error)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if not user:
            error = 'Error! Username does not exist.'
        else:
            if check_pw_hash(password, user.password):
                session['username'] = username
                return redirect('/newpost')
            else:
                error = 'Error! Password is incorrect.'

    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()
