from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Ticket

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def home():
    if current_user.is_agent:
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        return render_template("dashboard/agent.html", tickets=tickets)
    else:
        tickets = Ticket.query.filter_by(customer_id=current_user.id) \
            .order_by(Ticket.created_at.desc()).all()
        return render_template("dashboard/customer.html", tickets=tickets)
