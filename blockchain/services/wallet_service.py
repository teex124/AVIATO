import random
import string
from typing import Optional, List, Tuple
from blockchain.core.database import Database, UserRepository, HashRepository

class WalletService:
    def __init__(self):
        self.db = Database()
        self.user_repo = UserRepository(self.db)
        self.hash_repo = HashRepository(self.db)
    
    def generate_wallet(self) -> str:
        """Generate new wallet address"""
        return '0x' + ''.join(random.choices(string.hexdigits, k=10))
    
    def verify_login(self, words: List[str]) -> Optional[str]:
        """Verify login words and return wallet if valid"""
        result = self.user_repo.get_user_by_words(words)
        return result[0] if result else None
    
    def create_account(self, word_indexes: List[int]) -> Optional[str]:
        """Create new account with generated wallet"""
        wallet = self.generate_wallet()
        if self.user_repo.create_user(word_indexes, wallet):
            return wallet
        return None
    
    def get_balance(self, wallet: str) -> float:
        """Get wallet balance"""
        balance = self.user_repo.get_balance(wallet)
        print(f"Баланс кошелька {wallet}: {balance}")
        return balance
    
    def transfer_coins(self, from_wallet: str, to_wallet: str, amount: float) -> bool:
        """Transfer coins between wallets"""
        print(f"\nПопытка перевода {amount} монет")
        print(f"От: {from_wallet}")
        print(f"Кому: {to_wallet}")
        
        from_balance = self.user_repo.get_balance(from_wallet)
        to_balance = self.user_repo.get_balance(to_wallet)
        
        print(f"Баланс отправителя до перевода: {from_balance}")
        print(f"Баланс получателя до перевода: {to_balance}")
        
        if from_balance < amount:
            print(f"Ошибка: недостаточно средств. Нужно: {amount}, Доступно: {from_balance}")
            return False
            
        # Update both balances
        if not self.user_repo.update_balance(from_wallet, from_balance - amount):
            print("Ошибка при обновлении баланса отправителя")
            return False
            
        if not self.user_repo.update_balance(to_wallet, to_balance + amount):
            print("Ошибка при обновлении баланса получателя")
            # Rollback if second update fails
            self.user_repo.update_balance(from_wallet, from_balance)
            return False
        
        print("Перевод успешно выполнен!")
        print(f"Новый баланс отправителя: {self.user_repo.get_balance(from_wallet)}")
        print(f"Новый баланс получателя: {self.user_repo.get_balance(to_wallet)}")
        return True
    
    def mine_block(self, wallet: str) -> bool:
        """Mine new block and reward wallet"""
        current_difficulty = self.hash_repo.get_current_difficulty()
        reward = 100.0 / current_difficulty
        
        print(f"\nМайнинг блока")
        print(f"Текущая сложность: {current_difficulty}")
        print(f"Награда: {reward}")
        
        current_balance = self.user_repo.get_balance(wallet)
        new_balance = current_balance + reward
        
        print(f"Баланс до майнинга: {current_balance}")
        print(f"Баланс после майнинга: {new_balance}")
        
        if not self.user_repo.update_balance(wallet, new_balance):
            print("Ошибка при обновлении баланса после майнинга")
            return False
            
        # Increase difficulty after successful mining
        if self.hash_repo.increase_difficulty():
            print("Сложность майнинга увеличена")
        return True 