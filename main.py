import time
import ccxt
import pandas as pd
import requests

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = "8950898533:AAEU-FsEvHt5qUIAzXMwa-hCBWZMTGcDI_Y"
CHAT_ID = "853083506"


def telegram_mesaj_gonder(mesaj):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram mesaj hatası: {e}")


# --- BİNANCE VADELİ BAĞLANTISI ---
exchange = ccxt.binance({
    'options': {'defaultType': 'future'},
    'enableRateLimit': True,
})


def tarama_yap():
  print('Kaptan, Binance Vadeli piyasalar taranıyor...')
  try:
    markets = exchange.load_markets()
    symbols = [s for s in markets if s.endswith('/USDT:USDT')]

    for symbol in symbols:
      try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=30)
        if len(ohlcv) < 30:
          continue

        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'],
        )

        son_mum = df.iloc[-2]
        gecmis_20_mum = df.iloc[-22:-2]

        ortalama_hacim = gecmis_20_mum['volume'].mean()
        hacim_sarti = son_mum['volume'] >= (ortalama_hacim * 5)

        son_lh = gecmis_20_mum['high'].max()
        fiyat_sarti = son_mum['close'] > son_lh

        if hacim_sarti and fiyat_sarti:
          coin_adi = symbol.split('/')[0]
          mesaj = (
              f"🚨 *PUSU VAKTİ / HACİM PATLAMASI!* 🚨\n\n"
              f"🪙 *Coin:* `{coin_adi}/USDT`\n"
              f"⏱ *Zaman Dilimi:* 15 Dakikalık (15m)\n"
              f"📊 *Durum:* Son 20 mum ortalamasının 5 katı hacim ve LH kırılımı gerçekleşti!\n"
              f"💰 *Kapanış Fiyatı:* `{son_mum['close']}`\n\n"
              f"Kaptan, radarımıza takıldı, gözünü üstüne dik!"
          )
          telegram_mesaj_gonder(mesaj)
          time.sleep(1)

      except Exception:
        continue

  except Exception as e:
    print(f"Genel tarama hatası: {e}")


if __name__ == '__main__':
  telegram_mesaj_gonder(
      "Kaptan, Binance Vadeli 15m Hacim ve LH Tarama Botu GitHub üzerinden"
      " aktif! Pusuya yatıldı."
  )

  while True:
    tarama_yap()
    print('Tarama tamamlandı, 15 dakika bekleniyor...')
    time.sleep(900)
