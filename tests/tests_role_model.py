
import unittest

from app import create_app, db
from app.models import Role, User


class RoleModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()      
        
        self.admin_role = Role(name='Admin')
        self.mod_role = Role(name='Moderator')
        self.user_role = Role(name='User')
        self.user_susan = User(username='susan', role=self.user_role)
        self.user_david = User(username='david', role=self.user_role)
        self.user_john = User(username='john', role=self.admin_role)
        
        db.session.add_all([self.admin_role, self.mod_role, self.user_role,
                            self.user_john, self.user_susan, self.user_david])
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_user_role_users_order_by(self):        
        
        o = self.user_role.users.order_by(User.username).all()
        
        self.assertTrue(o[0].username == 'david')
        
    def test_user_role_users_count(self):
        self.assertTrue(self.user_role.users.count() == 2)
    