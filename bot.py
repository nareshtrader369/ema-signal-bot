import os
import time
import pandas as pd
import yfinance as yf
import requests

# Telegram credentials (set in Railway/Render as Environment Variables)
BOT_TOKEN = os.getenv("8345912007:AAHlblKgKfj5gXgHNCbf2qt9EFMFUVIpxh8")
CHAT_ID = os.getenv("795977824")

ASSETS = {
    "Gold": "GC=F",
    "Oil": "CL=F",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
}

TIMEFRAMES = ["5m", "15m"]
last_signal = {}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Error sending message:", e)

def check(asset, ticker, interval):
    df = yf.download(ticker, period="2d", interval=interval, progress=False)
    df["EMA9"] = df["Close"].ewm(span=9).mean()
    df["EMA30"] = df["Close"].ewm(span=30).mean()

    prev, curr = df.iloc[-2], df.iloc[-1]
    key = (asset, interval)

    if prev.EMA9 <= prev.EMA30 and curr.EMA9 > curr.EMA30:
        if last_signal.get(key) != "bull":
            msg = f"📈 BUY signal\n{asset} ({interval}) at {curr.Close:.2f}"
            send_message(msg)
            last_signal[key] = "bull"

    elif prev.EMA9 >= prev.EMA30 and curr.EMA9 < curr.EMA30:
        if last_signal.get(key) != "bear":
            msg = f"📉 SELL signal\n{asset} ({interval}) at {curr.Close:.2f}"
            send_message(msg)
            last_signal[key] = "bear"

def main():
    while True:
        for asset, ticker in ASSETS.items():
            for tf in TIMEFRAMES:
                try:
                    check(asset, ticker, tf)
                except Exception as e:
                    print("Error checking:", asset, tf, e)
        time.sleep(60)  # run every 1 min

if __name__ == "__main__":
    main()
