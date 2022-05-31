from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from website.models import User, Project, Organization



class SignUpForm(FlaskForm):

    def validate_email(self, email_to_check):
        existing_email = User.query.filter_by(email=email_to_check.data).first()
        if existing_email:
            raise ValidationError("User with that email already exists.")

    def validate_role(self, role_to_check):
        if role_to_check.data == "-- select a role --":
            raise ValidationError("Please select a role.")

    first_name = StringField(label="First Name", validators=[DataRequired(message="Please enter your first name."),
                                                             Length(min=2, max=50)])
    last_name = StringField(label="Last Name", validators=[DataRequired(message="Please enter your last name."),
                                                           Length(min=2, max=50)])
    email = StringField(label="Email", validators=[DataRequired(message="Please enter an email."), Email()])
    organization = StringField(label="Organization", validators=[DataRequired(message="Please enter an organization.")])
    role = SelectField(label="Job Role", choices=[('-- select a role --'), ('Developer'), ('Project Manager'), ('Admin'), ('Other')])
    password1 = PasswordField(label="Password", validators=[DataRequired(message="Please enter a password."), Length(min=8)])
    password2 = PasswordField(label="Confirm Password",
                              validators=[DataRequired(message="Please confirm your password."), EqualTo("password1", message="Passwords do not match.")])
    submit = SubmitField(label="Create Account")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Sign-In")


class CreateNewProjectForm(FlaskForm):
    name = StringField(label="Project Name", validators=[DataRequired(message="Please enter a name for the project."),
                                                         Length(min=2, max=100)])
    description = StringField(label="Project Description", validators=[Length(max=500)])
    submit = SubmitField(label="Create Project")


def init_CreateNewTicketForm():
    developer_names = ["-- assign a developer --"]
    user = User.query.get(current_user.id)
    organization = Organization.query.get(user.organization_id)
    developer_objs = organization.team
    for developer_obj in developer_objs:
        developer_names.append(developer_obj)

    class CreateNewTicketForm(FlaskForm):

        def validate_priority(self, priority_to_check):
            if priority_to_check.data == "-- select a priority --":
                raise ValidationError("Please select a ticket priority.")

        def validate_type(self, type_to_check):
            if type_to_check.data == "-- select a type --":
                raise ValidationError("Please select a ticket type.")

        def validate_status(self, status_to_check):
            if status_to_check.data == "-- select a status --":
                raise ValidationError("Please select a ticket status.")

        def validate_assigned_dev(self, assigned_dev_to_check):
            if assigned_dev_to_check.data == "-- assign a developer --":
                raise ValidationError("Please assign a developer to ticket.")

        name = StringField(label="Ticket Name", validators=[DataRequired(message="Please enter a name for the ticket."),
                                                            Length(min=2, max=100)])
        description = StringField(label="Description")
        priority = SelectField(label="Priority", choices=[("-- select a priority --"), ('Low'), ('Medium'), ('High'), ('Urgent')])
        type = SelectField(label="Type", choices=[("-- select a type --"), ("Bug/Error"), ("New Feature"), ("Refactor"), ("Design/UX"), ("Training Request"), ("Documentation"), ("Other")])
        status = SelectField(label="Status", choices=[("-- select a status --"), ("New"), ("Open"), ("In Progress"), ("Resolved"), ("Additional Info Required")])
        assigned_dev = SelectField(label="Assigned Developer", choices=[(developer_obj.id, developer_obj) for developer_obj in developer_objs])
        submit = SubmitField(label="Submit Ticket")

    return CreateNewTicketForm


class EditProfileForm(FlaskForm):

    def validate_role(self, role_to_check):
        if role_to_check.data == "-- select a role --":
            raise ValidationError("Please select a role.")

    first_name = StringField(label="First Name", validators=[DataRequired(message="Please enter your first name."),
                                                             Length(min=2, max=50)])
    last_name = StringField(label="Last Name", validators=[DataRequired(message="Please enter your last name."),
                                                           Length(min=2, max=50)])
    email = StringField(label="Email", validators=[DataRequired(message="Please enter an email."), Email()])
    role = SelectField(label="Job Role",
                       choices=[('-- select a role --'), ('Developer'), ('Project Manager'), ('Admin'), ('Other')])
    password1 = PasswordField(label="Current Password",
                              validators=[DataRequired(message="Enter new password."), Length(min=8)])
    password2 = PasswordField(label="New Password",
                              validators=[Length(min=8)])
    password3 = PasswordField(label="Confirm New Password",
                              validators=[EqualTo("password2", message="Passwords do not match.")])
    submit = SubmitField(label="Save Changes")


class NewCommentForm(FlaskForm):

    message = StringField(label="Comment")
    submit = SubmitField(label="Submit Comment")





