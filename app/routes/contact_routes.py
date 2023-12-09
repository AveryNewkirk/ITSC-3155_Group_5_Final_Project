from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_mail import Mail, Message

issues = {
    'website': 'the website',
    'order': 'an order',
    'account': 'my account',
    'another': 'another user'
}

contact = Blueprint('contact', __name__)

@contact.get('/contact')
def contact_page():
    return render_template('contact.html')

@contact.post('/contact')
def support_ticket():
    name = request.form.get('name')
    issue = issues[request.form.get('prob')]
    desc = request.form.get('details')
    mail = Mail(current_app)

    current_app.config['MAIL_SERVER']='smtp.gmail.com'
    current_app.config['MAIL_PORT'] = 465
    current_app.config['MAIL_USERNAME'] = 'thriftmehelp@gmail.com'
    current_app.config['MAIL_PASSWORD'] = 'jucr juli xkub ezbc'
    current_app.config['MAIL_USE_TLS'] = False
    current_app.config['MAIL_USE_SSL'] = True

    mail = Mail(current_app)
    
    msg = Message( 
                name + ' regarding ' + issue, 
                sender ='thriftmehelp@gmail.com', 
                recipients = ['thriftmehelp@gmail.com'] 
            ) 
    msg.body = desc
    mail.send(msg)
    return redirect('/contact')