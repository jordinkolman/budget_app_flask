INSERT INTO user (username, password)
VALUES
    ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f')
    ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79')

INSERT INTO transactions (user_id, date_occurred, time_occurred, vendor_id, category_id, type_id, amount, account_id, notes)
VALUES
    (1, date(datetime('now')), time(datetime('now')), 1, 1, 1, 1.0, 1, 'none')

INSERT INTO account (user_id, balance, account_type, name)
VALUES
    (1, 10000.00, 'checking', 'Chime')

INSERT INTO categories (name) VALUES (test_category)

INSERT INTO vendors (name) values (test_vendor)
