import time
import random
import threading
from datetime import datetime
from services.database import get_connection
from services.data_generator import generate_banking_data
from utils import logger

class TransactionSimulator:
    def __init__(self, interval=5):
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        banks = ['SBI', 'HDFC', 'ICICI', 'Axis Bank', 'PNB']
        accs = ['ACC001', 'ACC002', 'ACC003', 'ACC004', 'ACC005']
        
        while self.running:
            time.sleep(self.interval)
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Get latest balance for a random account
                acc = random.choice(accs)
                cursor.execute("SELECT balance, bank FROM transactions WHERE acc_no = ? ORDER BY date DESC LIMIT 1", (acc,))
                res = cursor.fetchone()
                last_bal, bank = res if res else (50000.0, random.choice(banks))
                
                trans_type = random.choice(['Deposit', 'Withdrawal'])
                amount = round(random.uniform(100, 15000), 2)
                
                if trans_type == 'Deposit':
                    new_bal = last_bal + amount
                else:
                    new_bal = last_bal - amount
                
                status = 'Success' if new_bal > 0 else 'Failed'
                if status == 'Failed': new_bal = last_bal
                
                # Simulation logic for fraud (1% chance)
                is_fraud = 1 if (amount > 14000 and trans_type == 'Withdrawal' and random.random() < 0.1) else 0
                
                cursor.execute('''
                    INSERT INTO transactions (date, acc_no, type, bank, amount, balance, status, is_fraud, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), acc, trans_type, bank, amount, new_bal, status, is_fraud, f"Live {trans_type}"))
                
                if is_fraud:
                    cursor.execute("INSERT INTO alerts (severity, message) VALUES (?, ?)", 
                                   ("High", f"Suspicious large withdrawal detected: ₹{amount} from {acc}"))
                    logger.warning(f"FRAUD DETECTED: Account {acc} attempted withdrawal of {amount}")
                
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Simulator Thread Error: {e}")

def seed_initial_data():
    """Seeds the database with 100+ transactions if empty."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        if cursor.fetchone()[0] == 0:
            logger.info("Empty database detected. Seeding initial data...")
            df = generate_banking_data(150)
            # Standardized on lowercase names in generate_banking_data
            df.to_sql('transactions', conn, if_exists='append', index=False)
            logger.info("Seeding complete.")
        conn.close()
    except Exception as e:
        logger.error(f"Seeding failure: {e}")
