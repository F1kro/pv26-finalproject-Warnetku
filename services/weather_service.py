import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import requests
from config import WEATHER_CITY
from PySide6.QtCore import QThread, Signal

# Deskripsi cuaca WMO code -> teks Indonesia
_WMO_DESC = {
    0: 'Cerah', 1: 'Sebagian cerah', 2: 'Berawan sebagian', 3: 'Mendung',
    45: 'Berkabut', 48: 'Kabut es',
    51: 'Gerimis ringan', 53: 'Gerimis', 55: 'Gerimis lebat',
    61: 'Hujan ringan', 63: 'Hujan', 65: 'Hujan lebat',
    71: 'Salju ringan', 73: 'Salju', 75: 'Salju lebat',
    80: 'Hujan lokal ringan', 81: 'Hujan lokal', 82: 'Hujan lokal lebat',
    95: 'Badai petir', 96: 'Badai petir + hujan es', 99: 'Badai petir lebat',
}

class WeatherWorker(QThread):
    """Fetch cuaca via Open-Meteo (100% gratis, tanpa API key)."""
    hasil = Signal(dict)
    error = Signal(str)

    def run(self):
        try:
            # Step 1: geocoding via Open-Meteo
            geo_url = (
                f'https://geocoding-api.open-meteo.com/v1/search'
                f'?name={WEATHER_CITY}&count=1&language=id&format=json'
            )
            geo_r = requests.get(geo_url, timeout=8)
            geo_data = geo_r.json()
            results = geo_data.get('results')
            if not results:
                self.error.emit(f'Kota "{WEATHER_CITY}" tidak ditemukan.')
                return

            loc = results[0]
            lat = loc['latitude']
            lon = loc['longitude']
            kota = loc.get('name', WEATHER_CITY)
            negara = loc.get('country_code', '')

            # Step 2: cuaca terkini
            wx_url = (
                f'https://api.open-meteo.com/v1/forecast'
                f'?latitude={lat}&longitude={lon}'
                f'&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m'
                f'&timezone=auto'
            )
            wx_r = requests.get(wx_url, timeout=8)
            wx_data = wx_r.json()
            current = wx_data.get('current', {})

            suhu = current.get('temperature_2m', 0)
            kelembaban = current.get('relative_humidity_2m', 0)
            kode = current.get('weathercode', 0)
            deskripsi = _WMO_DESC.get(kode, f'Kode {kode}')

            self.hasil.emit({
                'kota': f'{kota}, {negara}',
                'suhu': suhu,
                'deskripsi': deskripsi,
                'kelembaban': kelembaban,
                'ikon': str(kode),
            })
        except requests.exceptions.ConnectionError:
            self.error.emit('Tidak ada koneksi internet.')
        except Exception as e:
            self.error.emit(str(e))
