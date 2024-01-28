from flask import Blueprint, jsonify, request, current_app
from web3 import Web3, HTTPProvider
import json
import os

ether = Blueprint('ether', __name__)


def get_w3(network):
    config = current_app.config['networks'].get(network)
    if not config:
        return None, 'Network not supported'

    w3 = Web3(HTTPProvider(config['provider']))
    return w3, None


def get_contract(w3, network):
    config = current_app.config['networks'][network]
    with open(os.path.join(current_app.root_path, config['abi_file']), 'r') as file:
        abi = json.load(file)

    contract_address = config['contract_address']
    return w3.eth.contract(address=contract_address, abi=abi)


@ether.route('/<network>/create_wallet', methods=['GET'])
def create_wallet(network):
    w3, error = get_w3(network)
    if error:
        return jsonify({'error': error}), 400
    account = w3.eth.account.create()
    return jsonify({'private_key': account.key.hex(), 'address': account.address})


@ether.route('/<network>/get_balance_gas/<address>', methods=['GET'])
def get_balance_bnb(network, address):
    w3, error = get_w3(network)
    if error:
        return jsonify({'error': error}), 400

    balance = w3.eth.get_balance(address)
    return jsonify({'balance': Web3.from_wei(balance, 'ether')})


@ether.route('/<network>/get_balance_usdt/<address>', methods=['GET'])
def get_balance_usdt(network, address):
    w3, error = get_w3(network)
    if error:
        return jsonify({'error': error}), 400

    usdt_contract = get_contract(w3, network)
    balance = usdt_contract.functions.balanceOf(address).call()
    return jsonify({'balance': balance * 10**-18})


@ether.route('/<network>/transfer_gas', methods=['POST'])
def transfer_bnb(network):
    w3, error = get_w3(network)
    if error:
        return jsonify({'error': error}), 400

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
        'gas': current_app.config['networks'][network]['gas'],
        'gasPrice': current_app.config['networks'][network]['gasPrice'],
        'nonce': nonce,
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=from_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return jsonify({'status': 'sent', 'tx_hash': tx_hash.hex()})


@ether.route('/<network>/transfer_usdt', methods=['POST'])
def transfer_usdt(network):
    w3, error = get_w3(network)
    if error:
        return jsonify({'error': error}), 400

    data = request.json
    usdt_contract = get_contract(w3, network)

    from_private_key = data['from_private_key']
    from_address = data['from_address']
    to_address = data['to_address']
    amount = data['amount']

    # Получение десятичных разрядов из конфига для соответствующей сети
    decimals = current_app.config['networks'][network]['decimals']
    amount_in_wei = int(amount * (10 ** decimals))

    usdt_contract.functions.approve(from_address, amount_in_wei)
    transfer_txn = usdt_contract.functions.transfer(to_address, amount_in_wei).build_transaction({
        'chainId': w3.eth.chain_id,
        'from': from_address,
        'nonce': w3.eth.get_transaction_count(from_address),
        'gas': current_app.config['networks'][network]['gas'],
        'gasPrice': current_app.config['networks'][network]['gasPrice']
    })
    signed_transfer_txn = w3.eth.account.sign_transaction(transfer_txn, private_key=from_private_key)
    transfer_tx_hash = w3.eth.send_raw_transaction(signed_transfer_txn.rawTransaction)
    return jsonify({'status': 'sent', 'tx_hash': transfer_tx_hash.hex()})

