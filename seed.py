from models import db, User, Feedback
from app import app


db.drop_all()
db.create_all()

User.query.delete()

User1 = User.register("Wristbandz", "password", "TJKruger1319@gmail.com", "TJ", "Kruger")
db.session.add(User1)
db.session.commit()

fb1 = Feedback(title="Feedback 1", content="Personally, I disagree with your entire being", username="Wristbandz")
db.session.add(fb1)
db.session.commit()