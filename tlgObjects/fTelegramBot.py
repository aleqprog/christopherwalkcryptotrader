from telethon.sync import TelegramClient, events
from datetime import datetime, timedelta, timezone
from mexcProject.fExecAllMexc import fExecAllMexc
from latokenProject.fExecAllLatokeN import *
from kucoinProject.fExecAllKuCoin import *
from digifinexProject.fExecAllDigiFinex import *
import tlgObjects.regMessages as r
import os
import re
from dotenv import load_dotenv
load_dotenv()

# Exemplo de chamada:
# bot = TelegramBot(TG_SESSION, API_ID, API_HASH, COIN_REGEX, LISTA_DE_MOEDA, QTDE_A_COMPRAR, PERCENTUAIS, NOME_DA_EXCHANGE)
# bot.start()

phone_number=os.getenv('PHONE_NUMBER')
kupair = os.getenv('KU_PAIR_TEXT')
digiPair = os.getenv('DIGI_PAIR_TEXT')

class TelegramBot:
    def __init__(self, tg_session, api_id, api_hash, coin_regex, getCoinList, qtdtbuy, npercents, nqtysellorders, exchange):
        self.tg_channel = ''
        self.client = TelegramClient(tg_session, api_id, api_hash)
        self.coin_regex = coin_regex
        self.getCoinList = getCoinList
        self.qtdtbuy = qtdtbuy
        self.npercents = npercents
        self.exchange = exchange
        self.nqtysellorders = nqtysellorders

    def format_message_date(self,message_date):
        # Converte a data para o fuso horário de Brasília
        br_timezone = timezone(timedelta(hours=-3))
        message_date = message_date.replace(tzinfo=timezone.utc).astimezone(br_timezone)

        # Formata a data para o formato desejado
        formatted_date = message_date.strftime("%H:%M:%S.%f")[:-3]
        return formatted_date
    
    async def group_exists(self, client, group_username):
        """Verifica se o grupo existe"""
        await client.connect()

        #verifica se esta autorizado. caso contrario fica em loop e nao acha o grupo mesmo informando corretamente
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            await client.sign_in(phone_number, input('Digite o código recebido:'))
        
        try:
            await client.get_entity(group_username)
            return True
        except Exception as e:
            return False

    def start(self):
        while not self.client.loop.run_until_complete(self.group_exists(self.client, self.tg_channel)):
            print(f'O grupo / canal {self.tg_channel} nao foi encontrado! Informe novamente!')
            self.tg_channel = input(f'Qual canal do telegram sera postada a moeda? [{self.tg_channel}] ') or self.tg_channel

        @self.client.on(events.NewMessage(chats=self.tg_channel))
        async def getCoinName(event):
            message_date = self.format_message_date(event.message.date) 
            lSell = False
            # if re.search(self.coin_regex, event.raw_text):
            if r.getCoin(self.tg_channel, event.raw_text):
                cCoinTLG = event.raw_text
                print("-----------------------------------------------------------------------------------------------")
                print(f'MSG RECEBIDA EM: {message_date} | MSG LIDA EM: {datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} | COMPRAR moeda: {cCoinTLG}')

                if self.exchange == "MEXC":
                    coinFullName = cCoinTLG + "USDT"

                    if coinFullName in self.getCoinList:
                        respBuyTlg = fExecAllMexc().fBuyOnTLG(self.qtdtbuy, cCoinTLG, coinFullName, self.npercents)

                        if 'msg' not in respBuyTlg and len(respBuyTlg) > 0:
                            print(respBuyTlg)
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Preco da compra: {respBuyTlg['price']}. Vamos utiliza-lo para a venda com o acrescimo do percentual.")
                            lSell = True
                        else:
                            print(f"Falha na operação de compra: {respBuyTlg}")
                    else:
                        print("MOEDA não encontrada! *TLG")
                        print("-----------------------------------------------------------------------------------------------")

                elif self.exchange == "LATOKEN":
                    if cCoinTLG in self.getCoinList:
                        
                        getLastPrice = fExecAllLatokeN().getTicker(cCoinTLG)

                        if round((self.qtdtbuy / float(getLastPrice[0])),2) > 0:
                            if getLastPrice is not None:
                                respBuyTlg = fExecAllLatokeN().fBuyOnTLGLA(round((self.qtdtbuy / float(getLastPrice[0])),2), cCoinTLG, self.npercents, self.nqtysellorders,cCoinTLG )

                                if respBuyTlg['status'] != "FAILURE":
                                    print(respBuyTlg)
                                    print("-----------------------------------------------------------------------------------------------")
                                    getPricePay = fExecAllLatokeN().getorderByID(respBuyTlg['id'],0)
                                    print(f"Preco da compra: {getPricePay[1]}. Vamos utiliza-lo para a venda com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.
                                    lSell = True
                                else:
                                    print(f"Falha na operação de compra: {respBuyTlg}")
                        
                        
                        else:
                            print("-----------------------------------------------------------------------------------------------")
                            print(f"Só é possivel comprar acima de 0.01 da moeda! resultado {round((self.qtdtbuy / float(getLastPrice)),18)}")
                    else:
                        print("MOEDA não encontrada! *TLG")
                        print("-----------------------------------------------------------------------------------------------")
                elif self.exchange == "KUCOIN":
                    cCoinTLG+=kupair
                    if cCoinTLG in self.getCoinList:
                        
                        #pega a base minima para compra da moeda, caso o valor informado seja menor, sera realizado uma compra minima
                        baseMintoBuy = fExecAllKuCoin().get_kucoin_symbols('' , 3, '', cCoinTLG)
                        
                        #getticker pega o ultimo preco para usar na divisao e realizar a comprar pela qtde de moeda 
                        getLastPrice = fExecAllKuCoin().get_kucoin_ticker(cCoinTLG)

                        #transforma o valor informado em qtde em moedas e seus decimais
                        baseBuyCoin = fExecAllKuCoin().qtdBase(baseMintoBuy[0], float(self.qtdtbuy), float(getLastPrice))
                        
                        cFinalQtdToBuy = baseBuyCoin if float(baseMintoBuy[0]) < baseBuyCoin else float(baseMintoBuy[0])

                        if cFinalQtdToBuy is not None:
                            respBuyTlg = fExecAllKuCoin().fBuyOnTLGLA(str(cFinalQtdToBuy),cCoinTLG,self.npercents,1)

                            if respBuyTlg['code'] == "200000":
                                print(respBuyTlg)
                                print("-----------------------------------------------------------------------------------------------")
                                getPricePay = fExecAllKuCoin().getorderByID(respBuyTlg['data']['orderId'],0)
                                print(f"Preco da compra: {fExecAllKuCoin().priceBase(baseMintoBuy[1],getPricePay[1])}. Vamos utiliza-lo para a venda com o acrescimo do percentual.") #PEGO O PRECO DA COMPRA PARA USAR NAS VENDAS.
                                lSell = True
                            else:
                                print(f"Falha na operação de compra: {respBuyTlg}")
                elif self.exchange == "DIGIFINEX":


                    if cCoinTLG in self.getCoinList:
                        cCoinTLG += digiPair
                        cCoinTLG = cCoinTLG.lower()
                        respBuyTlg = fExecAllDigiFinex().fBuyOnTLG(self.qtdtbuy, cCoinTLG, self.npercents)

                        if respBuyTlg['code'] == 0:
                            print(respBuyTlg)
                            print("-----------------------------------------------------------------------------------------------")
                            getPricePay = fExecAllDigiFinex().getorderByID(respBuyTlg['order_id'],1)
                            print(f"Preco da compra: {getPricePay[0]}. Vamos utiliza-lo para a venda com o acrescimo do percentual.")
                            lSell = True
                        else:
                            print(f"Falha na operação de compra: {respBuyTlg}")
                                            
                    else:
                        print("MOEDA não encontrada! *TLG")
                        print("-----------------------------------------------------------------------------------------------")

                
                self.client.disconnect()

                if self.exchange == "MEXC":
                    if lSell:
                        fExecAllMexc().fSellFracOrders(float(respBuyTlg['price']), coinFullName, self.npercents, '2')
                        print("-----------------------------------------------------------------------------------------------")
                elif self.exchange == "LATOKEN":
                    if lSell:
                        fExecAllLatokeN().fSellFracOrders(float(getPricePay[0]),float(getPricePay[1]),cCoinTLG,self.npercents, self.nqtysellorders, cCoinTLG)
                        print("-----------------------------------------------------------------------------------------------")
                elif self.exchange == "KUCOIN":
                    if lSell:
                        fExecAllKuCoin().fSellFracOrders(float(getPricePay[0]),float(getPricePay[1]),cCoinTLG,self.npercents, self.nqtysellorders, baseMintoBuy[0], baseMintoBuy[1])
                        print("-----------------------------------------------------------------------------------------------")
                elif self.exchange == "DIGIFINEX":
                    if lSell:
                        fExecAllDigiFinex().fSellFracOrders(float(getPricePay[0]),float(getPricePay[1]),cCoinTLG,self.npercents, self.nqtysellorders)
                        print("-----------------------------------------------------------------------------------------------")
            else:
                print(f'MSG RECEBIDA EM: {message_date} | MSG LIDA EM: {datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} | MENSAGEM IGNORADA: {event.raw_text}')

        self.client.start()
        print(f'Sessao do Telegram: {self.tg_channel}. Conectado ao canal/grupo {self.tg_channel}.')
        self.client.run_until_disconnected()

