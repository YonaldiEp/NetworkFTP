import ftplib
import os

FTP_HOST = "127.0.0.1"
FTP_PORT = 2122

def clear():
    # Membersihkan layar terminal
    os.system("cls" if os.name == "nt" else "clear")

def garis():
    print("-" * 60)

def pause():
    input("\nTekan ENTER untuk lanjut...")

def cek_koneksi():
    garis()
    print("CEK KONEKSI FTP SERVER")
    garis()
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=5)
        print("[STATUS] Server FTP TERHUBUNG")
        ftp.close()
        return True
    except:
        print("[STATUS] Server FTP TIDAK TERHUBUNG")
        return False

def login_ftp():
    ftp = ftplib.FTP()
    try:
        ftp.connect(FTP_HOST, FTP_PORT)
        print("[LOGIN FTP]")
        user = input("Username: ")
        pwd = input("Password: ")
        ftp.login(user, pwd)
        print("[LOGIN BERHASIL]")
        print("Pesan Server:", ftp.getwelcome())
        return ftp
    except Exception as e:
        print(f"\n[LOGIN GAGAL] {e}")
        return None

def main():
    clear()
    
    # STEP 1: Cek Koneksi
    if not cek_koneksi():
        return
    pause()

    # STEP 2: Login
    clear()
    ftp = login_ftp()
    if not ftp:
        return
    
    home_dir = ftp.pwd() # Menyimpan direktori awal (root)

    while True:
        clear()
        print(f"Server saat ini: {ftp.pwd()}")
        garis()
        print("MENU FTP CLIENT")
        garis()
        print("1. Cek Direktori Saat Ini (PWD)")
        print("2. List File Server (DIR)")
        print("3. Pindah Direktori (CWD)")
        print("4. Kembali ke Home")
        print("5. Download File")
        print("6. Upload File")
        print("7. Keluar")
        garis()
        
        pilihan = input("Pilihan: ")

        if pilihan == '1': # PWD
            print("\n[INFO DIREKTORI]")
            print("Lokasi:", ftp.pwd())
        
        elif pilihan == '2': # List File
            print("\n[LIST FILE SERVER]")
            ftp.dir()
        
        elif pilihan == '3': # CWD
            print("\n[PINDAH DIREKTORI]")
            folder = input("Nama folder tujuan: ")
            try:
                ftp.cwd(folder)
                print(f"[BERHASIL] Sekarang di {ftp.pwd()}")
            except:
                print("[GAGAL] Folder tidak ditemukan")
        
        elif pilihan == '4': # Home
            ftp.cwd(home_dir)
            print(f"[HOME] Kembali ke: {ftp.pwd()}")

        elif pilihan == '5': # Download
            print("\n[DOWNLOAD FILE]")
            # Menampilkan file server terlebih dahulu
            ftp.dir() 
            garis()
            nama_file = input("Nama file yang akan didownload: ")
            try:
                # Membuka file lokal dalam mode write binary
                with open(nama_file, "wb") as f:
                    ftp.retrbinary(f"RETR {nama_file}", f.write)
                print("[BERHASIL] File berhasil didownload")
            except Exception as e:
                print(f"[GAGAL] {e}")

        elif pilihan == '6': # Upload
            print("\n[UPLOAD FILE]")
            print("File lokal saat ini:")
            print(os.listdir()) # List file lokal
            nama_file = input("Nama file lokal untuk diupload: ")
            if os.path.exists(nama_file):
                try:
                    # Membuka file lokal dalam mode read binary
                    with open(nama_file, "rb") as f:
                        ftp.storbinary(f"STOR {nama_file}", f)
                    print("[BERHASIL] Upload sukses")
                except Exception as e:
                    print(f"[GAGAL] {e}")
            else:
                print("[ERROR] File lokal tidak ditemukan")

        elif pilihan == '7':
            ftp.quit()
            print("Koneksi ditutup.")
            break
        
        else:
            print("Pilihan tidak valid")
        
        pause()

if __name__ == "__main__":
    main()