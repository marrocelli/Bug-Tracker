from . import db
from flask_login import UserMixin, current_user
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

# Create an association table to store the many-to-many relationship between users and projects.
user_project_assoc = db.Table('user_project_assoc',
                              db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                              db.Column('project_id', db.Integer(), db.ForeignKey('project.id')))


# Have a company/org object?? I'm thinking this will be necessary to make this program useful to more than just me.
class Organization(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False, unique=True)
    projects = db.relationship('Project', backref='organization')
    team = db.relationship('User', backref='organization')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(length=100), nullable=False, unique=True)
    first_name = db.Column(db.String(length=50), nullable=False)
    last_name = db.Column(db.String(length=50), nullable=False)
    organization_id = db.Column(db.String(length=100), db.ForeignKey("organization.id"))
    role = db.Column(db.String())
    password = db.Column(db.String(), nullable=False)
    # have access to projects attribute from project.team backref
    # have access to organization attribute from organization.team backref

    @hybrid_property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __repr__(self):
        return self.full_name

    # notifications every time they log in with what's new?


class Project(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False, unique=True)
    description = db.Column(db.String(length=500))
    organization_id = db.Column(db.String(length=100), db.ForeignKey("organization.id"))
    team = db.relationship('User', secondary='user_project_assoc', backref='projects')
    tickets = db.relationship('Ticket', backref='project')

    def __repr__(self):
        return f"<Project: {self.name}>"

    #    issues should be removed when resolved but still kept in archives some how.
    # have an archives property? (can aggregate from all projects and display??) (or have archive object?)
    # Owner/PM of project --> I'm thinking this person will have all admin privileges for this project.


class Ticket(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False, unique=True)
    description = db.Column(db.String(length=500), nullable=False)
    project_id = db.Column(db.Integer(), db.ForeignKey("project.id"))
    priority = db.Column(db.String(), nullable=False, default="Low")
    type = db.Column(db.String())
    status = db.Column(db.String())
    assigned_dev = db.Column(db.Integer(), db.ForeignKey("user.id"))
    created_by = db.Column(db.Integer(), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    comments = db.relationship('Comment', backref='ticket')
    history = db.relationship('TicketEdit', backref='ticket')
    # have access to developer attribute from user.assigned_tickets backref
    # have access to the project attribute from project.tickets backref

    # attachments


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    message = db.Column(db.String(length=500), nullable=False)
    ticket_id = db.Column(db.Integer(), db.ForeignKey("ticket.id"))
    commenter = db.Column(db.Integer())
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # have access to the ticket attribute from ticket.comments backref


class TicketEdit(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ticket_id = db.Column(db.Integer(), db.ForeignKey('ticket.id'))
    property = db.Column(db.String())
    old_value = db.Column(db.String())
    new_value = db.Column(db.String())
    date_changed = db.Column(db.DateTime(timezone=True), default=func.now())


    # id
    # name
    # attachments
    # description
    # tags
    # Creator --> User object who created Issue (will this be whole User object or just name?) maybe should
    #     be object that way anytime there is an update it will add notification to that user object.
    # should have a priority
    # should have comments
    # date bug was created
    # date bug was started
    # date bug was fixed
    # due date should only be able to be changed by issue owner/admin
    # check for duplicates during creation
    # custom fields?
    # have drop down menus for common stuff
    # should have status (Resolved, in-progress, open, closed)
    # should have an archive of all previously solved bugs.


