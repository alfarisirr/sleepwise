import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("sleepwise_data.json")

data = {}  # {"aktif": "nama", "profil": {nama: {"umur": x, "riwayat": [...]}}}


# ==================== PENYIMPANAN & MIGRASI ====================

def load_data():
    """Memuat data JSON. Format lama otomatis dimigrasikan."""
    global data
    if not DATA_FILE.exists():
        data = {"aktif": "", "profil": {}}
        return
    try:
        with DATA_FILE.open(encoding="utf-8") as file:
            isi = json.load(file)
    except (json.JSONDecodeError, OSError):
        data = {"aktif": "", "profil": {}}
        return

    if "riwayat" in isi and isinstance(isi.get("profil"), dict) and "nama" in isi["profil"]:
        # Format lama: {"profil": {"nama","umur"}, "riwayat": [...]}
        p = isi["profil"]
        nama = str(p.get("nama", "Profil Lama")).strip() or "Profil Lama"
        umur = p.get("umur", 0)
        try:
            umur = int(umur)
        except (TypeError, ValueError):
            umur = 0
        data = {
            "aktif": nama,
            "profil": {nama: {"umur": umur, "riwayat": isi.get("riwayat") or []}},
        }
        print(f"[Migrasi] Format JSON lama terdeteksi -> profil '{nama}' dibuat, "
              f"{len(data['profil'][nama]['riwayat'])} catatan dipindahkan.")
    elif isinstance(isi.get("profil"), dict):
        # Format baru: {"aktif": nama, "profil": {nama: {"umur","riwayat"}}}
        profil = {}
        for nama, p in isi["profil"].items():
            if isinstance(p, dict) and "riwayat" in p:
                profil[nama] = p
        data = {"aktif": isi.get("aktif", ""), "profil": profil}
    else:
        data = {"aktif": "", "profil": {}}


def save_data():
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def profil_aktif():
    nama = data["aktif"]
    if nama in data["profil"]:
        return nama, data["profil"][nama]
    if data["profil"]:
        nama = next(iter(data["profil"]))
        data["aktif"] = nama
        return nama, data["profil"][nama]
    return None, None


# ==================== MANAJEMEN PROFIL ====================

def tambah_profil():
    nama = input("Nama profil baru: ").strip()
    if not nama:
        print("Nama tidak boleh kosong.")
        return
    if nama in data["profil"]:
        print("Profil dengan nama itu sudah ada.")
        return
    try:
        umur = int(input("Umur: ").strip())
        if umur <= 0:
            raise ValueError
    except ValueError:
        print("Umur harus berupa angka positif.")
        return
    data["profil"][nama] = {"umur": umur, "riwayat": []}
    if not data["aktif"]:
        data["aktif"] = nama
    save_data()
    print(f"Profil '{nama}' berhasil ditambahkan.")


def lihat_semua_profil():
    print("\n=== SELURUH PROFIL ===")
    if not data["profil"]:
        print("Belum ada profil. Tambahkan lewat menu profil.")
        return
    aktif = data["aktif"]
    for nomor, (nama, p) in enumerate(data["profil"].items(), start=1):
        tanda = " (AKTIF)" if nama == aktif else ""
        print(f"{nomor}. {nama} | {p['umur']} tahun | {len(p['riwayat'])} catatan{tanda}")


def ganti_profil_aktif():
    lihat_semua_profil()
    if not data["profil"]:
        return
    pilihan = input("Pilih nomor profil yang ingin diaktifkan: ").strip()
    try:
        indeks = int(pilihan) - 1
        nama = list(data["profil"])[indeks]
    except (ValueError, IndexError):
        print("Pilihan tidak valid.")
        return
    data["aktif"] = nama
    save_data()
    print(f"Profil aktif sekarang: {nama}")


def ubah_profil():
    lihat_semua_profil()
    if not data["profil"]:
        return
    pilihan = input("Pilih nomor profil yang diubah: ").strip()
    try:
        indeks = int(pilihan) - 1
        nama_lama = list(data["profil"])[indeks]
    except (ValueError, IndexError):
        print("Pilihan tidak valid.")
        return
    p = data["profil"][nama_lama]
    nama = input(f"Nama [{nama_lama}]: ").strip() or nama_lama
    try:
        umur = int(input(f"Umur [{p['umur']}]: ").strip() or p["umur"])
        if umur <= 0:
            raise ValueError
    except ValueError:
        print("Umur harus berupa angka positif.")
        return
    if nama != nama_lama:
        if nama in data["profil"]:
            print("Nama profil sudah dipakai.")
            return
        data["profil"][nama] = data["profil"].pop(nama_lama)
        if data["aktif"] == nama_lama:
            data["aktif"] = nama
        p = data["profil"][nama]
    p["umur"] = umur
    save_data()
    print("Profil berhasil diperbarui.")


def target(umur):
    if umur < 6:
        return 10, 13
    elif umur <= 13:
        return 9, 11
    elif umur <= 17:
        return 8, 10
    elif umur <= 64:
        return 7, 9
    else:
        return 7, 8


def sleephour_minute(jam_tidur, jam_bangun):
    fmt = "%H:%M"
    mulai = datetime.strptime(jam_tidur, fmt)
    selesai = datetime.strptime(jam_bangun, fmt)
    menit_mulai = mulai.hour * 60 + mulai.minute
    menit_selesai = selesai.hour * 60 + selesai.minute
    if menit_selesai <= menit_mulai:
        menit_selesai += 24 * 60
    return menit_selesai - menit_mulai


def formatjam(total_menit):
    jam = total_menit // 60
    menit = total_menit % 60
    if menit == 0:
        return f"{jam} jam"
    return f"{jam} jam {menit} menit"


def cetak_riwayat(riwayat):
    for nomor, d in enumerate(riwayat, start=1):
        menit = sleephour_minute(d["jam_tidur"], d["jam_bangun"])
        print(f"{nomor}. {d['hari']:<7} {d['jam_tidur']}-{d['jam_bangun']} {formatjam(menit)}")


def show_Riwayat():
    nama, p = profil_aktif()
    print(f"\n=== Riwayat Tidur ({nama}) ===")
    if not p or not p["riwayat"]:
        print("Belum ada data. Tambahkan data tidur terlebih dahulu.")
        return
    cetak_riwayat(p["riwayat"])


def tambah_tidur():
    nama, p = profil_aktif()
    if not p:
        print("Belum ada profil aktif. Tambahkan profil terlebih dahulu.")
        return
    hari = input("Hari: ").strip().capitalize()
    jam_tidur = input("Jam tidur (HH:MM): ").strip()
    jam_bangun = input("Jam bangun (HH:MM): ").strip()
    try:
        sleephour_minute(jam_tidur, jam_bangun)
    except ValueError:
        print("Jam harus berformat HH:MM (00:00-23:59).")
        return
    p["riwayat"].append({"hari": hari, "jam_tidur": jam_tidur, "jam_bangun": jam_bangun})
    save_data()
    print("Catatan tidur berhasil ditambahkan.")


def show_analisis():
    nama, p = profil_aktif()
    print("\n=== ANALISIS ===")
    if not p:
        print("Belum ada profil aktif.")
        return
    riwayat = p["riwayat"]
    if not riwayat:
        print("Perlu ada minimal satu catatan tidur.")
        return
    batas_min, batas_maks = target(p["umur"])
    batas = batas_min * 60
    durasi = [sleephour_minute(d["jam_tidur"], d["jam_bangun"]) for d in riwayat]
    rata_rata = sum(durasi) // len(durasi)
    kurang = sum(1 for m in durasi if m < batas)
    ambang = max(1, len(durasi) // 3)

    if batas <= rata_rata <= batas_maks * 60 and kurang <= ambang:
        status = "TIDUR SUDAH OPTIMAL"
    elif rata_rata < batas:
        selisih = formatjam(batas - rata_rata)
        status = f"BELUM OPTIMAL, rata-rata tidur kurang {selisih} dari yang dibutuhkan"
    elif rata_rata > batas_maks * 60:
        selisih = formatjam(rata_rata - batas_maks * 60)
        status = f"BELUM OPTIMAL, rata-rata tidur melebihi {selisih} dari yang dibutuhkan"
    else:
        status = f"BELUM OPTIMAL, tercatat {kurang} dari {len(durasi)} hari tidur di bawah batas"

    print(f"Profil            : {nama} ({p['umur']} tahun)")
    print(f"Rekomendasi tidur : {batas_min}-{batas_maks} jam per malam")
    print(f"Rata-rata tidur   : {formatjam(rata_rata)}")
    print(f"Hari kurang tidur : {kurang} dari {len(durasi)} hari")
    print(f"Status            : {status}")


# ==================== MENU UTAMA ====================

def Menu():
    while True:
        nama, _ = profil_aktif()
        print("\n===== SLEEPWISE CLI =====")
        print(f"Profil aktif: {nama if nama else '(belum ada)'}")
        print("1. Lihat Riwayat Tidur")
        print("2. Tambah Riwayat Tidur")
        print("3. Analisis Riwayat Tidur")
        print("4. Menu Profil")
        print("5. Keluar")
        inputuser = input("Pilih Menu yang Diinginkan: ").strip()

        if inputuser == "1":
            show_Riwayat()
        elif inputuser == "2":
            tambah_tidur()
        elif inputuser == "3":
            show_analisis()
        elif inputuser == "4":
            menu_profil()
        elif inputuser == "5":
            print("Sampai ketemu. Semoga tidur lu lebih teratur.")
            break
        else:
            print("Menu tidak tersedia, pilih antara 1-5")


def menu_profil():
    while True:
        print("\n===== MENU PROFIL =====")
        print("1. Tambah profil baru")
        print("2. Lihat seluruh profil")
        print("3. Ganti profil aktif")
        print("4. Ubah nama dan umur profil")
        print("5. Kembali")
        pilihan = input("Pilih: ").strip()
        if pilihan == "1":
            tambah_profil()
        elif pilihan == "2":
            lihat_semua_profil()
        elif pilihan == "3":
            ganti_profil_aktif()
        elif pilihan == "4":
            ubah_profil()
        elif pilihan == "5":
            return
        else:
            print("Pilihan tidak valid, pilih 1-5")


if __name__ == "__main__":
    load_data()
    save_data()  # migrasi format lama langsung tersimpan
    Menu()
