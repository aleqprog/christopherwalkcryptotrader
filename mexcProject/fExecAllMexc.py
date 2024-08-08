import mexcProject.mexc_spot_v3 as mexc_spot_v3
from otherFuncs.fsendMail import send_email
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
import os
import json
import time
import re
from dotenv import load_dotenv
load_dotenv()


class fExecAllMexc:
    def __init__(self, hosts= "https://api.mexc.com", key=os.getenv('ACCESS_KEY'), secret=os.getenv('SECRET_KEY')):
        self.hosts = hosts
        self.key = key
        self.secret = secret
    

    def getVolume24(self,coin):
        """Pega o ultimo preco do book"""
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        params = {
            'symbol': coin
        }
        response= data.get_24hr_ticker(params)

        diffPercent24h = fExecAllMexc().calc_diff_percent(float(response['lowPrice']),float(response['highPrice']))

        return [float(response['quoteVolume']), diffPercent24h, [response['lowPrice'],response['highPrice']]]

    def getBookOrder(self,coin):
        """Pega o ultimo preco do book"""
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        params = {
            'symbol': coin
        }
        response= data.get_bookticker(params)
        return response['bidPrice']


    def getKlines(self,coin):
        """o kline"""
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        params = {
            'symbol': coin,
            'interval': '15m'#,
            #'limit': 100

        }
        response= data.get_kline(params)
        return self.analyze_candles(response,coin)


    def getDeals(self,coin):
        """o trades"""
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        params = {
            'symbol': coin#,
            #'limit': '500'#,
            #'limit': 100

        }
        response= data.get_deals(params)
        # return self.analyze_candles(response,coin)
        return self.process_trades(response)
    

    def process_trades(self,trades):
        # Dicionário para armazenar a soma de qty e price para cada tradeType
        soma_por_trade_type = defaultdict(lambda: {'qty_total': 0, 'price_total': 0})

        # Calcula a soma de qty e price para cada tradeType
        for trade in trades:
            trade_type = trade['tradeType']
            qty = Decimal(trade['qty'])
            price = Decimal(trade['price'])
            soma_por_trade_type[trade_type]['qty_total'] += qty
            soma_por_trade_type[trade_type]['price_total'] += price

        # Encontra o tradeType com o maior volume total
        maior_volume = max(soma_por_trade_type.items(), key=lambda x: x[1]['qty_total'])
        trade_type_maior_volume = maior_volume[0]

        print("TradeType com maior volume:", trade_type_maior_volume)
        # Retorna o tradeType com o maior volume total e o dicionário com as somas de qty e price
        for trade_type, soma in soma_por_trade_type.items():
            print(f"TradeType: {trade_type}, Qty Total: {round(soma['qty_total'],2)}, Price Total: {round(soma['price_total'],2)}")
        return trade_type_maior_volume

    
    def analyze_candles(self, candles,coin):
        lBuy = False
        ndefaultVol = 500000
        ndefaultPerc = 8
    # Calcula as EMAs de 9 e 55 períodos
        ema_9 = self.calculate_ema(candles, 9)
        ema_55 = self.calculate_ema(candles, 55)

        # Verifica as interações entre as EMAs para tomar decisões de compra/venda
        try:
            # Verifica se houve um cruzamento das EMAs e determina se foi de subida ou de queda
            if ema_9[-2] < ema_55[-2] and ema_9[-1] > ema_55[-1]:
                print("-----------------------------------------------------------------------------------------------")
                print(f"As EMAs acabaram de se cruzar. Isso pode ser um sinal de reversão para cima. {coin}")
                print("-----------------------------------------------------------------------------------------------")
                # cTradetype = fExecAllMexc().getDeals(coin)
                cTradetype = fExecAllMexc().getVolume24(coin)
                if cTradetype[0] >= ndefaultVol and cTradetype[1] >= ndefaultPerc:
                    lbidPrice = float(self.getBookDepth(coin, 0)[0]) 
                    difflow = abs(lbidPrice - float(cTradetype[2][0]))
                    diffhigh = abs(lbidPrice - float(cTradetype[2][1]))

                    if difflow < diffhigh:
                        lBuy = True
                    else:
                        print(f"O preco atual esta mais proximo do maior preco atigindo nas ultimas 24hrs.")
                        # print("-----------------------------------------------------------------------------------------------")
                else:
                    print(f"Baixo volume de negocição em USDT nas ultimas 24hrs.\nVol USDT: {cTradetype[0]} < {ndefaultVol}\nDiff. Em % (compra e venda) {round(float(cTradetype[1]),2)}% < {ndefaultPerc}%")
        
        except (KeyError, IndexError):
            lBuy = False
            print("-----------------------------------------------------------------------------------------------")
            print("err: Baixo volume de negocição em USDT nas ultimas 24h ")
        
        return lBuy

    def calculate_ema(self,candles, period):
        ema_values = []
        closes = [float(Decimal(candle[4])) for candle in candles]  # Utilizando a quarta posição (índice 4) que representa o close
        multiplier = 2 / (period + 1)
        ema = sum(closes[:period]) / period
        ema_values.append(ema)

        for close in closes[period:]:
            ema = (close - ema) * multiplier + ema
            ema_values.append(ema)

        return ema_values


    def converter_timestamp(self, timestamp):
        # Converter o timestamp para segundos dividindo por 1000 (já que o timestamp está em milissegundos)
        segundos = timestamp / 1000
        
        # Criar um objeto datetime a partir do timestamp
        data = datetime.utcfromtimestamp(segundos)
        
        # Extrair dia, mês, horas, minutos e segundos
        dia = '{:02d}'.format(data.day)
        mes = '{:02d}'.format(data.month)
        horas = '{:02d}'.format(data.hour)
        minutos = '{:02d}'.format(data.minute)
        segundos = '{:02d}'.format(data.second)
        
        return f"{dia}/{mes} {horas}:{minutos}:{segundos}"


    def getBookDepth(self,coin, opt):
        """Pega o preco das ordens de compra e venda listada no book(Depth)"""
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        params = {
            'symbol': coin
        }
        response= data.get_depth(params)

        try:
            bids = response['bids'][0][0] #MAIOR PRECO DE COMPRA (BOOK - GREEN) 
        except (KeyError, IndexError):
            bids = 0

        try:
            asks = response['asks'][0][0] #MENOR PRECO DE VENDA (BOOK - RED)
        except (KeyError, IndexError):
            asks = 0

        return [bids, asks]
    
    def priceBase(self, base, price):
        """converte o preco ou a quantidade para a base da moeda"""
        # Descobre o número de casas decimais na base
        priceDecimals = len(str(base).split('.')[1])
        formattedRes = "{:.{}f}".format(price, priceDecimals)
        return formattedRes

    def getPrice(self,coin):
        """pega o preco da moeda"""
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        params = {
            'symbol': coin
        }
        response= data.get_price(params)
        return response['price']
    
    
    def getDefSymbols(self):
        """retorna todas as moedas padrao"""
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        response= data.get_defaultSymbols()['data']

        retCoinsUSDT = [coin for coin in response if coin.endswith('USDT')]

        return retCoinsUSDT
    

    def addOneToDecimalPlaces(self,original_string):
        """Incrementa 1 ao final dos decimais para uso na LimitOrder"""
        # Convert to a float number
        original_number = float(original_string)
        decimal_places = len(original_string.split('.')[1])
        modified_number = original_number + 1 / (10 ** decimal_places)

        modified_string = '{:.{}f}'.format(modified_number, decimal_places)

        return modified_string


    def uSDTaccInfo(self,coin, choice):
        """Retorna o saldo da moeda na carteira"""
        balCoinWallet = 0
        data = mexc_spot_v3.mexc_account(mexc_hosts=self.hosts, mexc_key=self.key, mexc_secret=self.secret)
        response= data.get_account_info()
        resp = response['balances']#criptos
        
        if coin != 'USDT' and choice in ['2','5']:
            print("-----------------------------------------------------------------------------------------------")
            print("Iniciando a tentantiva de V E N D A ! ")
            print("-----------------------------------------------------------------------------------------------")

            for nTent in range(1,11):
                print(f"Tentativa {nTent} de 10...")
                print("-----------------------------------------------------------------------------------------------")
                time.sleep(1)

                response= data.get_account_info()
                resp = response['balances']#criptos

                for _ in resp:
                    if _['asset'] == coin:
                        balCoinWallet = float(_['free'])
                        break
                if balCoinWallet > 0:
                    print("Moeda ON! Go SeLL!!!")
                    break
        else:
            #CONSULTA SALDO USDT
            for _ in resp:
                if _['asset'] == coin:
                    balCoinWallet = float(_['free'])
                    break

        return balCoinWallet


    def retValcomp(self,coinName):
        """retorna o valor da moeda em carteira"""
        QtdInUSDT = self.uSDTaccInfo(coinName, '')
        return QtdInUSDT
    
    
    def getServerTime(self):
        """Pega o horario do servidor """
        data = mexc_spot_v3.mexc_market(mexc_hosts=self.hosts)
        response= data.get_timestamp()['serverTime']

        seconds = response / 1000.0
        date_hour = datetime.utcfromtimestamp(seconds)

        format = '%H:%M:%S:%f'
        formatted_time = date_hour.strftime(format)[:-3]
        formatted_date = date_hour.strftime("%d/%m/%Y")
        lastFormat = date_hour.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

        return [formatted_date, formatted_time, lastFormat]


    def validHourInput(self, input_str):
        "valida o input de hora e min no formato HH:MM"
        pad_hour = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')

        if pad_hour.match(input_str):
            return True
        else:
            return False
    

    def getOrderByID(self,coin, id, nOpt):
        """Pega os detalhes da ordem por Moeda e ID"""
        cummulativeQuote = 0
        origQty = 0
        returnValue = 0
        data = mexc_spot_v3.mexc_trade(mexc_hosts=self.hosts, mexc_key=self.key, mexc_secret=self.secret)
        params = {
            'symbol': coin, 
            'orderId': id 
        }
        response= data.get_order(params)
        # response= data.get_allorders(params)

        if nOpt == 1:
            try:
                if response['status'] != 'CANCELED':
                    cummulativeQuote = float(response['cummulativeQuoteQty'])
                    origQty = float(response['origQty'])

                    if response['status'] != 'NEW':
                        returnValue = cummulativeQuote / origQty
                else:
                    returnValue = 987654321

            except (KeyError, IndexError):
                returnValue = 0
            
            return returnValue
        else:
            return print(json.dumps(response, indent=4))


    def postOrder(self,coin, buyorsell, type, price, quant, quoteorder):
        """posta a ordem. compra e venda """
        data = mexc_spot_v3.mexc_trade(mexc_hosts=self.hosts, mexc_key=self.key, mexc_secret=self.secret)
        params = {
            'symbol': coin, 
            'side': buyorsell, 
            'type': type,
            'price': price,
            'quantity': quant,
            'quoteOrderQty': quoteorder
        }

        response= data.post_order(params)
        return response
    

    def fQtdBuy(self,QtdInUSDT,cRetUser):
        """Verifica se o que foi informado é suficiente para realizar a compra """
        lok = True
        
        if cRetUser == "1" or cRetUser == 'M':
            if cRetUser == 'M':
                if QtdInUSDT >= 6:
                    QtdInUSDT = 6
                else:
                    lok = False
                    print("Quantidade insuficiente")
            else:
                QtdInUSDT = QtdInUSDT
        elif 2 <= int(cRetUser) <= 20:
            if QtdInUSDT / int(cRetUser) >= 6:
                QtdInUSDT = (QtdInUSDT / int(cRetUser))
            else:
                lok = False
                print("Quantidade insuficiente")
        else:
            lok = False
            print("Quantidade fora do padrão")

        return QtdInUSDT if lok else 0


    #custom
    def divisor5_4(self,number):
        """Retorna o saldo dividido pelo minimo permtido para a compra"""
        nCont = 0
        for i in range(20, 0, -1):
            result_division = number / i
            if result_division > 6:
                nCont += 1
                print(f"Digite: {i} Para comprar: {round(result_division,4)} USDT.")
        return nCont
    

    #custom
    def fgGetPercents(self):
        #valida o que foi digitado *PERCENTUAL
        while True:
            input_string = input("Informe o percentual de ganho por order...\nPor exemplo numero inteiro em %: 1, 5, 10, 20, 30, 40... ou ESC para sair!\nDigite: ")

            #ESCREVA ESC para sair. nao utilizei a lib keyboard pq precisa instalar.
            if input_string.lower() == 'esc':
                print("Você digitou 'ESC'. Saindo...")
                exit()

            nPercents = input_string.split(',')
            # print("-----------------------------------------------------------------------------------------------")
            #VERIRICA SE SAO NUMEROS INTEIROS
            try:
                nPercents = [int(valor) for valor in nPercents]
                # Verificar se todos os valores são inteiros
                if all(isinstance(valor, int) for valor in nPercents):
                    break  # Se todos são inteiros, sair do loop
                else:
                    print("Por favor, digite apenas números inteiros. Ou digite ESC para sair.")
                    print("-----------------------------------------------------------------------------------------------")
            except ValueError:
                print("Por favor, digite apenas números inteiros válidos. Ou digite ESC para sair.")
                print("-----------------------------------------------------------------------------------------------")
        return nPercents
    

    #custom
    def fBuyOnTLG(self, QtdToBuy,cCoin,coinFullName,nPercents):
        """Compra a MARKET e venda a LIMIT"""
        responseBuy = {}

        #COMPRA MARKET >>>> COMPRAR POR quoteOrderQty <<<<
        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} USDT da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        responseBuy = self.postOrder(coinFullName, "BUY", "MARKET", 0, 0, (QtdToBuy - (QtdToBuy * 0.01)))#######################COMPRAAAAAAAAAAAAA MENOS 1% FIXO

        return responseBuy
    

    def fValidPerc(self,enterNumber):
        """Valdia o tipo informado no input do percentual"""
        try:
            float(enterNumber)
            return True
        except ValueError:
            return False
    

    #custom
    def fBuyAndSell(self, QtdToBuy,cCoin,coinFullName, nPerGain, nPercLoss,cTypeOrdr,cValidValue,  choice=''):
        """Compra do tipo (LIMIT/MARKET) e venda a MARKET"""
        lAvanca = True
        nCount = 0
        cMailmsG = ''
        responseBuy = {}

        print("-----------------------------------------------------------------------------------------------")
        print(f"Comprando {QtdToBuy} USDT da moeda: {coinFullName} a preco de mercado.")
        print("-----------------------------------------------------------------------------------------------")
        #COMPRANDO....
        quoteQty = (QtdToBuy - (QtdToBuy * 0.01)) if cTypeOrdr == 'MARKET' else 0
        qtyCoin = 0  if cTypeOrdr == 'MARKET' else (QtdToBuy/float(cValidValue))

        responseBuy = self.postOrder(coinFullName, "BUY", cTypeOrdr, cValidValue, qtyCoin, quoteQty)#######################COMPRAAAAAAAAAAAAA  MENOS 1% FIXO

        if 'msg' not in responseBuy and len(responseBuy) > 0:
            print(responseBuy)
            # priceWTtax = self.getOrderByID(coinFullName, responseBuy['orderId'],1)
            # responseBuy['price'] = float(responseBuy['price']) * 0.9539999999 if cTypeOrdr == 'MARKET' else float(responseBuy['price']) 
            # if cTypeOrdr == 'MARKET':
            print("-----------------------------------------------------------------------------------------------")
            while True:
                cPrintPriceMail = responseBuy['price']
                responseBuy['price'] = self.getOrderByID(coinFullName, responseBuy['orderId'],1)
                if responseBuy['price'] > 0 and responseBuy['price'] != 987654321:
                    # responseBuy['price'] = float(responseBuy['price']) 
                    print("-----------------------------------------------------------------------------------------------")
                    # print(f"Preco da compra: {priceWTtax} | Vamos utiliza-lo para a venda com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.
                    print(f"Preco da compra: {cPrintPriceMail} | Vamos utiliza-lo para a venda com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.
                    
                    qTdeSalSell = self.uSDTaccInfo(coinFullName.replace("USDT",""), choice)
                    # usdtBalance = round(fExecAllMexc().retValcomp("USDT"),4)
                    
                    cMailmsG = f">>>>>COMPRA<<<<<\n\nPreco da compra: {cPrintPriceMail}\nQuantidade da moeda em carteira: {qTdeSalSell}"

                    #Envia Email compra
                    send_email('MEXC SPOT','BUY',cTypeOrdr,coinFullName, cMailmsG)
                    break
                elif responseBuy['price'] == 987654321:
                    print("-----------------------------------------------------------------------------------------------")
                    print(f"Ordem de compra CANCELADA!")
                    print("-----------------------------------------------------------------------------------------------")
                    lAvanca = False
                    break
                else:
                    nCount += 1
                    print(f"[{nCount}/XXXX]: Aguardando a confirmação da ordem de compra...")
                    time.sleep(0.3)
                    #apos 50 repeticoes, sai fora pq eh certeza que a ordem limit nao rolow.
                    # if nCount == 50:
                    #     print("-----------------------------------------------------------------------------------------------")
                    #     print(f"Falha na operação de compra!\nVerifique o App/Site")
                    #     print("-----------------------------------------------------------------------------------------------")
                    #     lAvanca = False
                    #     break
                
            if lAvanca:
                #CHAMA A VENDA
                # self.fSellFracOrders(float(priceWTtax),coinFullName,nPercents, choice)
                if choice == '5':
                    self.fSellFracOrdersV2(responseBuy['price'],coinFullName,nPerGain, nPercLoss, choice)
                else:
                    self.fSellFracOrders(float(responseBuy['price']),coinFullName,nPerGain, choice)
        else:
            print(f"Falha na operação de compra: {responseBuy}")
        return
        

    #FUNCAO DE VENDA A MERCADO COM WHILE E GET COM PRINT DO ULTIMO PRECO
    def fSellFracOrdersV2(self,aprice,coinFullName, nPerGain, nPercLoss, choice):
        originPrice = aprice
        entryPrice = aprice
        cMailmsG = ''
        nCSell = 0
        nCountPositveOutPercent = 0
        nCountPositveOnGain = 0
        cOunterLimitOut = 40
        cOunterLimitGain = 5
        leverage = 0
        lOut = False
        lGain = False

        #QUANTIDADE DA MOEDA QUE QUER VENDER DA CARTEIRA. RETORNAR O TOTAL. AQUI PODE SER FEITA DA DIVISAO DAS VENDAS
        qTdeSalSell = self.uSDTaccInfo(coinFullName.replace("USDT",""), choice)

        if qTdeSalSell > 0:
            print("-----------------------------------------------------------------------------------------------")
            print(f"Quantidade da moeda em carteira: {qTdeSalSell}")
            print("-----------------------------------------------------------------------------------------------")
            
            while True:
                #preco atual da moeda
                cpricePrint = self.getBookDepth(coinFullName, 0)[0]
                # cpricePrint = float(self.getPrice(coinFullName))
                #calcula a diferenca em percentual
                diffPercent = self.calc_diff_percent(float(aprice),float(cpricePrint))
                #imprime o preco atual e a diferenca
                
                if nCountPositveOutPercent > 0 and lOut:
                    cTimerPrint = str(nCountPositveOutPercent)+'/'+str(cOunterLimitOut)
                elif nCountPositveOnGain > 0 and lGain:
                    cTimerPrint = str(nCountPositveOnGain)+'/'+str(cOunterLimitGain)
                else:
                    cTimerPrint = 'loop...'
                    time.sleep(0.5)
                print(f"{cTimerPrint} | Preco atual (bid): {cpricePrint} | {diffPercent}%")
                
                #vende se a diferenca for maior ou igual ao percentual de perda definido nos parametros
                if diffPercent <= nPercLoss:
                    nCSell += 1
                    print("-----------------------------------------------------------------------------------------------")
                    print("|||||||||||||||||||||||||||||||||||||||| INICIANDO A VENDA ||||||||||||||||||||||||||||||||||||")
                    print("-----------------------------------------------------------------------------------------------")
                    print(f"Venda de No: {nCSell}\nPreco da compra: {originPrice}\nQtde. a ser vendida: {qTdeSalSell} da moeda {coinFullName}.\nPreço da venda com {diffPercent}%: {cpricePrint}")
                    print("-----------------------------------------------------------------------------------------------")
                    #VENDA A MERCADO COM PREZUIJO
                    self.postOrder(coinFullName, "SELL", "MARKET", 0, qTdeSalSell, 0)

                    # usdtBalance = round(fExecAllMexc().retValcomp("USDT"),4)
                    cMailmsG = f">>>>>VENDA<<<<<\n\nPreco da compra: {originPrice}\nQtde. a ser vendida: {qTdeSalSell} da moeda {coinFullName}.\nPreço da venda com {diffPercent}%: {cpricePrint}"
                    
                    #Envia Email compra
                    send_email('MEXC SPOT','SELL','MARKET',coinFullName, cMailmsG)
                    break
                elif diffPercent > nPerGain:
                    lGain = True
                    #se o valor atingigo for maior do que o valor de entrada o valor de entrada sera alterado pelo valor atigindo
                    #e assim sucessivamente tendencia de alta (RARO MAS VAI QUE NEH... KKK!)
                    aprice = float(cpricePrint)
                    nPercLoss = -0.5 #muda o perccLoss
                    leverage += 1
                    nCountPositveOnGain += 1
                    cOunterLimitOut = 0 #zera o contador out para dar mais tempo para a alavancagem
                    #o preco subiu mais do que 4x do percentual ja vende 
                    if nCountPositveOnGain == cOunterLimitGain:
                        nCSell += 1
                        #VENDA A MERCADO COM LUCRO
                        print("-----------------------------------------------------------------------------------------------")
                        print("|||||||||||||||||||||||||||||||||||||||| INICIANDO A VENDA ||||||||||||||||||||||||||||||||||||")
                        print("-----------------------------------------------------------------------------------------------")
                        print(f"Venda de No: {nCSell}\nPreco de entrada: {originPrice}\nPreco da venda ajustado: {aprice} | Alavancado em: {leverage}x\nQtde. a ser vendida: {qTdeSalSell} da moeda {coinFullName}.\nPreço da venda com {(diffPercent + (leverage * nPerGain))}%: {cpricePrint}")
                        print("-----------------------------------------------------------------------------------------------")
                        print(self.postOrder(coinFullName, "SELL", "MARKET", 0, qTdeSalSell, 0))

                        # usdtBalance = round(fExecAllMexc().retValcomp("USDT"),4)
                        cMailmsG = f">>>>>VENDA<<<<<\n\nPreco de entrada: {originPrice}\nPreco da venda ajustado: {aprice} | Alavancado em: {leverage}x\nQtde. a ser vendida: {qTdeSalSell} da moeda {coinFullName}.\nPreço da venda com {(diffPercent + (leverage * nPerGain))}%: {cpricePrint}"
                    
                        #Envia Email compra
                        send_email('MEXC SPOT','SELL','MARKET',coinFullName, cMailmsG)
                        break
                elif diffPercent > round((nPerGain/6),2) and diffPercent < nPerGain:
                    lOut = True
                    #Aqui o percentual ja eh maior porem nao bate no percentual desejado
                    #criado apenas para evitar falha de many requests com muitas requisicoes ou tomar um ban
                    #criar um contador para que se repita por N vezes com percentual positivo
                    #excute a venda apos N repeticoes !
                    nCountPositveOutPercent += 1
                    # time.sleep(0.2)

                    if nCountPositveOutPercent == cOunterLimitOut:
                        nCSell += 1
                        cLevarStrPr = f"Alavancado em: {leverage}x" if leverage > 0 else ''
                        #VENDA A MERCADO COM LUCRO
                        print("-----------------------------------------------------------------------------------------------")
                        print("|||||||||||||||||||||||||||||||||||||||| INICIANDO A VENDA ||||||||||||||||||||||||||||||||||||")
                        print("-----------------------------------------------------------------------------------------------")
                        print(f"Venda de No: {nCSell}\nPreco da compra: {originPrice}\nQtde. a ser vendida: {qTdeSalSell} da moeda {coinFullName}.\nPreço da venda com {diffPercent if cLevarStrPr == '' else (diffPercent + (cLevarStrPr * nPerGain))}%: {cpricePrint}\n{cLevarStrPr}")
                        print("-----------------------------------------------------------------------------------------------")
                        print(self.postOrder(coinFullName, "SELL", "MARKET", 0, qTdeSalSell, 0))

                        # usdtBalance = round(fExecAllMexc().retValcomp("USDT"),4)
                        cMailmsG = f">>>>>VENDA<<<<<\n\nPreco da compra: {originPrice}\nQtde. a ser vendida: {qTdeSalSell} da moeda {coinFullName}.\nPreço da venda com {diffPercent if cLevarStrPr == '' else (diffPercent + (cLevarStrPr * nPerGain))}%: {cpricePrint}\n{cLevarStrPr}"
                    
                        #Envia Email compra
                        send_email('MEXC SPOT','SELL','MARKET',coinFullName, cMailmsG)
                        break
                else:
                    #atualiza as entradas dos contadores
                    lOut = False
                    lGain = False

        else:
            print("Moeda nao esta disponivel em carteira!")        


    def calc_percent(self, value, percent):
        """calcula o percentual para subtracao. Para subtracao, enviar o percentual como negativo (-1)"""
        return value * (1 + percent / 100)
    

    def calc_diff_percent(self, oldValue, newValue):
        """calcula a diferenca em percentual"""
        try:
            diff = newValue - oldValue
            percent = (diff / abs(oldValue)) * 100
            return round(percent,4)
        except ZeroDivisionError:
            # Tratamento para evitar divisão por zero se o valor_antigo for zero
            return float('inf')


    #OLD | Utilizada na compra manual e via telegram
    def fSellFracOrders(self,aprice,coinFullName, nPercents, choice):
        """Faz a venda do tipo (LIMIT) | Percentual por ordem | Controla a qtde de order por venda minima 6 USDT"""
        """MELHORAR ESSE TRECHO!!!"""
        idXDec = 4 #qtde max de orders de venda
        
        #QUANTIDADE DA MOEDA QUE QUER VENDER DA CARTEIRA. RETORNAR O TOTAL. AQUI PODE SER FEITA DA DIVISAO DAS VENDAS
        qTdeSalSell = self.uSDTaccInfo(coinFullName.replace("USDT",""), choice)
        
        #VERIFICA QUANTAS ORDERS DE VENDA PODE SER DIVIDIDO O VALOR EM CONTA. SENDO QUE NO MAXIMO 4 ORDERS DE VENDA.
        try:
            idXDec = 1 if (qTdeSalSell * aprice) >= 5 else 0
        except:
            return print("Quantidade insuficiente para venda! minimo: 5 USDT")

        print("-----------------------------------------------------------------------------------------------")
        print(f"Quantidade de moeda em carteira: {qTdeSalSell}")
        print("-----------------------------------------------------------------------------------------------")
        print(f"Quantidade de Orders a serem executadas: {idXDec}")
        print("-----------------------------------------------------------------------------------------------")

        if idXDec > len(nPercents):
            print(f"Voçê não informou todos os percentuais!\nSera utilizado o valor do primeiro para os demais! = {nPercents[0]}%")
            #Adciona o primeiro percentual as demais orders para nao dar crash. nesse caso nao foi informado.
            for x in range(idXDec):
                if x not in nPercents:
                    nPercents.append(nPercents[0])
            print("-----------------------------------------------------------------------------------------------")
        
        if idXDec > 0:
            print("||||||||||||||||||||||||||||||||||||||| INICIANDO AS VENDAS |||||||||||||||||||||||||||||||||||")
            _xNoveen = 0
            for _selling in range(idXDec):
                
                market25p = qTdeSalSell / idXDec
                _xNoveen +=1
                
                salesPricPercent = (aprice + ((nPercents[_selling] / 100) * aprice))
                print("-----------------------------------------------------------------------------------------------")
                print(f"Venda de No: {_xNoveen}\nQtde. a ser vendida: {market25p} da moeda.\nPreço da venda com {nPercents[_selling]}%: {salesPricPercent}\nLucro aproximado: {round((salesPricPercent * market25p) - (aprice * market25p),4)} USDT")
                print("-----------------------------------------------------------------------------------------------")

                print(self.postOrder(coinFullName, "SELL", "LIMIT", salesPricPercent, market25p, 0))#####VENDAAAAAAAAAAAAAAA

                idXDec -= 1
                qTdeSalSell -= market25p
        else:
            return print("Quantidade insuficiente para venda! minimo: 5 USDT")