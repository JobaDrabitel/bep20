from flask import Blueprint, jsonify, request, current_app
from tronpy import Tron, Contract
import os
import json

from tronpy.providers import HTTPProvider

tron = Blueprint('tron', __name__)

def get_client():
    config = current_app.config['networks'].get('trc20')
    if not config:
        return None, 'Client not supported'

    api_key = config.get('api_key')
    provider_url = f"{config['provider']}?apiKey={api_key}"
    client = Tron(network=provider_url)
    return client, None


def get_contract(client, network):
    config = current_app.config['networks'][network]
    contract_address = config['contract_address']

    contract = client.get_contract(contract_address)
    return contract


@tron.route('/create_wallet', methods=['GET'])
def create_wallet():
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400
    account = client.generate_address()
    return jsonify({'private_key': account['private_key'], 'address': account['base58check_address']})

@tron.route('/get_balance/<address>', methods=['GET'])
def get_balance(address):
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    balance = client.get_account_balance(address)
    return jsonify({'balance': balance})


@tron.route('/get_token_balance/<address>', methods=['GET'])
def get_token_balance(address):
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    # Получение контракта TRC20
    network = 'trc20'
    contract = get_contract(client, network)

    # Вызов функции balanceOf контракта
    balance = contract.functions.balanceOf(address).call()

    # Конвертация баланса из Wei (если ваш токен использует другие единицы, примените соответствующее преобразование)
    decimals = current_app.config['networks'][network]['decimals']
    balance_converted = balance / (10 ** decimals)

    return jsonify({'balance': balance_converted})


@tron.route('/transfer', methods=['POST'])
def transfer(network):
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    data = request.json
    from_private_key = data['from_private_key']
    to_address = data['to_address']
    amount = data['amount']

    with client.trx.sign_and_broadcast(from_private_key) as txn_builder:
        txn_builder.to(to_address).amount(amount)
        txn = txn_builder.build()
        txn_ret = txn.broadcast()

    return jsonify({'status': 'sent', 'tx_hash': txn_ret.txid})

@tron.route('/transfer_token', methods=['POST'])
def transfer_token():
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    data = request.json
    from_address = data['from_address']
    from_private_key = data['from_private_key']
    to_address = data['to_address']
    amount = data['amount']
    client, error = get_client()
    network  = current_app.config['networks'].get('trc20')
    contract = get_contract(client, network)

    txn = (
        contract.functions.transfer(to_address, amount)
        .with_owner(from_address)
        .fee_limit(current_app.config['fee_limit'])
        .build()
        .sign(from_private_key)
    )

    txn_ret = client.broadcast(txn)
    return jsonify({'status': 'sent', 'tx_hash': txn_ret.txid})