from flask import flash, redirect, render_template, session, url_for, current_app
from datetime import datetime

from flask_login import login_required

from decorators import admin_required, permission_required

from ..email import send_email
from ..models import Permission, User
from .. import db

from .forms import NameForm
from . import main


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


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

    return render_template('sampleform.html', form=form, name=session.get('name'))


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

    return render_template('formwithdb.html',
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
