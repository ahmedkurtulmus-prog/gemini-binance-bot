import time
import requests

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = "8950898533:AAEU-FsEvHt5qUIAzXMwa-hCBWZMTGcDI_Y"
CHAT_ID = "-1003795173448"  # Örn: -1001234567890


def telegram_mesaj_gonder(mesaj):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram mesaj hatası: {e}")


def borsa_verilerini_cek():
  print("Kaptan, Binance Vadeli 15m pusu taraması başlatıldı...")
  try:
    # Binance Vadeli halka açık 24s ticker ve sembol listesi
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    response = requests.get(url, timeout=15)
    data = response.json()

    if not isinstance(data, list):
      print(f"Veri formatı beklenmeyen tipte: {data}")
      return

    # USDT pariteli vadeli coinleri tarayalım
    for item in data:
      symbol = item.get("symbol", "")
      if not symbol.endswith("USDT"):
        continue

      coin_adi = symbol.replace("USDT", "")
      fiyat = float(item.get("lastPrice", 0))
      hacim_24s = float(item.get("quoteVolume", 0))  # USDT bazlı hacim

      # Her coin için son 15 dakikalık mumları ve LH/Hacim kontrolünü çekelim
      # Coğrafi engeli aşmak için doğrudan Binance fapi public klines uç noktası:
      klines_url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=15m&limit=25"
      k_resp = requests.get(klines_url, timeout=5)

      if k_resp.status_code == 200:
        k_data = k_resp.json()
        if len(k_data) >= 21:
          # Mum yapısı: [Open time, Open, High, Low, Close, Volume, ...]
          hacimler = [float(m[5]) for m in k_data[-21:-1]]  # Son 20 mumun hacmi
          ortalama_hacim = sum(hacimler) / len(hacimler)
          son_mum_hacmi = float(k_data[-1][5])  # İçinde olduğumuz son mumun hacmi

          # Son tepeler (LH kontrolü için son 5 mumun en yüksek noktası)
          yuksekler = [float(m[2]) for m in k_data[-6:-1]]
          son_lh = max(yuksekler)
          anlik_fiyat = float(k_data[-1][4])  # Son mumun kapanış/anlık fiyatı

          # --- DÜKKANIN PUSU ŞARTLARI ---
          # 1. Şart: Son mumun hacmi, son 20 mumun ortalama hacminin 1.5 katını (veya daha fazlasını) geçecek
          # 2. Şart: Anlık fiyat, son LH (düşen tepe) seviyesinin üzerine çıkmış olacak
          if (
              son_mum_hacmi > (ortalama_hacim * 1.5)
              and anlik_fiyat > son_lh
          ):
            mesaj = (
                f"🎯 *BALİNA PUSU SİNYALİ YAKALANDI* 🎯\n\n"
                f"🪙 *Coin:* `{coin_adi}/USDT`\n"
                f"💰 *Anlık Fiyat:* `{fiyat}`\n"
                f"📊 *Hacim Patlaması:* Son mum ortalamanın üstünde!\n"
                f"🚀 *Durum:* LH kırıldı, balinalar pusuya yattı!\n\n"
                f"Kaptan, kasayı büyütme ve pusuya geçme vaktidir!"
            )
            telegram_mesaj_gonder(mesaj)
            time.sleep(1)

    print("15m Pusu taraması başarıyla tamamlandı!")

  except Exception as e:
    print(f"Pusu tarama hatası: {e}")


if __name__ == "__main__":
  borsa_verilerini_cek()
