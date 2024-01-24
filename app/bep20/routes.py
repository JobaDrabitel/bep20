from flask import Flask, jsonify, request, Blueprint
from web3 import Web3, HTTPProvider
import json

bep20 = Blueprint('bep20', __name__)
w3 = Web3(HTTPProvider('https://bsc-dataseed.binance.org/'))


@bep20.route('/create_wallet', methods=['GET'])
def create_wallet():
    account = w3.eth.account.create()
    private_key_hex = account.key.hex()
    address = account.address
    return json.dumps({'private_key': private_key_hex, 'address': address})


@bep20.route('/get_balance_bnb/<address>', methods=['GET'])
def get_balance_bnb(address):
    balance = w3.eth.get_balance(address)
    return jsonify({'balance': balance*10**-18})


@bep20.route('/get_balance_usdt/<address>', methods=['GET'])
def get_balance_usdt(address):
    usdt_contract = w3.eth.contract(address=usdt_contract_address, abi=abi)
    balance = usdt_contract.functions.balanceOf(account=address).call()
    print(balance)
    return jsonify({'balance': balance*10**-18})


usdt_contract_address = '0x55d398326f99059fF775485246999027B3197955'
with open('api.json', 'r') as file:
    abi = json.load(file)


@bep20.route('/transfer_bnb', methods=['POST'])
def transfer_bnb():
    data = request.json
    from_address = data['from_address']
    to_address = data['to_address']
    amount = data['amount']
    from_private_key = data['from_private_key']
    nonce = w3.eth.get_transaction_count(from_address)
    tx = {
        'from': from_address,
        'to': to_address,
        'value': Web3.to_wei(amount, 'finney'),
        'gas': 70000,
        'gasPrice': 3000000000,
        'nonce': nonce,
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=from_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return jsonify({'status': 'sent', 'tx_hash': tx_hash.hex()})


@bep20.route('/transfer_usdt', methods=['POST'])
def transfer_usdt():
        data = request.json
        from_private_key = data['from_private_key']
        from_address = data['from_address']
        to_address = data['to_address']
        amount = data['amount']
        usdt_contract = w3.eth.contract(address=usdt_contract_address, abi=abi)
        print(from_address)
        usdt_contract.functions.approve(spender=from_address, amount=Web3.to_wei(amount, 'ether'))
        transfer_txn = usdt_contract.functions.transfer(to_address, Web3.to_wei(amount, 'ether')).build_transaction({
            'chainId': 56,
            'from': from_address,
            'nonce': w3.eth.get_transaction_count(from_address),
            'gasPrice': 3000000000,
            'gas': 70000
        })
        signed_transfer_txn = w3.eth.account.sign_transaction(transfer_txn, private_key=from_private_key)
        transfer_tx_hash = w3.eth.send_raw_transaction(signed_transfer_txn.rawTransaction)
        w3.eth.wait_for_transaction_receipt(transfer_tx_hash)
        return transfer_tx_hash.hex()


@bep20.route('/increase_allowance', methods=['POST'])
def increase_allowance():
    data = request.json
    from_private_key = data['from_private_key']
    owner_address = data['from_address']
    spender_address = data['to_address']
    additional_amount = data['amount']

    usdt_contract = w3.eth.contract(address=usdt_contract_address, abi=abi)

    # Подготовка транзакции для increaseAllowance
    increase_txn = usdt_contract.functions.increaseAllowance(spender_address, additional_amount).build_transaction({
        'chainId': 56,
        'from': owner_address,
        'nonce': w3.eth.get_transaction_count(owner_address),
        'gasPrice': 3000000000,
        'gas': 70000
    })

    # Подписываем транзакцию
    signed_increase_txn = w3.eth.account.sign_transaction(increase_txn, private_key=from_private_key)

    # Отправляем транзакцию в сеть
    increase_tx_hash = w3.eth.send_raw_transaction(signed_increase_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(increase_tx_hash)

    return jsonify({'status': 'success', 'tx_hash': increase_tx_hash.hex()})
