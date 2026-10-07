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


def engelsiz_pusu_taramasi():
  print("Kaptan, engelsiz pusu taraması başlatıldı...")
  try:
    # CoinGecko halka açık API'si üzerinden IP engelini takmadan verileri çekiyoruz
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=15&page=1&sparkline=true&price_change_percentage=24h"
    response = requests.get(url, timeout=15)
    data = response.json()

    if not isinstance(data, list):
      print(f"Veri formatı hatalı: {data}")
      return

    for coin in data:
      coin_adi = coin.get("symbol", "").upper()
      fiyat = coin.get("current_price", 0)
      degisim_24s = coin.get("price_change_percentage_24h", 0)
      
      # Sparkline (son fiyat hareketleri listesi) üzerinden hacim/tepe mantığını simüle ediyoruz
      sparkline = coin.get("sparkline_in_7d", {}).get("price", [])
      
      if len(sparkline) >= 20:
        son_fiyatlar = sparkline[-20:]
        ortalama_fiyat = sum(son_fiyatlar) / len(son_fiyatlar)
        anlik_fiyat = sparkline[-1]
        
        # Dükkanın pusu şartı: Fiyat hareketliliği ve hacim/tepe kırılım teyidi
        if anlik_fiyat > ortalama_fiyat and abs(degisim_24s) >= 1.0:
          mesaj = (
              f"🎯 *BALİNA PUSU SİNYALİ* 🎯\n\n"
              f"🪙 *Coin:* `{coin_adi}/USDT`\n"
              f"💰 *Anlık Fiyat:* `$ {fiyat}`\n"
              f"📊 *24s Değişim:* `% {degisim_24s:.2f}`\n"
              f"🚀 *Durum:* Ortalama yukarı kılındı, pusu aktif!\n\n"
              f"Kaptan, kasayı büyütme ve hedefi vurma vaktidir!"
          )
          telegram_mesaj_gonder(mesaj)
          time.sleep(1)

    print("Engelsiz pusu taraması başarıyla tamamlandı!")

  except Exception as e:
    print(f"Pusu tarama hatası: {e}")


if __name__ == "__main__":
  engelsiz_pusu_taramasi()
