#sleepwise
#MENU

def Menu():
    print("\n===== SLEEPWISE CLI =====")
    print("1. Lihat Riwayat tidur")
    print("2. Edit Riwayat Tidur")
    print("3. Analisis Riwayat Tidur")
    print("4. Ubah Profil")
    print("5. keluar")
    inputuser = int(input("Pilih Menu yang Diinginkan: "))

    if inputuser == 1:
        #riwayattidur()
    elif inputuser == 2:
        #edittidur()
    elif inputuser == 3:
        #show_analisis(profil, riwayat)
    elif inputuser == 4:
        #profil()
    elif inputuser == 5:
        #stop()
    else:
        print("menu tidak tersedia pilih antara 1-5")
