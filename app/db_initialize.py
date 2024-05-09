

from flask import current_app
from .models import Role, User
from app import create_app, db


class DbInitialize():

    @staticmethod
    def initialize():

        db.drop_all()
        db.create_all()

        Role.insert_roles()

        admin_role = Role.query.filter_by(name='Administrator').first()
        default_role = Role.query.filter_by(default=True).first()
        for u in User.query.all():
            if u.role is None:
                if u.email == current_app.config['FLASKY_ADMIN']:
                    u.role = admin_role
                else:
                    u.role = default_role

        db.session.commit()
