# pip install binance-futures-connector

from dotenv import load_dotenv, dotenv_values, set_key
from binance.um_futures import UMFutures as Client
from mexcProject.fExecAllMexc import fExecAllMexc
from otherFuncs.fsendMail import send_email
from otherFuncs.fDbTradeHistory import *
from binance.error import ClientError
from datetime import datetime
from decimal import Decimal
import numpy as np
import humanize
import logging
import random
import uuid 
import time
import os

load_dotenv(".env")

rslp = random.randint(5, 50)

idInstance = format(random.randint(1, 99), '02')

class fExecAllFuturesBinance:
    def __init__(self, key=os.getenv('BIN_API_KEY'), secret=os.getenv('BIN_SECRET_KEY')):
        self.key = key
        self.secret = secret


    def fGetServerTime(self):
        """get server time"""
        cTime = Client().time()['serverTime']
        return print(cTime)


    def fGetTickerPrice(self, coinN):
        """get TickerPrice"""
        ltkprice = Client().ticker_price(coinN)['price']
        return ltkprice


    def getOrderByID(self, coinN, orderId):
        """get TickerPrice"""
        statusOrder = Client(self.key,self.secret).query_order(coinN, orderId)
        return statusOrder
    

    def fGetKlines(self, coinN, interval, opt=0):
        """get klines """
        time.sleep(int(idInstance)/ 100)
        klines = Client().klines(coinN, **{"interval": interval, "limit": 300})
        return self.analyze_candles3(klines,coinN) if opt == 0 else klines
      

    # Função para calcular o RSI estocástico
    def calculate_stoch_rsi(self,close_prices, period):
        delta = np.diff(close_prices)
        gain = delta * (delta > 0)
        loss = -delta * (delta < 0)
        avg_gain = np.mean(gain[:period])
        avg_loss = np.mean(loss[:period])
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


    def returnStochRsi(self, symbol, close_prices, period):
        lret = '' 
        rsistoch = 0
        try:
            rsistoch = self.calculate_stoch_rsi(close_prices, period)

        except Exception as e:
            print("Ocorreu um erro:", e)

        return rsistoch

    def fAnalyzeBTC(self):
        lCruzUPBTC = ''
        periodRsiBTC = 14
        cGetCandleBTC = self.fGetKlines('BTCUSDT', '30m', 1)

        rsiBTC = round(self.calculate_rsi('BTCUSDT',cGetCandleBTC, periodRsiBTC),2)

        return int(rsiBTC)


    def analyze_candles3(self, candles,coin):
        ctimeNow = datetime.now().strftime('%H:%M')
        lBuy = False
        cType = ''
        cTradetype = ''
        retAnalysisBTC = 0
        ndefaultVol = 10000000#1 milhao
        ndefaultPerc = 3
        periodRsi = 14
        dirCruz = ''
        regra = 0
        difflow = 0
        diffhigh = 0
        newLossPerc = 0
    # Calcula as EMAs de 9 e 55 períodos
        if len(candles) > 0:
            
            ema_9 = self.calculate_ema(candles, 9)
            # ema_21 = self.calculate_ema(candles, 21)
            ema_55 = self.calculate_ema(candles, 55)
            ema_200 = self.calculate_ema(candles, 200)
            # ema_200 = self.calculate_ema(candles, 55)

            last_close = float(Decimal(candles[-1][4]))  # Último close
            last_ema = ema_9[-1]  # Último valor da EMA de 9 períodos


            rsi = round(self.calculate_rsi(coin,candles, periodRsi),2)

            outCoins = dotenv_values(".env").get("OUTCOINS", "")

            closes = [float(Decimal(candle[4])) for candle in candles]

            retAnalysisBTC = self.returnStochRsi(coin, closes, periodRsi)


        # Verifica as interações entre as EMAs para tomar decisões de compra/venda
            try:

                # if ema_9[-1] > ema_55[-1] and ema_55[-1] > ema_200[-1] and coin not in outCoins:
                if retAnalysisBTC >= 10 and coin not in outCoins:
            # if (0 < rsi < 29):
                    ctstPrce = self.fGetTickerPrice(coin)
                    # print("-----------------------------------------------------------------------------------------------")
                    print(f"As EMAs acabaram de se cruzar. Isso pode ser um sinal de reversão para cima. {coin} | preco : {ctstPrce}")
                    print("-----------------------------------------------------------------------------------------------")

                    cTradetype = self.getVolume24(coin)

                    lbidPrice = float(self.fGetDepth(coin, 0)[0]) 
                    difflow = abs((lbidPrice - float(cTradetype[2][0])))#+5%
                    diffhigh = abs((lbidPrice - float(cTradetype[2][1])))#-5%

                    dirCruz = 'UP'
                    if cTradetype[0] >= ndefaultVol  and cTradetype[1] > ndefaultPerc and  ema_9[-1] > ema_55[-1] and ema_55[-1] > ema_200[-1] and last_close > last_ema:
                        # and last_close > last_ema
                        lBuy = True
                        cType = 'BUY'
                        # cType = 'BUY'
                        regra = 33

                    else:
                        print(f"Baixo volume de negocição em USDT nas ultimas 24hrs.\nVol USDT: {cTradetype[0]} < {ndefaultVol}\nDiff. Em % (compra e venda) {round(float(cTradetype[1]),2)}% < {ndefaultPerc}%")
                        print("-----------------------------------------------------------------------------------------------")
            
                # elif ema_9[-1] < ema_55[-1] and  ema_55[-1] < ema_200[-1] and coin not in outCoins:
                elif retAnalysisBTC <= 80 and coin not in outCoins:
            # elif (71 < rsi < 100):
                    ctstPrce = self.fGetTickerPrice(coin)
                    print(f"As EMAs acabaram de se cruzar. Isso pode ser um sinal de reversão para baixo. {coin} | preco : {ctstPrce}")
                    print("-----------------------------------------------------------------------------------------------")

                    cTradetype = self.getVolume24(coin)

                    lbidPrice = float(self.fGetDepth(coin, 0)[0]) 
                    difflow = abs((lbidPrice - float(cTradetype[2][0])))#+5%
                    diffhigh = abs((lbidPrice - float(cTradetype[2][1])))#-5%

                    dirCruz = 'DOWN'
                    if cTradetype[0] >= ndefaultVol and cTradetype[1] > ndefaultPerc and ema_9[-1] < ema_55[-1] and  ema_55[-1] < ema_200[-1] and last_close < last_ema :
                        # and last_close < last_ema 
                        lBuy = True
                        # cType = 'SELL' if ((44 < rsi < 49) and last_close < ema_21[-1]) else 'BUY'
                        cType = 'SELL'
                        regra = 33
                    else:
                        print(f"Baixo volume de negocição em USDT nas ultimas 24hrs.\nVol USDT: {cTradetype[0]} < {ndefaultVol}\nDiff. Em % (compra e venda) {round(float(cTradetype[1]),2)}% < {ndefaultPerc}%")
                        print("-----------------------------------------------------------------------------------------------")


            except (KeyError, IndexError):
                lBuy = False
                print("err: Não foi possivel obter os candles! ")
                print("-----------------------------------------------------------------------------------------------")

            if lBuy:
                # retAnalysisBTC = self.returnStochRsi(coin, candles, periodRsi)
                newLossPerc =  round(cTradetype[1]/2,2)

        return [lBuy, cType, [retAnalysisBTC, periodRsi, rsi, dirCruz, cTradetype, regra, newLossPerc]]


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
    

    def getVolume24(self,coin):
        """Pega o ultimo preco do book"""
        response = Client().ticker_24hr_price_change(coin)

        diffPercent24h = fExecAllMexc().calc_diff_percent(float(response['lowPrice']),float(response['highPrice']))

        return [float(response['quoteVolume']), diffPercent24h, [response['lowPrice'],response['highPrice']]]
    

    def addCoinINOutList(self, new_string):
        # Load current values from the .env file
        env_values = dotenv_values(".env")
        current_list = env_values.get("OUTCOINS", "")

        # Convert the string into a list
        string_list = current_list.split(",") if current_list else []

        # Add the new string to the list
        string_list.append(new_string)

        # Update the value in the .env file
        new_list = ",".join(string_list)
        set_key(".env", "OUTCOINS", new_list)


    def removeCoinINOutList(self, string_to_remove):
        # Load current values from the .env file
        env_values = dotenv_values(".env")
        current_list = env_values.get("OUTCOINS", "")

        # Convert the string into a list
        string_list = current_list.split(",") if current_list else []

        # Remove the string from the list if it exists
        if string_to_remove in string_list:
            string_list.remove(string_to_remove)

        # Update the value in the .env file
        new_list = ",".join(string_list)
        set_key(".env", "OUTCOINS", new_list)


    def fGetDepth(self, coinN, slptime):
        """get lista com as ultimas compras e vendas min 5"""
        defslptime = 0.75

        #tempo de sleep para evitar limite de requicoes....
        time.sleep(defslptime if slptime < defslptime else slptime)

        listDepth = Client().depth(coinN, **{"limit": 5})

        try:
            lastBid = listDepth['bids'][0][0] #MAIOR PRECO DE COMPRA (DEPTH - GREEN) 
        except (KeyError, IndexError):
            lastBid = 0

        try:
            lastAsk = listDepth['asks'][0][0] #MENOR PRECO DE VENDA (DEPTH - RED)
        except (KeyError, IndexError):
            lastAsk = 0

        return [lastBid, lastAsk]
        

    def calculate_rsi(self, symbol, candles, period):
        """Calcula o RSI (Índice de Força Relativa) para um símbolo no intervalo especificado."""
        # Obtém os candles

        # Extrai os preços de fechamento
        close_prices = np.array([float(candle[4]) for candle in candles])

        # Calcula as diferenças de preço
        deltas = np.diff(close_prices)

        # Separa os ganhos e as perdas
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        # Calcula as médias de ganhos e perdas
        avg_gain = np.zeros(len(gains))
        avg_loss = np.zeros(len(losses))

        avg_gain[:period] = gains[:period].mean()
        avg_loss[:period] = losses[:period].mean()

        for i in range(period, len(gains)):
            avg_gain[i] = (avg_gain[i-1] * (period - 1) + gains[i]) / period
            avg_loss[i] = (avg_loss[i-1] * (period - 1) + losses[i]) / period

        # Calcula o RS e o RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi[-1]

    
    def fGetBalance(self, coin):
        """Pega o saldo disponivel em USDT"""
        try:
            response = Client(self.key,self.secret).balance()
            available_balance_usdt = next((item['availableBalance'] for item in response if (item['asset'] == 'USDT' if coin == '' else coin)), None)
        except:
            return print("Falha ao obter o saldo em USDT")
        return round(float(available_balance_usdt),4)


    def fGetExchangeInfo(self,option=0,cCoin=''):
        try:
            response = Client().exchange_info()
            if option == 0:
                actvSymbols = [dictonary['symbol'] for dictonary in response['symbols'] if dictonary['status'] == 'TRADING' and dictonary['marginAsset'] == 'USDT']
            else:
                actvSymbols = [dict(zip(['symbol','pricePrecision', 'quantityPrecision'],[dictonary['symbol'],dictonary['pricePrecision'],dictonary['quantityPrecision']])) for dictonary in response['symbols'] if dictonary['status'] == 'TRADING' and dictonary['symbol'] == cCoin]
        except:
            return print("Falha ao obter o retorno da moedas")
        
        return actvSymbols


    def fSetLeverageAndMarginType(self, symbol, nleverage):
        """Ajusta qtde de alavacagem e muda a margem para isolada por moeda"""
        retLeverage = ''

        cClient = Client(self.key,self.secret)

        try:
            retLeverage = cClient.change_leverage(symbol=symbol, leverage=nleverage, recvWindow=6000)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message))
        try:
            cClient.change_margin_type(symbol=symbol, marginType="ISOLATED", recvWindow=6000)
        except:
            pass

        return retLeverage['leverage']


    def cBaseConverter(self, decimals, price, qty):
        """converte o preco ou a quantidade para a base da moeda"""

        formattedRes = "{:.{}f}".format(price, decimals) if qty == 0 else "{:.{}f}".format(Decimal(price/qty), decimals)
        return float(formattedRes)
    

    def fPostNewOrder(self, coinFullName, side, type, valueUSDT, inputValue,cValueUsInputTP,cValueUsInputSL, nPercentG, nPercentL, listTPorSL1,listTPorSL2):
        defTimeInForce = 'GTC'
        defworkingType = 'MARK_PRICE'
        nCounter = 0
        price = float(fExecAllFuturesBinance().fGetTickerPrice(coinFullName)) if inputValue == 0 else inputValue
        cGetAllBases = fExecAllFuturesBinance().fGetExchangeInfo(1,coinFullName)
        quantityBase = self.cBaseConverter(cGetAllBases[0]['quantityPrecision'], valueUSDT if valueUSDT > 0 else inputValue, price) 
        priceBase = self.cBaseConverter(cGetAllBases[0]['pricePrecision'],price,0)
     
        wrongSide ='SELL' if side == 'BUY' else 'BUY' 
        profitType = 'TAKE_PROFIT_MARKET' if type == 'MARKET' else 'TAKE_PROFIT'
        stopType = 'STOP_MARKET' if type == 'MARKET' else 'STOP'

        #order market com wait price...
        if cValueUsInputTP > 0 or len(listTPorSL1) > 0:
            # print("-----------------------------------------------------------------------------------------------")
            while True:
                cLastBidPrice = float(fExecAllFuturesBinance().fGetDepth(coinFullName)[0], 0)
                diffPercent = fExecAllMexc().calc_diff_percent(inputValue,cLastBidPrice)

                if cLastBidPrice == inputValue:
                    stopprice = cValueUsInputSL
                    takeprofit = cValueUsInputTP
                    quantityBase = self.cBaseConverter(cGetAllBases[0]['quantityPrecision'], valueUSDT, inputValue) 
                    print("-----------------------------------------------------------------------------------------------")
                    print(f"** Alvo Atingido **\nLETS GO BUY/SELL!\nUltimo preco de compra (bid):{cLastBidPrice}\nPreco Entrada:{inputValue} Diff: {diffPercent}%")
                    break
                else:
                    time.sleep(0.3)
                    print(f"Em loop... Aguardando chegar no preco de entrada: {inputValue} Ultimo preco de compra (bid): {cLastBidPrice} Diff: {diffPercent}%")

        else:
            #adicionar os percentuais e ajusta as bases
            stopprice = self.cBaseConverter(cGetAllBases[0]['pricePrecision'],(price * (1 + nPercentL / 100)),0)
            takeprofit = self.cBaseConverter(cGetAllBases[0]['pricePrecision'],(price * (1 + nPercentG / 100)),0)

        cClient = Client(self.key,self.secret)

        params = {"symbol": coinFullName,"side": side,"type": type,"quantity": quantityBase,"price": priceBase,"timeInForce":defTimeInForce,}

        if type == "MARKET":
            del params["timeInForce"]
            del params["price"]
           

        try:
            #first order BUY/SELL
            buy_order = cClient.new_order(**params)
            print("-----------------------------------------------------------------------------------------------")
            print(f"Order type ({side} - {type})\n{buy_order}")
                                  
##########################################################################################################################################################################
            # nItensToForTP = listTPorSL1 if side == 'BUY' else listTPorSL2

            if len(listTPorSL1) > 1:
                cControl = quantityBase
                
                for itetp in listTPorSL1:
                    nCounter +=1
                    cQty = self.cBaseConverter(cGetAllBases[0]['quantityPrecision'], (valueUSDT/len(listTPorSL1)), itetp) 
                    cControl -= cQty
                    if cQty > cControl:
                        cQty -= cControl
                        cQty = self.cBaseConverter(cGetAllBases[0]['quantityPrecision'], (valueUSDT/len(listTPorSL1)), itetp) 

                    # print(f"cQty {cQty}")
                    # print(f"cControl {cControl}")
                    # print(f"preco {itetp}")
                    params = {"symbol": coinFullName,"side": wrongSide,"type": profitType,"quantity": cQty,"stopPrice": itetp, #if side == 'BUY' else stopprice,
                            "timeInForce":defTimeInForce,"workingType":defworkingType,"price": priceBase,"timeInForce":defTimeInForce,}
                    
                    if profitType == "TAKE_PROFIT_MARKET":
                        del params["timeInForce"]
                        del params["price"]

                    #second order TAKEPROFIT
                    tp_order = cClient.new_order(**params)
                    print("-----------------------------------------------------------------------------------------------")
                    print(f"Order Trigger {nCounter} TAKE_PROFIT ({wrongSide} - {type}) takeProfit: {itetp} USDT\n{tp_order}")
            else:
                params = {"symbol": coinFullName,"side": wrongSide,"type": profitType,"quantity": quantityBase,"stopPrice":takeprofit if side == 'BUY' else stopprice,
                        "timeInForce":defTimeInForce,"workingType":defworkingType,"price": priceBase,"timeInForce":defTimeInForce,}
                
                if profitType == "TAKE_PROFIT_MARKET":
                    del params["timeInForce"]
                    del params["price"]

                #second order TAKEPROFIT
                tp_order = cClient.new_order(**params)
                print("-----------------------------------------------------------------------------------------------")
                print(f"Order Trigger {nCounter}/{len(listTPorSL1)} TAKE_PROFIT ({wrongSide} - {type}) takeProfit: {takeprofit} USDT\n{tp_order}")


##########################################################################################################################################################################
            # nItensToForSL = listTPorSL2 if side == 'BUY' else listTPorSL1
            nCounter = 0
            if len(listTPorSL2) > 1:
                cControl = quantityBase
                
                for itesl in listTPorSL2:
                    nCounter +=1
                    cQty = self.cBaseConverter(cGetAllBases[0]['quantityPrecision'], (valueUSDT/len(listTPorSL2)), itesl) 
                    cControl -= cQty
                    if cQty > cControl:
                        cQty -= cControl
                        cQty = self.cBaseConverter(cGetAllBases[0]['quantityPrecision'], (valueUSDT/len(listTPorSL2)), itesl) 

                    params = {"symbol": coinFullName,"side": wrongSide,"type": stopType,"quantity": cQty,"stopPrice":itesl, #if side == 'BUY' else takeprofit,
                            "timeInForce":defTimeInForce,"workingType":defworkingType,"price": priceBase,"timeInForce":defTimeInForce,}
                    
                    if stopType == "STOP_MARKET":
                        del params["timeInForce"]
                        del params["price"]

                    #third order STOPLOSS
                    sl_order = cClient.new_order(**params)
                    print("-----------------------------------------------------------------------------------------------")
                    print(f"Order Trigger {nCounter} STOP_LOSS ({wrongSide} - {type}) Stoprice: {itesl} USDT\n{sl_order}")
            else:
                params = {"symbol": coinFullName,"side": wrongSide,"type": stopType,"quantity": quantityBase,"stopPrice":stopprice if side == 'BUY' else takeprofit,
                        "timeInForce":defTimeInForce,"workingType":defworkingType,"price": priceBase,"timeInForce":defTimeInForce,}
                
                if stopType == "STOP_MARKET":
                    del params["timeInForce"]
                    del params["price"]

                #third order STOPLOSS
                sl_order = cClient.new_order(**params)
                print("-----------------------------------------------------------------------------------------------")
                print(f"Order Trigger STOP_LOSS ({wrongSide} - {type}) Stoprice: {stopprice} USDT\n{sl_order}")
            # print("-----------------------------------------------------------------------------------------------")


        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message))
        return
    

    def check_division_by_six(self,value):
        count = 0
        
        while value >= 6:
            value -= 6
            count += 1
        
        return count

    def fGetInputTP(self,n,base,cValidValueN, cSide):

        print(f"Preco de entrada: {cValidValueN} | Tipo: {cSide}")
        print("-----------------------------------------------------------------------------------------------")

        inputs = []
        x = 0
        cPrintText = "Digite o preço (TAKE PROFIT) GANHO" if cSide == 'BUY' else "Digite o preço (STOP LOSS) PERDA"
        # cValueUsInput = input(f"{cPrintText}\nDigite: ")
        for _ in range(n):
            while True: 
                x += 1
                try:
                    while True:
                        cValueUsInput = float(input(f"{cPrintText} {x} de {n}: "))
                        try:
                            #Tente converter a entrada
                            if float(cValueUsInput) > cValidValueN:
                                cValueUsInput = self.cBaseConverter(base,float(cValueUsInput),0)
                                # cValueUsInputTP = BinanceFutures().cBaseConverter(cBaseDecs,float(cValueUsInputTP),0)
                                break
                            else:
                                print("-----------------------------------------------------------------------------------------------")
                                print(f"O preço tem que ser MAIOR do que o informado na entrada {cValidValueN}. Tente novamente.")
                                continue
                        except ValueError:
                            print("-----------------------------------------------------------------------------------------------")
                            print("Formato de preço inválido. Tente novamente.")
                    break
                except ValueError:
                    print("-----------------------------------------------------------------------------------------------")
                    print("Formato de preço inválido. Tente novamente.")

            inputs.append(cValueUsInput)

        return inputs


    def fGetInputTP2(self,n,base,cValidValueN, cSide):

        print(f"Preco de entrada: {cValidValueN} | Tipo: {cSide}")
        print("-----------------------------------------------------------------------------------------------")

        inputs = []
        x = 0
        cPrintText = cPrintText = "Digite o preço (STOP LOSS) PERDA" if cSide == 'BUY' else "Digite o preço (TAKE PROFIT) GANHO"
        for _ in range(n):
            while True: 
                x += 1
                try:
                    while True:
                        cValueUsInput = float(input(f"{cPrintText} {x} de {n}: "))
                        try:
                            #Tente converter a entrada
                            if float(cValueUsInput) < cValidValueN:
                                cValueUsInput = self.cBaseConverter(base,float(cValueUsInput),0)
                                # cValueUsInputTP = BinanceFutures().cBaseConverter(cBaseDecs,float(cValueUsInputTP),0)
                                break
                            else:
                                print("-----------------------------------------------------------------------------------------------")
                                print(f"O preço tem que ser MENOR do que o informado na entrada {cValidValueN}. Tente novamente.")
                                continue
                        except ValueError:
                            print("-----------------------------------------------------------------------------------------------")
                            print("Formato de preço inválido. Tente novamente.")
                    break
                except ValueError:
                    print("-----------------------------------------------------------------------------------------------")
                    print("Formato de preço inválido. Tente novamente.")

            inputs.append(cValueUsInput)

        return inputs

    def fBuyAndSell(self, coinFullName, side, type, valueUSDT, nPercentG, nPercentL, seTLeverage, entryRsi, simulator):
        transaction_id = str(uuid.uuid4())
        outCoins = dotenv_values(".env").get("OUTCOINS", "")
        cConvVol = humanize.intword(entryRsi[4][0])
        rdifperc = round(entryRsi[4][1])
        lAvanca = False
        nCount = 0
        cMailmsG = ''
        defTimeInForce = 'GTC'
        defworkingType = 'MARK_PRICE'
        cMailtype = '>>>>>COMPRA<<<<<' if side == 'BUY' else '>>>>>VENDA<<<<<'
        cMailSide = 'LONG' if side == 'BUY' else 'SHORT'
        buy_order = {'orderId': 0}
        nCounter = 0
        # price = float(fExecAllFuturesBinance().fGetTickerPrice(coinFullName)) 
        price = float(self.fGetDepth(coinFullName, 0)[1]) 
        cGetAllBases = fExecAllFuturesBinance().fGetExchangeInfo(1,coinFullName)

        quantityBase = self.cBaseConverter(cGetAllBases[0]['quantityPrecision'], valueUSDT, price) 
        priceBase = self.cBaseConverter(cGetAllBases[0]['pricePrecision'],price,0)
     
        cClient = Client(self.key,self.secret)

        params = {"symbol": coinFullName,"side": side,"type": type,"quantity": quantityBase}

        if simulator != "S":
            try:
                #first order BUY/SELL
                buy_order = cClient.new_order(**params)
                print("-----------------------------------------------------------------------------------------------")
                print(f"Order type ({side} - {type})\n{buy_order}")
            except:
                cMailmsG = f"Moeda: {coinFullName}\nValor: {valueUSDT}\nQtde: {quantityBase}\nPreco: {priceBase}\nRSI BTC({entryRsi[1]}) = {entryRsi[0]}\nRSI Moeda({entryRsi[1]}) = {entryRsi[2]}\n{entryRsi[3]}\nVol. USDT: {cConvVol}\nDiff %: {rdifperc}\nOrd. Regra: {entryRsi[5]}" 
                send_email('FALHA BINANCE FUTURES','','',coinFullName, cMailmsG, idInstance)
                print("falha na operacao de compra")

            if buy_order['orderId'] != 0:
                while True:
                    priceOrder = self.cBaseConverter(cGetAllBases[0]['pricePrecision'],float(self.getOrderByID(coinFullName, buy_order['orderId'])['avgPrice']),0) 
                    
                    if priceOrder > 0:

                        print("-----------------------------------------------------------------------------------------------")
                        print(f"Preco de entrada: {priceOrder} | Vamos utiliza-lo para a {side.lower()} com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.

                        
                        # cMailmsG = f"Moeda: {coinFullName}\n{cMailSide} {seTLeverage}x\n\nPreço de entrada: {priceOrder}\nRSI BTC({entryRsi[1]}) = {entryRsi[0]}\nRSI Moeda({entryRsi[1]}) = {entryRsi[2]}\n{entryRsi[3]}\nVol. USDT: {cConvVol}\nDiff %: {rdifperc}\nOrd. Regra: {entryRsi[5]}"
                        cMailmsGB = f"{cMailSide} {seTLeverage}x\n\nPreço de entrada: {priceOrder}\nRSI BTC({entryRsi[1]}) = {entryRsi[0]}\nRSI Moeda({entryRsi[1]}) = {entryRsi[2]}\n{entryRsi[3]}\nVol. USDT: {cConvVol}\nDiff %: {rdifperc}\nOrd. Regra: {entryRsi[5]}"
                
                        #Envia Email compra
                        # send_email('BINANCE FUTURES',cMailSide,'MARKET',coinFullName, cMailmsG, idInstance)
                        
                        #Grava compra no banco de dados local
                        insertDataInDB(coinFullName, cMailSide + ' ' +str(seTLeverage)+'x', entryRsi[0], entryRsi[2], entryRsi[3], cConvVol,rdifperc, entryRsi[5], 0, 0, idInstance, 0, transaction_id)
                        lAvanca = True

                        #atualiza lista de moedas em uso
                        if coinFullName not in outCoins:
                            self.addCoinINOutList(coinFullName)
                        break
                    else:
                        nCount += 1
                        print(f"[{nCount}/XXXX]: Aguardando a confirmação da ordem de compra...")
                        time.sleep(0.3)
        else:##MODO SIMUACAO DE COMPRA E VENDA
            priceOrder = priceBase

            #atualiza lista de moedas em uso
            if coinFullName not in outCoins:
                self.addCoinINOutList(coinFullName)

                cMailmsGB = f"{cMailSide} {seTLeverage}x\n\nPreço de entrada: {priceOrder}\nRSI BTC({entryRsi[1]}) = {entryRsi[0]}\nRSI Moeda({entryRsi[1]}) = {entryRsi[2]}\n{entryRsi[3]}\nVol. USDT: {cConvVol}\nDiff %: {rdifperc}\nOrd. Regra: {entryRsi[5]}"
                
                #Envia Email compra
                # send_email('BINANCE FUTURES',cMailSide,'MARKET',coinFullName, cMailmsG, 'SIMULACAO')
                
                #Grava compra no banco de dados local
                insertDataInDB(coinFullName, cMailSide + ' | SIMULACAO9', entryRsi[0], entryRsi[2], entryRsi[3], cConvVol,rdifperc, entryRsi[5], 0, 0, idInstance, 0, transaction_id)


                #CHAMA A VENDA
                self.fSellFracOrdersV2(priceOrder,coinFullName,nPercentG, nPercentL, 0, side, cMailtype, cMailSide, seTLeverage, entryRsi, transaction_id, simulator, cMailmsGB)
            else:
                print("-----------------------------------------------------------------------------------------------")
                print("Moeda já gravada")
                
 
        if lAvanca:
            #CHAMA A VENDA
            self.fSellFracOrdersV2(priceOrder,coinFullName,nPercentG, nPercentL,buy_order['clientOrderId'], side, cMailtype, cMailSide, seTLeverage, entryRsi, transaction_id, simulator, cMailmsGB)

                    
    def fSellFracOrdersV2(self,priceOrder,coinFullName, nPerGain, nPercLoss2, orderId, side, cMailtype, cMailSide, seTLeverage, entryRsi, uuidRef, simulator, cMailmsGB):
        cTimeEntry = datetime.now()
        cTimeNow = ''
        originPrice = priceOrder
        entryPrice = priceOrder
        wrongSide ='SELL' if side == 'BUY' else 'BUY' 
        cMailmsG = ''
        nCSell = 0
        diffPercent = 0
        nCountPositveOutPercent = 0
        nCountPositveOnGain = 0
        cOunterLimitOut = 10
        cOunterLimitGain = 2
        nPerTosellGainForLongTime = 0
        nPercGainSaved = 0
        leverage = 0
        lOut = False
        lGain = False
        lExit = False


        while True:
            #preco atual da moeda
            cpricePrint = self.fGetDepth(coinFullName, round(abs(diffPercent),2) )[0] #0 = bid | 1 = ask
            # cpricePrint = self.fGetwebSocketDepth(coinFullName)[0] #0 = bid | 1 = ask
            # cpricePrint = float(self.getPrice(coinFullName))
            #calcula a diferenca em percentual
            diffPercent = fExecAllMexc().calc_diff_percent(float(priceOrder if side == 'BUY' else cpricePrint),float(cpricePrint if side == 'BUY' else priceOrder))
            #imprime o preco atual e a diferenca
            
            if nCountPositveOutPercent > 0 and lOut:
                cTimerPrint = str(nCountPositveOutPercent)+'/'+str(cOunterLimitOut)
            elif nCountPositveOnGain > 0 and lGain:
                cTimerPrint = str(nCountPositveOnGain)+'/'+str(cOunterLimitGain)
            else:
                cTimerPrint = 'loop...'
                cTimeNow = datetime.now()
                
                timeDiff = cTimeNow - cTimeEntry
                diffMins = timeDiff.total_seconds() / 60

                if diffMins >= 3500 and diffPercent > 0:
                    lExit = True

                #ficou um tempo com mais de 1% ja vende para evitar o loss 10x 60s
                if diffPercent >= 1.25:
                   nPerTosellGainForLongTime +=1

                   if nPerTosellGainForLongTime >= 10:
                        lExit = True

                time.sleep(50)
                
            print(f"ID:{idInstance} | Prc.(bid):{cpricePrint} | {diffPercent}%")
            
            #vende se a diferenca for maior ou igual ao percentual de perda definido nos parametros
            if diffPercent <= nPercLoss2 or lExit:

                if nPercGainSaved > 0:
                    diffPercent += nPercGainSaved

                nCSell += 1
                print("-----------------------------------------------------------------------------------------------")
                print("|||||||||||||||||||||||||||||||||||||||| INICIANDO A VENDA ||||||||||||||||||||||||||||||||||||")
                print("-----------------------------------------------------------------------------------------------")
                print(f"Venda de No: {nCSell}\nPreco de entrada: {originPrice}\nPreço da venda com {round(diffPercent,2)}%: {cpricePrint}")
                print("-----------------------------------------------------------------------------------------------")
        
                while True:
                    lCan = self.fClosePosition(coinFullName, wrongSide,simulator)
                    if lCan: 
                        rsiOut = round(self.calculate_rsi(coinFullName,self.fGetKlines(coinFullName,'30m',1), 14),2)
                        rsiOutBTC = self.fAnalyzeBTC()
                        break

                cMailmsG = f"Moeda: {coinFullName}\n{cMailmsGB}\n\nClosePosition - {cMailSide} {seTLeverage}x\n\nPreco de entrada: {originPrice}\nPreço da venda com {round(diffPercent,2)}%: {cpricePrint}\nRSI de Saida: {rsiOut}\nRSI de Saida BTC: {rsiOutBTC}"
                
                #Envia Email compra
                send_email('BINANCE FUTURES',cMailSide,'MARKET',coinFullName, cMailmsG, (idInstance if simulator != "S" else 'SIMULACAO') )

                #atualiza dados do registro
                updateRegHistory(diffPercent if diffPercent > 0 else 0, diffPercent if diffPercent < 0 else 0, 0, uuidRef, rsiOut, rsiOutBTC)

                break
            elif diffPercent > nPerGain:
                lGain = True
                #se o valor atingigo for maior do que o valor de entrada o valor de entrada sera alterado pelo valor atigindo
                #e assim sucessivamente tendencia de alta (RARO MAS VAI QUE NEH... KKK!)
                priceOrder = float(cpricePrint)
                nPercLoss2 = -0.5 #muda o perccLoss
                leverage += 1
                nPercGainSaved += diffPercent
                nCountPositveOnGain += 1
                # cOunterLimitOut = 0 #zera o contador out para dar mais tempo para a alavancagem
                #o preco subiu mais do que 4x do percentual ja vende 
                if nCountPositveOnGain == cOunterLimitGain:

                    if nPercGainSaved > 0:
                       diffPercent += nPercGainSaved

                    nCSell += 1
                    #VENDA A MERCADO COM LUCRO
                    print("-----------------------------------------------------------------------------------------------")
                    print("|||||||||||||||||||||||||||||||||||||||| INICIANDO A VENDA ||||||||||||||||||||||||||||||||||||")
                    print("-----------------------------------------------------------------------------------------------")
                    print(f"Venda de No: {nCSell}\nPreco de entrada: {originPrice}\nPreco da venda ajustado: {priceOrder} | Alavancado em: {leverage}x\nPreço da venda com {(round(diffPercent,2) + (leverage * nPerGain))}%: {cpricePrint}")
                    print("-----------------------------------------------------------------------------------------------")
                    # print(self.postOrder(coinFullName, "SELL", "MARKET", 0, qTdeSalSell, 0))
                    # print("VENDA COM LUCRO ALAVANCADO")
                    while True:
                        lCan = self.fClosePosition(coinFullName, wrongSide,simulator)
                        if lCan:
                            rsiOut = round(self.calculate_rsi(coinFullName,self.fGetKlines(coinFullName,'30m',1), 14),2)
                            rsiOutBTC = self.fAnalyzeBTC()
                            break
                    # usdtBalance = round(fExecAllMexc().retValcomp("USDT"),4)
                    cMailmsG = f"Moeda: {coinFullName}\n{cMailmsGB}\n\nClosePosition - {cMailSide} {seTLeverage}x\n\nPreco de entrada: {originPrice}\nPreco da venda ajustado: {priceOrder} | Alavancado em: {leverage}x\nPreço da venda com {(round(diffPercent,2) + (leverage * nPerGain))}%: {cpricePrint}\nRSI de Saida: {rsiOut}\nRSI de Saida BTC: {rsiOutBTC}"
                
                    #Envia Email compra
                    send_email('BINANCE FUTURES',cMailSide,'MARKET',coinFullName, cMailmsG, (idInstance if simulator != "S" else 'SIMULACAO'))

                    #atualiza dados do registro
                    updateRegHistory(diffPercent if diffPercent > 0 else 0, diffPercent if diffPercent < 0 else 0, 0, uuidRef, rsiOut, rsiOutBTC)

                    break
            elif diffPercent > round((nPerGain/2),2) and diffPercent < nPerGain or lExit:
                lOut = True
                #Aqui o percentual ja eh maior porem nao bate no percentual desejado
                #criado apenas para evitar falha de many requests com muitas requisicoes ou tomar um ban
                #criar um contador para que se repita por N vezes com percentual positivo
                #excute a venda apos N repeticoes !
                nCountPositveOutPercent += 1
                nPercGainSaved += diffPercent
                priceOrder = float(cpricePrint)
                nPercLoss2 = -0.5 #muda o perccLoss

                if nCountPositveOutPercent == cOunterLimitOut or lExit:

                    if nPercGainSaved > 0:
                       diffPercent += nPercGainSaved

                    nCSell += 1
                    cLevarStrPr = f"Alavancado em: {leverage}x" if leverage > 0 else ''
                    #VENDA A MERCADO COM LUCRO
                    print("-----------------------------------------------------------------------------------------------")
                    print("|||||||||||||||||||||||||||||||||||||||| INICIANDO A VENDA ||||||||||||||||||||||||||||||||||||")
                    print("-----------------------------------------------------------------------------------------------")
                    print(f"Venda de No: {nCSell}\nPreco de entrada: {originPrice}\nPreço da venda com {diffPercent if cLevarStrPr == '' else (diffPercent + (cLevarStrPr * nPerGain))}%: {cpricePrint}\n{cLevarStrPr}")
                    print("-----------------------------------------------------------------------------------------------")

                    while True:
                        lCan = self.fClosePosition(coinFullName, wrongSide,simulator)
                        if lCan:
                            rsiOut = round(self.calculate_rsi(coinFullName,self.fGetKlines(coinFullName,'30m',1), 14),2)
                            rsiOutBTC = self.fAnalyzeBTC()
                            break

                    cMailmsG = f"Moeda: {coinFullName}\n{cMailmsGB}\n\nClosePosition - {cMailSide} {seTLeverage}x\n\nPreco de entrada: {originPrice}\nPreço da venda com {round(diffPercent,2) if cLevarStrPr == '' else (round(diffPercent,2) + (cLevarStrPr * nPerGain))}%: {cpricePrint}\n{cLevarStrPr}\nRSI de Saida: {rsiOut}\nRSI de Saida BTC: {rsiOutBTC}"
                
                    #Envia Email compra
                    send_email('BINANCE FUTURES',cMailSide,'MARKET',coinFullName, cMailmsG, (idInstance if simulator != "S" else 'SIMULACAO'))

                    #atualiza dados do registro
                    updateRegHistory(diffPercent if diffPercent > 0 else 0, diffPercent if diffPercent < 0 else 0, 0, uuidRef, rsiOut, rsiOutBTC)
                    break
            else:
                #atualiza as entradas dos contadores
                lOut = False
                lGain = False       



    def fClosePosition(self, symbol, side,simulator):
        outCoins = dotenv_values(".env").get("OUTCOINS", "")
        lRetCanc = False
        cClient = Client(self.key,self.secret)
        # stopprice = float(fExecAllFuturesBinance().fGetTickerPrice(symbol))
        stopprice = float(self.fGetDepth(symbol, 0)[1]) if side == 'BUY' else float(self.fGetDepth(symbol, 0)[0]) 

        if simulator != "S":
            try:
                params = {
                          "symbol": symbol,
                          "side":side,
                          "type": 'STOP_MARKET' if side == 'BUY' else 'TAKE_PROFIT_MARKET',
                          "stopPrice":stopprice,
                          "workingType":"MARK_PRICE",
                          "closePosition":'true'
                          }
                        
                sl_order = cClient.new_order(**params)
                time.sleep(0.1)

                if sl_order['orderId'] != 0:

                    #atualiza lista de moedas em uso
                    if symbol in outCoins:
                        self.removeCoinINOutList(symbol)
                    lRetCanc = True

            except:
                print("-----------------------------------------------------------------------------------------------")
                print("Aguardando retorno da venda...")
        else:
            #atualiza lista de moedas em uso
            if symbol in outCoins:
                self.removeCoinINOutList(symbol)
            lRetCanc = True


        return lRetCanc