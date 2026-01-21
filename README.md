# Dokumentasi Teknis NetworkFTP

Repositori ini berisi implementasi sistem **Client-Server FTP** (File Transfer Protocol) yang ditulis menggunakan bahasa pemrograman Python. Dokumentasi ini disusun secara rinci untuk menjelaskan setiap komponen, library yang digunakan, dan logika di balik layar.

## Persiapan Sistem (Prerequisites)
Sebelum menjalankan program, pastikan lingkungan kerja memenuhi syarat berikut:
1.  **Python 3.x**: Interpreter Python harus terinstal.
2.  **Library `pyftpdlib`**: Diperlukan untuk script `ftp_server.py`. Library ini menyediakan framework server FTP asynchronous yang robust.
    -   *Cara Install*: Buka terminal/CMD dan jalankan `pip install pyftpdlib`.
3.  **Library `ftplib`**: Digunakan oleh `ftp_client.py`. Ini adalah library bawaan Python (*Standard Library*), jadi tidak perlu instalasi tambahan.

---

## Bedah Kode: `ftp_server.py` (Sisi Server)

Script ini bertugas membuat layanan FTP yang selalu aktif (*listening*) menunggu koneksi client.

### 1. Import Module
-   `import os`: Modul standar untuk berinteraksi dengan Sistem Operasi. Digunakan server untuk membuat folder, mengecek path, dan menulis file dummy.
-   `import logging`: Digunakan untuk mencatat aktivitas server (siapa yang login, file apa yang didownload, error apa yang terjadi) ke layar konsol secara real-time.
-   `from pyftpdlib.authorizers import DummyAuthorizer`: Class untuk manajemen user. Disebut "Dummy" karena menyimpan data user di memori RAM runtime, bukan di database terenkripsi, sehingga cocok untuk pengembangan/belajar.
-   `from pyftpdlib.handlers import FTPHandler`: Menangani protokol FTP. Class ini yang mengerti perintah seperti `USER`, `PASS`, `LIST`, `RETR`.
-   `from pyftpdlib.servers import FTPServer`: Class utama yang membungkus socket jaringan (network socket) dan loop utama program.

### 2. Konfigurasi Log (Logging)
Baris `logging.basicConfig(level=logging.INFO)` mengaktifkan pencatatan log level INFO.
-   Setiap kali ada user login: `[I 2024-01-21 12:00:00] user connected`.
-   Setiap kali transfer selesai: `[I 2024-01-21 12:00:05] transfer complete`.
Ini sangat berguna untuk debugging.

### 3. Manajemen Root Directory (`data`)
Server didesain untuk "mengurung" user di dalam folder spesifik demi keamanan (*Sandbox*).
-   Script otomatis mendeteksi Current Working Directory (`os.getcwd()`).
-   Folder bernama `data` akan dicek keberadaannya. Jika tidak ada, `os.makedirs(server_dir)` akan membuatnya.
-   Ini adalah **Home Directory** bagi user FTP. User tidak bisa naik ke direktori di atasnya (C:\Windows, dll) karena batasan dari `DummyAuthorizer`.

### 4. Konfigurasi User & Permissions
Server mendefinisikan user hardcoded:
-   **User**: `user`
-   **Password**: `12345`
-   **Hak Akses (`elradfmw`)**: String ini merepresentasikan *bitmap permissions*:
    -   (e)lradfmw: Change Directory (CWD).
    -   e(l)radfmw: List files (LIST/NLST).
    -   el(r)adfmw: Retrieve/Download (RETR).
    -   elr(a)dfmw: Append mode upload.
    -   elra(d)fmw: Delete file (DELE).
    -   elrad(f)mw: Rename file (RNFR/RNTO).
    -   elradf(m)w: Make directory (MKD).
    -   elradfm(w): Store/Upload (STOR).

---

## Bedah Kode: `ftp_client.py` (Sisi Client)

Script ini bertindak sebagai antarmuka pengguna (User Interface) berbasis teks/CLI untuk mengirim perintah ke server.

### 1. Library `ftplib`
Ini adalah protokol wrapper untuk RFC 959 (Spesifikasi FTP).
-   `ftp = ftplib.FTP()`: Membuat instance objek sesi FTP.
-   Objek ini menangani pembuatan socket TCP ke port 21 (atau 2122 dalam kasus ini).

### 2. Fungsi Utilitas
-   `clear()`: Membersihkan layar terminal agar tampilan menu rapi. Menggunakan perintah sistem operasi (`cls` di Windows, `clear` di Linux/Mac).
-   `garis()` & `pause()`: Fungsi pembantu estetik untuk memisahkan output dan memberi jeda agar user sempat membaca pesan error/sukses.

### 3. Fungsi Inti
-   `cek_koneksi()`: Melakukan "Ping" logika ke server. Mencoba koneksi dengan timeout 5 detik. Jika server mati, program langsung berhenti daripada crash saat login.
-   `login_ftp()`: Menghandle input username/password dari keyboard dan mengirimnya lewat method `ftp.login(user, pwd)`. Mengembalikan objek `ftp` yang sudah terotentikasi jika sukses.

### 4. Penjelasan Command FTP (Di Balik Layar)
Client menerjemahkan pilihan menu user menjadi perintah FTP mentah yang dikirim ke server:

#### Menu 1: PWD (Print Working Directory)
-   **Python**: `ftp.pwd()`
-   **Protokol**: Mengirim `PWD`. Server membalas `257 "/directory"`.

#### Menu 2: List File
-   **Python**: `ftp.dir()`
-   **Protokol**:
    1.  Masuk *Passive Mode* (`PASV`).
    2.  Buka *Data Connection*.
    3.  Kirim `LIST`.
    4.  Terima data teks daftar file.
    5.  Tutup *Data Connection*.

#### Menu 5: Download (Binary Mode)
-   **Masalah**: File gambar/exe akan rusak jika didownload sebagai teks (karena konversi Line Ending CR/LF).
-   **Solusi**: Menggunakan `ftp.retrbinary("RETR namafile", callback)`.
-   **Cara Kerja**:
    1.  Membuka file lokal di mode `wb` (Write Binary).
    2.  Mengirim perintah `RETR`.
    3.  Server mengirim stream bytes murni.
    4.  Callback `f.write` menulis bytes tersebut langsung ke disk tanpa modifikasi.

#### Menu 6: Upload (Binary Mode)
-   **Python**: `ftp.storbinary("STOR namafile", file_object)`.
-   **Cara Kerja**: Kebalikan dari download. File lokal dibuka `rb` (Read Binary), dikirim ke server via *Data Connection*.

---

## Troubleshooting Umum
1.  **Connection Refused**: Server belum dijalankan. Pastikan run `ftp_server.py` dulu.
2.  **Permission Denied (550)**: Mencoba menulis ke folder Read-Only atau menghapus file yang sedang dibuka program lain.
3.  **Timeout**: Firewall Windows/Antivirus memblokir port 2122. Coba matikan firewall sementara atau allow python.exe.
