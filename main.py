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


def pusu_taramasi_15m():
  print("Kaptan, 15m yeşil mum, 5x hacim ve LH kırılım taraması başlatıldı...")
  try:
    # Küresel ve engelsiz Binance public ticker uç noktası
    ticker_url = "https://api3.binance.com/api/v3/ticker/24hr"
    resp = requests.get(ticker_url, timeout=15)
    data = resp.json()

    if not isinstance(data, list):
      print(f"Piyasa verisi alınamadı: {data}")
      return

    for item in data:
      symbol = item.get("symbol", "")
      if not symbol.endswith("USDT"):
        continue

      coin_adi = symbol.replace("USDT", "")
      anlik_fiyat = float(item.get("lastPrice", 0))

      # Engelsiz global veri yansımasından 15m mumları (klines) çekiyoruz
      klines_url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=15m&limit=25"
      k_resp = requests.get(klines_url, timeout=5)

      if k_resp.status_code == 200:
        k_data = k_resp.json()
        if len(k_data) >= 21:
          # Mum yapısı: [Open time, Open, High, Low, Close, Volume, ...]
          # Index 1: Open (Açılış), Index 2: High (Tepe), Index 4: Close (Kapanış), Index 5: Volume (Hacim)

          # Son 20 mumun hacimleri (içinde olduğumuz son mum hariç önceki 20 mum)
          gecmis_hacimler = [float(m[5]) for m in k_data[-21:-1]]
          ortalama_hacim_20 = sum(gecmis_hacimler) / len(gecmis_hacimler)

          son_mum_hacmi = float(k_data[-1][5])  # İçinde olduğumuz son 15m mumun hacmi
          son_mum_acilis = float(k_data[-1][1])
          son_mum_kapanis = float(k_data[-1][4])

          # 1. Şart: Mum kesinlikle YEŞİL olacak (Kapanış > Açılış)
          mum_yesil_mi = son_mum_kapanis > son_mum_acilis

          # Son LH (Lower High) tespiti: Son 5 mumun en yüksek tepe noktası (son mum hariç)
          tepeler = [float(m[2]) for m in k_data[-6:-1]]
          son_lh = max(tepeler)

          # Hacim çarpanı hesaplama (Anlık hacmin önceki 20 mumun ortalamasına oranı)
          hacim_orani = son_mum_hacmi / max(ortalama_hacim_20, 1)

          # --- İSTEDİĞİN TÜM ALTIN KURALLAR ---
          # - Mum yeşil olacak
          # - Anlık hacim, önceki 20 mumun ortalamasının en az 5 katı olacak (Devasa sütun)
          # - Fiyat, son LH seviyesinin üzerine çıkmış olacak
          if (
              mum_yesil_mi
              and hacim_orani >= 5.0
              and son_mum_kapanis > son_lh
          ):

            mesaj = (
                f"🚨 BALİNA YEŞİL MUM & 5X HACİM SİNYALİ 🚨\n\n"
                f"Coin: {coin_adi}/USDT\n"
                f"Anlık Fiyat: {anlik_fiyat}\n"
                f"Anlık 15m Hacim: {son_mum_hacmi:,.2f}\n"
                f"Önceki 20 Mum Ort. Hacim: {ortalama_hacim_20:,.2f}\n"
                f"Hacim Patlaması: {hacim_orani:.1f} Katı (DEVASA SÜTUN)\n"
                f"Durum: Mum yeşil patladı, son LH ({son_lh}) yukarı delindi!\n\n"
                f"Kaptan, mermi hedefe kilitlendi, kasayı büyütme vaktidir!"
            )
            telegram_mesaj_gonder(mesaj)
            time.sleep(1.5)

    print("15m pusu taraması başarıyla tamamlandı!")

  except Exception as e:
    print(f"Tarama hatası: {e}")


if __name__ == "__main__":
  pusu_taramasi_15m()
