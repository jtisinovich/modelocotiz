# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 07:08:30 2021

@author: jtisi
"""
from flask import Flask
from flask import render_template
import yfinance as yf
import pandas as pd
import investpy as inv
from datetime import date
import datetime
import plotly.graph_objects as go
import json
import plotly
import threading
import time

app = Flask(__name__)


@app.route('/')
def index1():
    
    for ticker in lista:
        tabla.loc[ticker,"Simbolo"] = ticker
        tabla.loc[ticker,"Open"] = df["Open"][ticker][-1].round(2)
        tabla.loc[ticker,"High"] = df.High[ticker][-1].round(2)
        tabla.loc[ticker,"Low"] = df.Low[ticker][-1].round(2)
        tabla.loc[ticker,"Close"] = df.Close[ticker][-1].round(2)
    
    
    data = tabla
    cols=data.columns
    
    
    return render_template('index1.html',
                            data=data, cols=cols, passstatic_url_path='/static')


@app.route('/datos/<ticker>')
def datos(ticker):
    data=pd.DataFrame()
    data["Open"] = df.Open[ticker]
    data["High"] = df.High[ticker]
    data["Low"] = df.Low[ticker]
    data["Close"] = df.Close[ticker]
    data.dropna(inplace=True)
    data.reset_index(inplace=True)
    fig = go.Figure(data=[go.Candlestick(
    x=data['Date'],
    open=data['Open'], high=data['High'],
    low=data['Low'], close=data['Close'],
    increasing_line_color= 'green', decreasing_line_color= 'red'
)])
    fig.update_layout(showlegend=False)
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=30))
    fig.update_layout(xaxis_rangeslider_visible=False)
    
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    data.sort_values("Date", ascending=False, inplace=True)
    data["Date"]=pd.to_datetime(data['Date']).apply(lambda x: x.date())
    cols=data.columns
    nombre=ticker
    data1=data.to_json()
    
    return render_template("datos.html", data=data, data1=data1, nombre=nombre, cols=cols, plot_json=plot_json)


        
tabla = pd.DataFrame()
tabla["Simbolo"] = 0
tabla["Open"] = 0
tabla["High"] = 0
tabla["Low"] = 0
tabla["Close"] = 0
lista = ["GGAL", "YPF", "BMA", "CRESY", "EDN", "IRS", "LOMA", "PAM",
             "SUPV", "TEO", "TGS", "TS"]

hoy = date.today()
finstr = hoy.strftime("%d/%m/%Y")
finstr2 = hoy.strftime("%Y-%m-%d")
inicio = hoy - datetime.timedelta(days=300)
iniciostr = inicio.strftime("%d/%m/%Y")
iniciostr2 = inicio.strftime("%Y-%m-%d")
    
df = yf.download(lista, start=iniciostr2, end=finstr2).round(2)

if __name__ == '__main__':
    app.run()