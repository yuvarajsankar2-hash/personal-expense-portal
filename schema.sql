PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('Received', 'Spend')),
    amount REAL NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_transactions_user_date
    ON transactions(user_id, transaction_date);

-- Sample data uses a placeholder password hash. The application creates real hashes.
INSERT INTO users (full_name, email, password_hash)
VALUES ('Demo User', 'demo@example.com', 'replace-with-werkzeug-password-hash');

INSERT INTO transactions (user_id, transaction_date, transaction_type, amount, category, description)
VALUES
    (1, date('now'), 'Received', 50000.00, 'Salary', 'Monthly salary'),
    (1, date('now'), 'Spend', 2500.00, 'Food', 'Groceries'),
    (1, date('now'), 'Spend', 8000.00, 'Rent', 'House rent'),
    (1, date('now'), 'Spend', 1500.00, 'Travel', 'Local travel');

-- Replace :user_id, :from_date and :to_date with application parameters.
-- Summary totals.
SELECT
    COALESCE(SUM(CASE WHEN transaction_type = 'Received' THEN amount ELSE 0 END), 0) AS total_received,
    COALESCE(SUM(CASE WHEN transaction_type = 'Spend' THEN amount ELSE 0 END), 0) AS total_spent,
    COALESCE(SUM(CASE WHEN transaction_type = 'Received' THEN amount ELSE -amount END), 0) AS balance
FROM transactions
WHERE user_id = :user_id
  AND transaction_date BETWEEN :from_date AND :to_date;

-- Category totals for the charts.
SELECT transaction_type, category, SUM(amount) AS total_amount
FROM transactions
WHERE user_id = :user_id
  AND transaction_date BETWEEN :from_date AND :to_date
GROUP BY transaction_type, category
ORDER BY total_amount DESC;

-- Last five transactions.
SELECT transaction_date, transaction_type, amount, category, description
FROM transactions
WHERE user_id = :user_id
ORDER BY transaction_date DESC, transaction_id DESC
LIMIT 5;
