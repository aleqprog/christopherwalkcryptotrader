import requests
import time
import base64
import hmac
import hashlib
import os
import json
import uuid
from dotenv import load_dotenv
load_dotenv()


class fExecAllKuCoin:
    def __init__(self, api_key=os.getenv('KU_PUBLIC_KEY'), api_secret=os.getenv('KU_PRIVATE_KEY'), api_passphrase=os.getenv('KU_API_PASSPHRASE')):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.url = 'https://api.kucoin.com/api/v1/accounts'

    def get_account_balance(self):
        now = int(time.time() * 1000)
        str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())

        passphrase = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), self.api_passphrase.encode('utf-8'), hashlib.sha256).digest())

        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2"
        }
        response = requests.request('get', self.url, headers=headers)

        #pega o USDT disponivel na carteira TRADE
        cretUSDT =  float([item['balance'] for item in response.json()['data'] if item['type'] == 'trade' and item['currency'] == 'USDT'][0])

        return cretUSDT
    

    def get_kucoin_symbols(self,coin, option, kupair, coinFuLL):
        base_url = 'https://api.kucoin.com'
        endpoint = '/api/v2/symbols'

        url = f'{base_url}{endpoint}'
        timestamp = int(time.time() * 1000)
        message = f'{timestamp}GET{endpoint}'

        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')

        headers = {
            'KC-API-KEY': self.api_key,
            'KC-API-SIGNATURE': signature,
            'KC-API-TIMESTAMP': str(timestamp),
            'KC-API-PASSPHRASE': self.api_passphrase,
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print('Falha na solicitação. Código de status:', response.status_code)
        else:
            if option == 1:
                return [item['symbol'] for item in response.json()['data'] if item['quoteCurrency'] == 'USDT']
            elif option == 2:
                cRet = [cx for cx in response.json()['data'] if cx['symbol'] == coin + kupair]
                return print(json.dumps(cRet, indent = 4))
            else:
                return [[base['baseMinSize'],base['priceIncrement']] for base in response.json()['data'] if base['symbol'] == coinFuLL][0]
    

    def qtdBase(self, base, value, price):
        """converte o valor para a base da moeda"""
        baseDecimals = len(str(base).split('.')[-1])
        resultCalc = value / price
        formattedRes = format(resultCalc, f'.{baseDecimals}f')
        return float(formattedRes)


    def priceBase(self, base, price):
        """converte o preco ou a quantidade para a base da moeda"""
        # Descobre o número de casas decimais na base
        priceDecimals = len(str(base).split('.')[1])
        formattedRes = "{:.{}f}".format(price, priceDecimals)
        return float(formattedRes)
 

    def get_kucoin_ticker(self,coin):
        """pega o ultimo preco da moeda"""
        base_url = 'https://api.kucoin.com'
        endpoint = f'/api/v1/market/orderbook/level1?symbol={coin}'
        url = f'{base_url}{endpoint}'
        response = requests.get(url)
    
        if response.status_code == 200:
            ticker_data = response.json()['data']
            return ticker_data['price']
        

    def get_currency_detail(self, coinName):
        """pega os detalhes da moeda"""
        base_url = 'https://api.kucoin.com'
        endpoint = f'/api/v3/currencies/{coinName}'
        url = f'{base_url}{endpoint}'
        timestamp = int(time.time() * 1000)
        message = f'{timestamp}GET{endpoint}'

        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')

        headers = {
            'KC-API-KEY': self.api_key,
            'KC-API-SIGNATURE': signature,
            'KC-API-TIMESTAMP': str(timestamp),
            'KC-API-PASSPHRASE': self.api_passphrase,
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print('Falha na solicitação. Código de status:', response.status_code)
        else:
            return print(json.dumps(response.json()['data'], indent = 4))


    def place_kucoin_order(self, symbol,side, type, price, quantity):
        """Monta ordem de compra ou venda"""
        url = "https://api.kucoin.com/api/v1/orders"

        now = int(time.time() * 1000)

        data = {
                "clientOid": str(uuid.uuid4()),
                "side": side,
                "symbol": symbol,
                "type": type,
                "price": price,
                "size": quantity
                }
        
        #remove o price quando for compra a MARKET
        if price == 0:
            del data['price']

        data_json = json.dumps(data)
        str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json

        signature = base64.b64encode(hmac.new(self.api_secret.encode(
            'utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())

        passphrase = base64.b64encode(hmac.new(self.api_secret.encode(
            'utf-8'), self.api_passphrase.encode('utf-8'), hashlib.sha256).digest())

        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=data_json)

        return response.json()
    

    def fBuyOnTLGLA(self, QtdToBuy,coinFullName,nPercents, nSellOrders):
        """Compra a MARKET TELEGRAM"""
        responseBuy = {}

        #COMPRA MARKET
        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} unidades da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        responseBuy = self.place_kucoin_order(coinFullName, "buy", "market", 0, QtdToBuy)#######################COMPRAAAAAAAAAAAAA 

        return responseBuy


    def fBuyAndSell(self, QtdToBuy,coinFullName,nPercents, nSellOrders,baseQtyMinCoin, basePriceMinIncrement):
        """Compra a MARKET e venda a LIMIT"""
        responseBuy = {}

        #COMPRA MARKET
        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} unidades da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        responseBuy = self.place_kucoin_order(coinFullName, "buy", "market", 0, QtdToBuy)#######################COMPRAAAAAAAAAAAAA 


        if responseBuy['code'] == '200000':
            print(responseBuy)
            print("-----------------------------------------------------------------------------------------------")
            getPricePay = self.getorderByID(responseBuy['data']['orderId'],0)
            print(f"Preco da compra: {self.priceBase(basePriceMinIncrement,getPricePay[1])} Vamos utiliza-lo para a venda com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.

             #CHAMA A VENDA
            self.fSellFracOrders(float(getPricePay[0]),float(getPricePay[1]),coinFullName,nPercents, nSellOrders,baseQtyMinCoin,basePriceMinIncrement)
        else:
            print(f"Falha na operação de compra: {responseBuy}")

        return

    #custom
    def fSellFracOrders(self,quantity,aprice,coinFullName, nPercents, nSellOrders,baseQtyMinCoin,basePriceMinIncrement):
        """Faz a venda do tipo (LIMIT) | Percentual por ordem """
        aprice2 = 0
        quantity2 = 0

        print("-----------------------------------------------------------------------------------------------")
        print(f"Quantidade de moeda em carteira: {quantity}")
        print("-----------------------------------------------------------------------------------------------")
        print(f"Quantidade de Orders a serem executadas: {nSellOrders}")
        print("-----------------------------------------------------------------------------------------------")

        if nSellOrders > len(nPercents):
            print(f"Voçê não informou todos os percentuais!\nSera utilizado o valor do primeiro para os demais! = {nPercents[0]}%")
            #Adciona o primeiro percentual as demais orders para nao dar crash. nesse caso nao foi informado.
            for x in range(nSellOrders):
                if x not in nPercents:
                    nPercents.append(nPercents[0])
            print("-----------------------------------------------------------------------------------------------")
        
        #TRATAR AQUI A QUESTAO DA QTDE DE ORDERS QUANDO FOR HABILITAR 
        #ESTA CHUMBADO UMA ORDEM DE VENDA

        if nSellOrders > 0:
            print("||||||||||||||||||||||||||||||||||||||| INICIANDO AS VENDAS |||||||||||||||||||||||||||||||||||")
            _xNoveen = 0

            for _selling in range(nSellOrders):
                
                _xNoveen +=1
                aprice = aprice + ((nPercents[_selling] / 100) * aprice)
                aprice2 = self.priceBase(basePriceMinIncrement, aprice )

                if baseQtyMinCoin.isdigit():
                    quantity2 = quantity
                else: 
                    quantity2 = self.priceBase(baseQtyMinCoin, quantity)

                print("-----------------------------------------------------------------------------------------------")
                print(f"Venda de No: {_xNoveen}\nQtde. a ser vendida: {quantity} da moeda.")
                print(f"Preço: {aprice} = {nPercents[_selling]}%")
                print("-----------------------------------------------------------------------------------------------")
                print(self.place_kucoin_order(coinFullName, "sell", "limit", aprice2, quantity2))#####VENDAAAAAAAAAAAAAAA
                nSellOrders -= 1
                quantity -= quantity
        else:
            return print("Quantidade insuficiente para venda! ")
    

    def getorderByID(self, orderid, opt):
        """PEGA os detalhes da order"""
        base_url = 'https://api.kucoin.com'
        endpoint = f'/api/v1/orders/{orderid}'
        url = f'{base_url}{endpoint}'
        timestamp = int(time.time() * 1000)
        message = f'{timestamp}GET{endpoint}'

        # Criando a assinatura usando HMAC-SHA256
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')
        
        passphrase = base64.b64encode(hmac.new(self.api_secret.encode(
            'utf-8'), self.api_passphrase.encode('utf-8'), hashlib.sha256).digest())

        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(timestamp),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)

        return [response.json()['data']['size'], (float(response.json()['data']['dealFunds']) / float(response.json()['data']['size']))] if opt != 1 else print(response.json()['data'])
        
