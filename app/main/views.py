from flask import flash, redirect, render_template, session, url_for
from datetime import datetime

from .forms import NameForm
from . import main

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
