import requests
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64,hashlib

class BlockchainCLI:
    def __init__(self, node_url="http://127.0.0.1:5000"):
        self.node_url = node_url
        self.private_key = None
        self.public_key = None
    
    def generate_wallet(self):
        private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        public_key = private_key.public_key()
        
        self.private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        
        self.public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        
        print("\nНовый кошелёк создан!")
        print(f"\nПриватный ключ:\nя{self.private_key}")
        print(f"\nПубличный ключ (адрес):\n{self.public_key}")
        print("\nСохраните эти ключи в безопасном месте!")
    
    def sign_transaction(self, transaction_data):
        if not self.private_key:
            print("Ошибка: Сначала создайте или загрузите кошелёк")
            return None
            
        private_key = serialization.load_pem_private_key(
            self.private_key.encode(),
            password=None,
            backend=default_backend()
        )
        
        transaction_str = json.dumps(transaction_data, sort_keys=True)
        digest = hashlib.sha256(transaction_str.encode()).digest()

        signature = private_key.sign(
            digest,
            ec.ECDSA(hashes.SHA256())
        )
        
        return base64.b64encode(signature).decode()
    
    def send_transaction(self):
        if not self.public_key:
            print("Ошибка: Сначала создайте или загрузите кошелёк")
            return
            
        receiver = input("Введите адрес получателя: ")
        amount = input("Введите сумму: ")
        
        try:
            amount = float(amount)
        except ValueError:
            print("Ошибка: Сумма должна быть числом")
            return
            
        transaction = {
            "sender": self.public_key,
            "receiver": receiver,
            "amount": amount
        }
        
        signature = self.sign_transaction(transaction)
        if not signature:
            return
            
        transaction["signature"] = signature
        
        response = requests.post(
            f"{self.node_url}/transactions/new",
            json=transaction
        )
        
        if response.status_code == 201:
            print("\nТранзакция успешно отправлена!")
        else:
            print(f"\nОшибка при отправке транзакции: {response.text}")
    
    def mine_block(self):
        if not self.public_key:
            print("Ошибка: Сначала создайте или загрузите кошелёк")
            return
            
        response = requests.get(
            f"{self.node_url}/mine",
            params={"miner": self.public_key}
        )
        
        if response.status_code == 200:
            print("\nНовый блок успешно создан!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nОшибка при майнинге блока: {response.text}")
    
    def view_chain(self):
        response = requests.get(f"{self.node_url}/chain")
        
        if response.status_code == 200:
            chain_data = response.json()
            print(f"\nДлина цепочки: {chain_data['length']}")
            print("\nБлоки в цепочке:")
            for block in chain_data["chain"]:
                print(f"\nБлок #{block['index']}:")
                print(f"Временная метка: {block['timestamp']}")
                print(f"Хеш предыдущего блока: {block['previous_hash']}")
                print(f"Доказательство работы: {block['proof']}")
                print(f"Количество транзакций: {len(block['transactions'])}")
        else:
            print(f"\nОшибка при получении цепочки: {response.text}")
    
    def view_wallets(self):
        try:
            response = requests.get(f"{self.node_url}/wallets")
            if response.status_code == 200:
                wallets_data = response.json()
                print(f"\nВсего кошельков в сети: {wallets_data['count']}")
                print("\nСписок кошельков (публичных ключей):")
                for i, wallet in enumerate(wallets_data['wallets'], 1):
                    print(f"\nКошелёк #{i}:")
                    print(wallet)
            else:
                print(f"\nОшибка сервера: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"\nОшибка соединения: {e}")
    
    def load_wallet(self):
        private_key_file = input("Введите путь к файлу с приватным ключом: ")
        
        try:
            with open(private_key_file, "r") as f:
                self.private_key = f.read()
                
            priv_key = serialization.load_pem_private_key(
                self.private_key.encode(),
                password=None,
                backend=default_backend()
            )
            self.public_key = priv_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode()
            
            print("\nКошелёк успешно загружен!")
            print(f"\nАдрес: {self.public_key}")
        except Exception as e:
            print(f"\nОшибка при загрузке кошелька: {e}")
            self.private_key = None
            self.public_key = None
    
    def run(self):
        print("\n=== Консольный интерфейс управления блокчейном ===")
        
        while True:
            print("\nВыберите действие:")
            print("1. Создать новый кошелёк")
            print("2. Загрузить кошелёк из файла")
            print("3. Отправить транзакцию")
            print("4. Майнить блок")
            print("5. Просмотреть цепочку блоков")
            print("6. Просмотреть все кошельки")
            print("7. Выход")
            
            choice = input("> ")
            
            if choice == "1":
                self.generate_wallet()
            elif choice == "2":
                self.load_wallet()
            elif choice == "3":
                self.send_transaction()
            elif choice == "4":
                self.mine_block()
            elif choice == "5":
                self.view_chain()
            elif choice == "6":
                self.view_wallets()
            elif choice == "7":
                print("Выход из программы...")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    cli = BlockchainCLI()
    cli.run()