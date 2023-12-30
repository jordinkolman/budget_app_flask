import sys
import os

from datetime import datetime

from Transaction import Transaction

def main():
    transactions = []

    print('Budget App')
    option = ''
    while True:
        while option not in [0, 1, 2]:
            option = int(input('Press 1 to enter a new transaction, or 2 to see a list of transactions. Press 0 to exit. \n'))
        match option:
            case 1:
                transactions.append(new_transaction())
                option = int(input('\nPress 1 to enter a new transaction, or 2 to see a list of transactions. Press 0 to exit. \n'))
            case 2:
                os.system('clear')
                print('Date         Time    Transaction    Category    Amount    Description')
                for transaction in transactions:
                    print(f'{transaction.date.strftime('%m/%d/%Y')}  {transaction.time}  {transaction.title}     {transaction.category}    {transaction.amount}    {transaction.description}')
                option = int(input('\nPress 1 to enter a new transaction, or 2 to see a list of transactions. Press 0 to exit. \n'))
            case 0:
                sys.exit()

def new_transaction():
    os.system('clear')
    print('New Transaction')
    date = datetime.strptime(input('Date (MM/DD/YYYY): '), '%m/%d/%Y').date()
    time = datetime.strptime(input('Time (HH:MM:SS): '), '%H:%M:%S').time()
    title = input('Transaction: ')
    trans_type = input('Income/Expense: ')
    category = input('Category: ')
    amount = float(input("Amount: "))
    description = input('Description: ')

    return Transaction(trans_type, title, date, time, category, amount, description)

if __name__ == "__main__":
    main()
