import os
import requests
import json
from datetime import datetime, timezone, timedelta

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = "8950898533:AAEU-FsEvHt5qUIAzXMwa-hCBWZMTGcDI_Y"
CHAT_ID = "-1003795173448"

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram token veya chat ID eksik!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram yanıt kodu: {response.status_code}")
        if response.status_code == 200:
            print("Telegram mesajı başarıyla gönderildi.")
        else:
            print(f"Telegram hata detayı: {response.text}")
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")

def get_binance_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        symbols = [s['symbol'] for s in data.get('symbols', []) if s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING']
        return symbols
    except Exception as e:
        print(f"Semboller alınırken hata: {e}")
        return []

def analyze_quick_surges():
    symbols = get_binance_futures_symbols()
    found_surges = []
    
    tr_tz = timezone(timedelta(hours=3))
    tr_zaman = datetime.now(tr_tz)
    
    print(f"Toplam {len(symbols)} adet USDT.P paritesi 15 dakikalık hızlı patlama için taranıyor...")

    for symbol in symbols[:80]:
        try:
            klines_url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=15m&limit=20"
            res = requests.get(klines_url, timeout=5)
            if res.status_code != 200:
                continue
            candles = res.json()
            if not isinstance(candles, list) or len(candles) < 15:
                continue

            volumes = [float(c[5]) for c in candles]
            closes = [float(c[4]) for c in candles]
            
            avg_volume = sum(volumes[:-1]) / len(volumes[:-1]) if len(volumes[:-1]) > 0 else 1
            last_volume = volumes[-1]
            
            price_change = ((closes[-1] - closes[-2]) / closes[-2]) * 100
            
            if last_volume > (avg_volume * 3.5) and abs(price_change) < 1.5:
                msg = (
                    f"🚀 *HIZLI FİŞEK AKÜMÜLASYON SİNYALİ* 🚀\n\n"
                    f"🪙 **Parite:** `{symbol}`\n"
                    f"⏱ **Zaman Dilimi:** 15 Dakikalık (1-2 Günlük Patlama Adayı)\n"
                    f"💰 **Anlık Fiyat:** `{closes[-1]}` USDT\n"
                    f"📊 **Hacim Patlaması:** Normalin `{(last_volume/avg_volume):.1f}` katı!\n"
                    f"🎯 **Durum:** Dipte yatayda mal toplandı, fişek kopmak üzere Kaptan!\n"
                    f"⏰ *Saat:* `{tr_zaman.strftime('%H:%M - %d.%m.%Y')}`"
                )
                found_surges.append(msg)
        except Exception as e:
            continue

    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

    if found_surges:
        final_msg = "\n\n-------------------\n\n".join(found_surges[:3])
        send_telegram_message(final_msg)
    else:
        print("Hızlı akümülasyon koşulunu sağlayan tahta bulunamadı.")
        if is_manual:
            durum_mesaji = (
                f"⚡ *Hızlı Fişek Tarama Raporu ({tr_zaman.strftime('%H:%M')})*\n\n"
                f"Toplam `{len(symbols)}` adet USDT.P paritesi tarandı. 15 dakikalık periyotta hacim patlaması arandı, pusu devrede bekliyor Kaptan!"
            )
            send_telegram_message(durum_mesaji)

if __name__ == "__main__":
    analyze_quick_surges()
