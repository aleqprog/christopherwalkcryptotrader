# Christopher Walk - CryptoTrader

Este projeto é um bot de trading de criptomoedas simples que realiza operações de compra e venda via APIs de várias corretoras. O bot inclui funcionalidades para gravar dados em um banco de dados, gera relatório para análise, e integrar com o Telegram para captar sinais de grupos.    
___
## 📌 Funcionalidades
Compra e Venda Automatizada nas seguintes corretoras:

Binance: Spot e Futures   
Mexc: Spot  
Kucoin: Spot   
Latoken: Spot   
Digifinex: Spot    

Gravação de Dados: Armazena informações de transações de mercado em um banco de dados SQL Server.     
Integração com o Telegram: Recebe sinais de grupos do Telegram para auxiliar nas decisões de trading.   
Geração de relatório para análise dos resultados obtidos.   

### 📋 Pré-requisitos

Instalação do Banco de Dados SQL Server:

Certifique-se de ter o SQL Server instalado e configurado em seu ambiente.
Crie um banco de dados para o bot e configure as tabelas necessárias.   
```
Use os scripts da pasta "scriptsSQL"
```

Configuração do Ambiente:    
Crie um arquivo .env na raiz do projeto com suas credenciais.   
```
Use o arquivo envModel.txt como modelo para as variáveis necessárias.
```
Instalação das Dependências:

Utilize o arquivo requirements.txt para instalar as bibliotecas necessárias:
```
pip install -r requirements.txt
```

## Bibliotecas utilizadas      
numpy: Cálculos numéricos.    
pyodbc: Conexão e manipulação de banco de dados SQL Server.    
humanize: Formatação de tempo e números.    
binance-connector: Conexão com a API da Binance.    
telethon: Integração com o Telegram.    
reportlab: Geração de relatórios em PDF.    
python-dotenv: Gerenciamento de variáveis de ambiente.      

## RUN 🚀

```
python fAllParameters.py
```
![init_christo](https://github.com/user-attachments/assets/b82a52b9-1ca5-488f-9e3a-d7429de5b1f2)
