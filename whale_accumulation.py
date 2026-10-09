import time
import requests
import json
import os
from datetime import datetime, timezone, timedelta

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = "8950898533:AAEU-FsEvHt5qUIAzXMwa-hCBWZMTGcDI_Y"
CHAT_ID = "-1003795173448"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def send_telegram_message(mesaj):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, headers=HEADERS)
  except Exception as e:
    print(f"Telegram mesaj hatası: {e}")


def scan_whale_accumulation():
  # Türkiye saati (UTC+3) tespiti
  tr_zaman = datetime.now(timezone(timedelta(hours=3)))
  
  event_name = os.getenv("GITHUB_EVENT_NAME", "manual")
  is_manual = event_name == "workflow_dispatch"

  print(f"Kaptan, Derin Balina Akümülasyon Taraması başladı (Saat: {tr_zaman.strftime('%H:%M')})...")

  try:
    # Binance Vision 24hr verileri
    ticker_url = "https://data-api.binance.vision/api/v3/ticker/24hr"
    resp = requests.get(ticker_url, headers=HEADERS, timeout=10)
    
    try:
      data = resp.json()
    except json.JSONDecodeError:
      print("Sunucu yanıtı JSON formatında değil.")
      return

    if not isinstance(data, list):
      return

    # Sadece USDT çiftleri ve hacme göre en büyük ilk 50 majör/aktif parite
    usdt_coinler = [item for item in data if item.get("symbol", "").endswith("USDT")]
    usdt_coinler.sort(key=lambda x: float(x.get("quoteVolume", 0)), reverse=True)
    hedef_liste = usdt_coinler[:50]

    found_accumulations = []

    for item in hedef_liste:
      symbol = item.get("symbol", "")
      coin_adi = symbol.replace("USDT", "")
      anlik_fiyat = float(item.get("lastPrice", 0))

      # 1 saatlik (1h) derin klines verisi ile balinaların yatay mal toplama (accumulation) bölgesi taranır
      klines_url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=1h&limit=50"
      try:
        k_resp = requests.get(klines_url, headers=HEADERS, timeout=3)
        if k_resp.status_code == 200:
          ohlcv = k_resp.json()
          if len(ohlcv) >= 40:
            closes = [float(x[4]) for x in ohlcv]
            highs = [float(x[2]) for x in ohlcv]
            lows = [float(x[3]) for x in ohlcv]
            volumes = [float(x[5]) for x in ohlcv]

            # Son 30 mumun ortalama hacmi ve fiyat bandı
            prev_volumes = volumes[:-1]
            vol_sma30 = sum(prev_volumes[-30:]) / 30

            current_volume = prev_volumes[-1]
            current_close = closes[-1]

            # Fiyat yatayda sıkışıyor mu? (Son 30 mumdaki tepe ve dip arasındaki mesafe dar mı?)
            recent_high = max(highs[-30:-1])
            recent_low = min(lows[-30:-1])
            fiyat_bandi_yuzde = ((recent_high - recent_low) / recent_low) * 100

            # Akümülasyon Kriteri: Fiyat dar bir bantta sıkışırken (yatay dip), hacim ortalamanın en az 3 katına çıkmışsa (sessiz mal toplama)
            is_tight_range = fiyat_bandi_yuzde <= 8.0  # Dar bant sıkışması (%8 altı)
            is_volume_accumulating = current_volume >= (vol_sma30 * 3.0) # Akıllı para hacim desteği

            if is_tight_range and is_volume_accumulating:
              hacim_carpani = current_volume / max(vol_sma30, 1)

              msg = (
                  f"🐋 *DERİN BALİNA AKÜMÜLASYON (MAL TOPLAMA) İZİ* 🐋\n\n"
                  f"🔥 Coin: `{coin_adi}USDT` (1h Periyot)\n"
                  f"Anlık Fiyat: `{anlik_fiyat}`\n"
                  f"Sıkışma Bandı: `%`{fiyat_bandi_yuzde:.1f} (Dip Yatay Bölge)\n"
                  f"Akümülasyon Hacmi: `{hacim_carpani:.1f}x` (Ortalama Üstü Mal Girişi)\n"
                  f"Durum: Fiyat patlamadan önce büyük oyuncular bu bölgede sessizce pozisyon topluyor!\n\n"
                  f"Kaptan, pusuya yatalım, tahta kuruluyor!"
              )
              found_accumulations.append(msg)
              time.sleep(0.1)
      except Exception:
        continue

    if found_accumulations:
      final_msg = "\n\n".join(found_accumulations)
      send_telegram_message(final_msg)
      print("Derin akümülasyon sinyalleri Telegram'a gönderildi.")
    else:
      print("Uygun akümülasyon (mal toplama) izi bulunamadı.")
      if is_manual:
        durum_mesaji = (
            f"🔍 *Derin Tarama Raporu ({tr_zaman.strftime('%H:%M')})*\n\n"
            "Majör paritelerin 1 saatlik dip bantları ve akümülasyon hacimleri tarandı. Şu an net bir balina mal toplama izi saptanmadı.\n"
            "Pusu devam ediyor Kaptan!"
        )
        send_telegram_message(durum_mesaji)
        print("Manuel test raporu iletildi.")

  except Exception as e:
    print(f"Derin tarama genel hatası: {e}")


if __name__ == "__main__":
  scan_whale_accumulation()
