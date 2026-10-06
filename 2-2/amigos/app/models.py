from app import db

class Amigo(db.Model):
    __tablename__ = "amigos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    longi = db.Column(db.String(32))
    lati = db.Column(db.String(32))

    def __repr__(self):
        return "<Amigo[{}]: {}>".format(self.id, self.name)