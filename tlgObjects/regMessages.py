import re

# Regular Expressions:
regs={
    # Regex padrao, caso nenhum grupo seja localizado nesse dicionario.
    'default': {
        # Padrao para localizar a mensagem que contem a moeda:
        'find_message': r'^[A-Z-0-9]{2,10}$',
        # Padrao para extrair a moeda da mensagem:
        'extract': r'^[A-Z-0-9]{2,10}$'
    } ,
    'best_cryptos_pumps': {
        'find_message': r'coin.*chosen.*[\$][A-Z-0-9]{2,10}$',
        'extract': r'[\$][A-Z-0-9]{2,10}'
    },
    'Crypto_Pumps_Signals_Big': {
        'find_message': r'^[A-Z-0-9]{2,10}[\/]USDT',
        'extract': r'^[A-Z-0-9]{2,10}'
    },
    'CryptoPumpsPoloniex': {
        'find_message': r'COIN IS.*USDT',
        'extract': r'[/][A-Z-0-9]{2,10}[_]'
    },
    'Crypto_Pumps_Signals_Group': {
        'find_message': r'[Ee][Ll][Ee][Cc][Tt][Re][Dd] [Cc][Oo][Ii][Nn].*[\$][A-Z-0-9]{2,10}',
        'extract': r'[\$][A-Z-0-9]{2,10}'
    },
    'bigpumpsbinance': {
        'find_message': r'we are pumping today.*[A-Z-0-9]{2,10}',
        'extract': r'[: ]+[A-Z-0-9]{2,10}'
    },
    'Binance_Hotbit_Kucoin_Pumps': {
        'find_message': r'oin name is.*[A-Z-0-9]{2,10}',
        'extract': r'[: ]+[A-Z-0-9]{2,10}'
    }
}

def getCoin(group_name, message):
    coin=None
    # Usar os padroes do grupo 'default' caso o grupo informado no parametro acima nao seja encontrado no dicionario de patterns.
    group=group_name if group_name in regs else 'default'

    # Localizar a mensagem do grupo contem o patter de mensagem da moeda:
    if re.search(regs[group]['find_message'], message):
        try:
            # Extrair o nome da moeda da mensagem
            coin=re.search(regs[group]['extract'], message).group()
            # Limpar caracteres que nao esteja no padrao de moedas.
            coin=re.search(r'[A-Z-0-9]{2,10}', coin).group()
        except:
            coin=None

    return coin