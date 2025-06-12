# app.py - Week 4: Finalization, Testing, and Documentation

# Import necessary modules from Flask and Flask-SQLAlchemy
# Added 'flash' and 'get_flashed_messages' for user feedback
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
import os # For path manipulation if needed, not strictly for this app

# Initialize the Flask application
app = Flask(__name__)
# Get SECRET_KEY from environment variable, provide a fallback for local development
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_for_dev')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recommended to disable
db = SQLAlchemy(app)

# Configure a secret key for flash messages (essential for security)
# In a real app, this should be an environment variable.
app.config['SECRET_KEY'] = 'your_super_secret_key_here' # IMPORTANT: Change this!

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
    description = db.Column(db.String(200), nullable=False) # Task description, cannot be null, max 200 chars
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

        # --- Input Validation ---
        if not task_description:
            flash('Task description cannot be empty!', 'error') # Flash an error message
        elif len(task_description) > 200:
            flash('Task description cannot be longer than 200 characters!', 'error')
        else:
            try:
                # Create a new Task object
                new_task = Task(description=task_description)
                # Add the new task to the database session
                db.session.add(new_task)
                # Commit the changes to the database
                db.session.commit()
                flash('Task added successfully!', 'success') # Flash a success message
            except Exception as e:
                db.session.rollback() # Rollback changes if an error occurs
                flash(f'Error adding task: {e}', 'error') # Flash an error message

        # Redirect to the home page to prevent form re-submission on refresh
        return redirect(url_for('index'))

    # Retrieve all tasks from the database, ordered by ID
    tasks = Task.query.order_by(Task.id).all()
    # Pass the list of Task objects to the HTML template
    # Also pass flashed messages to the template
    return render_template('index.html', tasks=tasks, messages=get_flashed_messages(with_categories=True))

# Route for marking a task as complete/incomplete
# '<int:task_id>' captures the task ID from the URL and converts it to an integer
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    try:
        # Query the database to find the task by its ID
        # get_or_404() automatically sends a 404 error if task not found
        task = Task.query.get_or_404(task_id)
        # Toggle the 'completed' status
        task.completed = not task.completed
        # Commit the change to the database
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task status: {e}', 'error')
    # Redirect back to the home page
    return redirect(url_for('index'))

# Route for deleting a task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    try:
        # Query the database to find the task by its ID
        task = Task.query.get_or_404(task_id)
        # Delete the task from the database session
        db.session.delete(task)
        # Commit the change to the database
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {e}', 'error')
    # Redirect back to the home page
    return redirect(url_for('index'))

# Run the Flask application
# debug=True allows for automatic reloading on code changes and provides a debugger
# IMPORTANT: Set debug=False and handle SECRET_KEY securely in production environments
if __name__ == '__main__':
    app.run(debug=True)
