from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

# Create an association table to store the many-to-many relationship between users and projects.
user_project_assoc = db.Table('user_project_assoc',
                              db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                              db.Column('project_id', db.Integer(), db.ForeignKey('project.id')))


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


class Project(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False, unique=True)
    description = db.Column(db.String(length=500))
    organization_id = db.Column(db.String(length=100), db.ForeignKey("organization.id"))
    team = db.relationship('User', secondary='user_project_assoc', backref='projects')
    tickets = db.relationship('Ticket', backref='project')

    def __repr__(self):
        return f"<Project: {self.name}>"


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



