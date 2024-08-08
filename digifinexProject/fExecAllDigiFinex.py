import requests
import time
import hmac
import hashlib
import urllib.parse
import os
from dotenv import load_dotenv
import json

load_dotenv()

pairusdt = os.getenv('DIGI_PAIR_TEXT')
baseUrl = "https://openapi.digifinex.com/v3"


class fExecAllDigiFinex:
    def __init__(self):
        self.appKey = os.getenv('DIGI_PUBLIC_KEY')
        self.appSecret = os.getenv('DIGI_PRIVATE_KEY')

    def _generate_accesssign(self, data):
        query_string = urllib.parse.urlencode(data)
        signature  = hmac.new(self.appSecret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def do_request(self, method, path, data, needSign=False):
        if needSign:
            headers = {
                "ACCESS-KEY": self.appKey,
                "ACCESS-TIMESTAMP": str(int(time.time())),
                "ACCESS-SIGN": self._generate_accesssign(data),
            }
        else:
            headers = {}
        if method == "POST":
            response = requests.request(method, baseUrl + path, data=data, headers=headers)
        else:
            response = requests.request(method, baseUrl + path, params=data, headers=headers)

        return response.json()


    def getLastPrice(self, symbol):
        """pega o ultimo preco"""
        endpoint = "/ticker"
        method="GET"
        params = {
            "symbol": symbol+pairusdt
            } 

        response = self.do_request(method,endpoint, '', False)

        return response['ticker'][0]['last']
    

    def getSymbols(self, nOpt):
        """pega os pares spot"""
        endpoint = "/spot/symbols"
        method="GET"

        response = self.do_request(method,endpoint, '', False)

        if nOpt == 1:
            rRet = [symbol['base_asset'] for symbol in response.get('symbol_list', []) if symbol.get('quote_asset') == 'USDT']
        
        return rRet

    def getAccBalance(self):
        """pega o saldo em USDT"""
        endpoint = "/spot/assets"
        method="GET"

        response = self.do_request(method,endpoint, '', True)

        return next((item['free'] for item in response['list'] if item['currency'] == 'USDT'), None)
    

    def postDigiOrder(self, symbol,type,size, price):
        """"CRIA UMA NOVA ORDER LIMIT(venda) OU MARKET(compra)"""
        endpoint = "/spot/order/new"
        method="POST"

        params = {
            "symbol": symbol,
            "type": type,
            "amount": size,
            "price": price
            }

        #remove o price quando for compra a MARKET
        if price == 0:
            del params['price'] 

        response = self.do_request(method,endpoint, params, True)

        return response


    def getorderByID(self, orderId, nopt):
        """pega o status da order"""
        endpoint = "/spot/order"
        method="GET"
        params = {
            "order_id": orderId
            } 
        response = self.do_request(method,endpoint, params, True)

        return [item['avg_price'] for item in response['data']] + [item['executed_amount'] for item in response['data']] if nopt == 1 else print(response)


    def fBuyOnTLG(self, QtdToBuy,coinFullName,nPercents):
        """Compra a MARKET e venda a LIMIT TLG"""
        responseBuy = {}

        #COMPRA MARKET >>>> COMPRAR POR quoteOrderQty <<<<
        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} USDT da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        responseBuy = self.postDigiOrder(coinFullName, "buy_market", (QtdToBuy - (QtdToBuy * 0.01)), 0 )#######################COMPRAAAAAAAAAAAAA MENOS 1% FIXO

        return responseBuy
    

    def fBuyAndSell(self, QtdToBuy, coinFullName, nPercents, nSellOrders):
        """Compra a MARKET e venda a LIMIT MANUAL"""
        responseBuy = {}
        coinFullName = coinFullName.lower()
        #COMPRA MARKET >>>> COMPRAR POR quoteOrderQty <<<<
        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} USDT da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        responseBuy = self.postDigiOrder(coinFullName, "buy_market", (QtdToBuy - (QtdToBuy * 0.01)), 0)#######################COMPRAAAAAAAAAAAAA 

        if responseBuy['code'] == 0:
            print(responseBuy)
            print("-----------------------------------------------------------------------------------------------")
            getPricePay = self.getorderByID(responseBuy['order_id'],1)
            print(f"Preco da compra: {getPricePay[0]} Vamos utiliza-lo para a venda com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.

        #      #CHAMA A VENDA
            self.fSellFracOrders(float(getPricePay[0]),float(getPricePay[1]),coinFullName,nPercents, nSellOrders)
        else:
            print(f"Falha na operação de compra: {responseBuy}")


        # return response
            
    def fSellFracOrders(self,aprice,quantity,coinFullName, nPercents, nSellOrders):
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
          
            for _selling in range(nSellOrders):
                
                market25p = quantity / nSellOrders
                _xNoveen +=1
                print("-----------------------------------------------------------------------------------------------")
                print(f"Venda de No: {_xNoveen}\nQtde. a ser vendida: {market25p} da moeda.")
                print(f"Preço: {round(aprice + ((nPercents[_selling] / 100) * aprice),5)} = {nPercents[_selling]}%")
                print("-----------------------------------------------------------------------------------------------")
                print(self.postDigiOrder(coinFullName, "sell", market25p, round(aprice + ((nPercents[_selling] / 100) * aprice),5) ))#####VENDAAAAAAAAAAAAAAA
                nSellOrders -= 1
                quantity -= market25p
        else:
            return print("Quantidade insuficiente para venda! ")
    

    #custom
    def divisor2_5(self,number):
        """Retorna o saldo dividido pelo minimo permtido para a compra"""
        nCont = 0
        for i in range(20, 0, -1):
            result_division = number / i
            if result_division >= 2.5:
                nCont += 1
                print(f"Digite: {i} Para comprar: {round(result_division,4)} USDT.")
        return nCont
    
    def fQtdBuy(self,QtdInUSDT,cRetUser):
        """Verifica se o que foi informado é suficiente para realizar a compra """
        lok = True

        if cRetUser == "1":
            QtdInUSDT = QtdInUSDT
        elif cRetUser == "2":
            if QtdInUSDT / 2 >= 2.5:
                QtdInUSDT = (QtdInUSDT / 2)
            else:
                lok = False
                print("Quantidade insuficiente")
        elif cRetUser == "3":
            if QtdInUSDT / 3 >= 2.5:
                QtdInUSDT = (QtdInUSDT / 3)
            else:
                lok = False
                print("Quantidade insuficiente")
        elif cRetUser == "4":
            if QtdInUSDT / 4 >= 2.5:
                QtdInUSDT = (QtdInUSDT / 4)
            else:
                lok = False
                print("Quantidade insuficiente")
        else:
            lok = False
            print("Quantidade fora do padrão")

        return QtdInUSDT if lok else 0