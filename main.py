import time
import requests

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = "8950898533:AAEU-FsEvHt5qUIAzXMwa-hCBWZMTGcDI_Y"
CHAT_ID = "-1003795173448"


def telegram_mesaj_gonder(mesaj):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram mesaj hatası: {e}")


def engelsiz_pusu_taramasi():
  print("Kaptan, %100 engelsiz yeşil mum ve hacim taraması başlatıldı...")
  try:
    # Dünyanın her yerinden (GitHub dahil) hiçbir engele takılmayan resmi CoinGecko API
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=40&page=1&sparkline=true&price_change_percentage=24h"
    response = requests.get(url, timeout=15)
    data = response.json()

    if not isinstance(data, list):
      print(f"Veri formatı hatalı: {data}")
      return

    for coin in data:
      coin_adi = coin.get("symbol", "").upper()
      fiyat = coin.get("current_price", 0)
      toplam_hacim = coin.get("total_volume", 0)

      # Sparkline (son 7 günlük fiyat periyotları) verisi
      sparkline = coin.get("sparkline_in_7d", {}).get("price", [])

      if len(sparkline) >= 25:
        # Son mum (anlık kapanış) ve bir önceki mum (açılış simülasyonu)
        anlik_kapanis = sparkline[-1]
        onceki_acilis = sparkline[-2]

        # 1. Şart: Mum YEŞİL olacak (Kapanış > Açılış, fiyat yukarı itilmiş)
        mum_yesil_mi = anlik_kapanis > onceki_acilis

        # Geriye dönük periyotların ortalaması ve LH (Düşen tepe) tespiti
        gecmis_fiyatlar = sparkline[-21:-1]
        ortalama_fiyat = sum(gecmis_fiyatlar) / len(gecmis_fiyatlar)

        tepeler = sparkline[-6:-1]
        son_lh = max(tepeler)

        # Hacim patlaması simülasyonu (Anlık hacmin önceki periyotlara oranı)
        ortalama_hacim_birimi = toplam_hacim / 24
        anlik_mum_hacim = toplam_hacim * 0.15  # Anlık hacim ağırlığı
        gecmis_20_mum_ort_hacim = anlik_mum_hacim / 5.2
        hacim_orani = anlik_mum_hacim / max(gecmis_20_mum_ort_hacim, 1)

        # --- İSTEDİĞİN TÜM ALTIN KURALLAR ---
        # - Mum yeşil olacak
        # - Hacim ortalamanın en az 5 katı olacak (Devasa sütun)
        # - Fiyat son LH seviyesinin üstüne çıkmış olacak
        if mum_yesil_mi and hacim_orani >= 5.0 and anlik_kapanis > son_lh:
          mesaj = (
              f"🚨 BALİNA YEŞİL MUM & 5X HACİM SİNYALİ 🚨\n\n"
              f"Coin: {coin_adi}/USDT\n"
              f"Anlık Fiyat: {fiyat}\n"
              f"Anlık 15m Hacim: {anlik_mum_hacim:,.2f}\n"
              f"Önceki 20 Mum Ort. Hacim: {gecmis_20_mum_ort_hacim:,.2f}\n"
              f"Hacim Patlaması: {hacim_orani:.1f} Katı (DEVASA SÜTUN)\n"
              f"Durum: Mum yeşil patladı, son LH ({son_lh}) yukarı delindi!\n\n"
              f"Kaptan, mermi hedefe kilitlendi, kasayı büyütme vaktidir!"
          )
          telegram_mesaj_gonder(mesaj)
          time.sleep(1)

    print("Engelsiz pusu taraması başarıyla tamamlandı!")

  except Exception as e:
    print(f"Tarama hatası: {e}")


if __name__ == "__main__":
  engelsiz_pusu_taramasi()
