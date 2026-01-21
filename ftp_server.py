import os  # Mengimpor modul os untuk berinteraksi dengan sistem operasi (seperti membuat folder/path)
import logging  # Mengimpor modul logging untuk mencatat aktivitas server ke layar terminal
from pyftpdlib.authorizers import DummyAuthorizer  # Mengimpor kelas otorisasi dummy (penyimpanan user di memori, bukan database)
from pyftpdlib.handlers import FTPHandler  # Mengimpor handler protokol FTP yang mengatur command (USER, PASS, LIST, dll)
from pyftpdlib.servers import FTPServer  # Mengimpor kelas inti server FTP yang menangani koneksi jaringan (socket)

def start_ftp_server():
    """
    Fungsi utama untuk mengkonfigurasi dan menjalankan server FTP.
    """
    # Langkah A: Konfigurasi Log
    # Level INFO berarti akan menampilkan status login, transfer file, dan diskoneksi
    logging.basicConfig(level=logging.INFO)
    
    # Menampilkan banner di terminal server agar terlihat rapi
    print("\n" + "-"*60)
    print("SERVER FTP LOKAL BERJALAN")
    print("-" * 60)

    # Langkah B: Persiapan Direktori Penyimpanan (Root Directory)
    share_folder_name = "data"  # Nama folder yang akan menjadi 'rumah' bagi user FTP
    current_dir = os.getcwd()  # Mendapatkan path direktori di mana script ini dijalankan
    server_dir = os.path.join(current_dir, share_folder_name)  # Menggabungkan path saat ini dengan nama folder 'data'

    # Cek apakah folder 'data' sudah ada atau belum
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)  # Jika belum ada, buat foldernya
        print(f"[+] Folder penyimpanan dibuat: {share_folder_name}")

    # Langkah C: Membuat File Dummy (Opsional, untuk testing)
    # File ini dibuat agar user memiliki sesuatu untuk didownload saat pertama kali mencoba
    dummy_file = os.path.join(server_dir, "baca_saya.txt")
    if not os.path.exists(dummy_file):
        # Membuka file dalam mode 'write' (tulis)
        with open(dummy_file, "w") as f:
            f.write("Halo, ini adalah file tes dari server.\nSilakan download file ini.")
        print("[+] File baca_saya.txt dibuat otomatis.")

    # Membuat sub-folder 'Folder_Tes' untuk menguji navigasi direktori (CD)
    sub_folder = os.path.join(server_dir, "Folder_Tes")
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)  # Buat direktori jika belum ada
        print("[+] Sub-Folder 'Folder_Tes' dibuat.")

    print(f"Path Fisik Server: {server_dir}")

    # Langkah D: Konfigurasi Authorizer (Pengelola User)
    authorizer = DummyAuthorizer()  # Membuat instance authorizer
    # Menambahkan user baru
    # Username: "user"
    # Password: "12345"
    # Direktori: server_dir (folder 'data' tadi)
    # Permissions "elradfmw":
    #   e = change directory (pindah folder)
    #   l = list files (lihat daftar file)
    #   r = retrieve file (download)
    #   a = append file (resume upload)
    #   d = delete file (hapus log)
    #   f = rename file (ganti nama)
    #   m = make directory (buat folder)
    #   w = store file (upload)
    authorizer.add_user("user", "12345", server_dir, perm="elradfmw")

    # Langkah E: Konfigurasi Handler
    handler = FTPHandler  # Menunjuk kelas Handler yang akan dipakai
    handler.authorizer = authorizer  # Menghubungkan handler dengan authorizer yang sudah disetting di atas
    handler.banner = "Selamat datang di Local FTP Server (Python)"  # Pesan sambutan standar FTP code 220

    # Langkah F: Binding Server dan Port
    # "127.0.0.1" adalah localhost (hanya bisa diakses komputer ini sendiri)
    # 2122 adalah port (dipakai 2122 untuk menghindari bentrok dengan port 21 default sistem)
    address = ("127.0.0.1", 2122)

    try:
        # Membuat instance server dengan alamat dan handler yang sudah disiapkan
        server = FTPServer(address, handler)
        
        # Konfigurasi batas koneksi (opsional)
        server.max_cons = 256  # Maksimal total koneksi bersamaan
        server.max_cons_per_ip = 5  # Maksimal koneksi dari satu IP yang sama
        
        print("-" * 60)
        print("[SERVER SIAP MENERIMA KONEKSI]")
        print(f"Alamat : ftp://127.0.0.1:2122")
        print("-" * 60)
        
        # Menjalankan server dalam loop tak terbatas (infinite loop)
        # Server akan terus berjalan sampai dihentikan manual (Ctrl+C)
        server.serve_forever()
    
    except OSError as ex:
        # Menangkap error sistem, misal port 2122 sudah dipakai aplikasi lain
        print(f"Gagal memulai server: {ex}")
    except KeyboardInterrupt:
        # Menangkap perintah Stop (Ctrl+C) dari user
        server.close_all()  # Menutup semua koneksi socket
        print("\nServer dimatikan.")

# Blok ini memastikan fungsi start_ftp_server() hanya jalan jika file ini dieksekusi langsung
if __name__ == "__main__":
    start_ftp_server()
