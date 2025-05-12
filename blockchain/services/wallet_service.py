import os
import json
from datetime import datetime
from ..core.database import Database

class WalletService:
    def __init__(self):
        self.db = Database()
        self.wallets_file = os.path.join(os.path.dirname(__file__), '..', '..', 'wallets.json')
        self.load_wallets()

    def load_wallets(self):
        if os.path.exists(self.wallets_file):
            with open(self.wallets_file, 'r') as f:
                self.wallets = json.load(f)
        else:
            self.wallets = {}
            self.save_wallets()

    def save_wallets(self):
        with open(self.wallets_file, 'w') as f:
            json.dump(self.wallets, f, indent=4)

    def create_wallet(self, user_email):
        if user_email in self.wallets:
            return self.wallets[user_email]['address']

        wallet_address = f"0x{os.urandom(8).hex().upper()}"
        self.wallets[user_email] = {
            'address': wallet_address,
            'balance': 0.0,
            'created_at': datetime.now().isoformat()
        }
        self.save_wallets()
        return wallet_address

    def get_balance(self, wallet):
        if wallet in self.wallets:
            return self.wallets[wallet]['balance']
        return 0.0

    def transfer_coins(self, from_wallet, to_wallet, amount):
        if from_wallet not in self.wallets:
            raise ValueError(f"Wallet {from_wallet} does not exist")
        if to_wallet not in self.wallets:
            raise ValueError(f"Wallet {to_wallet} does not exist")

        from_balance = self.wallets[from_wallet]['balance']
        if from_balance < amount:
            raise ValueError(f"Insufficient funds in wallet {from_wallet}")

        print(f"\nПопытка перевода {amount} монет")
        print(f"От: {from_wallet}")
        print(f"Кому: {to_wallet}")
        print(f"Баланс отправителя до перевода: {from_balance}")
        print(f"Баланс получателя до перевода: {self.wallets[to_wallet]['balance']}")

        self.wallets[from_wallet]['balance'] -= amount
        self.wallets[to_wallet]['balance'] += amount
        self.save_wallets()

        print("Перевод успешно выполнен!")
        print(f"Новый баланс отправителя: {self.wallets[from_wallet]['balance']}")
        print(f"Новый баланс получателя: {self.wallets[to_wallet]['balance']}")
        print(f"Баланс кошелька {from_wallet}: {self.wallets[from_wallet]['balance']}")
        print(f"Баланс кошелька {to_wallet}: {self.wallets[to_wallet]['balance']}")

    def add_coins(self, wallet, amount):
        if wallet not in self.wallets:
            raise ValueError(f"Wallet {wallet} does not exist")

        self.wallets[wallet]['balance'] += amount
        self.save_wallets()
        print(f"Баланс кошелька {wallet}: {self.wallets[wallet]['balance']}")

    def get_wallet_address(self, user_email):
        if user_email in self.wallets:
            return self.wallets[user_email]['address']
        return None 