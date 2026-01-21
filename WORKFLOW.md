# Alur Kerja Program (Workflow) Secara Mendalam

Dokumen ini menjelaskan alur kerja, logika internal, dan mekanisme protokol yang terjadi antara `ftp_server.py` dan `ftp_client.py`.

## I. Arsitektur Komunikasi
Program ini mengimplementasikan model **Client-Server** menggunakan protokol FTP (File Transfer Protocol).
- **Protokol**: TCP/IP.
- **Port Control**: 2122 (Custom port, default FTP biasanya 21).
- **Library Server**: `pyftpdlib` (Python FTP Server Library) - menangani socket, threading, dan protokol FTP secara asynchronous/multi-thread.
- **Library Client**: `ftplib` (Standard Library) - menyediakan interface high-level untuk mengirim command FTP.

---

## II. Detail Alur Kerja Server (`ftp_server.py`)

### 1. Inisialisasi & Import
- Program mengimpor modul `os` untuk operasi sistem file dan `logging` untuk mencatat log aktivitas (koneksi, error, transfer).
- **Komponen pyftpdlib**:
  - `DummyAuthorizer`: Mengelola otentikasi user secara sederhana (disimpan di memori, bukan database).
  - `FTPHandler`: Inti dari server yang menangani setiap perintah FTP yang masuk (seperti USER, PASS, LIST, RETR).
  - `FTPServer`: Class yang membungkus socket server, menerima koneksi masuk, dan menugaskannya ke Handler.

### 2. Persiapan Lingkungan (Environment Setup)
Sebelum server binding ke port, ia mempersiapkan "Sandbox" sistem file:
1.  **Cek Folder Root**: Mengecek apakah folder `data` ada. Jika tidak, dibuat dengan `os.makedirs`. Ini mencegah error "path not found".
2.  **Generasi Konten Dummy**:
    -   Membuat `baca_saya.txt`: Server menulis file teks sederhana agar user memiliki sesuatu untuk didownload saat pertama kali mencoba.
    -   Membuat `Folder_Tes`: Direktori kosong untuk menguji fitur navigasi (CD/CWD).

### 3. Konfigurasi Otentikasi (Authentication)
Server tidak mengizinkan akses anonim (kecuali dikonfigurasi demikian).
-   `authorizer.add_user("user", "12345", server_dir, perm="elradfmw")`
    -   **User/Pass**: user/12345.
    -   **Home Dir**: Folder `data` yang disiapkan sebelumnya.
    -   **Permissions (`elradfmw`)**:
        -   `e` (change directory): Boleh pindah folder.
        -   `l` (list): Boleh melihat isi folder.
        -   `r` (retrieve): Boleh download file.
        -   `a` (append): Boleh resume upload.
        -   `d` (delete): Boleh hapus file.
        -   `f` (rename): Boleh ganti nama file.
        -   `m` (make directory): Boleh buat folder.
        -   `w` (write): Boleh upload file baru.
    *Tanpa permission ini, client akan mendapat error "550 Permission denied".*

### 4. Server Binding & Listening
-   `FTPServer(("127.0.0.1", 2122), handler)`: Server membuka socket di localhost port 2122.
-   `server.serve_forever()`: Loop utama. Server terus berjalan (infinite loop) menunggu koneksi TCP masuk. Saat ada client terhubung, server membuat instance handler baru untuk sesi tersebut.

---

## III. Detail Alur Kerja Client (`ftp_client.py`)

Client bekerja secara sekuensial (langkah demi langkah) yang dikontrol oleh user.

### Tahap 1: Three-Way Handshake & Koneksi Awal
Kode: `ftp.connect(FTP_HOST, FTP_PORT)`
1.  Client mengirim paket **SYN** ke 127.0.0.1:2122.
2.  Server membalas **SYN-ACK**.
3.  Client membalas **ACK**.
4.  Koneksi TCP Control Channel terbentuk.
5.  Server mengirim **Banner** (Pesan sambutan): "220 Selamat datang di Local FTP Server".

### Tahap 2: Proses Login (Authentication)
1.  **USER Command**:
    -   Input: `user`
    -   Client kirim: `USER user`
    -   Server membalas: `331 Username okay, need password`.
2.  **PASS Command**:
    -   Input: `*****`
    -   Client kirim: `PASS 12345`
    -   Server membalas: `230 Login successful`.
    -   *Jika salah*: Server membalas `530 Login incorrect` dan ftplib akan raise `error_perm`.

### Tahap 3: Operasi Menu (Command Flow)

#### A. Cek Direktori (PWD)
-   **Tujuan**: Mengetahui posisi aktif user di server.
-   **Command**: `PWD`
-   **Respon Server**: `257 "/"` (Root direktori user, bukan root sistem operasi server. Ini disebut *chroot jail*).

#### B. List File (LIST/DIR)
-   **Tujuan**: Melihat isi folder.
-   **Mekanisme (Passive Mode - Default ftplib)**:
    1.  Client mengirim `PASV`.
    2.  Server membuka port ephemeral acak (misal: 50000) dan membalas `227 Entering Passive Mode (127,0,0,1,195,80)`.
    3.  Client membuka koneksi TCP kedua (Data Channel) ke port tersebut.
    4.  Client mengirim `LIST`.
    5.  Server mengirim daftar file teks lewat Data Channel.
    6.  Server menutup Data Channel.

#### C. Download File (RETR)
-   **Logika Code**:
    ```python
    with open(nama_file, "wb") as f:
        ftp.retrbinary(f"RETR {nama_file}", f.write)
    ```
-   **Analisis Mendalam**:
    1.  File lokal dibuka mode `wb` (Write Binary) agar data gambar/zip tidak rusak (bukan text mode).
    2.  Client kirim `PASV` -> Server OK.
    3.  Client connect Data Channel.
    4.  Client kirim `RETR nama_file`.
    5.  Server mulai streaming bit-bit file lewat Data Channel.
    6.  Fungsi callback `f.write` menerima potongan data (chunks) dan menulisnya ke harddisk lokal.
    7.  Setelah selesai, server kirim `226 Transfer complete`.

#### D. Upload File (STOR)
-   **Logika Code**:
    ```python
    with open(nama_file, "rb") as f:
        ftp.storbinary(f"STOR {nama_file}", f)
    ```
-   **sys**Analisis Mendalam**:
    1.  File lokal dibuka mode `rb` (Read Binary).
    2.  Client kirim `PASV` -> Server OK.
    3.  Client connect Data Channel.
    4.  Client kirim `STOR nama_file`.
    5.  Client membaca file lokal dan mengirim bit-bitnya ke server lewat Data Channel.
    6.  Server menerima dan menyimpannya di folder `data`.

#### E. Pindah Direktori (CWD)
-   **Command**: `CWD folder_tujuan`
-   Server mengecek apakah path valid.
    -   Jika ya: `250 Directory successfully changed`.
    -   Jika tidak: `550 Failed to change directory`.

## IV. Penanganan Error (Exception Handling)
Program client dilengkapi `try-except` blocks.
-   `ftplib.all_errors`: Menangkap semua error spesifik FTP (timeout, auth gagal, izin ditolak).
-   `Exception`: Menangkap error umum lain (misal file lokal tidak bisa dibuka karena dikunci oleh program lain).
-   Jika terjadi error koneksi, program client akan memberi notifikasi user tanpa crash (keluar paksa) secara tiba-tiba.
