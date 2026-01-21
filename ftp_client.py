import ftplib  # Mengimpor modul ftplib untuk menangani protokol FTP di sisi client
import os  # Mengimpor modul os untuk interaksi dengan sistem file lokal (daftar file, hapus layar)

# Konfigurasi Koneksi Server
FTP_HOST = "127.0.0.1"  # Alamat IP server tujuan (localhost)
FTP_PORT = 2122  # Port server tujuan (harus sama dengan yang disetting di server)

def clear():
    """Memberihkan layar terminal agar tampilan bersih."""
    # os.system menjalankan perintah shell ('cls' untuk Windows, 'clear' untuk Linux/Mac)
    os.system("cls" if os.name == "nt" else "clear")

def garis():
    """Membuat garis pemisah visual."""
    print("-" * 60)  # Mencetak karakter '-' sebanyak 60 kali

def pause():
    """Memberi jeda agar user bisa membaca output sebelum layar dibersihkan."""
    input("\nTekan ENTER untuk lanjut...")

def cek_koneksi():
    """
    Mengecek apakah server FTP aktif sebelum mencoba login.
    Mengembalikan True jika aktif, False jika mati.
    """
    garis()
    print("CEK KONEKSI FTP SERVER")
    garis()
    try:
        # Membuat objek FTP baru
        ftp = ftplib.FTP()
        # Mencoba connect ke host:port dengan timeout 5 detik
        # Jika dalam 5 detik tidak ada respon, akan dianggap gagal
        ftp.connect(FTP_HOST, FTP_PORT, timeout=5)
        print("[STATUS] Server FTP TERHUBUNG")
        # Menutup koneksi tes (karena kita hanya ingin ping saja)
        ftp.close()
        return True
    except:
        # Menangkap error jika server mati atau tidak bisa dihubungi
        print("[STATUS] Server FTP TIDAK TERHUBUNG")
        return False

def login_ftp():
    """
    Menangani proses login user.
    Mengembalikan objek koneksi 'ftp' yang sudah terautentikasi jika berhasil.
    """
    ftp = ftplib.FTP()  # Membuat instance baru
    try:
        # Melakukan koneksi awal (Handshake TCP)
        ftp.connect(FTP_HOST, FTP_PORT)
        print("[LOGIN FTP]")
        
        # Meminta input kredensial dari user
        user = input("Username: ")
        pwd = input("Password: ")
        
        # Mengirim perintah USER <user> dan PASS <pwd> ke server
        ftp.login(user, pwd)
        
        print("[LOGIN BERHASIL]")
        # Menampilkan pesan sambutan dari server (kode 220)
        print("Pesan Server:", ftp.getwelcome())
        return ftp  # Mengembalikan objek sesi yang aktif
    except Exception as e:
        # Jika login gagal (password salah atau user tidak ada), tangkap errornya
        print(f"\n[LOGIN GAGAL] {e}")
        return None

def main():
    """Logika Utama Program Client."""
    clear()  # Bersihkan layar saat mulai
    
    # STEP 1: Cek Koneksi
    # Jika server mati, program langsung berhenti
    if not cek_koneksi():
        return
    pause()

    # STEP 2: Login
    clear()
    ftp = login_ftp()
    if not ftp:
        return # Jika login gagal, keluar dari program
    
    # STEP 3: Masuk ke Menu Utama
    # ftp.pwd() mengambil 'Print Working Directory' (lokasi saat ini di server)
    home_dir = ftp.pwd() # Menyimpan direktori awal (root) sebagai patokan tombol 'Home'

    while True:
        # Loop infinite agar menu terus muncul setelah selesai satu aksi
        clear()
        print(f"Server saat ini: {ftp.pwd()}") # Menampilkan posisi user sekarang di server
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

        if pilihan == '1': # Fitur PWD
            print("\n[INFO DIREKTORI]")
            # Mengirim command PWD ke server, server membalas path string
            print("Lokasi:", ftp.pwd())
        
        elif pilihan == '2': # Fitur List File
            print("\n[LIST FILE SERVER]")
            # Mengirim command LIST/DIR. Output langsung dicetak ke layar oleh library
            ftp.dir()
        
        elif pilihan == '3': # Fitur Ganti Folder (CWD)
            print("\n[PINDAH DIREKTORI]")
            folder = input("Nama folder tujuan: ")
            try:
                # Mengirim command CWD <folder>
                ftp.cwd(folder)
                print(f"[BERHASIL] Sekarang di {ftp.pwd()}")
            except:
                print("[GAGAL] Folder tidak ditemukan")
        
        elif pilihan == '4': # Fitur Home
            # Langsung pindah ke variabel home_dir yang disimpan di awal
            ftp.cwd(home_dir)
            print(f"[HOME] Kembali ke: {ftp.pwd()}")

        elif pilihan == '5': # Fitur Download (RETR)
            print("\n[DOWNLOAD FILE]")
            # Menampilkan list file dulu agar user tahu mau download apa
            ftp.dir() 
            garis()
            nama_file = input("Nama file yang akan didownload: ")
            try:
                # Membuka file lokal baru dengan mode 'wb' (Write Binary)
                # Binary mode penting agar file gambar/exe tidak korup
                with open(nama_file, "wb") as f:
                    # retrbinary mengirim command 'RETR <namafile>'
                    # Setiap paket data yang diterima dari server ditulis ke file lokal via f.write
                    ftp.retrbinary(f"RETR {nama_file}", f.write)
                print("[BERHASIL] File berhasil didownload")
            except Exception as e:
                print(f"[GAGAL] {e}")

        elif pilihan == '6': # Fitur Upload (STOR)
            print("\n[UPLOAD FILE]")
            print("File lokal saat ini:")
            print(os.listdir()) # Menampilkan file yang ada di laptop user
            nama_file = input("Nama file lokal untuk diupload: ")
            
            # Cek apakah file lokal benar-benar ada
            if os.path.exists(nama_file):
                try:
                    # Membuka file lokal dengan mode 'rb' (Read Binary)
                    with open(nama_file, "rb") as f:
                        # storbinary mengirim command 'STOR <namafile>'
                        # Mengirim isi file 'f' ke server
                        ftp.storbinary(f"STOR {nama_file}", f)
                    print("[BERHASIL] Upload sukses")
                except Exception as e:
                    print(f"[GAGAL] {e}")
            else:
                print("[ERROR] File lokal tidak ditemukan")

        elif pilihan == '7':
            # Mengirim command QUIT untuk menutup koneksi server dengan sopan
            ftp.quit()
            print("Koneksi ditutup.")
            break # Keluar dari loop while, program selesai
        
        else:
            print("Pilihan tidak valid")
        
        # Memberi jeda sebelum layar dibersihkan kembali di awal loop
        pause()

# Memastikan main() hanya jalan jika file dijalankan langsung
if __name__ == "__main__":
    main()
