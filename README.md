HydroDah v3
===========

Dashboard web untuk THC-Hydra, tool brute force lebih dari 50 protokol
(SSH, FTP, HTTP form dan basic auth, MySQL, PostgreSQL, RDP, VNC, SMB,
Telnet, POP3, IMAP, SMTP, LDAP, dan banyak lagi).

  Dimodifikasi oleh : @andrewjoschelbian
  Berbasis          : THC-Hydra
  Platform          : Linux dan Windows
  Bahasa            : Indonesia


FITUR UTAMA
-----------

1. Mode Sederhana
   Form cepat: pilih modul, isi target, paste daftar user dan
   password, lalu langsung dijalankan.

2. Mode Lanjutan
   Semua opsi Hydra persis seperti CLI:
   -l -L -p -P -x -C -M -e -u -f -F -t -w -W -s -S -4 -6 -v -V -q -I -m
   Dilengkapi preview perintah secara live.

Fitur lain:
- Output Hydra mengalir real-time di dashboard
- Kredensial yang ditemukan di-highlight otomatis
- Laporan tersimpan otomatis di ~/hydrodah_downloads/
  (hydra_report_*.txt dan found_*.txt)


PERSYARATAN
-----------

- Python 3 (sudo apt install python3)
- THC-Hydra, wajib diinstall dulu:

  sudo apt update && sudo apt install -y hydra

Untuk dukungan modul lengkap:

  sudo apt install -y libssl-dev libssh-dev libpcre3-dev libpq-dev freetds-dev


CARA PAKAI
----------

1. Install Hydra (lihat langkah di atas)
2. Jalankan:
   - Linux   : python3 hydrodah.py
   - Windows : py hydrodah.py
3. Buka http://localhost:8091 di browser
4. Contoh Mode Sederhana (target DVWA lokal):
   - Modul    : http-post-form
   - Host     : localhost
   - Form spec:
     /dvwa/login.php:username=^USER^&password=^PASS^&Login=Login:Login failed
   - Centang -f agar berhenti setelah kredensial ketemu
5. Atau gunakan Mode Lanjutan untuk kontrol penuh seperti CLI Hydra
6. Jika muncul tulisan "hydra tidak ditemukan", berarti install
   di langkah 1 belum berhasil


CEK HASIL
---------

  ls ~/hydrodah_downloads/


DISCLAIMER
----------

Tool ini hanya untuk pembelajaran dan pengujian authorized
(lab sendiri, CTF, bug bounty resmi, atau sistem berizin tertulis).
Penggunaan tanpa izin merupakan pelanggaran UU ITE No. 11/2008
Pasal 30 sampai 36. Segala penyalahgunaan menjadi tanggung jawab
pengguna.
