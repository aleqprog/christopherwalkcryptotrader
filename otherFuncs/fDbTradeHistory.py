from otherFuncs.genReportTrades import *
from dotenv import load_dotenv
from datetime import datetime
import pyodbc
import os

load_dotenv(".env")

conn_str = f'DRIVER={{SQL Server}};SERVER={os.getenv("SERVER")};DATABASE={os.getenv("DBNAME")};UID={os.getenv("USERDB")};PWD={os.getenv("PASSDB")};'


def insertDataInDB(coin_name, type, rsi_btc, rsi_coin, reversed, vol_usdt, dif_percent, order_role, gain_percent, loss_percent, bot_info, return_usdt, transaction_id):

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = '''
        INSERT INTO TradeHist (CoinName, Type, RsiBtc, RsiCoin, Reveserd, volUSDT, DifPercent, OrderRole, GainPercent, LossPercent, BotInfo, ReturnUsdt, Created, TransactionId) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
        '''

        cursor.execute(query, (coin_name, type, rsi_btc, rsi_coin, reversed, vol_usdt, dif_percent, order_role, gain_percent, loss_percent, bot_info, return_usdt, transaction_id))
        
        conn.commit()
        cursor.close()
        conn.close()

        print("Data inserted successfully.")
        print("-----------------------------------------------------------------------------------------------")
    except Exception as e:
        print(f"Error inserting data: {e}")


def updateRegHistory(gain_percent, loss_percent, return_usdt, transaction_id, rsiout, rsiBTCout):

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = '''
        UPDATE TradeHist
        SET GainPercent = ?, LossPercent = ?, ReturnUsdt = ?, RsiCoinOut = ?, rsiBTCout = ?, roleType2= ?, Ended = GETDATE()
        WHERE TransactionId = ?
        '''
        cursor.execute(query, (gain_percent, loss_percent, return_usdt, rsiout, rsiBTCout, os.getenv('ROLETYPE2'), transaction_id))

        conn.commit()

        if cursor.rowcount == 0:
            print("No record found to update.")
        else:
            print(f"Record with Id {transaction_id} updated successfully.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error updating data: {e}")


def queryTradeHistByDate(date_input):

    modified_date = date_input.replace("/", "")

    now = datetime.now()
    formatted_time = now.strftime("%Hh%M")

    date_object = datetime.strptime(date_input, '%d/%m/%Y')
    formatted_date_sql = date_object.strftime('%Y-%m-%d')

    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                sql_query = """
                SELECT 
                    REPLACE(RTRIM(CoinName),'USDT','') AS Coin, 
                    RTRIM(Type) AS Type,
                    CONCAT('BTC_', RsiBtc,' | ',RsiCoin) AS RSI, 
                   -- RsiCoin, 
                    CONCAT(RTRIM(Reveserd), ' | ', DATEDIFF(MINUTE, Created, Ended),'Min') AS EMAcross, 
                    RTRIM(volUSDT) AS volUSDT, 
                    CONCAT(DifPercent,'%',' | Role (' ,OrderRole,')') AS DiffPercent,
                    --OrderRole, 
                    GainPercent AS GainPercent, 
                    LossPercent AS LossPercent,
                    CONVERT(varchar(5), Created, 108) EntryTime
                FROM 
                    TradeHist
                WHERE 
                   FORMAT(Created, 'yyyy-MM-dd') = ?
                   AND DATEDIFF(MINUTE, Created, Ended) > 0
                   ORDER BY OrderRole
                """

                cursor.execute(sql_query, formatted_date_sql)

                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()

                create_pdf(results, columns, modified_date, date_input + "_" + formatted_time)

    except pyodbc.Error as e:
        print("Error connecting to the database or executing the query:", e)
