from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def __init__(self, username, balance):
        self.username = username
        self.balance = balance

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update_balance(self, amount):
        if self.balance + amount >= 0:
            self.balance += amount
            db.session.commit()
        else:
            raise ValueError("Баланс не может быть отрицательным")

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)


appHasRunBefore:bool = False
@app.before_request
def create_tables():
    db.create_all()
    if User.query.count() == 0:
        users = [
            User("User1", 5000),
            User("User2", 7500),
            User("User3", 10000),
            User("User4", 12500),
            User("User5", 15000)
        ]
        db.session.bulk_save_objects(users)
        db.session.commit()


def fetch_weather(city):
    API_KEY = "107fbe090c284504a5d112411242102"
    city = city.capitalize()
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"
    response = requests.get(url)
    data = response.json()
    return data['current']['temp_c']


@app.route('/update_balance', methods=['POST'])
def update_balance():
    user_id = request.json['userId']
    city = request.json['city']
    user = User.find_by_id(user_id)
    if user:
        try:
            temperature = fetch_weather(city)
            user.update_balance(temperature)
            return jsonify({"message": "Баланс обновлён."}), 200
        except ValueError as e:
            return jsonify({"message": str(e)}), 400
    else:
        return jsonify({"message": "Нет такого пользователя"}), 404

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
