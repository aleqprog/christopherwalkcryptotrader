# Christopher Walk - _CryptoTrader_

Este projeto é um _bot_ de _trading_ de criptomoedas simples que realiza operações de compra e venda via APIs de várias corretoras. O _bot_ inclui funcionalidades adicionais para gravar dados em um banco de dados, gera relatório para análise, integrar com o Telegram para captar sinais de grupos e envio de e-mail com os resultados obtidos do trade.   
___


#### 📢 Indicadores disponíveis: _EMA_, _RSI_ e _Stochastic RSI_
___


## 📌 Funcionalidades
Compra e Venda Automatizada nas seguintes corretoras:

_Binance: Spot and Futures_   
_Mexc: Spot_  
_Kucoin: Spot_   
_Latoken: Spot_   
_Digifinex: Spot_    

Gravação de Dados: Armazena informações de transações de mercado em um banco de dados SQL Server.     
Integração com o Telegram: Recebe sinais de grupos do Telegram para auxiliar nas decisões de _trading_.   
Geração de relatório para análise dos resultados obtidos.  
Envio de e-mail com dados do trade.    

###  :shipit: Modo simulação 
Neste modo, é possível simular uma entrada com base no preço atual, passando o percentual de ganho e perda. Isso permite prever potenciais lucros e riscos.
___
### 🔴 Aviso Importante sobre Segurança
___
Por favor, leia atentamente antes de configurar o projeto.

Este projeto utiliza um arquivo .env para armazenar informações sensíveis, como chaves de API e credenciais de acesso. É essencial que estas chaves e credenciais sejam mantidas em segredo e não sejam compartilhadas sob nenhuma circunstância.    
___
### 📋 Pré-requisitos

Crie uma conta de e-mail no Gmail e habilite a senha de app a ser utilizada no arquivo .env 

Instalação do Banco de Dados SQL Server:

Certifique-se de ter o SQL Server instalado e configurado em seu ambiente.
Crie um banco de dados para o _bot_ e configure as tabelas necessárias.   
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

## 📦 Bibliotecas utilizadas      
numpy: Cálculos numéricos.    
pyodbc: Conexão e manipulação de banco de dados SQL Server.    
humanize: Formatação de tempo e números.    
binance-connector: Conexão com a API da Binance.    
telethon: Integração com o Telegram.    
reportlab: Geração de relatórios em PDF.    
python-dotenv: Gerenciamento de variáveis de ambiente.      

## 🚀 RUN! 

```
python fAllParameters.py
```
### Parâmetros iniciais 
___

