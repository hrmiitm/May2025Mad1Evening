from app import app
from app import db, User

users = [
    ('Ankit', 'user1', 'u1'),
    ('Rohan', 'user2', 'u3'),
    ('Mohan', 'user3', 'u2'),
]

creators = [
    ('Tom', 'creator1', 'c1'),
    ('Jerry', 'creator2', 'c3'),
    ('Don', 'creator3', 'c2'),
]

u = User(name='Dragon', email='admin', password='a', isAdmin=True) # row of admin == 1, Dragon, admin, a, 1, 0, 1
db.session.add(u)
db.session.commit()

for n, e, p in users:
    u = User(name=n, email=e, password=p) 
    db.session.add(u)
    db.session.commit()

for n, e, p in creators:
    u = User(name=n, email=e, password=p, isCreator=True) 
    db.session.add(u)
    db.session.commit()