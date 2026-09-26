from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer")  # customer | agent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets = db.relationship("Ticket", backref="customer", lazy=True,
                               foreign_keys="Ticket.customer_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_agent(self):
        return self.role == "agent"


PRIORITY_CHOICES = ["low", "normal", "high", "urgent"]
STATUS_CHOICES = ["open", "in_progress", "resolved", "closed"]


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default="normal")
    status = db.Column(db.String(20), default="open")
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_agent = db.relationship("User", foreign_keys=[assigned_agent_id])
    messages = db.relationship("Message", backref="ticket", lazy=True,
                                order_by="Message.created_at",
                                cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "priority": self.priority,
            "status": self.status,
            "customer": self.customer.name,
            "agent": self.assigned_agent.name if self.assigned_agent else None,
            "created_at": self.created_at.strftime("%b %d, %H:%M"),
            "message_count": len(self.messages),
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "author": self.author.name,
            "is_agent": self.author.is_agent,
            "body": self.body,
            "created_at": self.created_at.strftime("%H:%M"),
        }
