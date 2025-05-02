import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.nodes = set()
        self.create_block(proof=1, previous_hash="0")

    def create_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.pending_transactions,
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount, signature):
        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "signature": signature,
        }
        self.pending_transactions.append(transaction)
        return self.last_block["index"] + 1


    def mine_block(self, miner_address):
        last_block = self.last_block
        last_proof = last_block["proof"]
        proof = self.proof_of_work(last_proof)
        self.add_transaction(
            sender="0",
            receiver=miner_address,
            amount=1,
            signature="0",
        )
        previous_hash = self.hash(last_block)
        block = self.create_block(proof, previous_hash)
        return block

    @staticmethod
    def proof_of_work(last_proof):
        proof = 0
        while not Blockchain.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def get_all_wallets(self):
        wallets = set()
        for block in self.chain:
            for tx in block["transactions"]:
                wallets.add(tx["sender"])
                wallets.add(tx["receiver"])
        for tx in self.pending_transactions:
            wallets.add(tx["sender"])
            wallets.add(tx["receiver"])
        return list(wallets)

    @property
    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)
blockchain = Blockchain()

@app.route("/mine", methods=["GET"])
def mine():
    miner_address = request.args.get("miner")
    block = blockchain.mine_block(miner_address)
    response = {
        "message": "Новый блок создан!",
        "block": block,
    }
    return jsonify(response), 200

@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()
    required = ["sender", "receiver", "amount", "signature"]
    if not all(k in values for k in required):
        return "Не хватает данных", 400
    blockchain.add_transaction(
        values["sender"], values["receiver"], values["amount"], values["signature"]
    )
    return "Транзакция добавлена", 201

@app.route("/   ", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route("/wallets", methods=["GET"])
def get_wallets():
    wallets = blockchain.get_all_wallets()
    response = {
        "wallets": wallets,
        "count": len(wallets),
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)