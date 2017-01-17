
# from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import synonym
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr import db


class User(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)

    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)


    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, email, password):
        user = query(cls).filter(cls.email==email).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def __repr__(self):
        return '<User id={self.id} email={self.email!r}>'.format(self=self)
    # # @hybrid_property
    # def password(self):
    #     return self._password
    #
    #
    # @password.setter
    # def _set_password(self, plaintext):
    #     self._password = bcrypt.generate_password_hash(plaintext)
    #
    # def is_collect_password(self, plaintext):
    #     return bcrypt.check_password_hash(self._password, plaintext)


def init():
    db.create_all()