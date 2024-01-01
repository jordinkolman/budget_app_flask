from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from budget_app.auth import login_required
from budget_app.db import get_db

bp = Blueprint('budget', __name__)

def get_id(title, table):
    db = get_db()
    table_vals = []

    if table in ['vendors', 'categories']:
        query = f'SELECT name FROM {table}'
        table_rows = db.execute(query).fetchall()
        for row in table_rows:
            table_vals.append(row[0])
        print(table_vals)
    else:
        raise ValueError

    if title not in table_vals:
        query = f"INSERT INTO {table} (name) VALUES ('{title}')"
        db.execute(query)
        db.commit()

    query = f'SELECT id FROM {table} WHERE (name="{title}")'
    return db.execute(query).fetchone()[0]


@bp.route('/', methods=("GET", "POST"))
@login_required
def index():
    db = get_db()
    if request.method == "POST":
        date = request.form['date']
        time = request.form['time']
        vendor = request.form['vendor']
        category = request.form['category']
        transaction_type = request.form['transaction_type']
        amount = request.form['amount']
        account = request.form['account']
        error = None

        if not date:
            error = 'Date is Required'
        elif not time:
            error = 'Time is Required'
        elif not vendor:
            error = 'Vendor is Required'
        elif not category:
            error = 'Category is Required'
        elif not amount:
            amount = 0.0

        accounts = db.execute('SELECT * FROM account WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
        print(accounts)
        account_id = None
        for acc in accounts:
            if acc[2] == account:
                account_id = acc['id']

        if account_id is None:
            error = "Invalid Account. Please Enter a Valid Account or Add a New One."

        if error is not None:
            flash(error)
        else:
            category_id = get_id(title=category, table='categories')
            vendor_id = get_id(title=vendor, table='vendors')
            type_id = 1 if transaction_type == 'Income' else 2

            db.execute(
                'INSERT INTO transactions (user_id, date_occurred, time_occurred, vendor_id, category_id, type_id, amount, account_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (g.user['id'], date, time, vendor_id, category_id, type_id, amount, account_id,)
            )
            db.commit()
            return redirect(url_for('budget.index'))


    accounts = (db.execute(
        'SELECT id, name, balance, account_type FROM account WHERE user_id = ?',
        (g.user["id"],)
    ).fetchall())


    transactions = (db.execute(
        'SELECT date_occurred, time_occurred, v.name v_name, c.name c_name, ty.name ty_name, amount, a.name a_name'
        ' FROM transactions t JOIN vendors v ON t.vendor_id = v.id'
        '  JOIN categories c ON t.category_id = c.id'
        '  JOIN types ty ON t.type_id = ty.id'
        '  JOIN account a ON t.account_id = a.id'
        '  WHERE t.user_id = ?',
        (g.user["id"],)
    ).fetchall())

    return render_template('budget/index.html', accounts=accounts, transactions=transactions)

def get_account(id, check_user=True):
    account = (
        get_db()
        .execute(
            'SELECT a.id, name, balance, account_type, user_id, username'
            ' FROM account a JOIN user u ON a.user_id = u.id'
            ' WHERE a.id = ?',
            (id,),
        )
        .fetchone()
    )

    if account is None:
        abort(404, f"Account ID {id} doesn't exist")

    if check_user and account["id"] != g.user['id']:
        abort(403)

    return account


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

@bp.route('/<int:id>/update_account', methods=("GET", "POST"))
@login_required
def update_account(id):
    account = get_account(id)

    if request.method == 'POST':
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
                "UPDATE account SET name = ?, balance = ?, account_type = ? WHERE id = ?",
                (name, balance, account_type, id)
            )
            db.commit()
            return redirect(url_for('budget.index'))

    return render_template('budget/update_account.html', account=account)

@bp.route("/<int:id>/delete_account", methods=("POST",))
@login_required
def delete_account(id):
    get_account(id)
    db = get_db()
    db.execute("DELETE FROM account WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('budget.index'))
