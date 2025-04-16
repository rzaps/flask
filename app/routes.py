from flask import render_template,request, redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user, login_user, logout_user
import requests
from app.models import User
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, EditProfileForm

crew = []

    # API для получения данных о погоде
    # формируем путь и методы GET и POST
@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    # переменная для новостей
    news = get_news()
    quote = get_quotes()
    if request.method == 'POST':
        city = request.form['city']
        # прописываем переменную, куда будет сохраняться результат и функцию weather с указанием города, который берем из формы
        weather = get_weather(city)

    return render_template("index.html", user=current_user, crew=crew, weather=weather, news=news, quote=quote)



@app.route("/blog/")
def blog():
    return render_template("blog.html")

@app.route("/contacts/")
def contacts():
    return render_template("contacts.html")

@app.route("/form/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        city = request.form.get("city")
        age = request.form.get("age")
        hobby = request.form.get("hobby")
        if name and city and age:
            crew.append({"name": name, "city": city, "age": age, "hobby": hobby})
            return redirect(url_for("form"))
    return render_template("form.html", crew=crew)

@app.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Вы успешно зарегистрировались!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("index"))
        else:
            flash("Неправильный логин или пароль", "danger")
    return render_template("login.html", form=form)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("index"))


from app.forms import EditProfileForm  # Добавить в импорты


@app.route("/account/", methods=['GET', 'POST'])
@login_required
def account():
    form = EditProfileForm(original_username=current_user.username,
                           original_email=current_user.email)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.new_password.data:  # Если пользователь ввел новый пароль
            if not current_user.check_password(form.current_password.data):
                flash('Неверный текущий пароль', 'danger')
                return redirect(url_for('account'))
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')

        db.session.commit()
        flash('Ваш профиль успешно обновлен', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("account.html", form=form)



#в функции прописываем город, который мы будем вводить в форме
def get_weather(city):
   api_key = "8cf9ed27dae755ecf7ed9d97d85a2615"
   #адрес, по которомы мы будем отправлять запрос. Не забываем указывать f строку.
   url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
   #для получения результата нам понадобится модуль requests
   response = requests.get(url)
   #прописываем формат возврата результата
   return response.json()

# функция для получения новостей
def get_news():
    api_key = "3c46887207e54b72bedd56e1245243cc"
    url = f"https://newsapi.org/v2/top-headlines?category=technology&apiKey={api_key}"
    response = requests.get(url)
    return response.json().get("articles", [])

def get_quotes():
    url = f"https://zenquotes.io/api/random"
    response = requests.get(url)
    return response.json()