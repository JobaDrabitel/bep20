# config.py

networks = {
    'erc20': {
        'provider': 'https://mainnet.infura.io/v3/68bdfbf2b7a14287b3ab91afb2feba3d',
        'contract_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'abi_file': 'ether\\abi\\erc_abi.json',
        'gas': 80000,  # Можно увеличить до 100000, если требуется
        'gasPrice': 12000000000,  # 12 Gwei в wei
        'decimals': 6,
    },
    'bep20': {
        'provider': 'https://bsc-dataseed.binance.org/',
        'contract_address': '0x55d398326f99059fF775485246999027B3197955',
        'abi_file': 'ether\\abi\\bep_abi.json',
        'gas': 70000,
        'gasPrice': 3000000000,
        'decimals': 18,
    }
}
