import ccxt
import requests
import time

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = "8950898533:AAEU-FsEvHt5qUIAzXMwa-hCBWZMTGcDI_Y"
CHAT_ID = "-1003795173448"


def send_telegram_message(mesaj):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram mesaj hatası: {e}")


def scan_crypto():
  print("Kaptan, CCXT destekli 15m MSB ve Devasa Hacim taraması başladı...")
  try:
    # Binance Vadeli (USDT.P) bağlantısı (arkadaşının kullandığı engelsiz profesyonel yöntem)
    exchange = ccxt.binance({
        "options": {"defaultType": "future"},
        "enableRateLimit": True,
    })

    markets = exchange.load_markets()
    usdt_symbols = [s for s in markets if s.endswith("/USDT:USDT")]

    found_coins = []

    for symbol in usdt_symbols[:40]:  # En hacimli ilk 40 parite
      try:
        # 15 dakikalık mumları çekiyoruz
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe="15m", limit=30)
        if len(ohlcv) < 25:
          continue

        # Mum formatı: [timestamp, open, high, low, close, volume]
        # Kapanmış son mumları ve aktif mumları ayırıyoruz
        closes = [x[4] for x in ohlcv]
        highs = [x[2] for x in ohlcv]
        volumes = [x[5] for x in ohlcv]

        # Arkadaşının kodundaki mantık: Önceki kapanmış mumlar üzerinden hesaplama
        prev_closes = closes[:-1]
        prev_highs = highs[:-1]
        prev_volumes = volumes[:-1]

        # Son 20 mumun hacim ortalaması (vol_sma20)
        vol_sma20 = sum(prev_volumes[-20:]) / 20

        # Son LH (Lower High) seviyesi tespiti
        last_lh_level = max(prev_highs[-6:])

        current_closed_close = prev_closes[-1]
        current_closed_volume = prev_volumes[-1]
        coin_adi = symbol.split("/")[0]
        anlik_fiyat = closes[-1]

        # Kurallar:
        # 1. Kapanış mumu son LH seviyesinin üstüne çıkmış olacak
        # 2. Hacim, önceki 20 mumun ortalamasının en az 3 katı olacak (Devasa sütun)
        breakout_condition = current_closed_close >= last_lh_level
        volume_condition = current_closed_volume >= (vol_sma20 * 3.0)

        if breakout_condition and volume_condition:
          hacim_artisi = current_closed_volume / vol_sma20

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
          time.sleep(0.2)

      except Exception as e:
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
