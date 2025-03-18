# from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, StringField, SubmitField, DateTimeField, FloatField, IntegerField, TimeField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, NoneOf, AnyOf, ValidationError, Email


from Front import config 
from Front.forms import LoginForm
allowed_emails = config.allowed_emails
allowed_email_pattern = config.allowed_email_pattern


def test_email_pattern_allowed():
    not_allowed = ["a@carbon-water.com", "a@carbon-waters.fr", "a@carbonwaters.com"]
    form = LoginForm()

    # Simulate form submission
    for mail in not_allowed:
        form.email.data = mail
        form.password.data = 'aaaa'
        assert not form.validate(), f"Form should not validate for email: {mail}"

# Run the test
test_email_pattern_allowed()
