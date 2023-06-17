from models import db, User
from app import app


db.drop_all()
db.create_all()

User.query.delete()

User1 = User(username="Wristbandz", password="password", email="TJKruger1319@gmail.com", first_name="TJ", last_name="Kruger")

db.session.add(User1)
db.session.commit()