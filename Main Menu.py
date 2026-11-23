import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("sleepwise_data.json")

data = {}  

# ==================== PENYIMPANAN JSONN ====================

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

#MENU

#Edit catatan tidur

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


def menu_edit_riwayat():
    while True:
        nama, p = profil_aktif()
        print("\n===== EDIT RIWAYAT TIDUR =====")
        print(f"Profil aktif: {nama if nama else '(belum ada)'}")
        print("1. Tambah catatan")
        print("2. Ubah catatan")
        print("3. Hapus catatan")
        print("4. Kembali")
        pilihan = input("Pilih: ").strip()
        if pilihan == "1":
            tambah_tidur()
        elif pilihan == "2":
            ubah_catatan()
        elif pilihan == "3":
            hapus_catatan()
        elif pilihan == "4":
            return
        else:
            print("Pilihan tidak valid, pilih 1-4")


def pilih_catatan(p, aksi):
    if not p["riwayat"]:
        print("Belum ada catatan tidur untuk profil ini.")
        return None
    print(f"\nCatatan tidur ({data['aktif']}):")
    cetak_Riwayat(p["riwayat"])
    pilihan = input(f"Pilih nomor catatan yang akan {aksi}: ").strip()
    try:
        indeks = int(pilihan) - 1
        if not 0 <= indeks < len(p["riwayat"]):
            raise IndexError
    except (ValueError, IndexError):
        print("Pilihan tidak valid.")
        return None
    return indeks


def baca_jam(default_tidur, default_bangun):
    jam_tidur = input(f"Jam tidur (HH:MM) [{default_tidur}]: ").strip() or default_tidur
    jam_bangun = input(f"Jam bangun (HH:MM) [{default_bangun}]: ").strip() or default_bangun
    try:
        sleephour_minute(jam_tidur, jam_bangun)
    except ValueError:
        print("Jam harus berformat HH:MM (00:00-23:59).")
        return None
    return jam_tidur, jam_bangun


def ubah_catatan():
    nama, p = profil_aktif()
    if not p:
        print("Belum ada profil aktif. Tambahkan profil terlebih dahulu.")
        return
    indeks = pilih_catatan(p, "diubah")
    if indeks is None:
        return
    d = p["riwayat"][indeks]
    hari = input(f"Hari [{d['hari']}]: ").strip().capitalize() or d["hari"]
    jam = baca_jam(d["jam_tidur"], d["jam_bangun"])
    if jam is None:
        return
    p["riwayat"][indeks] = {"hari": hari, "jam_tidur": jam[0], "jam_bangun": jam[1]}
    save_data()
    print("Catatan berhasil diubah.")


def hapus_catatan():
    nama, p = profil_aktif()
    if not p:
        print("Belum ada profil aktif. Tambahkan profil terlebih dahulu.")
        return
    indeks = pilih_catatan(p, "dihapus")
    if indeks is None:
        return
    d = p["riwayat"][indeks]
    yakin = input(f"Hapus catatan {d['hari']} {d['jam_tidur']}-{d['jam_bangun']}? (y/n): ").strip().lower()
    if yakin == "y":
        p["riwayat"].pop(indeks)
        save_data()
        print("Catatan berhasil dihapus.")
    else:
        print("Penghapusan dibatalkan.")

#profil
def tambah_profil():
    nama = input("Masukkan nama profil baru:").strip()
    if not nama:
        print("Nama tidak boleh kosong.")
        return
    if nama in data["profil"]:
        print("Nama profil sudah ada.")
        return
    try:
        umur = int(input("Masukkan umur:").strip())
        if umur <= 0:
            raise ValueError
    except ValueError:
        print("Umur berupa angka positif.")
    data["profil"][nama] = {"umur": umur, "riwayat": []}
    if not data["aktif"]:
        data["aktif"] = nama
    save_data()
    print(f"Profil '{nama}' berhasil ditambahkan.")

def lihat_semua_profil():
    print("\n=== SELURUH PROFIL ===")
    if not data ["profil"]:
        return
    aktif = data["aktif"]
    for nomor, (nama, p) in enumerate(data["profil"].items(), start=1):
        tanda = " (AKTIF)" if nama == aktif else ""
        print(f"{nomor}. {nama} | {p['umur']} tahun | {len(p['riwayat'])} catatan{tanda}")

def ganti_profil():
    lihat_semua_profil()
    if not data["profil"]:
        return
    pilihan = input("Pilih nomor profil yang ingin diaktifkan:"). strip()
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
        umur = int(input(f"umur [{p['umur']}]: ").strip() or p["umur"])
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

def profil_Menu():
    while True:
        print("\n=== MENU PROFIL ===")
        print("1. Tambah profil baru")
        print("2. Lihat semua profil")
        print("3. Ganti profil aktif")
        print("4. Ubah nama dan umur profil")
        print("5. Kembali ke menu utama")  
        pilihan = input("Pilih menu yang diinginkan: ").strip()
        if pilihan == "1":
            tambah_profil()
        elif pilihan == "2":
            lihat_semua_profil()
        elif pilihan == "3":
            ganti_profil()
        elif pilihan == "4":
            ubah_profil()
        elif pilihan == "5":
            return
        else:
            print("Pilihan tidak valid. Pilih antara 1-5.")
    if __name__ == "__main__":
        load_data()
        save_data() 
        Menu()


def back(iniuser):
    print("\nKembali ke menu utama? (ketik 1 untuk kembali ke menu utama)")
    iniuser = input("Pilihan: ")
    if iniuser == "1":
        Menu()
    else:
        print("Pilihan tidak valid. Kembali ke menu utama.")
        Menu()

def target(umur):
    if umur < 6:
        return 10, 13
    elif umur <= 13:
        return 9, 11
    elif umur <= 17:
        return 8, 10
    elif umur <=64:
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

urutanhari = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]

def urut_hari(riwayat):
    terurut = []
    for i in urutanhari:
        for data in riwayat:
            if data["hari"].strip().lower() == i.lower():
                terurut.append(data)
    print("\n=== Riwayat Tidur Terurut ===")
    cetak_Riwayat(terurut)
    print("\nKembali ke menu utama? (ketik 1 untuk kembali ke menu utama)")
    iniuser = input("Pilihan: ")
    if iniuser == "1":
        Menu()
    else:
        print("Pilihan tidak valid. Kembali ke menu utama.")
        Menu()
    


def searchRiwayat_tidur(riwayat):
    searchday = input("Masukkan hari yang ingin dicari: ").lower()
    if searchday not in urutanhari:
        print("Hari tidak valid. Silakan masukkan hari yang benar.")
        Menu()
    hasil = [data for data in riwayat if data["hari"].strip().lower() == searchday]
    print(f"\n=== Hasil Pencarian Riwayat Tidur untuk '{searchday})===")
    if not hasil:
        print(f"Tidak ditemukan data riwayat tidur untuk hari {searchday}.")
        Menu()
    cetak_Riwayat(hasil)
    print("\nKembali ke menu utama? (ketik 1 untuk kembali ke menu utama)")
    iniuser = input("Pilihan: ")
    if iniuser == "1":
        Menu()
    else:
        print("Pilihan tidak valid. Kembali ke menu utama.")
        Menu()



def cetak_Riwayat(riwayat):
    for nomor, data in enumerate(riwayat, start=1):
            menit = sleephour_minute(data["jam_tidur"], data ["jam_bangun"])
            print(f"{nomor}. {data['hari']:<7} {data['jam_tidur']}-{data['jam_bangun']} {formatjam(menit)}")

def show_Riwayat(riwayat):
    print("\n=== Riwayat Tidur ===")
    if not riwayat:
        print("Belum ada data. Tambahkan data tidur terlebih dahulu.")
        return 
    for nomor, data in enumerate(riwayat, start=1):
        menit = sleephour_minute(data["jam_tidur"], data ["jam_bangun"])
        print(f"{nomor}. {data['hari']:<7} {data['jam_tidur']}-{data['jam_bangun']} {formatjam(menit)}")
    print("\n=== Menu Riwayat Tidur ===")
    print('1. Cari riwayat tidur berdasarkan hari')
    print('2. Urutkan riwayat tidur berdasarkan hari')
    print('3. Kembali ke menu utama')
    user2 = input("Pilih menu yang diinginkan: ").capitalize()
    if user2 == "1":
        searchRiwayat_tidur(riwayat)
    elif user2 == "2":
        urut_hari(riwayat)
    elif user2 == "3":
        Menu()

def analisis(rata_rata_menit, batas_min, batas_maks, kurang, jumlah_hari):
    min_menit = batas_min * 60
    maks_menit = batas_maks * 60
    ambang_kurang = max(1, jumlah_hari // 3)

    if min_menit <= rata_rata_menit <= maks_menit and kurang <= ambang_kurang:
        return "TIDUR SUDAH OPTIMAL"
    elif rata_rata_menit < min_menit:
        selisih = min_menit - rata_rata_menit
        return f"BELUM OPTIMAL, Rata - rata tidur masih kurang {formatjam(selisih)} dari yang dibutuhkan"
    elif rata_rata_menit > maks_menit:
        selisih = rata_rata_menit - maks_menit
        return f"BELUM OPTIMAL, Rata - rata tidur melebihi {formatjam(selisih)} dari yang dibutuhkan"
    else:
        return f"BELUM OPTIMAL, tercatat {kurang} dari {jumlah_hari} hari tidur di bawah batas yang dibutuhkan"
    
def show_analisis(profil,riwayat):
    print("\n=== ANALISIS ===")
    if not riwayat:
        print("Perlu ada minimal satu catatan tidur")
        return
    batas_min, batas_maks = target(profil["umur"])
    batas = batas_min * 60
    durasi = [sleephour_minute(data["jam_tidur"], data["jam_bangun"]) for data in riwayat]
    total = sum(durasi)
    rata_rata = total // len(durasi)
    kurang = sum(1 for menit in durasi if menit < batas)
    status = analisis(rata_rata, batas_min, batas_maks, kurang, len(durasi))

    print(f"Profil            : {profil['nama']} ({profil['umur']} tahun)")
    print(f"Rekomendasi tidur : {batas_min}-{batas_maks} jam per malam")
    print(f"Rata-rata tidur   : {formatjam(rata_rata)}")
    print(f"Hari kurang tidur : {kurang} dari {len(durasi)} hari")
    print(f"Status            : {status}")
    print("\nKembali ke menu utama? (ketik 1 untuk kembali ke menu utama)")
    iniuser = input("Pilihan: ")
    if iniuser == "1":
        Menu()
    else:
        print("Pilihan tidak valid. Kembali ke menu utama.")
        Menu()
def Menu():
    while True:
        print("\n===== SLEEPWISE CLI =====")
        print("1. Lihat Riwayat tidur")
        print("2. Edit Riwayat Tidur")
        print("3. Analisis Riwayat Tidur")
        print("4. Ubah Profil")
        print("5. keluar")
        inputuser = input("Pilih Menu yang Diinginkan: ").strip()

        if inputuser == "1":
         show_Riwayat(riwayat)
        elif inputuser == "2":
            menu_edit_riwayat()
        elif inputuser == "3":
            show_analisis(profil, riwayat)
        elif inputuser == "4":
            profil_Menu()
        elif inputuser == "5":
            print("test)")
        else:
            print("menu tidak tersedia pilih antara 1-5")

if __name__ == "__main__":
    load_data()
    save_data()  # migrasi format lama langsung tersimpan
    Menu()

