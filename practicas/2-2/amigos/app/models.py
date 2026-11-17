from app import db

class Amigo(db.Model):
    __tablename__ = "amigos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    lati = db.Column(db.String(32))
    longi = db.Column(db.String(32))
    device = db.Column(db.Text, nullable=True) # Nuevo campo

    def __repr__(self):
        return "<Amigo[{}]: {}>".format(self.id, self.name)
