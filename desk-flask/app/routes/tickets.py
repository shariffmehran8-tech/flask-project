from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user
from app.extensions import db, socketio
from app.models import Ticket, Message, User, PRIORITY_CHOICES, STATUS_CHOICES

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_ticket():
    if current_user.is_agent:
        abort(403)

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "normal")

        if not subject or not description:
            flash("Subject and description are required.", "error")
        else:
            ticket = Ticket(
                subject=subject,
                description=description,
                priority=priority if priority in PRIORITY_CHOICES else "normal",
                customer_id=current_user.id,
            )
            db.session.add(ticket)
            db.session.commit()

            opening = Message(ticket_id=ticket.id, author_id=current_user.id, body=description)
            db.session.add(opening)
            db.session.commit()

            socketio.emit("new_ticket", ticket.to_dict(), to="agents")
            flash("Ticket submitted — an agent will be with you shortly.", "success")
            return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))

    return render_template("tickets/new.html", priorities=PRIORITY_CHOICES)


@tickets_bp.route("/<int:ticket_id>")
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_agent and ticket.customer_id != current_user.id:
        abort(403)

    agents = User.query.filter_by(role="agent").all() if current_user.is_agent else []
    return render_template(
        "tickets/detail.html",
        ticket=ticket,
        agents=agents,
        statuses=STATUS_CHOICES,
    )


@tickets_bp.route("/<int:ticket_id>/message", methods=["POST"])
@login_required
def post_message(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_agent and ticket.customer_id != current_user.id:
        abort(403)

    body = request.form.get("body", "").strip()
    if body:
        message = Message(ticket_id=ticket.id, author_id=current_user.id, body=body)
        db.session.add(message)
        db.session.commit()
        socketio.emit("new_message", message.to_dict(), to=f"ticket_{ticket.id}")
        socketio.emit("ticket_activity", ticket.to_dict(), to="agents")

    return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/update", methods=["POST"])
@login_required
def update_ticket(ticket_id):
    if not current_user.is_agent:
        abort(403)
    ticket = Ticket.query.get_or_404(ticket_id)

    status = request.form.get("status")
    agent_id = request.form.get("assigned_agent_id")

    if status in STATUS_CHOICES:
        ticket.status = status
    if agent_id:
        ticket.assigned_agent_id = int(agent_id) if agent_id != "unassigned" else None

    db.session.commit()
    socketio.emit("ticket_activity", ticket.to_dict(), to="agents")
    socketio.emit("ticket_updated", ticket.to_dict(), to=f"ticket_{ticket.id}")
    flash("Ticket updated.", "success")
    return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))
