from datetime import datetime
import hashlib
from . import login_manager
from flask import current_app, request
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask_login import AnonymousUserMixin, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Permission:
    READ = 1
    ADD = 2
    EDIT = 4
    MODERATE = 8
    ADMIN = 16
    SYSTEM = 32


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    # ...
    @staticmethod
    def insert_roles():
        #
        roles = {
            'Users': [Permission.READ, Permission.ADD],
            'Officers': [Permission.READ, Permission.ADD,
                         Permission.EDIT],
            'Managers': [Permission.READ, Permission.ADD,
                         Permission.EDIT, Permission.MODERATE],
            'Administrators': [Permission.READ, Permission.ADD,
                               Permission.EDIT, Permission.MODERATE,
                               Permission.ADMIN],
            'SystemAdministrators': [Permission.READ, Permission.ADD,
                                     Permission.EDIT, Permission.MODERATE,
                                     Permission.ADMIN, Permission.SYSTEM],
        }

        default_role = 'Users'

        for r in roles:
            role = Role.query.filter_by(name=r).first()

            if role is None:
                role = Role(name=r)

            role.reset_permissions()

            for perm in roles[r]:
                role.add_permission(perm)
                role.default = (role.name == default_role)
                db.session.add(role)

        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(128))
    location = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrators').first()

            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @ property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @ password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # +user confirmation
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])  # , expiration)
        return s.dumps({'confirm': self.id})  # .decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # data = s.loads(token.encode('utf-8'))
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)

        return True
    # -user confirmation

    # +password reset
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])  # , expiration)
        return s.dumps({'reset': self.id})  # .decode('utf-8')

    @ staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)  # .encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True
    # -password reset

    # +email change
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])  # , expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email})  # .decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)  # .encode('utf-8'))
        except:
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')

        if new_email is None:
            return False

        if self.query.filter_by(email=new_email).first() is not None:
            return False

        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)

        return True
    # -email change

    # +roles
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def is_super_administrator(self):
        return self.can(Permission.SUPERADMIN)
    # -roles

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'

        hash = self.avatar_hash or self.gravatar_hash()
        return f'{url}/{hash}?s={size}&d={default}&r={rating}'

    def __repr__(self):
        return '<User %r>' % self.username

#


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

#


@ login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
