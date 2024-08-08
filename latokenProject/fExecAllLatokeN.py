import requests
import datetime
import hashlib
import hmac
import os
from dotenv import load_dotenv
load_dotenv()


class fExecAllLatokeN:
    def __init__(self, baseUrl= 'https://api.latoken.com', key=os.getenv('LTK_PUBLIC_KEY'), secret=os.getenv('LTK_PRIVATE_KEY'), usdtid = os.getenv('LTK_USDT_ID')):
        self.baseUrl = baseUrl
        self.key = key
        self.secret = secret.encode('utf-8')
        self.usdtid = usdtid


    def getCoinList(self):
        """"Pega a Lista de Moedas da correta"""
        endpoint = '/v2/currency/'
        url = self.baseUrl + endpoint
        response = requests.get(url)

        cOintags = [dictionary['tag'] for dictionary in response.json()]
        return cOintags

    def getTicker(self,coin):
        """"Pega a Lista de Moedas da correta"""
        endpoint = f'/v2/ticker/{coin}/{self.usdtid}'
        url = self.baseUrl + endpoint
        response = requests.get(url)
        return [response.json()['lastPrice'],response.json()['baseCurrency']]


    def getInfoCoinByName(self,coin, option = 0):
        """"Pega a Moeda pelo nome com todas as infos"""
        endpoint = f'/v2/currency/{coin}'
        url = self.baseUrl + endpoint
        response = requests.get(url)

        if response.json().get('error') == 'NOT_FOUND':
            print("-----------------------------------------------------------------------------------------------")
            return print(f"Moeda não encontrada! tag: {coin}")
        else:
            print("-----------------------------------------------------------------------------------------------")
            return print(response.json() if option <= 0 else response.json()['tag'])



    def getorderByID(self,orderid, option):
        endpoint = f'/v2/auth/order/getOrder/{orderid}'

        params = {
            'zeros': 'true'
        }
        serializeFunc = map(lambda it : it[0] + '=' + str(it[1]), params.items())
        queryParams = '&'.join(serializeFunc)
                        
        signature = hmac.new(
            self.secret, 
            ('GET' + endpoint + queryParams).encode('ascii'), 
            hashlib.sha512
        )

        url = self.baseUrl + endpoint + '?' + queryParams

        response = requests.get(
            url,
            headers = {
                'X-LA-APIKEY': self.key,
                'X-LA-SIGNATURE': signature.hexdigest(),
                'X-LA-DIGEST': 'HMAC-SHA512'
            }
        )

        return [response.json()['quantity'],response.json()['cost']] if option != 1 else print(response.json())


    def getBalancesWallet(self,pairusdt):
        endpoint = '/v2/auth/account'
        walletUSDT = ''

        params = {
            'zeros': 'false'
        }
        serializeFunc = map(lambda it : it[0] + '=' + str(it[1]), params.items())
        queryParams = '&'.join(serializeFunc)
                        
        signature = hmac.new(
            self.secret, 
            ('GET' + endpoint + queryParams).encode('ascii'), 
            hashlib.sha512
        )

        url = self.baseUrl + endpoint + '?' + queryParams

        response = requests.get(
            url,
            headers = {
                'X-LA-APIKEY': self.key,
                'X-LA-SIGNATURE': signature.hexdigest(),
                'X-LA-DIGEST': 'HMAC-SHA512'
            }
        )

        cOintags = [{'coinid': dictionary['currency'], 'available': dictionary['available'] } for dictionary in response.json() if dictionary['type'] == 'ACCOUNT_TYPE_SPOT']

        if len(pairusdt) > 0:
            walletUSDT = self.findByID(cOintags, pairusdt)       
        return walletUSDT


    def postOrderLA(self,cCoinTag,side,type,price,quantity):
        endpoint = '/v2/auth/order/place'

        params = {
            'baseCurrency': cCoinTag,
            'quoteCurrency': 'USDT',
            'side': side,
            'condition': 'GOOD_TILL_CANCELLED',
            'type': type,
            'clientOrderId': 'myCustomOrder',
            'price': price,
            'quantity': quantity
        }
        serializeFunc = map(lambda it : it[0] + '=' + str(it[1]), params.items())
        bodyParams = '&'.join(serializeFunc)
                        
        signature = hmac.new(
            self.secret, 
            ('POST' + endpoint + bodyParams).encode('ascii'), 
            hashlib.sha512
        )

        url = self.baseUrl + endpoint

        response = requests.post(
            url,
            headers = {
                'Content-Type': 'application/json',
                'X-LA-APIKEY': self.key,
                'X-LA-SIGNATURE': signature.hexdigest(),
                'X-LA-DIGEST': 'HMAC-SHA512'
            },
            json = params
        )

        return response.json()
            

    def findByID(self,lista, id_find):
        nUsdt = 0
        for dictOnr in lista:
            if 'coinid' in dictOnr and dictOnr['coinid'] == id_find:
                nUsdt += float(dictOnr['available'])
        return nUsdt
    
    def fBuyOnTLGLA(self, QtdToBuy,coinFullName,nPercents, nSellOrders, coinID):
        """Compra a MARKET"""
        responseBuy = {}

        #COMPRA MARKET >>>> COMPRAR POR quoteOrderQty <<<<
        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} unidades da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        responseBuy = self.postOrderLA(coinFullName, "BUY", "MARKET", 0, QtdToBuy)#######################COMPRAAAAAAAAAAAAA 

        return responseBuy

    def fBuyAndSell(self, QtdToBuy,coinFullName,nPercents, nSellOrders, coinID):
        """Compra a MARKET e venda a LIMIT"""
        responseBuy = {}

        #COMPRA MARKET >>>> COMPRAR POR quoteOrderQty <<<<
        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} unidades da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        responseBuy = self.postOrderLA(coinFullName, "BUY", "MARKET", 0, QtdToBuy)#######################COMPRAAAAAAAAAAAAA 


        if responseBuy['status'] != "FAILURE":
            print(responseBuy)
            print("-----------------------------------------------------------------------------------------------")
            getPricePay = self.getorderByID(responseBuy['id'],0)
            print(f"Preco da compra: {getPricePay[1]}. Vamos utiliza-lo para a venda com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.

             #CHAMA A VENDA
            self.fSellFracOrders(float(getPricePay[0]),float(getPricePay[1]),coinFullName,nPercents, nSellOrders, coinID)
        else:
            print(f"Falha na operação de compra: {responseBuy}")

        return
        
    #custom
    def fSellFracOrders(self,quantity,aprice,coinFullName, nPercents, nSellOrders, coinID):
        """Faz a venda do tipo (LIMIT) | Percentual por ordem """

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
        
        if nSellOrders > 0:
            print("||||||||||||||||||||||||||||||||||||||| INICIANDO AS VENDAS |||||||||||||||||||||||||||||||||||")
            _xNoveen = 0

            aprice = aprice / quantity
            
            for _selling in range(nSellOrders):
                
                market25p = quantity / nSellOrders
                _xNoveen +=1
                #preco decimais permitido = 5
                #quantidade decimais permitido = 2
                print("-----------------------------------------------------------------------------------------------")
                print(f"Venda de No: {_xNoveen}\nQtde. a ser vendida: {market25p} da moeda.")
                print(f"Preço: {round(aprice + ((nPercents[_selling] / 100) * aprice),5)} = {nPercents[_selling]}%")
                print("-----------------------------------------------------------------------------------------------")
                print(self.postOrderLA(coinFullName, "SELL", "LIMIT", round(aprice + ((nPercents[_selling] / 100) * aprice),5), round(market25p,2)))#####VENDAAAAAAAAAAAAAAA

                nSellOrders -= 1
                quantity -= market25p
        else:
            return print("Quantidade insuficiente para venda! ")


