  HydroDah v3 — Dashboard THC-Hydra (full CLI)
  Modify by @andrewjoschelbian

  Language: Indonesian
  Script : hydrodah.py
  Port   : 8091
  Buka   : http://localhost:8091
  
DISCLAIMER & ETIKA

Tool ini untuk PEMBELAJARAN dan pengujian AUTHORIZED saja:
lab sendiri (DVWA), challenge CTF, program bug bounty resmi,
atau sistem dengan IZIN TERTULIS.

Penggunaan ke sistem tanpa izin = pelanggaran UU ITE
No. 11/2008 (Pasal 30-36). Penyalahgunaan tanggung jawab
pengguna sepenuhnya.

Persyaratan umum: python3 (sudo apt install python3)
Jalankan:   python3 hydrodah.py
Buka:       http://localhost:8091
Stop:       Ctrl+C / pkill -f hydrodah.py

UNTUK APA
  Dashboard web untuk THC-Hydra — brute force 50+ protokol
  (SSH, FTP, HTTP form/basic, MySQL, PostgreSQL, RDP, VNC,
  SMB, Telnet, POP3, IMAP, SMTP, LDAP, custom, dll).
  Dua mode:
  - SEDERHANA : form cepat seperti tools lain
  - LANJUTAN  : SEMUA opsi hydra persis CLI:
    -l/-L/-p/-P/-x/-C/-M/-e/-u/-f/-F/-t/-w/-W/-s/-S/-4/-6
    /-v/-V/-q/-I/-m  + preview command live
  Output hydra mengalir real-time di terminal dashboard,
  kredensial di-highlight, laporan tersimpan otomatis di
  ~/hydrodah_downloads/ (hydra_report_*.txt + found_*.txt).

CARA PAKAI
  1. INSTALL HYDRA DULU (WAJIB):
       sudo apt update && sudo apt install -y hydra
     Untuk modul lengkap:
       sudo apt install -y libssl-dev libssh-dev libpcre3-dev                          libpq-dev freetds-dev
  2. Jalankan: python3 hydrodah.py
  3. Buka http://localhost:8091
  4. Mode Sederhana (contoh DVWA):
       Modul: HTTP POST form | Host: localhost
       Form spec: /dvwa/login.php:username=^USER^&password=^PASS^&Login=Login:Login failed
       Opsi: -f (stop setelah ketemu)
  5. Atau Mode Lanjutan untuk kontrol penuh hydra
  6. Kalau dashboard menampilkan "hydra tidak ditemukan" ->
     install langkah 1 belum berhasil

CEK HASIL
  ls ~/hydrodah_downloads/

INSTALL TAMBAHAN (WAJIB)
  sudo apt install -y hydra
