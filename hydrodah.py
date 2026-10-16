#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HydroDah CLI v3 — Dashboard THC-Hydra PURE TERMINAL (Windows & Linux)

Cara pakai:
  Linux  : python3 hydrodah_cli.py
  Windows: py hydrodah_cli.py     (atau python hydrodah_cli.py)
"""

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime

if os.name == "nt":
    os.system("")  # aktifkan ANSI color di Windows 10+

# ---------------- warna ----------------
R    = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
RED  = "\033[91m"; GRN = "\033[92m"; YEL = "\033[93m"
BLU  = "\033[94m"; CYN = "\033[96m"; GRY = "\033[90m"; MAG = "\033[95m"

MAX_LINES   = 20000
FIND_RE     = re.compile(r"login:\s*(?P<login>\S+)\s+password:\s*(?P<pw>\S+)")
STATUS_RE   = re.compile(r"\[(STATUS|ERROR|WARNING)\]")
DL_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "hydrodah_downloads")

FOUND   = []     # kredensial yang ketemu
OUTPUT  = []     # output terakhir (untuk laporan)

MODULES = ["ssh", "ftp", "http-post-form", "http-get-form",
           "http-get (basic auth)", "mysql", "rdp", "vnc", "smb",
           "telnet", "pop3", "imap", "ldap"]
HTTP_FORMS = ("http-post-form", "http-get-form", "http-head-form")


# ---------------- util ----------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def hr():
    print(GRY + "─" * 60 + R)

def banner():
    print(f"""{RED}{BOLD}
  ╔══════════════════════════════════════════════╗
  ║   HydroDah CLI v3 — copy Hydra Full Terminal         ║
  ║   @andrewjoschelbian                            ║
  ╚══════════════════════════════════════════════╝{R}
  {DIM}Dashboard THC-Hydra via terminal{R}""")

def ask(prompt, default=""):
    t = f" {GRY}[{default}]{R}" if default else ""
    try:
        s = input(f"{CYN}? {prompt}{R}{t}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(); return default
    return s or default

def ask_int(prompt, default=None):
    s = ask(prompt, "" if default is None else str(default))
    try:
        return int(s)
    except (ValueError, TypeError):
        return None

def ask_bool(prompt, default=True):
    d = "Y/n" if default else "y/N"
    try:
        s = input(f"{CYN}? {prompt} {GRY}[{d}]{R}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(); return default
    if not s:
        return default
    return s.startswith("y")

def read_multiline(prompt):
    print(f"{YEL}{prompt}{R} {GRY}(1 item per baris, baris kosong = selesai){R}")
    lines = []
    while True:
        try:
            line = input(f"  {GRY}|{R} ")
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line.strip():
            break
        lines.append(line.strip())
    return lines

def hr_timer(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s}s" if m else f"{s}s"


# ---------------- susun command ----------------
def build_cmd(p):
    tmpdir = tempfile.mkdtemp(prefix="hydrodah_")
    cmd = ["hydra"]
    files = {}

    # ---- credential ----
    if p.get("combo_file"):                         # -C
        cf = p["combo_file"]
        if not os.path.isfile(cf):
            cpath = os.path.join(tmpdir, "combo.txt")
            open(cpath, "w", encoding="utf-8").write(cf)
            cf = cpath
        cmd += ["-C", cf]
    else:
        if p.get("user_list"):
            uf = os.path.join(tmpdir, "users.txt")
            open(uf, "w", encoding="utf-8").write(p["user_list"])
            cmd += ["-L", uf]
        elif p.get("user"):
            cmd += ["-l", p["user"]]
        if p.get("pass_list"):
            pf = os.path.join(tmpdir, "pass.txt")
            open(pf, "w", encoding="utf-8").write(p["pass_list"])
            cmd += ["-P", pf]
        elif p.get("passwd"):
            cmd += ["-p", p["passwd"]]
        if p.get("xmask"):
            cmd += ["-x", p["xmask"]]

    for flag, key in [("-e", "e_ns"), ("-u", "loop_users"), ("-f", "stop_pair"),
                      ("-F", "stop_host"), ("-S", "ssl"), ("-4", "ipv4"),
                      ("-6", "ipv6"), ("-v", "verbose"), ("-V", "debug"),
                      ("-q", "quiet"), ("-I", "norestore")]:
        if p.get(key):
            cmd.append(flag)
    if p.get("tasks"):
        cmd += ["-t", str(min(int(p["tasks"]), 64))]
    if p.get("waittime"):
        cmd += ["-w", str(p["waittime"])]
    if p.get("conntimeout"):
        cmd += ["-W", str(p["conntimeout"])]
    if p.get("port"):
        cmd += ["-s", str(p["port"])]

    ofile = os.path.join(tmpdir, "out.txt")
    cmd += ["-o", ofile]
    files["ofile"] = ofile

    mod    = p.get("module") or "ssh"
    target = p.get("target", "")
    extra  = p.get("mod_param", "")

    if mod in HTTP_FORMS:
        if extra and "/" not in target:
            target = target + extra
        if "/" in target:
            host, spec = target.split("/", 1)
            cmd += [host, f"{mod}=/{spec}"]
        else:
            cmd += [target, mod]
    else:
        if p.get("targets_list"):
            mf = os.path.join(tmpdir, "targets.txt")
            open(mf, "w", encoding="utf-8").write(p["targets_list"])
            cmd += ["-M", mf]
        else:
            cmd.append(target)
        cmd.append(mod)
        if extra:
            cmd += ["-m", extra]
    return cmd, files, tmpdir


# ---------------- jalankan ----------------
def run_command(cmd, ofile=None, tmpdir=None, raw=False):
    global FOUND, OUTPUT
    FOUND, OUTPUT = [], []
    print()
    print(f"{BLU}$ {shlex.join(cmd) if hasattr(shlex, 'join') else ' '.join(cmd)}{R}")
    print()

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
    except FileNotFoundError:
        print(f"{RED}❌ binary 'hydra' tidak ditemukan!{R}")
        print(f"   Install: {YEL}sudo apt install hydra{R} (Linux) / "
              f"{YEL}https://github.com/vanhauser-thc/thc-hydra{R} (Windows)")
        return
    except Exception as e:
        print(f"{RED}❌ ERROR: {e}{R}")
        return

    t0     = time.time()
    n_line = 0
    stopped = False
    try:
        for line in proc.stdout:
            line = line.rstrip("\r\n")
            if not line:
                continue
            n_line += 1
            OUTPUT.append(line)
            if len(OUTPUT) > MAX_LINES:
                del OUTPUT[:5000]
            m = FIND_RE.search(line)
            if m and "[ATTEMPT]" not in line:
                FOUND.append({"login": m.group("login"),
                              "password": m.group("pw")})
                print(f"{GRN}{BOLD}  ✅ LOGIN: {m.group('login')}"
                      f"   PASSWORD: {m.group('pw')}{R}")
            elif STATUS_RE.search(line):
                print(f"{YEL}  {line}{R}")
            else:
                print(f"  {line}")
        proc.wait()
    except KeyboardInterrupt:
        stopped = True
        print(f"\n{YEL}[!] Ctrl+C — menghentikan hydra...{R}")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
    dur = time.time() - t0

    # parse file -o (hasil final)
    if ofile and os.path.isfile(ofile):
        try:
            for ln in open(ofile, encoding="utf-8", errors="ignore"):
                m = FIND_RE.search(ln)
                if m and not any(f["login"] == m.group("login") and
                                 f["password"] == m.group("pw") for f in FOUND):
                    FOUND.append({"login": m.group("login"),
                                  "password": m.group("pw")})
        except Exception:
            pass
    if tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)

    # ringkasan
    print()
    hr()
    print(f"  {BOLD}Selesai{R}  durasi: {CYN}{hr_timer(dur)}{R}"
          f"  |  baris output: {n_line}"
          f"  |  kredensial: {GRN}{BOLD}{len(FOUND)}{R}")
    if stopped:
        print(f"  {YEL}(dihentikan manual dengan Ctrl+C){R}")
    if FOUND:
        print(f"\n  {GRN}{BOLD}╔══ KREDENSIAL DITEMUKAN ══{R}")
        for f in FOUND:
            print(f"  {GRN}║ ✅ {f['login']} : {f['password']}{R}")
        print(f"  {GRN}{BOLD}╚{'═' * 26}{R}")
    hr()

    if ask_bool("Simpan laporan .txt?", True):
        save_report(cmd, dur)


def save_report(cmd, dur):
    os.makedirs(DL_DIR, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(DL_DIR, f"hydra_report_{ts}.txt")
    L = ["# HydroDah CLI v3 Report",
         f"# Waktu : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({hr_timer(dur)})",
         f"# CMD   : {' '.join(cmd)}",
         f"# Hasil : {len(FOUND)} kredensial",
         "", "=" * 60]
    for f in FOUND:
        L.append(f"  ✅ {f['login']} : {f['password']}")
    L += ["", "OUTPUT (potongan):"]
    L += [f"  {x}" for x in OUTPUT[-80:]]
    try:
        with open(path, "w", encoding="utf-8") as fp:
            fp.write("\n".join(L) + "\n")
        print(f"{GRN}💾 laporan tersimpan: {path}{R}")
    except Exception as e:
        print(f"{RED}gagal simpan: {e}{R}")


# ---------------- mode 1: sederhana ----------------
def wizard_simple():
    clear(); banner(); print()
    print(f"{BOLD}[ MODE SEDERHANA ]{R}")
    hr()
    for i, m in enumerate(MODULES, 1):
        print(f"  {GRY}{i:2}{R}. {m}")
    mod = MODULES[max(1, min(len(MODULES), ask_int("Pilih modul", 1))) - 1]
    mod = mod.split(" ")[0]          # buang keterangan "(basic auth)"
    target = ask("Target host/IP")
    if not target:
        print(f"{YEL}Target kosong, dibatalkan.{R}"); pause(); return
    port  = ask_int("Port (-s, kosong = default)")
    tasks = ask_int("Tasks (-t)", 4)
    wait  = ask_int("Wait time (-w)", 10)

    target_full = target
    if mod in HTTP_FORMS:
        print(f"\n{YEL}Format form spec:{R} {CYN}/path:body:^USER^ ^PASS^:fail_string{R}")
        spec = ask("Form spec", "/login.php:username=^USER^&password=^PASS^:Login failed")
        if spec:
            target_full = target + spec

    users = read_multiline("Daftar USER")
    if not users:
        print(f"{YEL}User kosong, dibatalkan.{R}"); pause(); return
    passes = read_multiline("Daftar PASSWORD")
    if not passes:
        print(f"{YEL}Password kosong, dibatalkan.{R}"); pause(); return

    p = {
        "module": mod, "target": target_full,
        "user_list": "\n".join(users), "pass_list": "\n".join(passes),
        "tasks": tasks, "waittime": wait, "port": port,
        "stop_pair": ask_bool("Stop setelah 1 pasangan ketemu (-f)?", True),
        "ssl": ask_bool("Pakai SSL/TLS (-S)?", False),
        "norestore": True,
    }
    cmd, files, tmpdir = build_cmd(p)
    print(f"\n{MAG}Perintah yang akan dijalankan:{R}")
    print(f"  {CYN}{' '.join(cmd)}{R}")
    if not ask_bool("Jalankan sekarang?", True):
        shutil.rmtree(tmpdir, ignore_errors=True); return
    run_command(cmd, ofile=files["ofile"], tmpdir=tmpdir)


# ---------------- mode 2: lanjutan ----------------
def wizard_adv():
    clear(); banner(); print()
    print(f"{BOLD}[ MODE LANJUTAN — semua opsi persis CLI hydra ]{R}")
    hr()
    p = {}
    print(f"{YEL}— CREDENTIAL (kosongkan yang tidak dipakai) —{R}")
    p["user"]       = ask("-l login (satu user)")
    p["user_list"]  = "\n".join(read_multiline("-L daftar user (paste)")) or None
    p["passwd"]     = ask("-p password (satu)")
    p["pass_list"]  = "\n".join(read_multiline("-P daftar password (paste)")) or None
    p["combo_file"] = "\n".join(read_multiline("-C combo user:pass (paste)")) or None
    p["xmask"]      = ask("-x mask (min:max:charset)")
    if p["combo_file"]:
        p.update({k: None for k in ("user", "user_list", "passwd", "pass_list", "xmask")})
    if p["xmask"]:
        p.update({k: None for k in ("passwd", "pass_list")})

    print(f"\n{YEL}— TARGET & MODUL —{R}")
    p["module"]       = ask("Modul hydra", "ssh")
    p["target"]       = ask("Target host/IP")
    p["targets_list"] = "\n".join(read_multiline("-M daftar target (paste)")) or None
    p["mod_param"]    = ask("-m parameter modul (opsional)")
    p["port"]         = ask_int("-s port")
    p["tasks"]        = ask_int("-t tasks", 4)
    p["waittime"]     = ask_int("-w wait time", 10)
    p["conntimeout"]  = ask_int("-W connect timeout")

    print(f"\n{YEL}— FLAGS (y = aktif) —{R}")
    p["e_ns"]       = ask_bool("-e  coba pass kosong/sama-login/reversed", False)
    p["loop_users"] = ask_bool("-u  loop per user", False)
    p["stop_pair"]  = ask_bool("-f  stop setelah 1 pasangan", True)
    p["stop_host"]  = ask_bool("-F  stop setelah 1 host (dg -M)", False)
    p["ssl"]        = ask_bool("-S  pakai SSL", False)
    p["ipv4"]       = ask_bool("-4  IPv4 saja", False)
    p["ipv6"]       = ask_bool("-6  IPv6 saja", False)
    p["verbose"]    = ask_bool("-v  verbose", False)
    p["debug"]      = ask_bool("-V  debug", False)
    p["quiet"]      = ask_bool("-q  quiet", False)
    p["norestore"]  = ask_bool("-I  abaikan restore file", True)

    if not p.get("target") and not p.get("targets_list"):
        print(f"{YEL}Target kosong, dibatalkan.{R}"); pause(); return
    if not any([p.get("user"), p.get("user_list"), p.get("combo_file")]):
        print(f"{YEL}User kosong, dibatalkan.{R}"); pause(); return
    if not any([p.get("passwd"), p.get("pass_list"), p.get("combo_file"), p.get("xmask")]):
        print(f"{YEL}Password/mask kosong, dibatalkan.{R}"); pause(); return

    cmd, files, tmpdir = build_cmd(p)
    print(f"\n{MAG}Perintah yang akan dijalankan:{R}")
    print(f"  {CYN}{' '.join(cmd)}{R}")
    if not ask_bool("Jalankan sekarang?", True):
        shutil.rmtree(tmpdir, ignore_errors=True); return
    run_command(cmd, ofile=files["ofile"], tmpdir=tmpdir)


# ---------------- mode 3: perintah mentah ----------------
def wizard_raw():
    clear(); banner(); print()
    print(f"{BOLD}[ KETIK PERINTAH HYDRA MENTAH ]{R}")
    hr()
    print(f"{GRY}Contoh:{R}")
    print(f"  hydra -l admin -P pass.txt -f -t 4 ssh://192.168.1.10")
    print(f"  hydra -L users.txt -P pass.txt -f -t 16 {CYN}192.168.1.10 http-post-form{R}"
          f"{CYN}\"/dvwa/login.php:username=^USER^&password=^PASS^:Login failed\"{R}")
    print()
    raw = ask('Perintah (awali "hydra" atau tidak)')
    if not raw:
        return
    if not raw.lower().startswith("hydra"):
        raw = "hydra " + raw
    try:
        cmd = shlex.split(raw, posix=(os.name != "nt"))
    except ValueError as e:
        print(f"{RED}❌ perintah tidak valid: {e}{R}"); pause(); return
    run_command(cmd, raw=True)


# ---------------- menu ----------------
def pause():
    try:
        input(f"\n{GRY}Tekan Enter untuk kembali...{R}")
    except (EOFError, KeyboardInterrupt):
        print()

def check_hydra():
    path = shutil.which("hydra")
    hr()
    if path:
        print(f"  {GRN}✅ hydra ditemukan:{R} {path}")
        try:
            out = subprocess.run([path, "-h"], capture_output=True, text=True, timeout=10)
            ver = [l for l in (out.stdout + out.stderr).splitlines() if "Hydra" in l]
            if ver:
                print(f"  {GRN}{ver[0].strip()}{R}")
        except Exception:
            pass
    else:
        print(f"  {RED}❌ hydra TIDAK ditemukan di PATH{R}")
        print(f"  Linux  : {YEL}sudo apt install hydra{R}")
        print(f"  Windows: compile dari {YEL}github.com/vanhauser-thc/thc-hydra{R}")
    hr()
    pause()

def main():
    ap = argparse.ArgumentParser(description="HydroDah CLI v3 — hydra terminal dashboard")
    ap.add_argument("-p", "--port", type=int, default=0,
                    help="(tidak dipakai, kompatibilitas versi lama)")
    args = ap.parse_args()

    while True:
        clear(); banner()
        hydra_path = shutil.which("hydra")
        status = (f"{GRN} hydra OK{R}" if hydra_path else f"{RED}❌ hydra tidak ada{R}")
        print(f"\n  Status : {status}")
        print(f"  Folder : {GRY}{DL_DIR}{R}")
        print(f"""
  {GRY}1{R}.  Mode Sederhana        (wizard cepat: modul+target+user+pass)
  {GRY}2{R}.  Mode Lanjutan         (semua opsi CLI hydra: -l -L -p -P -C -x -e -M ...)
  {GRY}3{R}.  Perintah Mentah        (ketik command hydra apa adanya)
  {GRY}4{R}.  Cek Instalasi Hydra
  {GRY}0{R}.  Keluar
        """)
        try:
            choice = ask("Pilih menu", "1")
        except (EOFError, KeyboardInterrupt):
            print(); break
        if choice == "1":
            wizard_simple()
        elif choice == "2":
            wizard_adv()
        elif choice == "3":
            wizard_raw()
        elif choice == "4":
            check_hydra()
        elif choice == "0":
            print(f"\n{DIM}Sampai jumpa.{R}\n")
            break
        else:
            print(f"{YEL}Pilihan tidak dikenal.{R}"); pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{DIM}Keluar (Ctrl+C).{R}")
        sys.exit(0)