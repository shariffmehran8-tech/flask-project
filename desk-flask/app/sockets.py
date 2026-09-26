from flask_socketio import join_room, leave_room
from flask_login import current_user
from app.extensions import socketio


@socketio.on("connect")
def on_connect():
    if current_user.is_authenticated and current_user.is_agent:
        join_room("agents")


@socketio.on("join_ticket")
def on_join_ticket(data):
    ticket_id = data.get("ticket_id")
    if ticket_id:
        join_room(f"ticket_{ticket_id}")


@socketio.on("leave_ticket")
def on_leave_ticket(data):
    ticket_id = data.get("ticket_id")
    if ticket_id:
        leave_room(f"ticket_{ticket_id}")
