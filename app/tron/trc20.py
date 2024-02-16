from flask import Blueprint, jsonify, request, current_app
from tronpy import Tron, Contract
import os
import json

from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey

tron = Blueprint('tron', __name__)


def get_client():
    config = current_app.config['networks'].get('trc20')
    if not config:
        return None, 'Client not supported'

    api_key = config.get('api_key')
    client = Tron(HTTPProvider(api_key=api_key))
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


@tron.route('/get_balance_gas/<address>', methods=['GET'])
def get_balance_gas(address):
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    balance = client.get_account_balance(address)
    return jsonify({'balance': balance})\

@tron.route('/get_energy/<address>', methods=['GET'])
def get_energy(address):
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    account_info = client.get_account(address)

    return jsonify({'acc': account_info})


@tron.route('/get_balance_usdt/<address>', methods=['GET'])
def get_balance_usdt(address):
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    # Получение контракта TRC20
    network = 'trc20'
    contract = get_contract(client, network)
    # Вызов функции balanceOf контракта
    balance = contract.functions.balanceOf(address)

    # Конвертация баланса из Wei (если ваш токен использует другие единицы, примените соответствующее преобразование)
    decimals = current_app.config['networks'][network]['decimals']
    balance_converted = balance / (10 ** decimals)

    return jsonify({'balance': balance_converted})


@tron.route('/transfer_gas', methods=['POST'])
def transfer_gas():
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    data = request.json
    from_private_key = data['from_private_key']
    from_address = data['from_address']
    private_key = PrivateKey(bytes.fromhex(from_private_key))
    to_address = data['to_address']
    amount = data['amount']
    decimals = current_app.config['networks']['trc20']['decimals']
    amount = int(amount * (10 ** decimals))
    txn = (
        client.trx.transfer(from_address, to_address, amount)
        .build()
        .sign(private_key)
    )
    txn_ret = client.broadcast(txn)
    return jsonify({'status': 'sent', 'tx_hash': txn_ret})


@tron.route('/transfer_usdt', methods=['POST'])
def transfer_usdt():
    client, error = get_client()
    if error:
        return jsonify({'error': error}), 400

    data = request.json
    from_address = data['from_address']
    from_private_key = data['from_private_key']
    to_address = data['to_address']
    amount = data['amount']
    decimals = current_app.config['networks']['trc20']['decimals']
    amount = int(amount * (10 ** decimals))
    client, error = get_client()
    network = 'trc20'
    contract = get_contract(client, network)
    private_key = PrivateKey(bytes.fromhex(from_private_key))
    txn = (
        contract.functions.transfer(to_address, amount)
        .with_owner(from_address)
        .fee_limit(current_app.config['networks']['trc20']['fee_limit'])
        .build()
        .sign(private_key)
    )

    txn_ret = client.broadcast(txn)
    return jsonify({'status': 'sent', 'tx_hash': txn_ret})