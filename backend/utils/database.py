import sqlite3
import json
import os

class Database:
    def __init__(self, db_file="blockchain.db"):
        self.db_file = db_file
        self.conn = None
        self.init_db()

    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Blocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                block_index INTEGER PRIMARY KEY,
                hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                timestamp REAL NOT NULL,
                nonce INTEGER NOT NULL,
                transactions_json TEXT NOT NULL
            )
        ''')

        # Transactions table (for history/explorer)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                tx_hash TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp REAL NOT NULL,
                signature TEXT,
                block_index INTEGER,
                FOREIGN KEY (block_index) REFERENCES blocks (block_index)
            )
        ''')

        # Accounts table (for fast balance lookups - Account Model)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                address TEXT PRIMARY KEY,
                balance REAL DEFAULT 0
            )
        ''')

        # Wallets table (for server-side wallet persistence)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT PRIMARY KEY,
                public_key TEXT NOT NULL,
                private_key TEXT NOT NULL
            )
        ''')

        conn.commit()

    def save_block(self, block):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Save Block
            cursor.execute('''
                INSERT OR IGNORE INTO blocks (block_index, hash, previous_hash, timestamp, nonce, transactions_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                block.index,
                block.hash,
                block.previous_hash,
                block.timestamp,
                block.nonce,
                json.dumps([tx.to_dict() for tx in block.transactions])
            ))

            # Save Transactions and Update Balances
            for tx in block.transactions:
                # Save Transaction
                cursor.execute('''
                    INSERT OR IGNORE INTO transactions (tx_hash, sender, recipient, amount, timestamp, signature, block_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tx.calculate_hash(),
                    tx.sender,
                    tx.recipient,
                    tx.amount,
                    tx.timestamp,
                    tx.signature,
                    block.index
                ))

                # Update Balances (Atomic update)
                # Sender deduction (if not reward)
                if tx.sender != "GENESIS" and tx.sender != "MINING_REWARD":
                    cursor.execute('''
                        INSERT INTO accounts (address, balance) VALUES (?, ?)
                        ON CONFLICT(address) DO UPDATE SET balance = balance - ?
                    ''', (tx.sender, -tx.amount, tx.amount))

                # Recipient addition
                cursor.execute('''
                    INSERT INTO accounts (address, balance) VALUES (?, ?)
                    ON CONFLICT(address) DO UPDATE SET balance = balance + ?
                ''', (tx.recipient, tx.amount, tx.amount))

            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving block: {e}")
            conn.rollback()
            return False

    def save_wallet(self, wallet):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO wallets (address, public_key, private_key)
                VALUES (?, ?, ?)
            ''', (wallet.address, wallet.public_key, wallet.private_key))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving wallet: {e}")
            return False

    def get_wallet(self, address):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wallets WHERE address = ?', (address,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all_wallets(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wallets')
        return [dict(row) for row in cursor.fetchall()]

    def get_last_block(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM blocks ORDER BY block_index DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_chain(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM blocks ORDER BY block_index ASC')
        return [dict(row) for row in cursor.fetchall()]

    def get_balance(self, address):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM accounts WHERE address = ?', (address,))
        row = cursor.fetchone()
        return row['balance'] if row else 0.0

    def close(self):
        if self.conn:
            self.conn.close()
