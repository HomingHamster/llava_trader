import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from numpy import mean
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import ta
import yfinance as yf
import requests
import base64

# OpenAI API Key
#TODO: DONT PUBLISH KEY
api_key = "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"

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def plot(name, df):
    df = ta.add_all_ta_features(df, open="Open", high="High", low="Low", close="Close",
                                   volume="Volume")

    # Individual Plot Elements:

    ## OHLC Candlestick Chart
    trace_candles = go.Candlestick(x=df.index,  # df.index stores dates (x-axis)
                                   open=df.Open,  # Open for OHLC candlesticks
                                   high=df.High,  # High for OHLC candlesticks
                                   low=df.Low,  # Low for OHLC candlesticks
                                   close=df.Close,  # Close for OHLC candlesticks
                                   name='Candlestick')  # Naming this to Candlestick for legend on the side of plot

    ## OHLC Bar Chart
    trace_bars = go.Ohlc(x=df.index,  # index stores dates (x-axis)
                         open=df.Open,  # Open for OHLC bars
                         high=df.High,  # High for OHLC bars
                         low=df.Low,  # Low for OHLC bars
                         close=df.Close,  # Close for OHLC bars
                         name='Bar Chart')  # Naming this to Bar Chart

    ## Daily Close Line
    trace_close = go.Scatter(x=list(df.index),  # index stores dates (x-axis)
                             y=list(df.Close),  # want only close values plotted
                             name='Close',  # Name this to Close
                             line=dict(color='#87CEFA',  # Define color for line
                                       width=2))  # Define width for line

    # Open and Close markers
    d = 1  # Marker will be placed d position points above or below daily open/close valu, respectively.
    df["marker"] = np.where(df["Open"] < df["Close"], df["High"] + d, df["Low"] - d)
    df["Symbol"] = np.where(df["Open"] < df["Close"], "triangle-up", "triangle-down")
    df["Color"] = np.where(df["Open"] < df["Close"], "green", "red")

    # Arrows corresponding to daily increasing/decreasing values
    trace_arrow = go.Scatter(x=list(df.index),
                             y=list(df.marker),
                             mode='markers',
                             name='Markers',
                             marker=go.scatter.Marker(size=8,
                                                      symbol=df["Symbol"],
                                                      color=df["Color"]))


    ## EMA
    trace_ema8 = go.Scatter(x=list(df.trend_ema_fast.index),
                            y=list(df.trend_ema_fast),
                            name='8 Day EMA',
                            line=dict(color='#E45756',  # Define color for line
                                      width=1,  # Define width for line
                                      dash='dot'))  # Define dash (I want my line to be dotted)

    trace_ema21 = go.Scatter(x=list(df.trend_ema_slow.index),
                             y=list(df.trend_ema_slow),
                             name='EMA',
                             line=dict(color='#4C78A8',  # Define color for line
                                       width=1,  # Define width for line
                                       dash='dot'))  # Define dash (I want my line to be dotted)

    ## SMA
    trace_sma = go.Scatter(x=list(df.trend_sma_fast.index),
                           y=list(df.trend_sma_fast),
                           name='Day SMA',
                           line=dict(color='#E45756',
                                     width=1,
                                     dash='dot'))

    ## Volume
    trace_volume = go.Bar(x=list(df.index),
                          y=list(df.Volume),
                          name='Volume',
                          marker=dict(color='gray'),
                          yaxis='y2',
                          legendgroup='two')

    ## MACD Histogram
    trace_macd_hist = go.Bar(x=list(df.trend_macd.index),
                             y=list(df.trend_macd_diff),
                             name='MACD Histogram',
                             marker=dict(color='gray'),
                             yaxis='y3',
                             legendgroup='three')

    ## MACD Line
    trace_macd = go.Scatter(x=list(df.trend_macd.index),
                            y=list(df.trend_macd),
                            name='MACD',
                            line=dict(color='black', width=1.5),  # red
                            yaxis='y3',
                            legendgroup='three')

    ## MACD Signal Line
    trace_macd_signal = go.Scatter(x=list(df.trend_macd.index),
                                   y=list(df.trend_macd_signal),
                                   name='Signal',
                                   line=dict(color='red', width=1.5),  # plum
                                   yaxis='y3',
                                   legendgroup='three')

    ## RSI
    trace_rsi = go.Scatter(x=list(df.momentum_rsi.index),
                           y=list(df.momentum_rsi),
                           mode='lines',
                           name='RSI',
                           line=dict(color='black',
                                     width=1.5),
                           yaxis='y4',
                           legendgroup='four')

    # RSI Overbought
    trace_rsi_70 = go.Scatter(mode='lines',
                              x=[min(df.momentum_rsi.index), max(df.momentum_rsi.index)],
                              y=[70, 70],
                              name='Overbought > 70%',
                              line=dict(color='green',
                                        width=0.5,
                                        dash='dot'),
                              yaxis='y4',
                              legendgroup='four')

    # RSI Oversold
    trace_rsi_30 = go.Scatter(mode='lines',
                              x=[min(df.momentum_rsi.index), max(df.momentum_rsi.index)],
                              y=[30, 30],
                              name='Oversold < 30%',
                              line=dict(color='red',
                                        width=0.5,
                                        dash='dot'),
                              yaxis='y4',
                              legendgroup='four')

    # RSI Center Line
    trace_rsi_50 = go.Scatter(mode='lines',
                              x=[min(df.momentum_rsi.index), max(df.momentum_rsi.index)],
                              y=[50, 50],
                              line=dict(color='gray',
                                        width=0.5,
                                        dash='dashdot'),
                              name='50%',
                              yaxis='y4',
                              legendgroup='four')

    ## Plotting Layout
    layout = go.Layout(xaxis=dict(titlefont=dict(color='rgb(200,115,115)'),  # Color of our X-axis Title
                                  tickfont=dict(color='rgb(100,100,100)'),  # Color of ticks on X-axis
                                  linewidth=1,  # Width of x-axis
                                  linecolor='black',  # Line color of x-axis
                                  gridwidth=1,  # gridwidth on x-axis marks
                                  gridcolor='rgb(204,204,204)',  # grid color

                                  #Define ranges to view data. I chose 3 months, 6 months, 1 year, and year to date
                                  # rangeselector=dict(
                                  #     buttons=(dict(count=3, label='3 mo', step='month', stepmode='backward'),
                                  #              dict(count=6, label='6 mo', step='month', stepmode='backward'),
                                  #              dict(count=1, label='1 yr', step='year', stepmode='backward'),
                                  #              dict(count=1, label='YTD', step='year', stepmode='todate'),
                                  #              dict(step='all')))
                                  ),

                       # Define different y-axes for each of our plots: daily, volume, MACD, and RSI -- hence 4 y-axes
                       yaxis=dict(domain=[0.40, 1.0], fixedrange=False,
                                  titlefont=dict(color='rgb(200,115,115)'),
                                  tickfont=dict(color='rgb(200,115,115)'),
                                  linecolor='black',
                                  mirror='all',
                                  gridwidth=1,
                                  gridcolor='rgb(204,204,204)'),
                       yaxis2=dict(domain=[0.26, 0.36], fixedrange=False, title='Volume',
                                   titlefont=dict(color='rgb(200,115,115)'),
                                   tickfont=dict(color='rgb(200,115,115)'),
                                   linecolor='black',
                                   mirror='all',
                                   gridwidth=1,
                                   gridcolor='rgb(204,204,204)'),
                       yaxis3=dict(domain=[0.13, 0.23], fixedrange=False, title='MACD',
                                   titlefont=dict(color='rgb(200,115,115)'),
                                   tickfont=dict(color='rgb(200,115,115)'),
                                   linecolor='black',
                                   constraintoward='center',  # might not be necessary
                                   mirror='all',
                                   gridwidth=1,
                                   gridcolor='rgb(204,204,204)'),
                       yaxis4=dict(domain=[0., 0.10], range=[10, 90], title='RSI',
                                   tick0=10, dtick=20,
                                   titlefont=dict(color='rgb(200,115,115)'),
                                   tickfont=dict(color='rgb(200,115,115)'),
                                   linecolor='black',
                                   mirror='all',
                                   gridwidth=1,
                                   gridcolor='rgb(204,204,204)'),
                       title=(name + ' Daily Data'),  # Give our plot a title
                       title_x=0.5,  # Center our title
                       paper_bgcolor='rgba(37,37,37)',  # Background color of main background
                       plot_bgcolor='rgb(226,238,245)',  # Background color of plot
                       height=2700, # overall height of plot
                       width=1500,
                       margin=dict(l=20, r=20, t=30, b=5)  # define margins: left, right, top, and bottom
                       )

    # All individual plots in data element
    plotting_data = [trace_close, trace_candles, trace_bars, trace_arrow, trace_ema8, trace_ema21, trace_sma,
                     trace_volume,
                     trace_macd_hist, trace_macd, trace_macd_signal, trace_rsi, trace_rsi_30, trace_rsi_50,
                     trace_rsi_70]

    # Plot
    fig = go.Figure(data=plotting_data, layout=layout)

    # Uncomment the following line to write your plot to full_figure.html, and auto open
    # fig.write_html('first_figure.html', auto_open=True)
    fig.write_image("plots/" + name + ".png")

    return "plots/" + name + ".png"


def ask(image_path):
    print("generating prediction")

    base64_image = encode_image(image_path)

    payload = {

        "model": "gpt-4o",
        "n": 7,
        "messages": [
            {"role": "system", "content": 'You are an expert financial analyst. You are part of an API. You will always'
                                          ' without fail return the necessary value and never anything else or any '
                                          'supporting information. You always do the best you can with the information'
                                          ' you have. You output a projected stock price and a confidence value '
                                          'separated by a space and nothing else. e.g. <price> <confidence>%'},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please give a one day projection and confidence rating for the "
                                             "stock price based on the attached information."},
                    {
                      "type": "image_url",
                      "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                      }
                    },
                ],
            }
        ],
        "max_tokens": 20
    }

    while True:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response = response.json()
        response = [x["message"]["content"] for x in response["choices"]]

        low_score = 0
        values = []
        scores = []

        for cont in response:
            if cont[-1] != "%":
                continue
            cont = cont[:-1]
            a = float(cont.split(" ")[0])
            b = int(cont.split(" ")[1])

            if b >= 55:
                values.append(a)
                scores.append(b)
            else:
                low_score += 1

        no_outlier_values = []
        no_outlier_scores = []

        needed_confidence = round(len(values)*0.7)

        if low_score > needed_confidence:
            return False

        for i in range(len(values)):
            good_test_values = []
            for j in range(len(values)):
                if i != j:
                    if values[j]*1.15 > values[i] > values[j]*0.85:
                        good_test_values.append(values[j])
            if len(good_test_values) > needed_confidence:
                no_outlier_values.append(values[i])
                no_outlier_scores.append(scores[i])

        if no_outlier_values and no_outlier_scores:
            out = float(round(mean(no_outlier_values), 2))
            out_score = int(round(mean(no_outlier_scores)))
            return out
        else:
            return False


if __name__ == "__main__":

    tech_list = ['NVDA']

    end = datetime.now()
    start = datetime(end.year - 1, end.month, end.day)

    stock = {}
    for ticker in tech_list:
        stock[ticker] = yf.download(ticker, start, end, interval='1d')
        print(stock[ticker].head())

    for ticker in tech_list:
        print(ask(plot(ticker, stock[ticker])))
