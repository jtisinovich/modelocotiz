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
import json
import threading
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, CategoricalColorMapper
import geopandas as gpd
from bokeh.plotting import figure
from bokeh.io import output_notebook, show, output_file
from bokeh.resources import CDN
from bokeh.embed import json_item, file_html, components
from bokeh.models import Range1d

app = Flask(__name__)

def mundo():
    
    shapefile = 'static/ne_110m_admin_0_countries.shp'
    #datafile = 'tickers_indices.csv'
    
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country', 'country_code', 'geometry']
    gdf = gdf.drop(gdf.index[159])
    
    #Perform left merge to preserve every row in gdf.
    merged = gdf.merge(df_2016, left_on = 'country_code', right_on = 'Code', how = 'left')
    merged.drop("Code", axis=1, inplace=True)
    merged.drop("entity",axis=1,  inplace=True)
    tabla = pd.DataFrame()
    tabla["Pais"] = merged.country
    tabla["Ticker"] = merged.ticker
    tabla["Cotizacion"] = merged.Cotizacion
    tabla["Variacion"] = merged.porcentaje

    merged.colores = merged.colores.fillna("gris")

    #Read data to json
    merged_json = json.loads(merged.to_json())

    #Convert to str like object
    json_data = json.dumps(merged_json)


    #Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson = json_data)

    
    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = CategoricalColorMapper(palette=["red", "green", "white"], factors=["rojo", "verde", "gris"])


    #Create figure object.
    p = figure(title = ' ', plot_height = 400 , plot_width = 1000, toolbar_location = None, 
               sizing_mode='scale_width', x_range=(-200, 200))
    p.x_range = Range1d(-200, 200)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    #Add patch renderer to figure. 
    p.patches('xs','ys', source = geosource,fill_color = {'field' :'colores', 'transform' : color_mapper},
              line_color = 'black', line_width = 0.25, fill_alpha = 1)

    output_notebook()

    #Display figure.
    return tabla, merged, p

def candlestick_plot(df):
    #df.reset_index(inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])

    fig = figure(sizing_mode='scale_width', plot_height = 350 , plot_width = 1000, 
                 toolbar_location = None,
                 
                 x_axis_type='datetime')

    inc = df.Close > df.Open
    dec = ~inc

    fig.segment(df.Date[inc], df.High[inc], df.Date[inc], df.Low[inc], color="green")
    fig.segment(df.Date[dec], df.High[dec], df.Date[dec], df.Low[dec], color="red")
    width_ms = 12*60*60*1000 # half day in ms
    fig.vbar(df.Date[inc], width_ms, df.Open[inc], df.Close[inc], color="green")
    fig.vbar(df.Date[dec], width_ms, df.Open[dec], df.Close[dec], color="red")
    return fig



def consultaMercadospy(i):
    
    
        
        nombre= df_2016.loc[i, "Nombre"]
        pais = df_2016.loc[i,"entity"]
        hoy = date.today()
        finstr = hoy.strftime("%d/%m/%Y")
        finstr2 = hoy.strftime("%Y-%m-%d")
        inicio = hoy - datetime.timedelta(days=5)
        iniciostr = inicio.strftime("%d/%m/%Y")
        iniciostr2 = inicio.strftime("%Y-%m-%d")
        
        cotiz = inv.get_index_historical_data(nombre, pais, from_date = iniciostr,
                                       to_date = finstr)
    
            
        
        variacion = cotiz.Close[-1] - cotiz.Open[-1]
        df_2016.loc[i,"Cotizacion"] = cotiz.Close[-1]
        if variacion >= 0:
                df_2016.loc[i,"colores"] = "verde"
                df_2016.loc[i,"porcentaje"] = ((cotiz.Close[-1] / cotiz.Open[-1] *100)-100).round(2)
        else:
                df_2016.loc[i,"colores"] = "rojo"
                df_2016.loc[i,"porcentaje"] = ((cotiz.Close[-1] / cotiz.Open[-1] *100)-100).round(2)
 
        
        return         




@app.route('/')
def index1():
    ticker_indices = ["^MERV" , "^AXJO", "^BFX", "^BVSP", "^GSPTSE", "^IPSA",
                      "^HSI", "^FCHI", "^GDAXI", "^BSESN", "^JKSE", "FTSEMIB.MI",
                      "^N225", "^KLSE", "^MXX", "^AEX", "^NZ50", "^OBX", "IMOEX.ME",
                      "^KS11", "^IBEX", "^OMX", "^SSMI", "^FTSE", "^GSPC"]

    try:
        for i in range(0,len(df_2016)):
            t = threading.Thread(target=consultaMercadospy, args=(i,))
            threads.append(t)
            t.start()
    
        for t in threads:
            t.join()

    except:
        hoy = date.today()
        finstr = hoy.strftime("%d/%m/%Y")
        finstr2 = hoy.strftime("%Y-%m-%d")
        inicio = hoy - datetime.timedelta(days=5)
        iniciostr = inicio.strftime("%d/%m/%Y")
        iniciostr2 = inicio.strftime("%Y-%m-%d")
        dft=yf.download(ticker_indices, start=iniciostr2, end=finstr2)
        porcentaje = ((dft.Close[ticker_indices] / dft.Open[ticker_indices] *100)-100).round(2)
        ultimos_porcentaje= porcentaje[ticker_indices][-1:]
        ultimos_porcentaje.reset_index(inplace=True)
        a = ultimos_porcentaje.loc[0,ticker_indices]
        lista_porcentajes = a.to_list()
        df_2016["porcentaje"] = lista_porcentajes
        variacion = dft.Close[ticker_indices] - dft.Open[ticker_indices]
        ultimos_variacion= variacion[ticker_indices][-1:]
        ultimos_variacion.reset_index(inplace=True)
        a = ultimos_variacion.loc[0,ticker_indices]
        lista_variacion= a.to_list()
        df_2016["Variacion"] = lista_variacion
        ultimo = dft.Close[ticker_indices]
        ultimos_cotiz= ultimo[ticker_indices][-1:]
        ultimos_cotiz.reset_index(inplace=True)
        a = ultimos_cotiz.loc[0,ticker_indices]
        lista_ultimos = a.to_list()
        df_2016["Cotizacion"] = lista_ultimos
        df_2016['colores'] = ['rojo' if x < 0 else 'verde' for x in df_2016['Variacion']]
        
    
    tabla, df, p = mundo()
    tabla = tabla.dropna()
    cols = tabla.columns
    script1, div1 = components(p)
    cdn_js=CDN.js_files[0]
    
    
    return render_template('index1.html',
                           script1=script1, div1=div1, cdn_js=cdn_js, data=tabla, 
                           cols = cols, passstatic_url_path='/static')
    




@app.route('/adrs')
def adrs():
    
    
    hoy = date.today()
    finstr = hoy.strftime("%d/%m/%Y")
    finstr2 = hoy.strftime("%Y-%m-%d")
    inicio = hoy - datetime.timedelta(days=300)
    iniciostr = inicio.strftime("%d/%m/%Y")
    iniciostr2 = inicio.strftime("%Y-%m-%d")
    
    df_adr = yf.download(lista, start=iniciostr2, end=finstr2).round(2)
    
    for ticker in lista:
        tabla.loc[ticker,"Simbolo"] = ticker
        tabla.loc[ticker,"Open"] = df_adr["Open"][ticker][-1].round(2)
        tabla.loc[ticker,"High"] = df_adr.High[ticker][-1].round(2)
        tabla.loc[ticker,"Low"] = df_adr.Low[ticker][-1].round(2)
        tabla.loc[ticker,"Close"] = df_adr.Close[ticker][-1].round(2)
    
    
    
    cols=tabla.columns
    #fig = candlestick_plot(tabla)
    #script1, div1 = components(fig)
    #cdn_js=CDN.js_files[0]
    
    return render_template('adrs.html', 
                            data=tabla, cols=cols, passstatic_url_path='/static')


@app.route('/datos/<ticker>')
def datos(ticker):
    hoy = date.today()
    finstr = hoy.strftime("%d/%m/%Y")
    finstr2 = hoy.strftime("%Y-%m-%d")
    inicio = hoy - datetime.timedelta(days=300)
    iniciostr = inicio.strftime("%d/%m/%Y")
    iniciostr2 = inicio.strftime("%Y-%m-%d")
    
    data= yf.download(ticker, start=iniciostr2, end=finstr2)
    data.reset_index(inplace=True)
    fig = candlestick_plot(data)
    script1, div2 = components(fig)
    cdn_js=CDN.js_files[0]
    data.sort_values("Date", ascending=False, inplace=True)
    data["Date"]=pd.to_datetime(data['Date']).apply(lambda x: x.date())
    cols=data.columns
    nombre=ticker
    data1=data.to_json()
    output_notebook()
    
    return render_template("datos.html", script1=script1, div2=div2, cdn_js=cdn_js,
                           data=data, data1=data1, nombre=nombre, cols=cols)


@app.route('/indice/<indice>')
def indice(indice):
    print(indice)
    ticker_ind = int(df_2016.Nombre2.loc[df_2016["entity"] == indice].index[0])
    ticker = df_2016.loc[ticker_ind,"Nombre2"]
    nombre = df_2016.loc[ticker_ind,"Nombre"]
    
    df = yf.download(ticker, start="2019-01-01").round(2)
    df.reset_index(inplace=True)
    fig = candlestick_plot(df)
    script1, div3 = components(fig)
    cdn_js=CDN.js_files[0]
    df.sort_values("Date", ascending=False, inplace=True)
    df["Date"]=pd.to_datetime(df['Date']).apply(lambda x: x.date())
    cols=df.columns
    nombre=ticker
    data1=df.to_json()
    output_notebook()
    
    return render_template("indice.html", script1=script1, div3=div3, cdn_js=cdn_js,
                           data=df, data1=data1, nombre=nombre, cols=cols)
    


tabla = pd.DataFrame()
tabla["Simbolo"] = 0
tabla["Open"] = 0
tabla["High"] = 0
tabla["Low"] = 0
tabla["Close"] = 0
lista = ["GGAL", "YPF", "BMA", "CRESY", "EDN", "IRS", "LOMA", "PAM",
             "SUPV", "TEO", "TGS", "TS"]
        
datafile = 'static/tickers_indices_investpy.csv'
df = pd.read_csv(datafile, names = ['entity', 'Code', 'ticker', "Nombre", "Nombre2"], skiprows = 1)

df_2016 = df[df['ticker'] != "vacio"]
df_2016 = df_2016.dropna()
threads = []
workers = 5
df_2016.reset_index(inplace=True)
df_2016.drop(["index"], axis=1, inplace=True)



if __name__ == '__main__':
    app.run()