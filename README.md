# Deskline — Real-time Support Ticket Desk (Flask)

A lightweight helpdesk portfolio piece. Customers submit tickets; agents work a
live queue that updates instantly (no refresh) via Socket.IO, with a real-time
per-ticket chat thread.

## Features

- Customer + agent roles (chosen at signup)
- Customer: submit tickets, view "My tickets", reply on a ticket thread
- Agent: live queue (new tickets appear instantly), filter by status, assign
  agent, change status, reply in a live per-ticket thread
- Real-time via Flask-SocketIO: agents join an `agents` room and get pushed
  new tickets and activity; each ticket has its own room for live chat
- Auth via Flask-Login with hashed passwords (Werkzeug)

## Setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python run.py
```

Visit `http://127.0.0.1:5000/`. Sign up once as a customer and once as an
agent (in two browser windows / an incognito tab) to see the live flow:
submit a ticket as the customer, watch it land instantly on the agent's
queue, reply from either side and watch the thread update live on both ends.

## Project structure

```
app/
  __init__.py       # app factory, extensions, blueprint registration
  extensions.py      # db, login_manager, socketio singletons
  models.py          # User, Ticket, Message
  sockets.py          # Socket.IO room join/leave handlers
  routes/
    auth.py           # signup/login/logout
    dashboard.py       # role-aware home (customer list vs agent queue)
    tickets.py          # create/view/reply/update ticket
  templates/           # Jinja templates
  static/css/main.css   # styling (palette pending)
  static/js/main.js
config.py
run.py
```

## What to extend next

- Email notification when a ticket is assigned or replied to
- File attachments on tickets/messages
- SLA timers / auto-escalation on priority
- Read receipts / typing indicators on the thread
