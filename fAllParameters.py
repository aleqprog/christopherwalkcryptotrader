from binanceProject.fExecAllBinance import fExecAllFuturesBinance as BinanceFutures
from mexcProject.fExecAllMexc import fExecAllMexc
from digifinexProject.fExecAllDigiFinex import *
from tlgObjects.fTelegramBot import TelegramBot
from latokenProject.fExecAllLatokeN import *
from kucoinProject.fExecAllKuCoin import *
from otherFuncs.fHeaderParameters import *
from otherFuncs.fDbTradeHistory import *
from dotenv import load_dotenv
from datetime import datetime
import platform
import time
import os

load_dotenv(".env")

pairusdt = os.getenv('LTK_USDT_ID')
kupair = os.getenv('KU_PAIR_TEXT')
digiPair = os.getenv('DIGI_PAIR_TEXT')


#PLAY!
if __name__ == "__main__":
    TG_SESSION=platform.node() or 'test'
    usdtBalance = 0
    getCoin = ''
    _i = 0
    while True:
        headerCrhispWalk()
        print("|       Escolha o Mercado      |")
        print("|------------------------------|")
        print("1. Spot")
        print("2. Futures")
        print("3. Sair")
        print(" ")
        
        choice = input("Digite o número correspondente à sua ESCOLHA: ") or '2'
        print(" ")

        if choice == '1':
            # Menu principal
            while True:
                fTypeSpot()
                print("|      Escolha a Exchange      |")
                print("|------------------------------|")
                print("1. Mexc")
                print("2. Latoken")
                print("3. KuCoin")
                print("4. DigiFinex")
                print("5. Sair")
                print(" ")
                
                choice = input("Digite o número correspondente à sua ESCOLHA: ")
                print(" ")

                if choice == '1':
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> M E X C <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    while True:
                        headerMexc()
                        print("Escolha uma opção:")
                        print("--------------------------------------------------------------------------------------------------------------------------------------------------------")
                        print("1. Ver saldo em USDT")
                        print("2. Compra e Venda (Manual)")
                        print("3. Compra e Venda (Telegram - telethon)")
                        print("4. Consultar Ordem (ID)")
                        print("5. Compra e Venda (Auto - Horario do Servidor)")
                        print("6. Horario do Servidor")
                        print("7. Horario Atual/Horario do servidor e Preco da Moeda(DepthBook-Compra, DepthBook-Venda e GetPrice-Ultimo preco) *loop function*")
                        print("8. Análise - Horario do servidor e da calculo diferença em %")
                        print("9. kLines")
                        print("10. Sair")
                        print("--------------------------------------------------------------------------------------------------------------------------------------------------------")
                        
                        choice = input("Digite o número correspondente à sua ESCOLHA: ")
                        #carrega o saldo em USDT
                        usdtBalance = round(fExecAllMexc().retValcomp("USDT"),4)
                        #carrega a lista de moedas disponiveis
                        getCoinList = fExecAllMexc().getDefSymbols()

                        if choice == '1':#PEGA O SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira. Só é possivel comprar acima de: 6 USDT")
                            print("-----------------------------------------------------------------------------------------------")
                        elif choice == '2' or choice == '3':#PLAY NA COMPRA E VENDA
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira. Só é possivel comprar acima de: 6 USDT")
                            print("-----------------------------------------------------------------------------------------------")
                            _i = fExecAllMexc().divisor5_4(usdtBalance) #MOSTRA QUANTO PODE SER COMPRADO COM BASE NO SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")

                            if _i > 1:
                                cRetUser = input("Escolha quanto quer comprar em USDT com base no resultado acima. ou Digite M para comprar o minimo (6)\nDigite: ")
                            else:
                                print("Vou comprar pq só da pra executar uma ordem de venda!")
                                cRetUser = '1'

                            if cRetUser.upper() != 'M':
                                if int(cRetUser) in range(1,20):
                                    QtdToBuy = fExecAllMexc().fQtdBuy(usdtBalance,cRetUser)
                                else:
                                    print("Dado invalido.\nOpcoes disponiveis: 1,2,.....20.")
                            else:
                                QtdToBuy = fExecAllMexc().fQtdBuy(usdtBalance,cRetUser.upper())

                            if QtdToBuy > 0:
                                print("-----------------------------------------------------------------------------------------------")
                                nPercents = fExecAllMexc().fgGetPercents()
                                
                                if _i > 1:
                                    print("-----------------------------------------------------------------------------------------------")
                                
                                if choice == '2': #COMPRA INFORMANDO A MOEDA
                                    cCoin = input("Digite a moeda para iniciar a compra: " ).upper()
                                    coinFullName = cCoin + "USDT"

                                    if coinFullName in getCoinList:
                                        fExecAllMexc().fBuyAndSell(QtdToBuy,cCoin,coinFullName,nPercents, 0, 'MARKET', 0, choice)
                                    else:
                                        print("MOEDA não encontrada! *INPUT")

                                else:#COMPRA AUTO PELO GRUPO DO TELEGRAM
                                    
                                    bot = TelegramBot(TG_SESSION, os.getenv('API_ID'), os.getenv('API_HASH'), os.getenv('COIN_REGEX'),  getCoinList, QtdToBuy, nPercents, 0, exchange="MEXC")
                                    bot.start()

                        elif choice == '4':
                            print("-----------------------------------------------------------------------------------------------")
                            coinFullName = input("Digite a moeda: ").upper()
                            nID = input("Digite o OrderID Ex.: C01__371714309840990211: ").upper()
                            
                            coinFullName += 'USDT'

                            if coinFullName in getCoinList:
                                print("-----------------------------------------------------------------------------------------------")
                                fExecAllMexc().getOrderByID(coinFullName, nID, 0)
                                print("-----------------------------------------------------------------------------------------------")
                            else:
                                print("-----------------------------------------------------------------------------------------------")
                                print(">>>>>>>>>>> Moeda inválida! <<<<<<<<<<<")
                                print("-----------------------------------------------------------------------------------------------")

                        elif choice == '5':#compra auto pelo serverTime (TESTE)
                            cValidValue = 0
                            nRoundDecs = 0
                            ndiffEntryOrOutPrice = 0
                            entryPrice = 0
                            lastold = 0

                            #copia da opcao 2 com pequeno ajuste apos a escolha. aqui nos informamos quando a compra sera iniciada
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira. Só é possivel comprar acima de: 6 USDT")
                            print("-----------------------------------------------------------------------------------------------")
                            
                            while True:
                                nbuyWithUSDT = input("Escolha quanto quer comprar em USDT com base no saldo disponível em carteira.\nDigite: ") or usdtBalance

                                # Verifica se a entrada é um número inteiro positivo
                                try:
                                    if float(nbuyWithUSDT) <= usdtBalance and float(nbuyWithUSDT) >= 6:
                                        QtdToBuy = float(nbuyWithUSDT)
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido. Igual ou inferior ao saldo de: {usdtBalance} ou 6 para comprar o minimo.")
                                        print("-----------------------------------------------------------------------------------------------")
                                except ValueError:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")

                            if QtdToBuy > 0:
                                print("-----------------------------------------------------------------------------------------------")
                                while True:
                                    nPercentG = input("Informe o percentual de GANHO.\nDigite: ") or 3

                                    if fExecAllMexc().fValidPerc(nPercentG):
                                        nPercentG = int(nPercentG)
                                        print("-----------------------------------------------------------------------------------------------")
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido.")
                                        print("-----------------------------------------------------------------------------------------------")
        
                                while True:
                                    nPercentL = input("Informe o percentual de PERDA.\nDigite: ") or 3

                                    if fExecAllMexc().fValidPerc(nPercentL):
                                        nPercentL = int(nPercentL)
                                        print("-----------------------------------------------------------------------------------------------")
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido.")
                                        print("-----------------------------------------------------------------------------------------------")
            
                                if _i > 1:
                                    print("-----------------------------------------------------------------------------------------------")
                                
                                cCoin = input("Digite a moeda para iniciar a compra: " ).upper() or 'MAVIA'
                                coinFullName = cCoin + "USDT"

                                if coinFullName in getCoinList:
                                    #tipo de order
                                    while True:
                                        print("-----------------------------------------------------------------------------------------------")
                                        cTypeOrdr = input("Informe o tipo de Order de compra\n1 = LIMIT\n2 = MARKET\nDigite: ") or 2
                                        
                                        if not cTypeOrdr:
                                            print("-----------------------------------------------------------------------------------------------")
                                            print(f"Digite uma opcao válida.")
                                        else:
                                            if int(cTypeOrdr) in [1,2]:
                                                cTypeOrdr = 'LIMIT' if int(cTypeOrdr) == 1 else 'MARKET'
                                                break
                                            else:
                                                print("-----------------------------------------------------------------------------------------------")
                                                print(f"Digite uma opcao válida.")
                                    
                                    if cTypeOrdr == 'LIMIT':
                                        while True:
                                            cPrintPrice = fExecAllMexc().getBookDepth(coinFullName, 0)[1]
                                            print("-----------------------------------------------------------------------------------------------")
                                            print(f" Ultimo preco de venda book: {cPrintPrice}")

                                            print("-----------------------------------------------------------------------------------------------")
                                            cValidValue = input("Digite o preço caso queira inseri-lo manualmente ou\npressione Enter para usar o preço do book ou\ndigite X para atualizar o ultimo preco:  ")

                                            if cValidValue.upper() == 'X':
                                                continue
                                            elif not cValidValue:
                                                cValidValue = 0
                                                # Se o usuário pressionar Enter, encerre o loop
                                                break
                                            try:
                                                # Tente converter a entrada 
                                                cBaseDecs = fExecAllMexc().priceBase(fExecAllMexc().getBookDepth(coinFullName, 1)[1],float(cValidValue))
                                                cValidValue =  fExecAllMexc().addOneToDecimalPlaces(cBaseDecs)
                                                # cValidValue = float(cValidValue)
                                                break
                                            except ValueError:
                                                print("-----------------------------------------------------------------------------------------------")
                                                print("Formato de preço inválido. Tente novamente.")
                                                continue

                                    cRetTSrv = fExecAllMexc().getServerTime()
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Data: {cRetTSrv[0]}\nHorario do servidor: {cRetTSrv[1].rsplit(':', 1)[-2]}")
                                    print("-----------------------------------------------------------------------------------------------")
                                    while True:
                                        date_choice = input("Digite a data (d/m/yyyy) ou pressione Enter para comprar no mesmo dia: ")

                                        if not date_choice:
                                            date_choice = datetime.now()
                                            # Se o usuário pressionar Enter, encerre o loop
                                            break
                                        try:
                                            # Tente converter a entrada para um objeto datetime
                                            date_choice = datetime.strptime(date_choice, "%d/%m/%Y")
                                            break
                                        except ValueError:
                                            print("-----------------------------------------------------------------------------------------------")
                                            print("Formato de data inválido. Tente novamente.")
                                            print("-----------------------------------------------------------------------------------------------")
                                            continue
                                    print("-----------------------------------------------------------------------------------------------")
                                    while True:
                                        hour_choice = input("Informe o horário de início no formato HH:MM (UTC+3) ou pressione Enter para comprar AGORA: ")

                                        if not hour_choice:
                                            hour_choice = cRetTSrv[1].rsplit(':', 2)[0]
                                            # Se o usuário pressionar Enter, encerre o loop
                                            break
                                        elif fExecAllMexc().validHourInput(hour_choice):
                                            break
                                        else:
                                            print("-----------------------------------------------------------------------------------------------")
                                            print("Formato de horário inválido. Tente novamente.")
                                            print("-----------------------------------------------------------------------------------------------")
                                    print("-----------------------------------------------------------------------------------------------")

                                    hour, minute = map(int, hour_choice.split(':'))

                                    hour_conv = date_choice.replace(hour=hour,minute=minute,second=0,microsecond=0)

                                    timestamp_wantedC = hour_conv.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

                                    # cValidValue = float(cValidValue)
                                    while True:
                                        timestamp_serverC = fExecAllMexc().getServerTime()
                                        
                                        #TESTEX DE COMPRA LIMIT COM SEM ORDENS DE COMPRA (LANCAMENTO)
                                        #PEGA A MENOR VENDA E ADD +1
                                        if cTypeOrdr != 'MARKET':
                                            dt_format = '%d/%m/%Y %H:%M:%S.%f'
                                            date_hour_S = datetime.strptime(timestamp_serverC[2], dt_format)
                                            date_hour_W = datetime.strptime(timestamp_wantedC, dt_format)

                                            # Calcular a diferença em segundos
                                            diffinSecs = abs((date_hour_S - date_hour_W).total_seconds())

                                            #pega o menor valor de venda para comprar cmaior = +1
                                            if diffinSecs <= 1 and cValidValue == 0:
                                                cValidValue = fExecAllMexc().addOneToDecimalPlaces(fExecAllMexc().getBookDepth(coinFullName, 0)[1])
                                        #FIM TESTE

                                        # Verificar se o horário desejado foi atingido
                                        if timestamp_serverC[2] >= timestamp_wantedC and int(timestamp_serverC[1].rsplit(':', 1)[-1]) > (120 if cTypeOrdr == 'MARKET' else 000): #serverTime acima de 120 ms para marketOrder
                                            print("-----------------------------------------------------------------------------------------------")
                                            # O horário desejado foi atingido, execute a função e saia do loop
                                            print(f"Horario do Servidor: {timestamp_serverC[1]}\nHorario Desejado: {timestamp_wantedC[-12:]} ")
                                            

                                            #FAZ A COMPRA !
                                            # nCountLoop = 0
                                            diffPercent = 0
                                            # nOutLold = 0
                                            # lastold = 0
                                            # oldDiff = 0
                                            nIter = 0
                                            newConlist = getCoinList
                                            while True:
                                                
                                                if diffPercent == 0:
                                                    # entryPrice = 0
                                                    # diffPercent = 0
                                                    if len(newConlist) > 0:
                                                        for cCoinAnalise in newConlist:
                                                            lRun = False
                                                            newConlist.remove(cCoinAnalise)
                                                        
                                                            coinFullName=cCoinAnalise
                                                            # time.sleep(5)
                                                            print("-----------------------------------------------------------------------------------------------")
                                                            print(f"Analisando a Moeda... {coinFullName}")
                                                            # print("-----------------------------------------------------------------------------------------------")
                                                            
                                                            lRun = fExecAllMexc().getKlines(coinFullName)
                                                            # time.sleep(3)

                                                            if lRun:
                                                                # print("-----------------------------------------------------------------------------------------------")
                                                                print("----------------------------- I N I C I A N D O  A  A N A L I S E -----------------------------")
                                                                print("-----------------------------------------------------------------------------------------------")
                                                                break
                                                            else:
                                                                if len(newConlist) == 0:
                                                                    newConlist = fExecAllMexc().getDefSymbols()
                                                                    cCoinAnalise = newConlist[0]  
                                                                continue
                                                    else:
                                                        newConlist = fExecAllMexc().getDefSymbols()
                                                        cCoinAnalise = newConlist[0]
                                                        newConlist = getCoinList
                                                        diffPercent = 0
                                                        continue
                                                    
                                                if lRun:
                                                    nWaiting = 0
                                                    lastOld = 0
                                                    oscilationPrice = 0
                                                    nIter = 0
                                                    while True:
                                                        lprice = fExecAllMexc().getBookDepth(coinFullName, 1)[0] #bids

                                                        # #guarda preco entrada para calculo
                                                        if float(entryPrice) == 0:
                                                            entryPrice = fExecAllMexc().getBookDepth(coinFullName, 1)[1] #preco de entrada

                                                        diffPercent = fExecAllMexc().calc_diff_percent(float(entryPrice),float(lprice))

                                                        if float(lastOld) == 0:
                                                            lastOld = diffPercent

                                                        if float('%.1f' % diffPercent) in [-0.0,0.0,0.1,0.2] and nIter > 0 and lRun:        
                                                            if cTypeOrdr == 'MARKET':
                                                                #compra tudo
                                                                QtdToBuy = round(fExecAllMexc().retValcomp("USDT"),4)
                                                                fExecAllMexc().fBuyAndSell(QtdToBuy,cCoin,coinFullName,nPercentG,-nPercentL,cTypeOrdr, 0, choice)
                                                                # print("hahah")
                                                                # continue
                                                                # lastold = 0
                                                                # oldDiff = 0
                                                                # entryPrice = 0
                                                                # nCountLoop = 0
                                                                diffPercent = 0
                                                                entryPrice = 0
                                                                lastOld = 0
                                                                oscilationPrice = 0
                                                                nWaiting = 0
                                                                # nOutLold = 0
                                                                nIter = 0
                                                                
                                                                break
                                                        else:
                                                            nWaiting +=1
                                                            nIter += 1

                                                            if diffPercent == lastOld:
                                                                lastOld = diffPercent
                                                                oscilationPrice +=1

                                                            if nWaiting >= 100 and oscilationPrice < 50:
                                                                diffPercent = 0
                                                                entryPrice = 0
                                                                lastOld = 0
                                                                oscilationPrice = 0
                                                                nWaiting = 0
                                                                nIter = 0
                                                                break
                                                            else:
                                                                if oscilationPrice > 50 and nWaiting > 100 and float('%.1f' % diffPercent) not in [-0.1,-0.2]:
                                                                    diffPercent = 0
                                                                    entryPrice = 0
                                                                    lastOld = 0
                                                                    oscilationPrice = 0
                                                                    nWaiting = 0
                                                                    nIter = 0
                                                                    break
                                                                else:
                                                                    print("--------------------------------------")
                                                                    print(f"diff {diffPercent} | lPrice {lprice}")
                                                                    continue
                                        else:
                                            print(f"ServerTime: {timestamp_serverC[1]} ")                                   
                                else:
                                    print("MOEDA não encontrada! *INPUT")

                        elif choice == '6':
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Horario do servidor: {fExecAllMexc().getServerTime()[1]}")
                            print("-----------------------------------------------------------------------------------------------")
                        
                        elif choice == '7':
                            print("-----------------------------------------------------------------------------------------------")
                            coinFullName = input("Digite a moeda: ").upper()
                            coinFullName += 'USDT'
                            print("-----------------------------------------------------------------------------------------------")
                            while True:
                                sleepTime = input("Digite o tempo de consulta: ")

                                if fExecAllMexc().fValidPerc(sleepTime):
                                    sleepTime = int(sleepTime)
                                    print("-----------------------------------------------------------------------------------------------")
                                    break
                                else:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")
                            while True:
                                optTime = input("Usar o timenow ou o serverTime?\n1 = DatetimeNow\n2 = ServerTime\nDigite: ")

                                if fExecAllMexc().fValidPerc(optTime) and int(optTime) in [1,2]:
                                    optTime = int(optTime)
                                    print("-----------------------------------------------------------------------------------------------")
                                    break
                                else:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")
                        
                            if coinFullName in getCoinList:
                                while sleepTime > 0:

                                    sleepTime -= 1

                                    cTimenow = datetime.now().strftime("%H:%M:%S.%f")[:-3] if optTime == 1 else fExecAllMexc().getServerTime()[1]
                                    
                                    cListDepth = fExecAllMexc().getBookDepth(coinFullName, 1)
                                    lprice = fExecAllMexc().getPrice(coinFullName)
                                    print(f"Horario {'Atual' if optTime == 1 else 'do Servidor'}: {cTimenow} | Book_Depth( Prc.Compra: {cListDepth[0]} | Prc.Venda: {cListDepth[1]} | Ultimo preco: {lprice} ) Resta: {sleepTime} iters...")
                                    
                                    # if optTime == 1:
                                    #     #sleep para nao dar crash 
                                    #     time.sleep(0.15) #150ms
                            else:
                                print("MOEDA não encontrada! *INPUT")
                        elif choice == '8':
                            print("-----------------------------------------------------------------------------------------------")
                            coinFullName = input("Digite a moeda: ").upper()
                            coinFullName += 'USDT'
                            print("-----------------------------------------------------------------------------------------------")
                            while True:
                                sleepTime = input("Digite o tempo de consulta: ")

                                if fExecAllMexc().fValidPerc(sleepTime):
                                    sleepTime = int(sleepTime)
                                    print("-----------------------------------------------------------------------------------------------")
                                    break
                                else:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")

                            if coinFullName in getCoinList:
                                entryPrice = 0
                                diffPercent = 0
                                moredif = 0
                                minumdif = 0
                                entrySleep = sleepTime
                                clastMString = ''
                                clastNString = ''

                                while sleepTime > 0:
                                    sleepTime -= 1
                                    time.sleep(0.3) # 1seg

                                    cTimeServer = fExecAllMexc().getServerTime()[1]
                                    # cListDepth = fExecAllMexc().getBookDepth(coinFullName, 1)[0]
                                    lprice = fExecAllMexc().getPrice(coinFullName)

                                    if float(entryPrice) == 0:
                                        entryPrice = lprice #preco de entrada

                                    if diffPercent > 0 and diffPercent >= moredif:
                                        moredif = diffPercent
                                        clastMString = f"Horario: {cTimeServer} | Preco: {lprice} | {moredif}%" 

                                    if diffPercent < 0 and diffPercent <= minumdif:
                                        minumdif = diffPercent
                                        clastNString = f"Horario: {cTimeServer} | Preco: {lprice} | {minumdif}%" 
                
                                    diffPercent = fExecAllMexc().calc_diff_percent(float(entryPrice),float(lprice))
                                    
                                    print(f"{cTimeServer} | Ultimo preco: {lprice} | Diferenca: {diffPercent}% | Aguarde: {sleepTime}segs...")

                                print("-----------------------------------------------------------------------------------------------")
                                print("Resultado:")
                                print("-----------------------------------------------------------------------------------------------")
                                print(f"Preco de entrada: {entryPrice} ")
                                print(f"Maior preco: {clastMString} ")
                                print(f"Menor preco: {clastNString} ")
                                print(f"Meoda: {coinFullName} ")
                                print(f"Tempo: {entrySleep}Segs")
                            else:
                                print("MOEDA não encontrada! *INPUT")
                        elif choice == '9':
                            print("-----------------------------------------------------------------------------------------------")
                            coinFullName = input("Digite a moeda: ").upper()
                            coinFullName += 'USDT'
                            print("-----------------------------------------------------------------------------------------------")

                            fExecAllMexc().getVolume24(coinFullName)
                        elif choice == '10':
                            break
                        else:
                            print("Opção inválida. Por favor, escolha um número de 1 a 5.")

                elif choice == '2':
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>> L A T O K E N <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    while True:
                        print("|----------------------------------------|")
                        print("| Christopher Walk (LATOKEN) - CryptoMan |")
                        print("|----------------------------------------|")
                        print("Escolha uma opção:")
                        print("1. Ver saldo em USDT")
                        print("2. Compra e Venda")
                        print("3. Compra e Venda (Telegram)")
                        print("4. Consultar informações da Moeda")
                        print("5. Consultar dados da Order")
                        print("6. Sair")
                        print(" ")
                        
                        choice = input("Digite o número correspondente à sua ESCOLHA: ")
                        #carrega o saldo em USDT
                        usdtBalance = round(fExecAllLatokeN().getBalancesWallet(pairusdt),4)
                        #carrega a lista de moedas disponiveis
                        getCoinList = fExecAllLatokeN().getCoinList()

                        if choice == '1':#PEGA O SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira.")
                            print("-----------------------------------------------------------------------------------------------")
                        elif choice == '2' or choice == '3':#PLAY NA COMPRA E VENDA
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira.")
                            print("-----------------------------------------------------------------------------------------------")

                            while True:
                                nbuyWithUSDT = input("Escolha quanto quer comprar em USDT com base no saldo disponível em carteira.\nDigite: ")

                                # Verifica se a entrada é um número inteiro positivo
                                try:
                                    if float(nbuyWithUSDT) <= usdtBalance:
                                        QtdUSDToBuy = float(nbuyWithUSDT)
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido. Igual ou inferior ao saldo de: {usdtBalance}")
                                        print("-----------------------------------------------------------------------------------------------")
                                except ValueError:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")
        
                            
                            while True:
                                print("-----------------------------------------------------------------------------------------------")
                                nSellOrders = input("Escolha quantas orders de venda quer gerar. Entre 1 e 4.\nDigite: ")
                                
                                if nSellOrders.isdigit():
                                    if int(nSellOrders) in range(1,5): #max 4
                                        nSellOrders = int(nSellOrders)
                                        break
                                    else:
                                        print("Digite um número inteiro válido. Entre 1 e 4.")
                                else:
                                    print("Digite um número inteiro válido.")


                            if QtdUSDToBuy > 0:
                                print("-----------------------------------------------------------------------------------------------")
                                nPercents = fExecAllMexc().fgGetPercents()
                                                        
                                if choice == '2': #COMPRA INFORMANDO A MOEDA

                                    print("-----------------------------------------------------------------------------------------------")
                                    cCoin = input("Digite a moeda para iniciar a compra: " ).upper()

                                    if cCoin in getCoinList:
                                        #>>>>>>>>>>>>>>>>>>>>>> POST COMPRA MARKET <<<<<<<<<<<<<<<<<<<<<<<<
                                        #>>>>>>>>>>>>>>>>>>>>>> POST VENDA A LIMIT <<<<<<<<<<<<<<<<<<<<<<<<
                                        #getticker pega o ultimo preco para usar na divisao e realizar a comprar pela qtde de moeda 
                                        getLastPrice = fExecAllLatokeN().getTicker(cCoin)

                                        if round((QtdUSDToBuy / float(getLastPrice[0])),2) > 0:
                                            # if getLastPrice is not None and round((QtdUSDToBuy / float(getLastPrice)),2) > 0 :
                                            if getLastPrice[0] is not None:
                                                fExecAllLatokeN().fBuyAndSell(round((QtdUSDToBuy / float(getLastPrice[0])),2), cCoin,  nPercents, nSellOrders,getLastPrice[1]  )
                                            else:
                                                print("Falha na obtenção do ultimo preço")
                                        else:
                                            print("-----------------------------------------------------------------------------------------------")
                                            print(f"Só é possivel comprar acima de 0.01 da moeda! resultado {round((QtdUSDToBuy / float(getLastPrice[0])),18)}")
                                    else:
                                        print("MOEDA não encontrada! *INPUT")

                                else:#COMPRA AUTO PELO GRUPO DO TELEGRAM
                                    
                                    bot = TelegramBot(TG_SESSION, os.getenv('API_ID'), os.getenv('API_HASH'), os.getenv('COIN_REGEX'),  getCoinList, QtdUSDToBuy, nPercents, nSellOrders, exchange="LATOKEN")
                                    bot.start()
                        elif choice == "4":
                            print("-----------------------------------------------------------------------------------------------")
                            cCNaame = input("Digite a moeda: ").upper()
                            fExecAllLatokeN().getInfoCoinByName(cCNaame)
                        
                        elif choice == "5":
                            print("-----------------------------------------------------------------------------------------------")
                            cOrdID = input("Digite o numero da Order: ").lower()
                            fExecAllLatokeN().getorderByID(cOrdID,1)
                        else:
                            break
                elif choice == '3':
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>> K U C O I N <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    while True:
                        print("|---------------------------------------|")
                        print("| Christopher Walk (KUCOIN) - CryptoMan |")
                        print("|---------------------------------------|")
                        print("Escolha uma opção:")
                        print("1. Ver saldo em USDT")
                        print("2. Compra e Venda")
                        print("3. Compra e Venda (Telegram)")
                        print("4. Consulta informações da Moeda")
                        print("5. Consultar Order pelo ID")
                        print("6. Sair")
                        print(" ")
                        
                        choice = input("Digite o número correspondente à sua ESCOLHA: ")

                        #carrega o saldo em USDT
                        usdtBalance = round(fExecAllKuCoin().get_account_balance(),4)
                        #lista de meodas disponiveis
                        getCoinList = fExecAllKuCoin().get_kucoin_symbols('', 1, kupair, '')

                        if choice == '1':#PEGA O SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira.")
                            print("-----------------------------------------------------------------------------------------------")
                        elif choice == '2' or choice == '3':#PLAY NA COMPRA E VENDA
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira.")
                            print("-----------------------------------------------------------------------------------------------")

                            while True:
                                nbuyWithUSDT = input("Escolha quanto quer comprar em USDT com base no saldo disponível em carteira.\nDigite: ")

                                # Verifica se a entrada é um número inteiro positivo
                                try:
                                    if float(nbuyWithUSDT) <= usdtBalance:
                                        QtdUSDToBuy = float(nbuyWithUSDT)
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido. Igual ou inferior ao saldo de: {usdtBalance}")
                                        print("-----------------------------------------------------------------------------------------------")
                                except ValueError:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")
                            
                            if QtdUSDToBuy > 0:
                                print("-----------------------------------------------------------------------------------------------")
                                nPercents = fExecAllMexc().fgGetPercents()
                                                        
                                if choice == '2': #COMPRA INFORMANDO A MOEDA
                                    print("-----------------------------------------------------------------------------------------------")
                                    cCoin = input("Digite a moeda para iniciar a compra: " ).upper()
                                    cCoin += kupair

                                    if cCoin in getCoinList:
                                        #pega a base minima para compra da moeda
                                        baseMintoBuy = fExecAllKuCoin().get_kucoin_symbols('' , 3, '', cCoin)                               
                                        #pega o ultimo preco para usar na divisao e realizar a comprar pela qtde de moeda 
                                        getLastPrice = fExecAllKuCoin().get_kucoin_ticker(cCoin)
                                        #transforma o valor informado em qtde em moedas e seus decimais
                                        baseBuyCoin = fExecAllKuCoin().qtdBase(baseMintoBuy[0], float(QtdUSDToBuy), float(getLastPrice))

                                        cFinalQtdToBuy = baseBuyCoin if float(baseMintoBuy[0]) < baseBuyCoin else float(baseMintoBuy[0])

                                        if cFinalQtdToBuy is not None:
                                            fExecAllKuCoin().fBuyAndSell(str(cFinalQtdToBuy),cCoin,nPercents,1,baseMintoBuy[0], baseMintoBuy[1])
                                        else:
                                            print("-----------------------------------------------------------------------------------------------")
                                            print("Falha na obtenção do ultimo preço")
                                    else:
                                        print("MOEDA não encontrada! *INPUT")

                                else:#COMPRA AUTO PELO GRUPO DO TELEGRAM
                                    bot = TelegramBot(TG_SESSION, os.getenv('API_ID'), os.getenv('API_HASH'), os.getenv('COIN_REGEX'),  getCoinList, QtdUSDToBuy, nPercents, 1, exchange="KUCOIN")
                                    bot.start()

                        elif choice == "4":
                            print("-----------------------------------------------------------------------------------------------")
                            cCNaame = input("Digite a moeda: ").upper()
                            print("-----------------------------------------------------------------------------------------------")
                            fExecAllKuCoin().get_kucoin_symbols(cCNaame, 2, kupair, '' )
                        elif choice == "5":
                            # '659f229bcfe6220007405235'
                            cOrderID = input("Digite o ID da ordem: ")
                            fExecAllKuCoin().getorderByID(cOrderID, 1)
                        elif choice == "6":
                            break
                elif choice == '4':
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>> D I G I F I N E X <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    while True:
                        print("|------------------------------------------|")
                        print("| Christopher Walk (DIGIFINEX) - CryptoMan |")
                        print("|------------------------------------------|")
                        print("Escolha uma opção:")
                        print("1. Ver saldo em USDT")
                        print("2. Compra e Venda")
                        print("3. Compra e Venda (Telegram)")
                        print("4. Consultar Order pelo ID")
                        print("5. Sair")
                        print(" ")
                        
                        choice = input("Digite o número correspondente à sua ESCOLHA: ")

                        #carrega o saldo em USDT
                        usdtBalance = round(fExecAllDigiFinex().getAccBalance(),4)
                        #lista de meodas disponiveis
                        getCoinList = fExecAllDigiFinex().getSymbols(1)

                        if choice == '1':#PEGA O SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira. Só é possivel comprar acima de: 2.5 USDT")
                            print("-----------------------------------------------------------------------------------------------")
                        elif choice == '2' or choice == '3':#PLAY NA COMPRA E VENDA
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira.")
                            print("-----------------------------------------------------------------------------------------------")
                            _i = fExecAllDigiFinex().divisor2_5(usdtBalance) #MOSTRA QUANTO PODE SER COMPRADO COM BASE NO SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")

                            if _i > 1:
                                cRetUser = input("Escolha quanto quer comprar em USDT com base no resultado acima.\nDigite: ") 
                            else:
                                print("Vou comprar pq só da pra executar uma ordem de venda!")
                                cRetUser = '1'

                            QtdUSDToBuy = 0
                            
                            if int(cRetUser) in range(1,20):
                                QtdUSDToBuy = fExecAllDigiFinex().fQtdBuy(usdtBalance,cRetUser)
                            else:
                                print("-----------------------------------------------------------------------------------------------")
                                print("Dado invalido.\nOpcoes disponiveis: 1,2,.....20.")


                            if QtdUSDToBuy > 0:
                                print("-----------------------------------------------------------------------------------------------")
                                nPercents = fExecAllMexc().fgGetPercents()
                                                        
                                if choice == '2': #COMPRA INFORMANDO A MOEDA
                                    print("-----------------------------------------------------------------------------------------------")
                                    cCoin = input("Digite a moeda para iniciar a compra: " ).upper()

                                    if cCoin in getCoinList:
                                        cCoin += digiPair

                                        fExecAllDigiFinex().fBuyAndSell(QtdUSDToBuy,cCoin,nPercents,1)
                                    else:
                                        print("MOEDA não encontrada! *INPUT")

                                else:#COMPRA AUTO PELO GRUPO DO TELEGRAM
                                    bot = TelegramBot(TG_SESSION, os.getenv('API_ID'), os.getenv('API_HASH'), os.getenv('COIN_REGEX'),  getCoinList, QtdUSDToBuy, nPercents, 1, exchange="DIGIFINEX")
                                    bot.start()
                            else:
                                print("-----------------------------------------------------------------------------------------------")
                                print("Valor abaixo do minimo permitido. Minimo 2.5 USDT")
                        elif choice == "4":
                            print("-----------------------------------------------------------------------------------------------")
                            cOrdID = input("Digite o numero da Order: ").lower()
                            fExecAllDigiFinex().getorderByID(cOrdID,2)
                        elif choice == "5":
                            break
                elif choice == '5':
                    print("-----------------------------------------------------------------------------------------------")
                    print("Saindo do programa. Até logo!")
                    break
        elif choice == '2':
            while True:
                fTypeFutures()
                print("|      Escolha a Exchange      |")
                print("|------------------------------|")
                print("1. Binance")
                print("2. Mexc")
                print("3. Sair")
                print(" ")
                
                choice = input("Digite o número correspondente à sua ESCOLHA: ") or '1'
                print(" ")
                #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                #>>>>>>>>>>>>>>>>>>>>>>>>>>>> B I N A N C E <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                if choice == '1':
                    while True:
                        cValidValueN = 0
                        cValidValue = 0
                        cValueUsInputTP = 0
                        cValueUsInputSL = 0
                        nSetQtyOrder1 = 0
                        nSetQtyOrder2 = 0
                        listTPorSL1 = []
                        listTPorSL2 = []
                        nPercentG = 0
                        nPercentL = 0
                        headerBinance()
                        print("Escolha uma opção:")
                        print("1. Ver saldo em USDT")
                        print("2. Compra e Venda por percentual / valor manual TP/SL")
                        print("3. Compra e Venda Market percentual EMA")
                        print("4. getOrder ID")
                        print("5. Relatório Diário")
                        # print("3. Compra e Venda (Telegram)")
                        # print("4. Consultar Order pelo ID")
                        print("6. Sair")
                        print(" ")
                        
                        choice = input("Digite o número correspondente à sua ESCOLHA: ") or '3'

                        #carrega o saldo em USDT
                        usdtBalance = BinanceFutures().fGetBalance('')
                        #lista de meodas disponiveis
                        getCoinList = BinanceFutures().fGetExchangeInfo(0,'')

                        if choice == '1':#PEGA O SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira USD-M Futures. ")
                            print("-----------------------------------------------------------------------------------------------")
                        elif choice == '2':# or choice == '3':#PLAY NA COMPRA E VENDA
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira USD-M Futures.")
                            print("-----------------------------------------------------------------------------------------------")

                            while True:
                                nbuyWithUSDT = input("Escolha quanto quer comprar em USDT com base no saldo disponível em carteira. Minimo 6 USDT\nDigite: ")

                                # Verifica se a entrada é um número inteiro positivo
                                try:
                                    if float(nbuyWithUSDT) <= usdtBalance and float(nbuyWithUSDT) >= 6:
                                        QtdUSDToBuy = float(nbuyWithUSDT)
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido. >= 6 USDT ou inferior ao saldo de: {usdtBalance}")
                                        print("-----------------------------------------------------------------------------------------------")
                                except ValueError:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")
                            
                            if QtdUSDToBuy > 0:
                                print("-----------------------------------------------------------------------------------------------")                                                        
                                if choice == '2': #COMPRA INFORMANDO A MOEDA
                                    # print("-----------------------------------------------------------------------------------------------")
                                    coinFullName = input("Digite a moeda para iniciar a compra: " ).upper()
                                    coinFullName += 'USDT'

                                    if coinFullName in getCoinList:
                                        while True:
                                            print("-----------------------------------------------------------------------------------------------")
                                            cTypeOrdr = input("Informe o tipo de Order de compra\n1 = LIMIT\n2 = MARKET\nDigite: ")
                                            
                                            if not cTypeOrdr:
                                                print("-----------------------------------------------------------------------------------------------")
                                                print(f"Digite uma opcao válida.")
                                            else:
                                                if int(cTypeOrdr) in [1,2]:
                                                    cTypeOrdr = 'LIMIT' if int(cTypeOrdr) == 1 else 'MARKET'
                                                    break
                                                else:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print(f"Digite uma opcao válida.")
                                        
                                        while True:
                                            print("-----------------------------------------------------------------------------------------------")
                                            nSetLeverage = input("Informe em quantos X quer alavancar. Ou Pressione Enter para alavancar em 1x\nDigite: ")
                                            
                                            if not nSetLeverage:
                                                print("-----------------------------------------------------------------------------------------------")
                                                nSetLeverage = BinanceFutures().fSetLeverageAndMarginType(coinFullName, 1)
                                                
                                                print(f"{coinFullName}: Alavancado em {nSetLeverage}x | Margem: ISOLATED")#A margem tambem eh atualizada nessa mesma funcao
                                                break
                                            else:
                                                if int(nSetLeverage):
                                                    nSetLeverage = BinanceFutures().fSetLeverageAndMarginType(coinFullName, int(nSetLeverage))
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print(f"{coinFullName}: Alavancado em {nSetLeverage}x | Margem: ISOLATED")#A margem tambem eh atualizada nessa mesma funcao
                                                    break
                                                else:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print(f"Digite um numero válido.")
                                        
                                        while True:
                                            print("-----------------------------------------------------------------------------------------------")
                                            cSide = input("Informe se quer comprar ou vender\n1 = COMPRA(LONG)\n2 = VENDA(SHORT)\nDigite: ")
                                            
                                            if not cSide:
                                                print("-----------------------------------------------------------------------------------------------")
                                                print(f"Digite uma opcao válida.")
                                            else:
                                                if int(cSide) in [1,2]:
                                                    cSide = 'BUY' if int(cSide) == 1 else 'SELL'
                                                    break
                                                else:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print(f"Digite uma opcao válida.")
                                        
                                        if cTypeOrdr == 'LIMIT':
                                            while True:
                                                cPrintPrice = BinanceFutures().fGetTickerPrice(coinFullName)
                                                print("-----------------------------------------------------------------------------------------------")
                                                print(f" Ultimo preco: {cPrintPrice}")
                                            
                                                cValidValue = input("Digite o preço caso queira inseri-lo manualmente ou\npressione Enter para usar o ultimo preco ou\ndigite X para atualizar o ultimo preco:  ")

                                                if cValidValue.upper() == 'X':
                                                    continue
                                                elif not cValidValue:
                                                    cValidValue = 0
                                                    # Se o usuário pressionar Enter, encerre o loop
                                                    break
                                                try:
                                                    
                                                    #Tente converter a entrada 
                                                    cBaseDecs = BinanceFutures().fGetExchangeInfo(1,coinFullName)[0]['pricePrecision']
                                                    cValidValueN =  BinanceFutures().cBaseConverter(cBaseDecs,float(cValidValue),0)

                                                    cValidValue = 0
                                                    # cValidValue = float(cValidValue)
                                                    break
                                                except ValueError:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print("Formato de preço inválido. Tente novamente.")
                                                    continue
                                        else:
                                            while True:
                                                cPrintPrice = BinanceFutures().fGetTickerPrice(coinFullName)
                                                print("-----------------------------------------------------------------------------------------------")
                                                print(f" Ultimo preco: {cPrintPrice}")
                                                print("-----------------------------------------------------------------------------------------------")

                                                cValidValueN = input("Digite o preço (ENTRY PRICE) caso queira inseri-lo manualmente (LOOP FUNCTION) ou\npressione Enter comprar a mercado com percentual de ganho e de perda: ")
                                            
                                                if not cValidValueN:
                                                        cValidValueN = 0
                                                        # Se o usuário pressionar Enter, encerre o loop
                                                        break
                                                try:
                                                    
                                                    #Tente converter a entrada 
                                                    cBaseDecs = BinanceFutures().fGetExchangeInfo(1,coinFullName)[0]['pricePrecision']
                                                    cValidValueN = BinanceFutures().cBaseConverter(cBaseDecs,float(cValidValueN),0)

                                                    cValidValue = 0
                                                    # cValidValue = float(cValidValue)
                                                    break
                                                except ValueError:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print("Formato de preço inválido. Tente novamente.")
                                                    continue
                                            
                                            if cValidValueN > 0:
                                                while True:
                                                    nRetQtyOrders = BinanceFutures().check_division_by_six(QtdUSDToBuy)
                                                        
                                                    
                                                    if nRetQtyOrders > 1:
                                                        cPrintText = "(TAKE PROFIT) GANHO" if cSide == 'BUY' else "(STOP LOSS) PERDA"
                                                        print("-----------------------------------------------------------------------------------------------")
                                                        print(f" Com base no valor de entrada é possivel gerar: {nRetQtyOrders} orders do tipo {cPrintText}")
                                                        print("-----------------------------------------------------------------------------------------------")

                                                        while True:
                                                            
                                                            nSetQtyOrder1 = input("Informe quantas orders TP quer gerar. Ou Pressione Enter para gerar apenas UMA order\nDigite: ")                                                        
                                                            if not nSetQtyOrder1:
                                                                print("-----------------------------------------------------------------------------------------------")
                                                                nSetQtyOrder1 = 1
                                                        
                                                                print("Voce escolheu gerar apenas uma Order TP! ")
                                                                break
                                                            else:
                                                                nSetQtyOrder1 = int(nSetQtyOrder1)
                                                                if nSetQtyOrder1 <= nRetQtyOrders:
                                                                    print("-----------------------------------------------------------------------------------------------")
                                                                    listTPorSL1 = BinanceFutures().fGetInputTP(nSetQtyOrder1,cBaseDecs, cValidValueN,cSide) if cSide == 'BUY' else BinanceFutures().fGetInputTP2(nSetQtyOrder1,cBaseDecs, cValidValueN,cSide)

                                                                    print("-----------------------------------------------------------------------------------------------")
                                                                    # for i, item in enumerate(integer_inputs, start=1):
                                                                    #     print(f"TP: {i}: {item}")
                                                                    break
                                                                else:
                                                                    print("-----------------------------------------------------------------------------------------------")
                                                                    print("Digito inválido. Tente novamente.")
                                                                    continue

                                                        if len(listTPorSL1) > 1:
                                                            while True:
                                                                
                                                                nSetQtyOrder2 = input("Informe quantas orders SL quer gerar. Ou Pressione Enter para gerar apenas UMA order\nDigite: ")
                                                                
                                                                if not nSetQtyOrder2:
                                                                    print("-----------------------------------------------------------------------------------------------")
                                                                    nSetQtyOrder2 = 1
                                                            
                                                                    print("Voce escolheu gerar apenas uma Order SL! ")
                                                                    while True:
                                                                        print("-----------------------------------------------------------------------------------------------")
                                                                        print(f"Preco de entrada: {cValidValueN}")
                                                                        print("-----------------------------------------------------------------------------------------------")
                                                                        cPrintText = "Digite o preço (STOP LOSS) PERDA" if cSide == 'BUY' else "Digite o preço (TAKE PROFIT) GANHO"
                                                                        cValueUsInputSL = input(f"{cPrintText}\nDigite: ")

                                                                        try:
                                                                            #Tente converter a entrada
                                                                            if float(cValueUsInputSL) < cValidValueN: 
                                                                                cValueUsInputSL = BinanceFutures().cBaseConverter(cBaseDecs,float(cValueUsInputSL),0)
                                                                                break
                                                                            else:
                                                                                print("-----------------------------------------------------------------------------------------------")
                                                                                print(f"O preço tem que ser MENOR do que o informado na entrada {cValidValueN}. Tente novamente.")
                                                                                continue
                                                                        except ValueError:
                                                                            print("-----------------------------------------------------------------------------------------------")
                                                                            print("Formato de preço inválido. Tente novamente.")
                                                                            continue
                                                                    break
                                                                else:
                                                                    nSetQtyOrder2 = int(nSetQtyOrder2)
                                                                    if nSetQtyOrder2 <= nRetQtyOrders:
                                                                        print("-----------------------------------------------------------------------------------------------")
                                                                        listTPorSL2 = BinanceFutures().fGetInputTP2(nSetQtyOrder2,cBaseDecs, cValidValueN,cSide) if cSide == 'BUY'else BinanceFutures().fGetInputTP(nSetQtyOrder2,cBaseDecs, cValidValueN,cSide)

                                                                        print("-----------------------------------------------------------------------------------------------")
                                                                        # for i, item in enumerate(integer_inputs, start=1):
                                                                        #     print(f"TP: {i}: {item}")
                                                                        break
                                                                    else:
                                                                        print("-----------------------------------------------------------------------------------------------")
                                                                        print("Digito inválido. Tente novamente.")
                                                                        continue
                                                            break
                                                    break


                                                if cValidValueN > 0 and len(listTPorSL1) == 0:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print(f"Preco de entrada: {cValidValueN} | Tipo: {cSide}")
                                                    

                                                    while True:
                                                        print("-----------------------------------------------------------------------------------------------")
                                                        cPrintText = "Digite o preço (TAKE PROFIT) GANHO" if cSide == 'BUY' else "Digite o preço (STOP LOSS) PERDA"
                                                        cValueUsInputTP = input(f"{cPrintText}\nDigite: ")

                                                        try:
                                                            #Tente converter a entrada
                                                            if float(cValueUsInputTP) > cValidValueN:
                                                                cValueUsInputTP = BinanceFutures().cBaseConverter(cBaseDecs,float(cValueUsInputTP),0)
                                                                break
                                                            else:
                                                                print("-----------------------------------------------------------------------------------------------")
                                                                print(f"O preço tem que ser MAIOR do que o informado na entrada {cValidValueN}. Tente novamente.")
                                                                continue

                                                        except ValueError:
                                                            print("-----------------------------------------------------------------------------------------------")
                                                            print("Formato de preço inválido. Tente novamente.")
                                                            continue
                                                    
                                                    while True:
                                                        print("-----------------------------------------------------------------------------------------------")
                                                        cPrintText = "Digite o preço (STOP LOSS) PERDA" if cSide == 'BUY' else "Digite o preço (TAKE PROFIT) GANHO"
                                                        cValueUsInputSL = input(f"{cPrintText}\nDigite: ")

                                                        try:
                                                            #Tente converter a entrada
                                                            if float(cValueUsInputSL) < cValidValueN: 
                                                                cValueUsInputSL = BinanceFutures().cBaseConverter(cBaseDecs,float(cValueUsInputSL),0)
                                                                break
                                                            else:
                                                                print("-----------------------------------------------------------------------------------------------")
                                                                print(f"O preço tem que ser MENOR do que o informado na entrada {cValidValueN}. Tente novamente.")
                                                                continue
                                                        except ValueError:
                                                            print("-----------------------------------------------------------------------------------------------")
                                                            print("Formato de preço inválido. Tente novamente.")
                                                            continue


                                            if cValidValueN == 0:
                                                while True:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    cPrintText = "Informe o percentual de GANHO" if cSide == 'BUY' else "Informe o percentual de PERDA"
                                                    nPercentG = input(f"{cPrintText}\nDigite: ")

                                                    if fExecAllMexc().fValidPerc(nPercentG):
                                                        nPercentG = int(nPercentG)
                                                        print("-----------------------------------------------------------------------------------------------")
                                                        break
                                                    else:
                                                        print("-----------------------------------------------------------------------------------------------")
                                                        print(f"Digite um número válido.")
                                                        print("-----------------------------------------------------------------------------------------------")
                        
                                                while True:
                                                    cPrintText = "Informe o percentual de PERDA" if cSide == 'BUY' else "Informe o percentual de GANHO"
                                                    nPercentL = input(f"{cPrintText}\nDigite: ")

                                                    if fExecAllMexc().fValidPerc(nPercentL):
                                                        nPercentL = int(nPercentL)
                                                        # print("-----------------------------------------------------------------------------------------------")
                                                        break
                                                    else:
                                                        print("-----------------------------------------------------------------------------------------------")
                                                        print(f"Digite um número válido.")
                                                        print("-----------------------------------------------------------------------------------------------")
                                        
                                        if float(cValidValue) == 0:
                                            cValidValue = QtdUSDToBuy

                                        if float(cValidValue) > 0 or float(cValidValueN) > 0:
                                            # print("-----------------------------------------------------------------------------------------------")
                                            BinanceFutures().fPostNewOrder(coinFullName,cSide,cTypeOrdr, cValidValue, cValidValueN,cValueUsInputTP,cValueUsInputSL, nPercentG if cTypeOrdr == 'MARKET' else 0, -nPercentL if cTypeOrdr == 'MARKET' else 0, listTPorSL1,listTPorSL2)
                                            # break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print("MOEDA não encontrada! *INPUT")

                                else:#COMPRA AUTO PELO GRUPO DO TELEGRAM
                                    bot = TelegramBot(TG_SESSION, os.getenv('API_ID'), os.getenv('API_HASH'), os.getenv('COIN_REGEX'),  getCoinList, QtdUSDToBuy, nPercents, 1, exchange="KUCOIN")
                                    bot.start()
                        elif choice == '3':#XPTO
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira USD-M Futures.")
                            print("-----------------------------------------------------------------------------------------------")

                            while True:
                                nbuyWithUSDT = input("Escolha quanto quer comprar em USDT com base no saldo disponível em carteira. Minimo 6 USDT\nDigite: ") or os.getenv('DEFVALUE')

                                # Verifica se a entrada é um número inteiro positivo
                                try:
                                    if float(nbuyWithUSDT) <= usdtBalance and float(nbuyWithUSDT) >= 0:
                                        QtdUSDToBuy = float(nbuyWithUSDT)
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido. >= 6 USDT ou inferior ao saldo de: {usdtBalance}") 
                                        print("-----------------------------------------------------------------------------------------------")
                                except ValueError:
                                    print("-----------------------------------------------------------------------------------------------")
                                    print(f"Digite um número válido.")
                                    print("-----------------------------------------------------------------------------------------------")
                            
                            if QtdUSDToBuy >= 0:
                                print("-----------------------------------------------------------------------------------------------")
                                while True:
                                    nPercentG = input("Informe o percentual de GANHO.\nDigite: ") or os.getenv('DEFPERCGAIN')

                                    if fExecAllMexc().fValidPerc(nPercentG):
                                        nPercentG = float(nPercentG)
                                        print("-----------------------------------------------------------------------------------------------")
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido.")
                                        print("-----------------------------------------------------------------------------------------------")
        
                                while True:
                                    nPercentL = input("Informe o percentual de PERDA.\nDigite: ") or os.getenv('DEFPERCLOSS')

                                    if fExecAllMexc().fValidPerc(nPercentL):
                                        nPercentL = float(nPercentL)
                                        print("-----------------------------------------------------------------------------------------------")
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um número válido.")
                                        print("-----------------------------------------------------------------------------------------------")

                                while True:
                                    simulator = input("Digite 'S' Para entrar no modo simulação \nDigite: ") or os.getenv('SIMULATOR')

                                    if simulator == os.getenv('SIMULATOR'):
                                        # nPercentL = float(nPercentL)
                                        # print("-----------------------------------------------------------------------------------------------")
                                        break
                                    else:
                                        print("-----------------------------------------------------------------------------------------------")
                                        print(f"Digite um caracter válido.")
                                        print("-----------------------------------------------------------------------------------------------")
                                
                                
                                diffPercent = 0
                                entryPrice = 0
                                lastold = 0
                                nIter = 0
                                newConlist = getCoinList

                                while True:
                                    
                                    if diffPercent == 0:
                                        # entryPrice = 0
                                        # diffPercent = 0
                                        if len(newConlist) > 0:
                                            for cCoinAnalise in newConlist:
                                                lRun = False
                                                newConlist.remove(cCoinAnalise)
                                            
                                                coinFullName=cCoinAnalise
                                                time.sleep(10)
                                                print(f"Analisando a Moeda... {coinFullName}")
                                                print("-----------------------------------------------------------------------------------------------")
                                                # klines
                                                # 1m |3m | 5m | 15m | 30m | 1h | 2h | 4h | 6h | 8h | 12h | 1d | 3d | 1w | 1M
                                                
                                                lRun = BinanceFutures().fGetKlines(coinFullName,'5m',)
                                                # lRun = BinanceFutures().fGetWebSocketKlines(coinFullName,'5m',)
                                                # time.sleep(3)

                                                if lRun[0]:
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    print("----------------------------- I N I C I A N D O  A  A N A L I S E -----------------------------")
                                                    print("-----------------------------------------------------------------------------------------------")
                                                    break
                                                else:
                                                    if len(newConlist) == 0:
                                                      newConlist = BinanceFutures().fGetExchangeInfo(0,'')
                                                      cCoinAnalise = newConlist[0]  
                                                    continue

                                        else:
                                            newConlist = BinanceFutures().fGetExchangeInfo(0,'')
                                            cCoinAnalise = newConlist[0]
                                            diffPercent = 0
                                            continue

                                    if lRun[0]:   
                                    #pega o ultimo preco
                                    # lprice = fExecAllMexc().getPrice(coinFullName)
                                        nWaiting = 0
                                        lastOld = 0
                                        oscilationPrice = 0
                                        nIter = 0
                                        while True:
                                            lprice = BinanceFutures().fGetDepth(coinFullName, round(abs(diffPercent),2))[0] #bids

                                            # #guarda preco entrada para calculo
                                            if float(entryPrice) == 0:
                                                entryPrice = BinanceFutures().fGetDepth(coinFullName, round(abs(diffPercent),2))[1] #preco de entrada

                                            diffPercent = fExecAllMexc().calc_diff_percent(float(entryPrice),float(lprice))

                                            if float(lastOld) == 0:
                                                lastOld = diffPercent

                                            if float('%.2f' % diffPercent) in [0.00,0.0,-0.01,-0.02] and nIter > 0 and lRun[0]:        

                                                print("-----------------------------------------------------------------------------------------------")
                                                nSetLeverage = BinanceFutures().fSetLeverageAndMarginType(coinFullName, 5)#xpto2
                                                
                                                print(f"{coinFullName}: Alavancado em {nSetLeverage}x | Margem: ISOLATED")#A margem tambem eh atualizada nessa mesma funcao
                                                print("-----------------------------------------------------------------------------------------------")

                                                nNewValue = BinanceFutures().fGetBalance('')

                                                #atualiza vlr entrada caso tome um preju
                                                #temporaria
                                                if QtdUSDToBuy != nNewValue:
                                                    if nNewValue < 10:
                                                        QtdUSDToBuy = 6
                                                    else:
                                                        QtdUSDToBuy = 6
                                                
                                                BinanceFutures().fBuyAndSell(coinFullName, lRun[1], 'MARKET', ((QtdUSDToBuy * nSetLeverage) * 0.95 ), nPercentG, -nPercentL, nSetLeverage, lRun[2], simulator)

                                                diffPercent = 0
                                                entryPrice = 0
                                                lastOld = 0
                                                oscilationPrice = 0
                                                nWaiting = 0
                                                nIter = 0
                                                
                                                break
                                            else:
                                                nWaiting +=1
                                                nIter += 1

                                                if diffPercent == lastOld:
                                                    lastOld = diffPercent
                                                    oscilationPrice +=1

                                                if nWaiting >= 10 and oscilationPrice < 5:
                                                    diffPercent = 0
                                                    entryPrice = 0
                                                    lastOld = 0
                                                    oscilationPrice = 0
                                                    nWaiting = 0
                                                    nIter = 0
                                                    break
                                                else:
                                                    if oscilationPrice > 5 and nWaiting > 10 and float('%.1f' % diffPercent) not in [-0.1,-0.2]:
                                                        diffPercent = 0
                                                        entryPrice = 0
                                                        lastOld = 0
                                                        oscilationPrice = 0
                                                        nWaiting = 0
                                                        nIter = 0
                                                        break
                                                    else:
                                                        print("--------------------------------------")
                                                        print(f"diff {diffPercent} | lPrice {lprice}")
                                                        if nWaiting > 10:
                                                            break
                                                        else:
                                                            continue
                
                        elif choice == '4':
                            print(BinanceFutures().getOrderByID('SPELLUSDT',1439514173))
                        elif choice == '5':
                            print("-----------------------------------------------------------------------------------------------")
                            cDataFiltro = input("Informe o Dia a ser pesquisa. Exemplo: 04/04/2024: ")
                            print("-----------------------------------------------------------------------------------------------")


                            if BinanceFutures().validar_data(cDataFiltro):
                                consulta_trade_hist_por_data(cDataFiltro)
                            else:
                                print("A data NÃO está no formato correto.")


                        elif choice == '6':
                            break
                elif choice == '2':
                    # ctime = fExecAllMexcFutures().getDefSymbols()
                        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> M E X C <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    while True:
                        headerMexc()
                        print("Escolha uma opção:")
                        print("1. Ver saldo em USDT")
                        print("2. Compra e Venda")
                        print("4. Sair")
                        print(" ")
                        
                        choice = input("Digite o número correspondente à sua ESCOLHA: ")

                        #lista de meodas disponiveis
                        # getCoinList = fExecAllMexcFutures().getDefSymbols()
                        #carrega o saldo em USDT
                        # usdtBalance = fExecAllMexcFutures().uSDTaccInfo()

                        if choice == '1':#PEGA O SALDO EM USDT
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira USD-M Futures. ")
                            print("-----------------------------------------------------------------------------------------------")
                        elif choice == '2':# or choice == '3':#PLAY NA COMPRA E VENDA
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Saldo disponivel em USDT: {usdtBalance} na carteira USD-M Futures.")
                            print("-----------------------------------------------------------------------------------------------")
                    print(ctime)
                    
                elif choice == '3':
                    print("-----------------------------------------------------------------------------------------------")
                    print("Saindo do programa. Até logo!")
                    break       
        else:
            print("-----------------------------------------------------------------------------------------------")
            print("Saindo do programa. Até logo!")
            break
        