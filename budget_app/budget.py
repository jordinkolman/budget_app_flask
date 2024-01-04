from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from budget_app.auth import login_required
from budget_app.db import get_db

import re

bp = Blueprint("budget", __name__)


def get_id(title, table):
    db = get_db()
    table_vals = []

    if table in ["vendors", "categories"]:
        query = f"SELECT name FROM {table}"
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



def get_account(id, check_user=True):
    account = (
        get_db()
        .execute(
            "SELECT a.id, a.name, balance, ty.name, user_id, username"
            " FROM accounts a JOIN user u ON a.user_id = u.id"
            " JOIN account_types ty ON a.type_id = ty.id"
            " WHERE a.id = ?",
            (id,),
        )
        .fetchone()
    )

    if account is None:
        abort(404, f"Account ID {id} doesn't exist")

    if check_user and account["user_id"] != g.user["id"]:
        abort(403)

    return account


def update_balance(account_id, amount, transaction_type):
    account = get_account(account_id)
    if account is None:
        abort(404, f"Account ID {account_id} does not exist")
    account_balance = float(account['balance'])
    if transaction_type == 'Income':
        account_balance += amount
    else:
        account_balance -= amount
    db = get_db()
    db.execute(
        'UPDATE accounts SET balance = ? WHERE id = ?', (account_balance, account_id)
    )
    db.commit()

    return


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    db = get_db()
    if request.method == "POST":
        date = request.form["date"]
        time = request.form["time"]
        vendor = request.form["vendor"]
        category = request.form["category"]
        transaction_type = request.form["transaction_type"]
        amount = request.form["amount"]
        account = request.form["account"]
        error = None

        if not date:
            error = "Date is Required"
        # I want the time field for when I add account linking for automatic updates, but I don't expect to actually track all my transaction times
        # So rather than make it required I just set a default time
        elif not time:
            time = '12:00'
        elif not vendor:
            error = "Vendor is Required"
        elif not category:
            error = "Category is Required"
        elif not amount:
            amount = 0.0

        if not re.fullmatch(r"(3[01]|[12][0-9]|0[1-9])/(1[0-2]|0[1-9])/[0-9]{4}", date):
            error = "Date must be in format MM/DD/YYYY, including leading zeroes"


        accounts = db.execute(
            "SELECT * FROM accounts WHERE user_id = ? ORDER BY name", (g.user["id"],)
        ).fetchall()
        print(accounts)
        account_id = None
        for acc in accounts:
            if acc[2] == account:
                account_id = acc["id"]

        if account_id is None:
            error = "Invalid Account. Please Enter a Valid Account or Add a New One."

        if error is not None:
            flash(error)
        else:
            category_id = get_id(title=category, table="categories")
            vendor_id = get_id(title=vendor, table="vendors")
            # Because get_id() inserts a new entry if the queried entry doesn't exist, I don't want to use it for type_id, which I only want to be Income or Expense
            # So we just return the first element of the row returned by the fetchone query
            type_id = db.execute("SELECT id FROM transaction_types WHERE name = ?",(transaction_type,)).fetchone()[0]

            db.execute(
                "INSERT INTO transactions (user_id, date_occurred, time_occurred, vendor_id, category_id, type_id, amount, account_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    g.user["id"],
                    date,
                    time,
                    vendor_id,
                    category_id,
                    type_id,
                    amount,
                    account_id,
                ),
            )
            db.commit()
            update_balance(account_id, float(amount), transaction_type)
            return redirect(url_for("budget.index"))

    accounts = db.execute(
        "SELECT a.id, a.name, balance, ty.name ty_name FROM accounts a"
        " JOIN account_types ty ON a.type_id = ty.id"
        " WHERE user_id = ?",
        (g.user["id"],),
    ).fetchall()

    transactions = db.execute(
        "SELECT t.id, date_occurred, time_occurred, v.name v_name, c.name c_name, ty.name ty_name, amount, a.name a_name"
        " FROM transactions t JOIN vendors v ON t.vendor_id = v.id"
        "  JOIN categories c ON t.category_id = c.id"
        "  JOIN transaction_types ty ON t.type_id = ty.id"
        "  JOIN accounts a ON t.account_id = a.id"
        "  WHERE t.user_id = ?",
        (g.user["id"],),
    ).fetchall()

    types = db.execute(
        'SELECT id, name FROM types'
    ).fetchall()

    return render_template(
        "budget/index.html", accounts=accounts, transactions=transactions, types=types,
    )



@bp.route("/<int:id>/delete_transaction", methods=("POST",))
@login_required
def delete_transaction(id):
    db = get_db()
    account_id, amount, transaction_type = db.execute('SELECT account_id, amount, ty.name FROM transactions t JOIN transaction_types ty ON t.type_id = ty.id WHERE t.id = ?', (id,)).fetchone()
    if transaction_type == 'Expense':
        transaction_type = 'Income'
    else:
        transaction_type = 'Expense'
    update_balance(account_id, amount, transaction_type)
    db.execute("DELETE FROM transactions WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("budget.index"))


@bp.route("/add_account", methods=("GET", "POST"))
@login_required
def add_account():
    if request.method == "POST":
        db = get_db()
        name = request.form["name"]
        balance = request.form["balance"]
        account_type = request.form["account_type"]
        type_id = db.execute('SELECT id FROM account_types WHERE name = ?', (account_type,)).fetchone()[0]
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
            db.execute(
                "INSERT INTO accounts (user_id, name, balance, type_id) VALUES (?, ?, ?, ?)",
                (
                    g.user["id"],
                    name,
                    balance,
                    type_id,
                ),
            )
            db.commit()
            return redirect(url_for("budget.index"))

    return render_template("budget/add_account.html")


@bp.route("/<int:id>/update_account", methods=("GET", "POST"))
@login_required
def update_account(id):
    account = get_account(id)

    if request.method == "POST":
        name = request.form["name"]
        balance = request.form["balance"]
        account_type = request.form["account_type"]
        type_id = db.execute('SELECT id FROM account_types WHERE name = ?', (account_type,)).fetchone()[0]
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
                "UPDATE accounts SET name = ?, balance = ?, type_id = ? WHERE id = ?",
                (name, balance, type_id, id),
            )
            db.commit()
            return redirect(url_for("budget.index"))

    return render_template("budget/update_account.html", account=account)


@bp.route("/<int:id>/delete_account", methods=("POST",))
@login_required
def delete_account(id):
    get_account(id)
    db = get_db()
    db.execute("DELETE FROM accounts WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("budget.index"))
