import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_banking_data(rows=100):
    """
    Generates a realistic Indian banking dataset with schema-aligned column names.
    """
    transaction_types = ['Deposit', 'Withdrawal']
    statuses = ['Success', 'Success', 'Success', 'Success', 'Failed'] # 80% success rate
    
    # Pre-define accounts for 5 users
    accounts = {
        'ACC001': {'bank': 'SBI', 'balance': 50000.0},
        'ACC002': {'bank': 'HDFC', 'balance': 75000.0},
        'ACC003': {'bank': 'ICICI', 'balance': 30000.0},
        'ACC004': {'bank': 'Axis Bank', 'balance': 120000.0},
        'ACC005': {'bank': 'PNB', 'balance': 45000.0}
    }
    
    data = []
    start_date = datetime.now() - timedelta(days=60) # Generate 60 days of data
    
    for i in range(rows):
        acc_no = random.choice(list(accounts.keys()))
        bank = accounts[acc_no]['bank']
        trans_type = random.choice(transaction_types)
        status = random.choice(statuses)
        
        # Amount logic
        if trans_type == 'Deposit':
            amount = round(random.uniform(500, 50000), 2)
            if status == 'Success':
                accounts[acc_no]['balance'] += amount
        else:
            amount = round(random.uniform(100, 20000), 2)
            if status == 'Success':
                if accounts[acc_no]['balance'] >= amount:
                    accounts[acc_no]['balance'] -= amount
                else:
                    status = 'Failed'
        
        trans_date = start_date + timedelta(
            seconds=random.randint(0, 60*60*24*60) # random second within 60 days
        )
        
        # Use database schema names
        data.append({
            'date': trans_date.strftime('%Y-%m-%d %H:%M:%S'),
            'acc_no': acc_no,
            'type': trans_type,
            'bank': bank,
            'amount': amount,
            'balance': round(accounts[acc_no]['balance'], 2),
            'status': status,
            'is_fraud': 0,
            'description': f"Retail {trans_type}"
        })
    
    df = pd.DataFrame(data)
    df['date_dt'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date_dt').drop(columns=['date_dt']).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    df = generate_banking_data(120)
    print(df.head())
