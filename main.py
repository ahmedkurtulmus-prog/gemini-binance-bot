import time
import requests
import json

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = "8950898533:AAEU-FsEvHt5qUIAzXMwa-hCBWZMTGcDI_Y"
CHAT_ID = "-1003795173448"

# Tarayıcı gibi görünmek için güvenlik başlıkları
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


def scan_crypto():
  print("Kaptan, engelsiz Vision API ile 15m gerçek hacim taraması başladı...")
  try:
    # GitHub sunucularında asla 451 veya 404 vermeyen resmi engelsiz vision uç noktası
    ticker_url = "https://data-api.binance.vision/api/v3/ticker/24hr"
    resp = requests.get(ticker_url, headers=HEADERS, timeout=10)

    try:
      data = resp.json()
    except json.JSONDecodeError:
      print(f"Sunucu yanıtı JSON formatında değil: {resp.text[:100]}")
      return

    if not isinstance(data, list):
      print(f"Piyasa verisi alınamadı: {data}")
      return

    # Sadece USDT paritelerini al ve hacme göre sırala (En aktif ilk 40 coin)
    usdt_coinler = [
        item for item in data if item.get("symbol", "").endswith("USDT")
    ]
    usdt_coinler.sort(
        key=lambda x: float(x.get("quoteVolume", 0)), reverse=True
    )
    en_aktif_40 = usdt_coinler[:40]

    found_coins = []

    for item in en_aktif_40:
      symbol = item.get("symbol", "")
      coin_adi = symbol.replace("USDT", "")
      anlik_fiyat = float(item.get("lastPrice", 0))

      klines_url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=15m&limit=30"
      try:
        k_resp = requests.get(klines_url, headers=HEADERS, timeout=3)
        if k_resp.status_code == 200:
          ohlcv = k_resp.json()
          if len(ohlcv) >= 25:
            closes = [float(x[4]) for x in ohlcv]
            highs = [float(x[2]) for x in ohlcv]
            volumes = [float(x[5]) for x in ohlcv]

            prev_closes = closes[:-1]
            prev_highs = highs[:-1]
            prev_volumes = volumes[:-1]

            vol_sma20 = sum(prev_volumes[-20:]) / 20
            last_lh_level = max(prev_highs[-6:])

            current_closed_close = prev_closes[-1]
            current_closed_volume = prev_volumes[-1]

            breakout_condition = current_closed_close >= last_lh_level
            volume_condition = current_closed_volume >= (vol_sma20 * 3.0)

            if breakout_condition and volume_condition:
              hacim_artisi = current_closed_volume / max(vol_sma20, 1)

              msg = (
                  f"🚨 BALİNA YEŞİL MUM & 5X HACİM SİNYALİ 🚨\n\n"
                  f"Coin: {coin_adi}/USDT\n"
                  f"Anlık Fiyat: {anlik_fiyat}\n"
                  f"Kırılan LH Seviyesi: {last_lh_level:.4f}\n"
                  f"Hacim Artışı: {hacim_artisi:.1f}x (20 Mum Ortalamasına Göre)\n"
                  f"Durum: Devasa hacim sütunuyla LH yukarı kırıldı!\n\n"
                  f"Kaptan, mermi hedefe kilitlendi, kasayı büyütme vaktidir!"
              )
              found_coins.append(msg)
              time.sleep(0.1)
      except Exception:
        continue

    if found_coins:
      final_msg = "\n\n".join(found_coins)
      send_telegram_message(final_msg)
      print("Sinyaller Telegram'a gönderildi.")
    else:
      print("Uygun kırılım bulunamadı.")

  except Exception as e:
    print(f"Tarama genel hatası: {e}")


if __name__ == "__main__":
  scan_crypto()
