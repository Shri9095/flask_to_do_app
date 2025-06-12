import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration ---
# Get SECRET_KEY from environment variable, provide a fallback for local development
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_for_dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recommended to disable

# --- SQLAlchemy Database Initialization ---
# This line MUST only be called once globally
db = SQLAlchemy(app)

# --- Database Model Definition ---
# This should be defined AFTER db = SQLAlchemy(app)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.id}: {self.description}>'

# --- Routes (your @app.route functions) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_description = request.form.get('task_description')
        if task_description:
            new_task = Task(description=task_description)
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
        else:
            flash('Task description cannot be empty.', 'danger')
        return redirect(url_for('index'))
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/complete/<int:task_id>')
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    flash('Task status updated!', 'info')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'warning')
    return redirect(url_for('index'))

# --- Run Application and Create Database Tables ---
# This ensures db.create_all() is only called when you run 'python app.py' directly,
# not when imported by Gunicorn for production.
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # This creates tables if they don't exist
    app.run(debug=True)