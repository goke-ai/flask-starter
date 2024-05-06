from flask import flash, redirect, render_template, session, url_for
from datetime import datetime

from ..email import send_email
from ..models import User
from .. import db

from .forms import NameForm
from . import main
import app

@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@main.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)


@main.route('/sampleform', methods=['GET','POST'])
def sampleform():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('main.sampleform'))
    
    return render_template('sampleform.html', form=form, name=session.get('name'))


@main.route('/formwithdb', methods=['GET', 'POST'])
def formwithdb():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            
            # send email
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
            
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.formwithdb'))
        
    return render_template('formwithdb.html', 
                           form=form, name=session.get('name'),
                           known=session.get('known', False))