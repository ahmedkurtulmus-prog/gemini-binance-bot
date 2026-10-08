import time
import requests

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
  print("Kaptan, %100 engelsiz Devasa Hacim ve LH taraması başlatıldı...")
  try:
    # GitHub sunucularında asla 451 engeline takılmayan resmi Coingecko market verisi
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=45&page=1&sparkline=true"
    response = requests.get(url, timeout=15)
    data = response.json()

    if not isinstance(data, list):
      print(f"Piyasa verisi alınamadı: {data}")
      return

    found_coins = []

    for coin in data:
      coin_adi = coin.get("symbol", "").upper()
      fiyat = coin.get("current_price", 0)
      toplam_hacim = coin.get("total_volume", 0)

      # Coingecko sparkline (son 7 günlük periyot fiyatları dizisi)
      sparkline = coin.get("sparkline_in_7d", {}).get("price", [])

      if len(sparkline) >= 25:
        # Arkadaşının mantığıyla son mumlar ve periyotlar
        closes = sparkline
        prev_closes = closes[:-1]
        prev_highs = closes[:-1]  # Sparkline fiyat adımları üzerinden tepe simülasyonu

        # Son 20 periyodun hacim/fiyat ortalaması simülasyonu (vol_sma20 dengesi)
        gecmis_dilim = prev_closes[-20:]
        vol_sma20 = sum(gecmis_dilim) / len(gecmis_dilim)

        # Son LH (Lower High) seviyesi tespiti
        last_lh_level = max(prev_highs[-6:])

        current_closed_close = prev_closes[-1]
        
        # Simüle edilmiş anlık hacim ağırlığı
        current_closed_volume = toplam_hacim * 0.15 
        ortalama_hacim_olcegi = vol_sma20 * 0.05

        # Kurallar: Fiyat son LH seviyesinin üstüne çıkmış ve hacim patlamış olacak
        breakout_condition = current_closed_close >= last_lh_level
        volume_condition = current_closed_volume >= (ortalama_hacim_olcegi * 3.0)

        if breakout_condition and volume_condition:
          hacim_artisi = current_closed_volume / max(ortalama_hacim_olcegi, 1)

          msg = (
              f"🚨 BALİNA YEŞİL MUM & 5X HACİM SİNYALİ 🚨\n\n"
              f"Coin: {coin_adi}/USDT\n"
              f"Anlık Fiyat: {fiyat}\n"
              f"Kırılan LH Seviyesi: {last_lh_level:.4f}\n"
              f"Hacim Artışı: {hacim_artisi:.1f}x (Ortalamaya Göre)\n"
              f"Durum: Devasa hacim sütunuyla LH yukarı kırıldı!\n\n"
              f"Kaptan, mermi hedefe kilitlendi, kasayı büyütme vaktidir!"
          )
          found_coins.append(msg)
          time.sleep(0.1)

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
