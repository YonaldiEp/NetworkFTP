import os
import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def start_ftp_server():
    # Konfigurasi logging untuk memantau aktivitas server
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "-"*60)
    print("SERVER FTP LOKAL BERJALAN")
    print("-" * 60)

    # 1. Menyiapkan Folder Server
    share_folder_name = "data"
    current_dir = os.getcwd()
    server_dir = os.path.join(current_dir, share_folder_name)

    if not os.path.exists(server_dir):
        os.makedirs(server_dir)
        print(f"[+] Folder penyimpanan dibuat: {share_folder_name}")

    # Membuat dummy file untuk pengujian
    dummy_file = os.path.join(server_dir, "baca_saya.txt")
    if not os.path.exists(dummy_file):
        with open(dummy_file, "w") as f:
            f.write("Halo, ini adalah file tes dari server.\nSilakan download file ini.")
        print("[+] File baca_saya.txt dibuat otomatis.")

    # Membuat sub-folder tes
    sub_folder = os.path.join(server_dir, "Folder_Tes")
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)
        print("[+] Sub-Folder 'Folder_Tes' dibuat.")

    print(f"Path Fisik Server: {server_dir}")

    # 2. Konfigurasi Authorizer
    authorizer = DummyAuthorizer()
    # Menambahkan user 'user' dengan password '12345' dan hak akses penuh
    authorizer.add_user("user", "12345", server_dir, perm="elradfmw")

    # 3. Konfigurasi Handler
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Selamat datang di Local FTP Server (Python)"

    # 4. Inisialisasi Server
    # Menggunakan port 2122 sesuai instruksi modul
    address = ("127.0.0.1", 2122)

    try:
        server = FTPServer(address, handler)
        server.max_cons = 256
        server.max_cons_per_ip = 5
        
        print("-" * 60)
        print("[SERVER SIAP MENERIMA KONEKSI]")
        print(f"Alamat : ftp://127.0.0.1:2122")
        print("-" * 60)
        
        server.serve_forever()
    
    except OSError as ex:
        print(f"Gagal memulai server: {ex}")
    except KeyboardInterrupt:
        server.close_all()
        print("\nServer dimatikan.")

if __name__ == "__main__":
    start_ftp_server()