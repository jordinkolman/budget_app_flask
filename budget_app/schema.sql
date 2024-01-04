DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS transaction_types;
DROP TABLE IF EXISTS account_types;
DROP TABLE IF EXISTS vendors;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date_occurred TEXT NOT NULL,
    time_occurred TEXT NOT NULL,
    vendor_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    account_id INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (vendor_id) REFERENCES vendor (id),
    FOREIGN KEY (category_id) REFERENCES categories (id),
    FOREIGN KEY (type_id) REFERENCES transaction_types (id),
    FOREIGN KEY (account_id) REFERENCES account (id)
);

CREATE TABLE account (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT UNIQUE NOT NULL,
    balance REAL NOT NULL,
    account_type TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE transaction_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE account_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)

CREATE TABLE vendors (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO transaction_types (name) VALUES ('Income');
INSERT INTO transaction_types (name) VALUES ('Expense');

INSERT INTO account_types (name) VALUES ('Checking');
INSERT INTO account_types (name) VALUES ('Savings');
INSERT INTO account_types (name) VALUES ('Credit');
