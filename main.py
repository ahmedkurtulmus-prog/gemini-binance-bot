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
  print('Kaptan, Binance Vadeli piyasalar 15m taranıyor...')
  try:
    markets = exchange.load_markets()
    symbols = [s for s in markets if s.endswith('/USDT:USDT')]

    bulunan_coinler = 0

    for symbol in symbols:
      try:
        # Son 30 mumluk veriyi çekiyoruz
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=30)
        if len(ohlcv) < 30:
          continue

        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'],
        )

        # Son kapanmış mum ve önceki 20 mum
        son_mum = df.iloc[-2]
        gecmis_20_mum = df.iloc[-22:-2]

        # 1. Kural: Son 20 mumun ortalama hacminin 5 katı hacim
        ortalama_hacim = gecmis_20_mum['volume'].mean()
        hacim_sarti = son_mum['volume'] >= (ortalama_hacim * 5)

        # 2. Kural: Son LH (Düşen Tepe / en yüksek direnç) seviyesinin kırılması
        son_lh = gecmis_20_mum['high'].max()
        fiyat_sarti = son_mum['close'] > son_lh

        if hacim_sarti and fiyat_sarti:
          coin_adi = symbol.split('/')[0]
          bulunan_coinler += 1
          mesaj = (
              f"🚨 *PUSU VAKTİ / HACİM PATLAMASI!* 🚨\n\n"
              f"🪙 *Coin:* `{coin_adi}/USDT`\n"
              f"⏱ *Zaman Dilimi:* 15 Dakikalık (15m)\n"
              f"📊 *Durum:* Son 20 mum ortalamasının 5 katı hacim ve LH kırılımı!\n"
              f"💰 *Kapanış Fiyatı:* `{son_mum['close']}`\n\n"
              f"Kaptan, radarımıza takıldı, gözünü üstüne dik!"
          )
          telegram_mesaj_gonder(mesaj)

      except Exception:
        continue

    print(f'Tarama tamamlandı. Eşleşen coin sayısı: {bulunan_coinler}')

  except Exception as e:
    print(f"Genel tarama hatası: {e}")


if __name__ == '__main__':
  tarama_yap()
