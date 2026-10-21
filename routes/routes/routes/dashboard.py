from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Event, Expense
from forms import EventForm, ExpenseForm

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    events = Event.query.order_by(Event.event_date.asc()).all()
    expenses = Expense.query.order_by(Expense.created_at.desc()).all()
    
    total_approved_expenses = sum(e.amount for e in expenses if e.status == 'Approved')
    
    return render_template('dashboard.html', 
                           events=events, 
                           expenses=expenses, 
                           total_approved=total_approved_expenses)

@dashboard_bp.route('/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_date=form.event_date.data,
            location=form.location.data,
            organizer=current_user
        )
        db.session.add(event)
        db.session.commit()
        flash('Event successfully scheduled!', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('create_event.html', form=form)

@dashboard_bp.route('/expense/new', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            title=form.title.data,
            amount=form.amount.data,
            category=form.category.data,
            submitted_by=current_user
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense request submitted.', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('add_expense.html', form=form)

@dashboard_bp.route('/expense/<int:expense_id>/<string:action>')
@login_required
def update_expense_status(expense_id, action):
    if current_user.role not in ['Admin', 'Treasurer']:
        flash('Unauthorized action: Only Treasurers and Admins can approve expenses.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    expense = Expense.query.get_or_404(expense_id)
    if action == 'approve':
        expense.status = 'Approved'
    elif action == 'reject':
        expense.status = 'Rejected'
    
    db.session.commit()
    flash(f'Expense request status updated to {expense.status}.', 'info')
    return redirect(url_for('dashboard.index'))
