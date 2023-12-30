from datetime import datetime
from dataclasses import dataclass

CURRENT_TIME = datetime.now()

@dataclass
class Transaction:
    transaction_type: str
    title: str
    date: datetime = CURRENT_TIME.date()
    time: datetime = CURRENT_TIME.time()
    category: str = None
    amount: float = 0.0
    description: str = None

    def __str__(self):
        return f"""Date: {self.date.strftime("%m/%d/%Y")}
Time: {self.time.strftime("%H:%M:%S")}
Transaction: {self.title}
Type: {self.transaction_type}
Category: {self.category}
Amount: {self.amount}
Description: {self.description}"""

if __name__ == "__main__":
    transaction = Transaction("Paycheck", "Income")
    print(transaction)
