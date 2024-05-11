import json
import plotly.express as px
import plotly
import pandas as pd
from flask import flash, redirect, render_template, session, url_for, current_app
from datetime import datetime

from flask_login import current_user, login_required

from ..decorators import admin_required, permission_required

from ..email import send_email
from ..models import Permission, Role, User
from .. import db

from .forms import EditProfileAdminForm, EditProfileForm, NameForm
from . import main


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@main.route('/about')
def about():
    return render_template('about.html', current_time=datetime.utcnow())


@main.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)


@main.route('/sample-form', methods=['GET', 'POST'])
def sample_form():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')

        session['name'] = form.name.data
        return redirect(url_for('main.sample_form'))

    return render_template('sample_form.html', form=form, name=session.get('name'))


@main.route('/form-with-db', methods=['GET', 'POST'])
def form_with_db():
    form = NameForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            # send email
            if current_app.config['FLASKY_ADMIN']:
                send_email(
                    current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True

        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.form_with_db'))

    return render_template('form_with_db.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user,
                           current_time=datetime.utcnow())


@main.route('/system')
@login_required
@admin_required
def for_system_admins_only():
    return "For system administrators!"


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@main.route('/manager')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "For comment managers!"


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        db.session.add(user)
        db.session.commit()

        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location

    return render_template('edit_profile.html', form=form, user=user)


@main.route('/plotly')
def plotly():

    # Existing DataFrame
    df = pd.DataFrame({
        'id': ['S001', 'S002', 'S003'],
        'name': ['John Doe', 'Jane Smith', 'Emily Johnson'],
        'math': ['A', 'B', 'C'],
        'science': ['B', 'A', 'B'],
        'history': ['A', 'B', 'C'],
        'english': ['A', 'A', 'B']
    }).set_index('id')

    # Define a mapping of grades to points
    grade_points = {
        'A': 4,
        'B': 3,
        'C': 2,
        'D': 1,
        'F': 0
    }

    # Function to convert grades to points
    def convert_to_points(grade):
        return grade_points.get(grade, 0)

    # Apply the function to each grade column
    for subject in ['math', 'science', 'history', 'english']:
        df[subject + '_points'] = df[subject].apply(convert_to_points)

    dataJson = df.math_points.to_json()
    dataJson2 = df.science_points.to_json()

    return render_template('plotly.html', dataJson=dataJson, dataJson2=dataJson2)
