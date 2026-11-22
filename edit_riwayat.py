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
    cetak_riwayat(p["riwayat"])
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
