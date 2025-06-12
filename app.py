# app.py - Week 3: Persistence with SQLite (Flask-SQLAlchemy)

# Import necessary modules from Flask and Flask-SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os # Used for path manipulation if needed, not strictly for this app

# Initialize the Flask application
app = Flask(__name__)

# --- Database Configuration ---
# Define the path to your SQLite database file
# '///' means relative path to the current directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
# Suppress a warning related to event system overhead
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database object
db = SQLAlchemy(app)

# --- Define the Task Model ---
# This class represents your 'tasks' table in the database
class Task(db.Model):
    # Define columns for the table
    id = db.Column(db.Integer, primary_key=True) # Primary key, auto-increments
    description = db.Column(db.String(200), nullable=False) # Task description, cannot be null
    completed = db.Column(db.Boolean, default=False) # Completion status, defaults to False

    # A representation method, useful for debugging
    def __repr__(self):
        return f'<Task {self.id}: {self.description}>'

# --- Database Table Creation ---
# This block ensures that the database tables are created when the application starts
# 'app.app_context()' is necessary because db operations need the Flask app context
with app.app_context():
    db.create_all()

# --- Routes and View Functions ---

# Route for the home page. Handles both GET (displaying tasks) and POST (adding tasks) requests.
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get task description from the form
        task_description = request.form.get('task_description')
        if task_description:
            # Create a new Task object
            new_task = Task(description=task_description)
            # Add the new task to the database session
            db.session.add(new_task)
            # Commit the changes to the database
            db.session.commit()
        # Redirect to the home page to prevent form re-submission on refresh
        return redirect(url_for('index'))

    # Retrieve all tasks from the database, ordered by ID
    tasks = Task.query.order_by(Task.id).all()
    # Pass the list of Task objects to the HTML template
    return render_template('index.html', tasks=tasks)

# Route for marking a task as complete/incomplete
# '<int:task_id>' captures the task ID from the URL and converts it to an integer
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    # Query the database to find the task by its ID
    # get_or_404() automatically sends a 404 error if task not found
    task = Task.query.get_or_404(task_id)
    # Toggle the 'completed' status
    task.completed = not task.completed
    # Commit the change to the database
    db.session.commit()
    # Redirect back to the home page
    return redirect(url_for('index'))

# Route for deleting a task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    # Query the database to find the task by its ID
    task = Task.query.get_or_404(task_id)
    # Delete the task from the database session
    db.session.delete(task)
    # Commit the change to the database
    db.session.commit()
    # Redirect back to the home page
    return redirect(url_for('index'))

# Run the Flask application
# debug=True allows for automatic reloading on code changes and provides a debugger
# IMPORTANT: Set debug=False in production environments
if __name__ == '__main__':
    app.run(debug=True)
