from datetime import datetime
#profil sementara
profil = {
    "nama": "eha",
    "umur": 5
}
riwayat = [
    {"hari": "senin", "jam_tidur": "21:00", "jam_bangun": "05:00"},
    {"hari": "selasa", "jam_tidur": "22:00", "jam_bangun": "05:00"}
]

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
    print("\=== ANALISIS ===")
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
    print("Kembali? (ketik 1 untuk kembali ke menu utama)")
    kembali = input("Pilihan: ")
    # if kembali == "1":
    #     #Menu()
show_analisis(profil, riwayat)

