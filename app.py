
import yliveticker
from collections import defaultdict, deque
from functools import partial
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title='CryptoYahoo: Entrega Dashboard 2', layout='wide')

st.write("# COMPARACIÓN DE BTH y ETH EN TIEMPO REAL")
st.write(f"### Datos tomados desde {str(datetime.datetime.now()).split('.')[0]}")

st.write("Este aplicación extrae la información de Yahoo Finance **en tiempo real** para el Bitcoin y el Ethereum en dólares y la presenta"
         " lado a lado para su comparación entre las monedas. Se eligen estás monedas al ser los cripto activos más conocidos")


st.write("Para esta comparación, tenemos a cada lado la fecha de actualización de la moneda, "
         "el valor actual de cada moneda en USD, el cambio de la moneda con respecto a su último valor en USD"
         ", y un gráfico del precio de la moneda en el tiempo.")

st.write("Esta aplicación fue desarrollada por Jorge Esteban Caballero R para la entrega 'Dashboard 2: Una herramienta propia con código' "
         "de la asignatura 'Visualización y storytelling' de MIAD" )

con = st.empty()

class DatosTiempoReal():
    def __init__(self) -> None:

        self.tickers = ["ETH-USD" ,"BTC-USD"]  # list of tickers to be read from socket
        self.data = defaultdict(partial(deque, maxlen=20))  # {TICKER : DEQUE}, each deque keeps 20 vals
        self.df=pd.DataFrame(columns= ['COIN', 'Tiempo', 'Precio (USD)'])

        self.open_socket()  # initializes the socket connection

    def open_socket(self, ) -> None:
        yliveticker.YLiveTicker(on_ticker=self.on_new_msg,
                                ticker_names=self.tickers)  # uses the yliveticker to create the websocket

    def on_new_msg(self, ws,
                   msg) -> None:  # every time new data comes in from the websocket, it is processed in this function

        print(str(msg['id']) + '\t' + str(msg['price']) + '\t' + str(msg['timestamp']))
        self.data_proc(str(msg['id']), float(msg['price']),
                       str(msg['timestamp']))  # with the data, send it to another function to store in our dictionary

        with con.container():
            eth, btc = st.columns(2)
            eth_data = self.df[self.df['COIN']=="ETH-USD"]
            btc_data = self.df[self.df['COIN']=="BTC-USD"]

            eth.write("# Datos ETH")
            eth.write(f"Última actualización en: {max(eth_data['Tiempo'])}")

            if len(eth_data)<=1:
                eth.metric(delta="O.00000 USD",
                           value=f"{str([eth_data['Precio (USD)'].iloc[-1]][0])[:8]} USD", label="VALOR ETH")
            else:
                eth.metric(delta=f"{str([-[eth_data['Precio (USD)'].iloc[-2] - eth_data['Precio (USD)'].iloc[-1]][0]][0])[:8]} USD",
                           value=f"{str([eth_data['Precio (USD)'].iloc[-1]][0])[:8]} USD", label="VALOR ETH")
            eth.write("## Valor de ETH en USD en el tiempo")
            eth.plotly_chart(px.line(eth_data, x='Tiempo', y='Precio (USD)'), use_container_width=True)

            #eth.write("Datos obtenidos: ")
            #eth.write(eth_data)
            btc.write("# Datos BTC")
            btc.write(f"Última actualización en: {max(btc_data['Tiempo'])}")

            if len(btc_data) <= 1:
                btc.metric(delta="O.00000 USD",
                           value=f"{str([btc_data['Precio (USD)'].iloc[-1]][0])[:9]} USD", label="VALOR BTC")
            else:
                btc.metric(delta=f"{str([-btc_data['Precio (USD)'].iloc[-2] + btc_data['Precio (USD)'].iloc[-1]][0])[:9]} USD",
                           value=f"{str([btc_data['Precio (USD)'].iloc[-1]][0])[:9]} USD", label="VALOR BTC")
            btc.write("## Valor de BTC en USD en el tiempo")

            btc.plotly_chart(px.line(btc_data, x='Tiempo', y='Precio (USD)'), use_container_width=True)

            #btc.write("Datos obtenidos: ")
            #btc.write(btc_data)

            st.write("Con el tiempo, veremos en estas gráfica la volatilidad de estos activos financieros, pero además"
                     " podremos conocer el precio actual de estas dos monedas.")

            st.write()


    def data_proc(self, ticker, price, timestamp) -> None:
        if not self.data[ticker] or self.data[ticker][-1][
            1] != timestamp:  # only store new data if it's from a new timestamp, prevents duplicate prices @ same time
            self.data[ticker].append([price, timestamp])
            df = pd.DataFrame(columns= ['COIN', 'Tiempo', 'Precio (USD)'], data=[[ticker, datetime.datetime.now(),price]])
            self.df = pd.concat([self.df, df])



DatosTiempoReal()
