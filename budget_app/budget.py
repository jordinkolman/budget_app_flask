from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from budget_app.auth import login_required
from budget_app.db import get_db

bp = Blueprint('budget', __name__)

@bp.route('/')
@login_required
def index():
    print(g)
    db = get_db()
    accounts = (db.execute(
        'SELECT name, balance, account_type FROM account WHERE user_id = ?',
        (g.user["id"],)
    ).fetchall())

    transactions = (db.execute(
        'SELECT date_occurred, time_occurred, v.name, c.name, ty.name, amount, a.name'
        ' FROM transactions t JOIN vendors v ON t.vendor_id = v.id'
        '  JOIN categories c ON t.category_id = c.id'
        '  JOIN types ty ON t.type_id = ty.id'
        '  JOIN account a ON t.account_id = a.id'
        '  WHERE t.user_id = ?',
        (g.user["id"],)
    ).fetchall())

    return render_template('budget/index.html', accounts=accounts, transactions=transactions)


@bp.route('/add_account', methods=("GET", "POST"))
@login_required
def add_account():
    if request.method == "POST":
        name = request.form['name']
        balance = request.form['balance']
        account_type = request.form['account_type']
        error = None

        if not name:
            error = "Account Name is Required."
        elif not account_type:
            error = "Account Type is Required."

        if not balance:
            balance = 0.0

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO account (user_id, name, balance, account_type) VALUES (?, ?, ?, ?)",
                (g.user['id'], name, balance, account_type,)
            )
            db.commit()
            return redirect(url_for('budget.index'))

    return render_template('budget/add_account.html')
