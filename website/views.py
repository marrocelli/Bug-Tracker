import flask_login
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from website.forms import CreateNewProjectForm, init_CreateNewTicketForm, EditProfileForm, NewCommentForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Organization, Project, Ticket, Comment, TicketEdit


views = Blueprint("views", __name__)


@views.route('/dashboard')
@login_required
def dashboard():

    user = User.query.get(current_user.id)
    organization = Organization.query.get(user.organization_id)
    low = []
    medium = []
    high = []
    urgent = []

    for project in organization.projects:
        for ticket in project.tickets:
            if ticket.priority == "Low":
                low.append(ticket)
            elif ticket.priority == "Medium":
                medium.append(ticket)
            elif ticket.priority == "High":
                high.append(ticket)
            elif ticket.priority == "Urgent":
                urgent.append(ticket)
    priority_data = [len(low), len(medium), len(high), len(urgent)]

    return render_template("dashboard.html", priority_data=priority_data)


# Create routes
@views.route('/my-projects/create-project', methods=["GET", "POST"])
@login_required
def create_project():

    form = CreateNewProjectForm()

    user = User.query.get(current_user.id)
    organization = Organization.query.get(user.organization_id)

    if form.validate_on_submit():

        existing_project = Project.query.filter_by(name=form.name.data).first()

        if existing_project:
            flash("Project with that name already exists.", category="danger")
        else:
            new_project = Project(name=form.name.data, description=form.description.data)
            db.session.add(new_project)

            # Add current user to project team by default.
            new_project.team.append(current_user)
            # Add new_project to organization.projects
            organization.projects.append(new_project)

            db.session.commit()
            flash(f"{new_project.name} project created successfully", category="success")

        return redirect(url_for("views.my_projects"))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"{err_msg}", category="danger")

    return render_template("create_project.html", form=form)


@views.route('/my-projects/<project_id>/create-ticket', methods=["GET", "POST"])
@login_required
def create_ticket(project_id):

    createNewTicketFormObject = init_CreateNewTicketForm()
    form = createNewTicketFormObject()

    user = User.query.get(current_user.id)
    organization = Organization.query.get(user.organization_id)

    if form.validate_on_submit():

        existing_ticket = Ticket.query.filter_by(name=form.name.data).first()

        if existing_ticket:
            flash("Ticket with that name already exists.", category="danger")
        else:
            project = Project.query.get(int(project_id))
            new_ticket = Ticket(name=form.name.data, description=form.description.data, priority=form.priority.data, type=form.type.data, status=form.status.data, assigned_dev=form.assigned_dev.data, project=project, created_by=flask_login.current_user.id)
            db.session.add(new_ticket)
            db.session.commit()
            flash("Ticket created successfully.", category="success")

            return redirect(url_for("views.project_details", project_id=project_id))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"{err_msg}", category="danger")

    return render_template("create_ticket.html", form=form, organization=organization)


# Read routes
@views.route('/my-projects', methods=["GET", "POST"])
@login_required
def my_projects():

    projects = current_user.projects

    # When user selects delete project.
    if request.method == "POST":
        project_id = request.form["project_id"]
        project_to_delete = Project.query.get(int(project_id))
        if project_to_delete:
            db.session.delete(project_to_delete)
            # Delete all tickets within project_to_delete.
            for ticket in project_to_delete.tickets:
                db.session.delete(ticket)
            db.session.commit()
            flash(f"{project_to_delete.name} deleted successfully.", category="success")
            projects = current_user.projects

            return redirect(url_for("views.my_projects", projects=projects))

    return render_template("my_projects.html", projects=projects)


@views.route('/my-projects/<project_id>')
@login_required
def project_details(project_id):

    project = Project.query.get(int(project_id))

    return render_template("project_details.html", project=project)


@views.route('/my-tickets', methods=["GET", "POST"])
@login_required
def my_tickets():

    user = User.query.get(current_user.id)
    organization = Organization.query.get(user.organization_id)
    tickets = []

    for project in organization.projects:
        if user in project.team:
            for ticket in project.tickets:
                tickets.append(ticket)

    if request.method == "POST":
        ticket_id = request.form["ticket_id"]
        action = request.form["action"]
        ticket_to_edit = Ticket.query.get(int(ticket_id))
        if action == "edit":
            return redirect(url_for("views.edit_ticket", project_id=ticket_to_edit.project_id, ticket_id=ticket_id))
        elif action == "delete":
            db.session.delete(ticket_to_edit)
            db.session.commit()
            flash(f"{ticket_to_edit.name} {action}d successfully.", category="success")
            return redirect(url_for("views.my_tickets", organization=organization, tickets=tickets))
        elif action == "details":
            return redirect(url_for("views.ticket_details", project_id=ticket_to_edit.project.id, ticket_id=ticket_id))

    return render_template("my_tickets.html", organization=organization, tickets=tickets)


@views.route('/my-profile', methods=["GET", "POST"])
@login_required
def my_profile():

    form = EditProfileForm()

    if form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        role = form.role.data
        current_password = form.password1.data
        new_password = form.password2.data

        if check_password_hash(current_user.password, current_password):
            user = User.query.get(current_user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.role = role
            user.password = generate_password_hash(new_password, method="sha256")

            db.session.commit()
            flash(f"Changes saved successfully", category="success")

            return redirect(url_for("views.my_profile"))
        else:
            flash("Incorrect password.", category="danger")

    return render_template("my_profile.html", form=form)


@views.route('/my-projects/<project_id>/ticket-details/<ticket_id>', methods=["GET", "POST"])
@login_required
def ticket_details(project_id, ticket_id):

    form = NewCommentForm()

    project = Project.query.get(int(project_id))
    ticket = Ticket.query.get(int(ticket_id))
    ticket_edits = TicketEdit.query.filter_by(ticket_id=ticket_id)

    # When submitting a comment.
    if form.validate_on_submit():
        new_comment = Comment(message=form.message.data, ticket=ticket, commenter=current_user.full_name)
        print(new_comment)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment submitted successfully.", category="success")

        return redirect(url_for('views.ticket_details', ticket_id=ticket_id, project_id=project_id))

    # When selecting ticket options.
    if request.method == "POST":
        ticket_id = request.form["ticket_id"]
        action = request.form["action"]
        ticket_to_edit = Ticket.query.get(int(ticket_id))
        if action == "edit":
            return redirect(url_for("views.edit_ticket", project_id=project_id, ticket_id=ticket_id))
        elif action == "delete":
            if ticket_to_edit:
                db.session.delete(ticket_to_edit)
                db.session.commit()
                flash(f"{ticket_to_edit.name} {action}d successfully.", category="success")

                return redirect(url_for("views.edit_project_tickets", project_id=project_id))

    return render_template("ticket_details.html", ticket=ticket, project=project, form=form, ticket_edits=ticket_edits)


# Update/Delete routes
@views.route('/my-projects/<project_id>/edit-project-tickets', methods=["GET", "POST"])
@login_required
def edit_project_tickets(project_id):

    project = Project.query.get(int(project_id))
    tickets = Ticket.query.filter_by(project=project)
    users = User.query.all()

    if request.method == "POST":
        ticket_id = request.form["ticket_id"]
        action = request.form["action"]
        ticket_to_edit = Ticket.query.get(int(ticket_id))
        if action == "edit":
            return redirect(url_for("views.edit_ticket", project_id=project_id, ticket_id=ticket_id))
        elif action == "delete":
            db.session.delete(ticket_to_edit)
            db.session.commit()
            flash(f"{ticket_to_edit.name} {action}d successfully.", category="success")
        elif action == "details":
            return redirect(url_for("views.ticket_details", project_id=project.id, ticket_id=ticket_id))

    return render_template("edit_project_tickets.html", project=project, tickets=tickets, users=users)


@views.route('/my-project/<project_id>/edit-project-tickets/<ticket_id>', methods=["GET", "POST"])
@login_required
def edit_ticket(project_id, ticket_id):

    EditTicketFormObject = init_CreateNewTicketForm()
    form = EditTicketFormObject()

    project = Project.query.get(int(project_id))
    ticket = Ticket.query.get(int(ticket_id))

    if request.method == "POST":
        if ticket.name != request.form["name"]:
            ticket_edit = TicketEdit(property="Name", ticket=ticket, old_value=ticket.name, new_value=request.form["name"])
            db.session.add(ticket_edit)
            ticket.name = request.form["name"]
        if ticket.description != request.form["description"]:
            ticket_edit = TicketEdit(property="Description", ticket=ticket, old_value=ticket.description, new_value=request.form["description"])
            db.session.add(ticket_edit)
            ticket.description = request.form["description"]
        if ticket.priority != request.form["priority"]:
            ticket_edit = TicketEdit(property="Priority", ticket=ticket, old_value=ticket.priority, new_value=request.form["priority"])
            db.session.add(ticket_edit)
            ticket.priority = request.form["priority"]
        if ticket.type != request.form["type"]:
            ticket_edit = TicketEdit(property="Type", ticket=ticket, old_value=ticket.type, new_value=request.form["type"])
            db.session.add(ticket_edit)
            ticket.type = request.form["type"]
        if ticket.status != request.form["status"]:
            ticket_edit = TicketEdit(property="Status", ticket=ticket, old_value=ticket.status, new_value=request.form["status"])
            db.session.add(ticket_edit)
            ticket.status = request.form["status"]

        db.session.commit()
        flash(f"{ticket.name} edited successfully", category="success")

        return redirect(url_for("views.edit_project_tickets", project_id=project_id))

    return render_template("edit_ticket.html", form=form, project=project, ticket=ticket)


@views.route('/my-projects/<project_id>/edit-project-members', methods=["GET", "POST"])
@login_required
def edit_project_members(project_id):

    project = Project.query.get(int(project_id))
    user = User.query.get(current_user.id)
    organization = Organization.query.get(user.organization_id)

    if request.method == "POST":
        user_id = request.form["user_id"]
        if request.form["action"] == "add":
            user_to_edit = User.query.get(int(user_id))
            project.team.append(user_to_edit)
            db.session.commit()
            flash(f"{user_to_edit.first_name} {user_to_edit.last_name} added to {project.name}.", category="success")
        elif request.form["action"] == "remove":
            user_to_edit = User.query.get(int(user_id))
            project.team.remove(user_to_edit)
            db.session.commit()
            flash(f"{user_to_edit.first_name} {user_to_edit.last_name} removed from {project.name}.", category="success")

    return render_template("edit_project_members.html", organization=organization, project=project)
