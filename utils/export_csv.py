import csv
import os
from datetime import datetime


def export_transaksi(data: list, path: str) -> bool:
    """
    Export list transaksi ke CSV.
    data: list of dict dari transaksi_model.ambil_rentang()
    """
    try:
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            if not data:
                return True
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f'Export CSV error: {e}')
        return False


def nama_file_default(prefix='laporan'):
    tgl = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{tgl}.csv'
