# config.py

networks = {
    'erc20': {
        'provider': 'https://mainnet.infura.io/v3/68bdfbf2b7a14287b3ab91afb2feba3d',
        'contract_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'abi_file': 'ether/abi/erc_abi.json',
        'gas': 50000,  # Можно увеличить до 100000, если требуется
        'gasPrice': 47000000000,  # 12 Gwei в wei
        'decimals': 6,
    },
    'bep20': {
        'provider': 'https://bsc-dataseed.binance.org/',
        'contract_address': '0x55d398326f99059fF775485246999027B3197955',
        'abi_file': 'ether/abi/bep_abi.json',
        'gas': 70000,
        'gasPrice': 3000000000,
        'decimals': 18,
    },
    'trc20': {
        'provider': 'https://api.trongrid.io',
        'api_key': 'c71f2212-2803-4128-a265-719a3425d882',
        'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
        'abi_file': 'tron/abi/trx_abi.json',
        'fee_limit': 10000000,  # Лимит комиссии в SUN (1 TRX = 1,000,000 SUN)
        'decimals': 6,
    }
}
