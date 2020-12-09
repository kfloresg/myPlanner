import os
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "user.db"))

app = Flask(__name__)
application = app

app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_BINDS'] = {
    'todo' : "sqlite:///{}".format(os.path.join(project_dir, "todo.db")),
    'homework' : "sqlite:///{}".format(os.path.join(project_dir, "homework.db")),
    'course' : "sqlite:///{}".format(os.path.join(project_dir, "courses.db"))
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Todo(db.Model):
    __bind_key__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200)) 
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, nullable=False)

class Homework(db.Model):
    __bind_key__ = 'homework'
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(200))
    task = db.Column(db.String(200))
    due = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, nullable=False)


class Courses(db.Model):
    __bind_key__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(200))
    start = db.Column(db.String(200))
    end = db.Column(db.String(200))
    day = db.Column(db.String(200))
    user_id = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=["POST","GET"])
def login():
    return render_template('login.html')

@app.route('/login', methods=["POST", "GET"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Incorrect username or password")
        else:
            if password == user.password:
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Incorrect username or password")
    return render_template("login.html")

@app.route('/signup', methods=["POST", "GET"])
def signup():
    return render_template('signup.html')

@app.route('/signup/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        user = User.query.filter_by(username=username).first()
        if not user:
            new_user = User(username=username,password=password,email=email)
            db.session.add(new_user)
            db.session.commit()
        else:
            flash("You already have an account, Sign In instead")
            return redirect(url_for('login'))
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home', methods=["GET", "POST"])
@login_required
def home():
    user_id = current_user.id
    incomplete = Homework.query.filter_by(user_id=user_id,complete=False).all()
    courses = Courses.query.filter_by(user_id=user_id).all()
    return render_template('home.html', incomplete=incomplete, courses=courses)

@app.route('/home/addHomework', methods=["POST"])
@login_required
def addHomework():
    user_id = current_user.id
    homework = Homework(course=request.form['course'], task=request.form['assignment'], due=request.form['due'], complete=False, user_id=user_id)
    db.session.add(homework)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/home/addCourse', methods=["POST"])
@login_required
def addCourse():
    user_id = current_user.id
    course = Courses(course=request.form['classname'], start=request.form['start'],end=request.form['end'], day=request.form['days'], user_id=user_id)
    db.session.add(course)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/home/deleteCourse', methods=["POST"])
@login_required
def deleteCourse():
    user_id = current_user.id
    course = Courses.query.filter_by(course=request.form['delete'],user_id=user_id).first()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/homework', methods=["GET", "POST"])
@login_required
def homework():
    user_id = current_user.id
    incomplete = Homework.query.filter_by(complete=False,user_id=current_user.id).all()
    allHomework = Homework.query.all()
    return render_template('homework.html', upcoming=incomplete, allHomework=allHomework)

@app.route('/homework/new', methods=['POST'])
@login_required
def newHomework():
    user_id = current_user.id
    homework = Homework(course=request.form['course'], task=request.form['assignment'], due=request.form['due'], complete=False, user_id=user_id)
    db.session.add(homework)
    db.session.commit()
    return redirect(url_for('homework'))

@app.route('/homework/completed', methods=['POST'])
@login_required
def markAssignment():
    user_id = current_user.id
    completed = Homework.query.filter_by(task=request.form['complete'], user_id=user_id).first()
    completed.complete = True
    db.session.commit()
    return redirect(url_for('homework'))

@app.route('/homework/delete', methods=['POST'])
@login_required
def deleteAssignment():
    user_id = current_user.id
    item = Homework.query.filter_by(task=request.form['delete'], user_id=user_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('homework'))

@app.route('/lists', methods=["GET", "POST"])
@login_required
def lists():
    user_id = current_user.id
    incomplete = Todo.query.filter_by(complete=False,user_id=user_id).all()
    complete = Todo.query.filter_by(complete=True,user_id=user_id).all()
    return render_template('list.html', incomplete=incomplete, complete=complete)

@app.route('/lists/add', methods=['POST'])
@login_required
def addLists():
    user_id = current_user.id
    todo = Todo(text=request.form['todoitem'], complete=False, user_id=user_id)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('lists'))

@app.route('/lists/finished', methods=['POST'])
@login_required
def markLists():
    user_id = current_user.id
    completed = Todo.query.filter_by(text=request.form['complete'],user_id=user_id).first()
    completed.complete = True
    db.session.commit()
    return redirect(url_for('lists'))

@app.route('/lists/delete', methods=['POST'])
@login_required
def deleteLists():
    user_id = current_user.id
    item = Todo.query.filter_by(text=request.form['delete'], user_id=user_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('lists'))

if __name__ == '__main__':
    app.run(debug=True)