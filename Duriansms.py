# Duriansms.py - Complete Bot with Multiple OTP Check & No Popup Alerts

import requests
import time
import json
import threading
import re
import os
from datetime import datetime

BOT_TOKEN = "8666173297:AAEBcbVPdUdXmLt8ZvCyIWzmhfg-OU8eM0c"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ============= টেলিগ্রাম ব্যাকআপ গ্রুপ কনফিগারেশন =============
BACKUP_GROUP_ID = -1003713267585
BACKUP_FILE_IDS = {}

# ============= অ্যাডমিন কনফিগারেশন =============
ADMIN_IDS = [948283424, -1003713267585]
ADMIN_PASSWORD = "mamun1132"
ADMIN_USERNAME = "rana1132"
CHANNEL_LINK = "https://t.me/updaterange"

# ============= ফাইল নাম =============
ACCESS_FILE = "user_access.json"
POINTS_FILE = "user_points.json"
CONFIG_FILE = "users_data.json"
STATS_FILE = "user_stats.json"

# ============= ডিফল্ট কনফিগারেশন =============
DEFAULT_CONFIG = {
    "username": "Aman2022",
    "api_key": "S2E1cklMWXJBSXM2ODZFaWI5OW5lQT09",
    "base_url": "https://api.durianrcs.com/out/ext_api"
}

# ============= পয়েন্ট সিস্টেম =============
DEFAULT_POINTS = 0
OTP_COST = 100

# ============= স্ট্যাটিস্টিক্স ডিফল্ট =============
DEFAULT_STATS = {
    "total_users_started": 0,
    "total_numbers_used": 0,
    "total_otp_received": 0,
    "total_points_used": 0,
    "user_numbers": {},
    "user_otp": {},
    "user_started": [],
    "daily_activity": {},
    "country_usage": {}
}

# ============= স্ট্যাটিস্টিক্স ফাংশন =============

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_STATS.copy()
    return DEFAULT_STATS.copy()

def save_stats(stats_data):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats_data, f, indent=2)
        save_backup_to_group(STATS_FILE, stats_data)
    except:
        pass

def update_stats_user_started(user_id):
    stats = load_stats()
    user_id_str = str(user_id)
    if user_id_str not in stats["user_started"]:
        stats["user_started"].append(user_id_str)
        stats["total_users_started"] = len(stats["user_started"])
        save_stats(stats)
        print(f"📊 New user started: {user_id} (Total: {stats['total_users_started']})")

def update_stats_number_used(user_id, country_name):
    stats = load_stats()
    user_id_str = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    stats["user_numbers"][user_id_str] = stats["user_numbers"].get(user_id_str, 0) + 1
    stats["total_numbers_used"] += 1
    if country_name:
        stats["country_usage"][country_name] = stats["country_usage"].get(country_name, 0) + 1
    if today not in stats["daily_activity"]:
        stats["daily_activity"][today] = {"numbers": 0, "otp": 0}
    stats["daily_activity"][today]["numbers"] += 1
    save_stats(stats)

def update_stats_otp_received(user_id):
    stats = load_stats()
    user_id_str = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    stats["user_otp"][user_id_str] = stats["user_otp"].get(user_id_str, 0) + 1
    stats["total_otp_received"] += 1
    stats["total_points_used"] += OTP_COST
    if today not in stats["daily_activity"]:
        stats["daily_activity"][today] = {"numbers": 0, "otp": 0}
    stats["daily_activity"][today]["otp"] += 1
    save_stats(stats)

def get_statistics_text(chat_id=None, is_admin=False):
    stats = load_stats()
    auth_users = get_all_authorized_users()
    
    if is_admin:
        total_users = stats.get("total_users_started", 0)
        authorized_count = len(auth_users)
        pending = total_users - authorized_count if total_users > authorized_count else 0
        
        user_otp = stats.get("user_otp", {})
        top_users = sorted(user_otp.items(), key=lambda x: x[1], reverse=True)[:5]
        top_users_text = ""
        for i, (uid, otp) in enumerate(top_users, 1):
            user_numbers = stats.get("user_numbers", {}).get(uid, 0)
            top_users_text += f"{i}. User {uid} - {otp} OTPs, {user_numbers} numbers\n"
        
        today = datetime.now().strftime("%Y-%m-%d")
        daily_activity = stats.get("daily_activity", {})
        today_activity = daily_activity.get(today, {"numbers": 0, "otp": 0})
        
        country_usage = stats.get("country_usage", {})
        top_countries = sorted(country_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        countries_text = ""
        for country, count in top_countries:
            countries_text += f"• {country}: {count} numbers\n"
        
        text = f"""📊 <b>Bot Statistics (Admin View)</b>

╭─────────────────────────────────────╮
│ 📈 <b>Overview</b>                    │
│ • Total Users Started: {total_users}          │
│ • Authorized Users: {authorized_count}        │
│ • Pending Access: {pending}                   │
│ • Total Numbers Used: {stats.get('total_numbers_used', 0)}        │
│ • Total OTP Received: {stats.get('total_otp_received', 0)}        │
│ • Total Points Used: {stats.get('total_points_used', 0)}          │
╰─────────────────────────────────────╯

╭─────────────────────────────────────╮
│ 🏆 <b>Top Users (by OTP)</b>          │
{top_users_text if top_users_text else '• No data yet'}
╰─────────────────────────────────────╯

╭─────────────────────────────────────╮
│ 📅 <b>Today's Activity</b>            │
│ • Numbers Used: {today_activity.get('numbers', 0)}        │
│ • OTP Received: {today_activity.get('otp', 0)}            │
╰─────────────────────────────────────╯

╭─────────────────────────────────────╮
│ 🌍 <b>Country Usage</b>               │
{countries_text if countries_text else '• No data yet'}
╰─────────────────────────────────────╯

🆘 <b>Support:</b> @{ADMIN_USERNAME}"""
    else:
        user_id_str = str(chat_id) if chat_id else "unknown"
        user_numbers = stats.get("user_numbers", {}).get(user_id_str, 0)
        user_otp = stats.get("user_otp", {}).get(user_id_str, 0)
        
        text = f"""📊 <b>Your Statistics</b>

╭─────────────────────────────────────╮
│ 📱 <b>Your Usage</b>                  │
│ • Numbers Used: {user_numbers}               │
│ • OTP Received: {user_otp}                  │
│ • Points Used: {user_otp * OTP_COST}               │
╰─────────────────────────────────────╯

╭─────────────────────────────────────╮
│ 📈 <b>Global Stats</b>                │
│ • Total Users: {stats.get('total_users_started', 0)}         │
│ • Total Numbers: {stats.get('total_numbers_used', 0)}        │
│ • Total OTPs: {stats.get('total_otp_received', 0)}           │
╰─────────────────────────────────────╯

🆘 <b>Support:</b> @{ADMIN_USERNAME}"""
    
    return text

# ============= টেলিগ্রাম গ্রুপ ব্যাকআপ ফাংশন =============

def get_backup_message_ids():
    global BACKUP_FILE_IDS
    try:
        r = requests.get(TG_API + "getUpdates", params={
            "chat_id": BACKUP_GROUP_ID,
            "limit": 100
        }, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    if "message" in update:
                        msg = update["message"]
                        text = msg.get("text", "")
                        msg_id = msg["message_id"]
                        
                        if "user_access.json" in text:
                            BACKUP_FILE_IDS["user_access"] = msg_id
                        elif "user_points.json" in text:
                            BACKUP_FILE_IDS["user_points"] = msg_id
                        elif "users_data.json" in text:
                            BACKUP_FILE_IDS["users_data"] = msg_id
                        elif "user_stats.json" in text:
                            BACKUP_FILE_IDS["user_stats"] = msg_id
    except Exception as e:
        print(f"Get backup IDs error: {e}")

def restore_from_telegram_backup():
    print("🔄 Checking for backups in Telegram group...")
    
    try:
        get_backup_message_ids()
        
        restored = False
        
        for file_key, msg_id in BACKUP_FILE_IDS.items():
            try:
                r = requests.get(TG_API + "getUpdates", params={
                    "chat_id": BACKUP_GROUP_ID,
                    "limit": 100
                }, timeout=10)
                
                if r.status_code == 200:
                    data = r.json()
                    if data.get("ok") and data.get("result"):
                        for update in data["result"]:
                            if "message" in update and update["message"]["message_id"] == msg_id:
                                text = update["message"].get("text", "")
                                json_part = text.split("\n", 1)[1] if "\n" in text else text
                                json_part = json_part.replace("```json", "").replace("```", "").strip()
                                data_content = json.loads(json_part)
                                
                                if file_key == "user_access":
                                    with open(ACCESS_FILE, 'w') as f:
                                        json.dump(data_content, f, indent=2)
                                    print(f"✅ Restored {ACCESS_FILE} from backup")
                                elif file_key == "user_points":
                                    with open(POINTS_FILE, 'w') as f:
                                        json.dump(data_content, f, indent=2)
                                    print(f"✅ Restored {POINTS_FILE} from backup")
                                elif file_key == "users_data":
                                    with open(CONFIG_FILE, 'w') as f:
                                        json.dump(data_content, f, indent=2)
                                    print(f"✅ Restored {CONFIG_FILE} from backup")
                                elif file_key == "user_stats":
                                    with open(STATS_FILE, 'w') as f:
                                        json.dump(data_content, f, indent=2)
                                    print(f"✅ Restored {STATS_FILE} from backup")
                                restored = True
                                break
            except Exception as e:
                print(f"Restore error for {file_key}: {e}")
        
        if not restored:
            print("⚠️ No backup files found, creating fresh files")
            if not os.path.exists(ACCESS_FILE):
                with open(ACCESS_FILE, 'w') as f:
                    json.dump({"authorized_users": []}, f, indent=2)
            if not os.path.exists(POINTS_FILE):
                with open(POINTS_FILE, 'w') as f:
                    json.dump({}, f, indent=2)
            if not os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'w') as f:
                    json.dump({}, f, indent=2)
            if not os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'w') as f:
                    json.dump(DEFAULT_STATS, f, indent=2)
        else:
            print("✅ Backup restore completed!")
            
    except Exception as e:
        print(f"Restore error: {e}")

def save_backup_to_group(filename, data):
    try:
        get_backup_message_ids()
        
        text = f"📁 {filename}\n{json.dumps(data, indent=2, ensure_ascii=False)}"
        if len(text) > 4096:
            text = f"📁 {filename}\n{json.dumps(data, indent=2, ensure_ascii=False)[:3500]}\n... (truncated)"
        
        file_key = filename.replace(".json", "")
        
        if file_key in BACKUP_FILE_IDS and BACKUP_FILE_IDS[file_key]:
            try:
                r = requests.post(TG_API + "editMessageText", json={
                    "chat_id": BACKUP_GROUP_ID,
                    "message_id": BACKUP_FILE_IDS[file_key],
                    "text": text
                }, timeout=10)
                if r.status_code == 200:
                    print(f"✅ Updated backup: {filename}")
                    return True
            except:
                pass
        
        r = requests.post(TG_API + "sendMessage", json={
            "chat_id": BACKUP_GROUP_ID,
            "text": text
        }, timeout=10)
        
        if r.status_code == 200:
            print(f"✅ New backup sent: {filename}")
            return True
        else:
            print(f"❌ Backup failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"Backup error: {e}")
        return False

def backup_all_data():
    if os.path.exists(ACCESS_FILE):
        with open(ACCESS_FILE, 'r') as f:
            save_backup_to_group(ACCESS_FILE, json.load(f))
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            save_backup_to_group(POINTS_FILE, json.load(f))
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            save_backup_to_group(CONFIG_FILE, json.load(f))
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            save_backup_to_group(STATS_FILE, json.load(f))

# ============= ইউজার এক্সেস ম্যানেজমেন্ট =============

def load_access():
    if os.path.exists(ACCESS_FILE):
        try:
            with open(ACCESS_FILE, 'r') as f:
                data = json.load(f)
                if "authorized_users" not in data:
                    data = {"authorized_users": []}
                return data
        except:
            return {"authorized_users": []}
    return {"authorized_users": []}

def save_access(access_data):
    try:
        with open(ACCESS_FILE, 'w') as f:
            json.dump(access_data, f, indent=2)
        save_backup_to_group(ACCESS_FILE, access_data)
    except:
        pass

def is_authorized(user_id):
    if user_id in ADMIN_IDS:
        return True
    access_data = load_access()
    authorized = access_data.get("authorized_users", [])
    return user_id in authorized

def add_user_access(user_id):
    access_data = load_access()
    if "authorized_users" not in access_data:
        access_data["authorized_users"] = []
    if user_id not in access_data["authorized_users"]:
        access_data["authorized_users"].append(user_id)
        save_access(access_data)
        print(f"✅ User {user_id} added to authorized list")
        return True
    return False

def remove_user_access(user_id):
    access_data = load_access()
    if "authorized_users" not in access_data:
        access_data["authorized_users"] = []
    if user_id in access_data["authorized_users"]:
        access_data["authorized_users"].remove(user_id)
        save_access(access_data)
        print(f"✅ User {user_id} removed from authorized list")
        return True
    return False

def get_all_authorized_users():
    access_data = load_access()
    return access_data.get("authorized_users", [])

# ============= পয়েন্ট ম্যানেজমেন্ট =============

def load_points():
    if os.path.exists(POINTS_FILE):
        try:
            with open(POINTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_points(points_data):
    try:
        with open(POINTS_FILE, 'w') as f:
            json.dump(points_data, f, indent=2)
        save_backup_to_group(POINTS_FILE, points_data)
    except:
        pass

def get_user_points(chat_id):
    points = load_points()
    return points.get(str(chat_id), 0)

def set_user_points(chat_id, points):
    points_data = load_points()
    points_data[str(chat_id)] = points
    save_points(points_data)

def add_user_points(chat_id, points):
    current = get_user_points(chat_id)
    set_user_points(chat_id, current + points)

def deduct_user_points(chat_id, points):
    current = get_user_points(chat_id)
    if current >= points:
        set_user_points(chat_id, current - points)
        return True
    return False

def has_sufficient_points(chat_id):
    return get_user_points(chat_id) >= OTP_COST

# ============= ইউজার কনফিগারেশন =============

def load_user_configs():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_configs(configs):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=2)
        save_backup_to_group(CONFIG_FILE, configs)
    except:
        pass

def get_user_config(chat_id):
    configs = load_user_configs()
    if str(chat_id) in configs:
        return configs[str(chat_id)]
    return DEFAULT_CONFIG.copy()

def set_user_config(chat_id, username, api_key, base_url=None):
    configs = load_user_configs()
    configs[str(chat_id)] = {
        "username": username,
        "api_key": api_key,
        "base_url": base_url or DEFAULT_CONFIG["base_url"]
    }
    save_user_configs(configs)
    return True

def remove_user_config(chat_id):
    configs = load_user_configs()
    if str(chat_id) in configs:
        del configs[str(chat_id)]
        save_user_configs(configs)
        return True
    return False

def get_all_user_configs():
    return load_user_configs()

def has_user_config(chat_id):
    configs = load_user_configs()
    return str(chat_id) in configs

# ============= API থেকে রিয়েল ব্যালেন্স আনার ফাংশন =============

def get_real_api_balance(username, api_key, base_url):
    try:
        url = f"{base_url}/getUserInfo"
        params = {"name": username, "ApiKey": api_key}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == 200:
                return data.get("data", {}).get("score", 0)
        return None
    except:
        return None

# ============= সব দেশের তালিকা =============
COUNTRIES = {
    "bangladesh": {"code": "+880", "name": "Bangladesh", "cuy": "bd", "flag": "🇧🇩"},
    "india": {"code": "+91", "name": "India", "cuy": "in", "flag": "🇮🇳"},
    "usa": {"code": "+1", "name": "USA", "cuy": "us", "flag": "🇺🇸"},
    "uk": {"code": "+44", "name": "United Kingdom", "cuy": "uk", "flag": "🇬🇧"},
    "canada": {"code": "+1", "name": "Canada", "cuy": "ca", "flag": "🇨🇦"},
    "australia": {"code": "+61", "name": "Australia", "cuy": "au", "flag": "🇦🇺"},
    "germany": {"code": "+49", "name": "Germany", "cuy": "de", "flag": "🇩🇪"},
    "france": {"code": "+33", "name": "France", "cuy": "fr", "flag": "🇫🇷"},
    "italy": {"code": "+39", "name": "Italy", "cuy": "it", "flag": "🇮🇹"},
    "spain": {"code": "+34", "name": "Spain", "cuy": "es", "flag": "🇪🇸"},
    "turkey": {"code": "+90", "name": "Turkey", "cuy": "tr", "flag": "🇹🇷"},
    "egypt": {"code": "+20", "name": "Egypt", "cuy": "eg", "flag": "🇪🇬"},
    "uae": {"code": "+971", "name": "UAE", "cuy": "ae", "flag": "🇦🇪"},
    "saudiarabia": {"code": "+966", "name": "Saudi Arabia", "cuy": "sa", "flag": "🇸🇦"},
    "thailand": {"code": "+66", "name": "Thailand", "cuy": "th", "flag": "🇹🇭"},
    "malaysia": {"code": "+60", "name": "Malaysia", "cuy": "my", "flag": "🇲🇾"},
    "indonesia": {"code": "+62", "name": "Indonesia", "cuy": "id", "flag": "🇮🇩"},
    "vietnam": {"code": "+84", "name": "Vietnam", "cuy": "vn", "flag": "🇻🇳"},
    "philippines": {"code": "+63", "name": "Philippines", "cuy": "ph", "flag": "🇵🇭"},
    "japan": {"code": "+81", "name": "Japan", "cuy": "jp", "flag": "🇯🇵"},
    "southkorea": {"code": "+82", "name": "South Korea", "cuy": "kr", "flag": "🇰🇷"},
    "russia": {"code": "+7", "name": "Russia", "cuy": "ru", "flag": "🇷🇺"},
    "brazil": {"code": "+55", "name": "Brazil", "cuy": "br", "flag": "🇧🇷"},
    "mexico": {"code": "+52", "name": "Mexico", "cuy": "mx", "flag": "🇲🇽"},
    "southafrica": {"code": "+27", "name": "South Africa", "cuy": "za", "flag": "🇿🇦"},
    "nigeria": {"code": "+234", "name": "Nigeria", "cuy": "ng", "flag": "🇳🇬"},
    "kenya": {"code": "+254", "name": "Kenya", "cuy": "ke", "flag": "🇰🇪"},
    "ghana": {"code": "+233", "name": "Ghana", "cuy": "gh", "flag": "🇬🇭"},
    "morocco": {"code": "+212", "name": "Morocco", "cuy": "ma", "flag": "🇲🇦"},
    "algeria": {"code": "+213", "name": "Algeria", "cuy": "dz", "flag": "🇩🇿"},
}

# ============= গ্লোবাল ভেরিয়েবল =============
user_data = {}
running_watches = {}
sent_numbers = {}
country_threads = {}
admin_session = {}

# ============= কিবোর্ড =============

MAIN_KEYBOARD = {
    "keyboard": [
        ["🚀 Start Watch", "🛑 Stop Watch"],
        ["📱 Single Number", "🌍 Set Single Country"],
        ["➕ Add Countries", "📋 Selected Countries"],
        ["❌ Remove Countries", "💰 Balance"],
        ["📊 Statistics", "🔄 Switch Project"],
        ["⚙️ Help", "👑 Admin Panel"]
    ],
    "resize_keyboard": True
}

ADMIN_KEYBOARD = {
    "keyboard": [
        ["➕ Add Country to Bot", "📋 All Countries"],
        ["👤 User Access Management"],
        ["📁 User Config Management"],
        ["💰 Points Management"],
        ["📊 Statistics", "🔙 Main Menu"]
    ],
    "resize_keyboard": True
}

USER_ACCESS_KEYBOARD = {
    "keyboard": [
        ["👤 Add User Access", "📋 User Access List"],
        ["🗑️ Remove User Access", "🔙 Admin Panel"]
    ],
    "resize_keyboard": True
}

USER_CONFIG_KEYBOARD = {
    "keyboard": [
        ["⚙️ Add/Edit User Config", "📋 All User Configs"],
        ["🗑️ Remove User Config", "🔙 Admin Panel"]
    ],
    "resize_keyboard": True
}

POINTS_KEYBOARD = {
    "keyboard": [
        ["➕ Add Points", "➖ Remove Points"],
        ["📋 All Users Points", "🔙 Admin Panel"]
    ],
    "resize_keyboard": True
}

WELCOME_BUTTON = {
    "inline_keyboard": [
        [
            {"text": "📢 Join Channel", "url": "https://t.me/updaterange"},
            {"text": "👤 Contact Admin", "url": "https://t.me/rana1132"}
        ]
    ]
}

def get_inline_buttons(phone, country_name, flag):
    return {
        "inline_keyboard": [[
            {"text": "✅ Get OTP", "callback_data": f"get_otp_{phone}"},
            {"text": "🚫 Block", "callback_data": f"block_{phone}"},
            {"text": "❌ Cancel", "callback_data": f"cancel_{phone}"}
        ]]
    }

# ============= সেন্ড মেসেজ ফাংশন =============

def send_msg(chat_id, text, kb=None, reply_markup=None):
    if chat_id == BACKUP_GROUP_ID:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if kb:
            data["reply_markup"] = json.dumps(kb)
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            return requests.post(TG_API + "sendMessage", json=data, timeout=10).json()
        except:
            return None
    
    if "Welcome to Durian World Bot" in text or "Join Now My Channel" in text:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if kb:
            data["reply_markup"] = json.dumps(kb)
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            return requests.post(TG_API + "sendMessage", json=data, timeout=10).json()
        except:
            return None
    
    if not is_authorized(chat_id) and chat_id not in ADMIN_IDS:
        return None
    
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if kb:
        data["reply_markup"] = json.dumps(kb)
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        return requests.post(TG_API + "sendMessage", json=data, timeout=10).json()
    except Exception as e:
        print(f"Send error: {e}")
        return None

def edit_message(chat_id, msg_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        return requests.post(TG_API + "editMessageText", json=data, timeout=10).json()
    except:
        return None

def delete_message(chat_id, msg_id):
    data = {"chat_id": chat_id, "message_id": msg_id}
    try:
        return requests.post(TG_API + "deleteMessage", json=data, timeout=10).json()
    except:
        return None

def answer_callback(callback_id, text, alert=False):
    data = {"callback_query_id": callback_id, "text": text, "show_alert": alert}
    try:
        requests.post(TG_API + "answerCallbackQuery", json=data, timeout=10)
    except:
        pass

def get_updates(offset=0):
    try:
        r = requests.get(TG_API + "getUpdates", params={"offset": offset, "timeout": 15}, timeout=20)
        return r.json().get("result", [])
    except:
        return []

def find_country(text):
    text_lower = text.lower().strip()
    for key, c in COUNTRIES.items():
        if c['name'].lower() == text_lower or key == text_lower or c['code'] == text:
            return c
        if text_lower in c['name'].lower():
            return c
    return None

def add_new_country(code, name, cuy, flag):
    key = name.lower().replace(" ", "")
    COUNTRIES[key] = {
        "code": code,
        "name": name,
        "cuy": cuy,
        "flag": flag
    }
    return True

def parse_countries_input(input_text):
    input_text = input_text.replace(",", " ")
    parts = input_text.split()
    found, not_found = [], []
    for p in parts:
        country = find_country(p)
        if country:
            found.append(country['name'])
        else:
            not_found.append(p)
    return found, not_found

def extract_country_from_number(phone, config):
    for country in COUNTRIES.values():
        if phone.startswith(country['code']):
            return country
    return None

def get_number_once(cuy, pid, config):
    url = f"{config['base_url']}/getMobile"
    params = {"name": config['username'], "ApiKey": config['api_key'], "pid": pid, "cuy": cuy, "num": "1", "noblack": "0", "serial": "2"}
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == 200:
                d = data.get("data")
                phone = d[0] if isinstance(d, list) else (d if isinstance(d, str) else (list(d.keys())[0] if isinstance(d, dict) else None))
                if phone:
                    actual = extract_country_from_number(phone, config)
                    if actual and actual['cuy'] == cuy:
                        return {"ok": True, "num": phone}
                    else:
                        release(phone, pid, config)
                        return {"ok": False, "err": "wrong_country"}
            elif data.get("code") == 906:
                return {"ok": False, "err": "empty_list"}
            return {"ok": False, "err": data.get("msg")}
        return {"ok": False, "err": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def get_sms(phone, pid, config):
    url = f"{config['base_url']}/getMsg"
    params = {"name": config['username'], "ApiKey": config['api_key'], "pid": pid, "pn": phone, "serial": "2"}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == 200:
                return data.get("data")
    except:
        pass
    return None

def release(phone, pid, config):
    url = f"{config['base_url']}/passMobile"
    params = {"name": config['username'], "ApiKey": config['api_key'], "pid": pid, "pn": phone, "serial": "2"}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.status_code == 200
    except:
        return False

def add_to_blacklist(phone, pid, config):
    url = f"{config['base_url']}/addBlack"
    params = {"name": config['username'], "ApiKey": config['api_key'], "pid": pid, "pn": phone}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.status_code == 200
    except:
        return False

# ============= পার দেশ ওয়াচ থ্রেড =============

def country_watch_worker(chat_id, country_name, retry_msg_id):
    country = COUNTRIES.get(country_name.lower())
    if not country:
        return
    
    config = get_user_config(chat_id)
    pid = user_data.get(chat_id, {}).get("current_pid", "0257")
    attempt = 0
    
    while running_watches.get(chat_id, {}).get("active", False):
        attempt += 1
        edit_message(chat_id, retry_msg_id, f"🔄 Searching for {country['name']} {country['flag']}...\nAttempt #{attempt}\n⏳ Still trying...")
        
        res = get_number_once(country['cuy'], pid, config)
        
        if res.get('ok'):
            phone = res['num']
            
            if chat_id not in sent_numbers:
                sent_numbers[chat_id] = {}
            
            update_stats_number_used(chat_id, country['name'])
            
            msg_text = f"""<b>✅ New Number!</b>
<b>Number</b>    : <code>{phone}</code>
<b>Country</b>   : {country['name']} {country['flag']}
<b>Project</b>   : {'Telegram Default' if pid == '0257' else 'Telegram Extended'} ({pid})
<b>Attempts</b>  : {attempt}
<b>Status</b>    : Fresh ✅
<b>Code</b>      : Waiting ❌"""
            
            result = send_msg(chat_id, msg_text, reply_markup=get_inline_buttons(phone, country['name'], country['flag']))
            if result and 'result' in result:
                msg_id = result['result']['message_id']
                sent_numbers[chat_id][phone] = {
                    "country": country['name'],
                    "flag": country['flag'],
                    "pid": pid,
                    "msg_id": msg_id,
                    "otp_list": []  # OTP ইতিহাস রাখার জন্য
                }
            
            attempt = 0
            time.sleep(5)
            continue
        
        time.sleep(3)
    
    edit_message(chat_id, retry_msg_id, f"🛑 Stopped searching for {country['name']} {country['flag']}")
    if chat_id in country_threads and country_name in country_threads[chat_id]:
        del country_threads[chat_id][country_name]

def start_auto_watch(chat_id):
    if running_watches.get(chat_id, {}).get("active"):
        return False
    
    if not is_admin(chat_id):
        if not has_user_config(chat_id):
            if not has_sufficient_points(chat_id):
                send_msg(chat_id, f"❌ <b>Insufficient Balance!</b>\n\nYour balance: {get_user_points(chat_id)} points\nNeed: {OTP_COST} points per OTP\n\nContact admin to add points.", MAIN_KEYBOARD)
                return False
    
    countries = user_data.get(chat_id, {}).get("countries", [])
    if not countries:
        send_msg(chat_id, "❌ No countries selected!\nPress '➕ Add Countries' first.", MAIN_KEYBOARD)
        return False
    
    running_watches[chat_id] = {"active": True}
    country_threads[chat_id] = {}
    
    for country_name in countries:
        country = COUNTRIES.get(country_name.lower())
        if country:
            result = send_msg(chat_id, f"🔄 Searching for {country['name']} {country['flag']}...\nAttempt #0\n⏳ Continuous mode (will keep getting numbers)")
            if result and 'result' in result:
                retry_msg_id = result['result']['message_id']
                thread = threading.Thread(target=country_watch_worker, args=(chat_id, country_name, retry_msg_id), daemon=True)
                thread.start()
                country_threads[chat_id][country_name] = {"thread": thread, "msg_id": retry_msg_id}
    
    return True

def stop_auto_watch(chat_id):
    if chat_id in running_watches:
        running_watches[chat_id]["active"] = False
        return True
    return False

def is_admin(chat_id):
    return chat_id in ADMIN_IDS

# ============= ব্যাকআপ থ্রেড =============

def auto_backup_worker():
    while True:
        time.sleep(300)
        try:
            backup_all_data()
            print("✅ Auto backup completed")
        except Exception as e:
            print(f"Auto backup error: {e}")

def start_auto_backup():
    backup_thread = threading.Thread(target=auto_backup_worker, daemon=True)
    backup_thread.start()

# ============= মেইন লুপ =============

print("=" * 60)
print("🤖 Durian SMS Bot - Complete Edition with Multiple OTP Check")
print("=" * 60)
print(f"👤 Admin ID: {ADMIN_IDS}")
print(f"🔑 Admin Password: {ADMIN_PASSWORD}")
print(f"📁 Backup Group ID: {BACKUP_GROUP_ID}")
print(f"🌍 Total Countries: {len(COUNTRIES)}")
print(f"💰 OTP Cost: {OTP_COST} points")
print("=" * 60)

restore_from_telegram_backup()
current_users = get_all_authorized_users()
print(f"📋 Current authorized users: {current_users}")
start_auto_backup()

print("✅ Bot is running with multiple OTP check feature!")
print("📌 Get OTP button can be used multiple times for the same number")
print("=" * 60)

last = 0

while True:
    try:
        updates = get_updates(last + 1)
        for u in updates:
            last = u["update_id"]
            
            if "callback_query" in u:
                cb = u["callback_query"]
                cid = cb["message"]["chat"]["id"]
                msg_id = cb["message"]["message_id"]
                data = cb["data"]
                cb_id = cb["id"]
                
                print(f"🔘 Callback: {data}")
                
                if data.startswith("get_otp_"):
                    phone = data.replace("get_otp_", "")
                    answer_callback(cb_id, "🔍 Checking for OTP...", alert=False)
                    
                    config = get_user_config(cid)
                    pid = sent_numbers.get(cid, {}).get(phone, {}).get("pid", "0257")
                    country = sent_numbers.get(cid, {}).get(phone, {}).get("country", "Unknown")
                    flag = sent_numbers.get(cid, {}).get(phone, {}).get("flag", "")
                    
                    # OTP চেক করুন
                    otp = None
                    for i in range(12):
                        time.sleep(3)
                        otp = get_sms(phone, pid, config)
                        if otp:
                            break
                        edit_message(cid, msg_id, f"🔍 Checking for OTP... ({i+1}/12)\n📱 {phone}")
                    
                    if otp:
                        update_stats_otp_received(cid)
                        
                        # OTP ইতিহাসে যোগ করুন
                        if "otp_list" not in sent_numbers[cid].get(phone, {}):
                            sent_numbers[cid][phone]["otp_list"] = []
                        sent_numbers[cid][phone]["otp_list"].append(otp)
                        otp_count = len(sent_numbers[cid][phone]["otp_list"])
                        
                        # OTP ইতিহাস দেখানোর জন্য টেক্সট তৈরি করুন
                        otp_history = ""
                        for idx, old_otp in enumerate(sent_numbers[cid][phone]["otp_list"], 1):
                            otp_history += f"<b>OTP #{idx}</b>: <code>{old_otp}</code>\n"
                        
                        if not is_admin(cid):
                            if has_user_config(cid):
                                new_text = f"""<b>✅ SMS Received!</b>
<b>Number</b>: <code>{phone}</code>
<b>Country</b>: {country} {flag}
{otp_history}
<b>Points Used</b>: {OTP_COST * otp_count}
<b>Note</b>: Points deducted from your API panel"""
                                edit_message(cid, msg_id, new_text, reply_markup=get_inline_buttons(phone, country, flag))
                            else:
                                if has_sufficient_points(cid):
                                    deduct_user_points(cid, OTP_COST)
                                    new_text = f"""<b>✅ SMS Received!</b>
<b>Number</b>: <code>{phone}</code>
<b>Country</b>: {country} {flag}
{otp_history}
<b>Points Used</b>: {OTP_COST * otp_count}
<b>Remaining Balance</b>: {get_user_points(cid)}"""
                                    edit_message(cid, msg_id, new_text, reply_markup=get_inline_buttons(phone, country, flag))
                                else:
                                    new_text = f"""<b>✅ SMS Received!</b>
<b>Number</b>: <code>{phone}</code>
<b>Country</b>: {country} {flag}
{otp_history}
<b>Points Used</b>: 0 (Insufficient balance)"""
                                    edit_message(cid, msg_id, new_text, reply_markup=get_inline_buttons(phone, country, flag))
                        else:
                            new_text = f"""<b>✅ SMS Received!</b>
<b>Number</b>: <code>{phone}</code>
<b>Country</b>: {country} {flag}
{otp_history}"""
                            edit_message(cid, msg_id, new_text, reply_markup=get_inline_buttons(phone, country, flag))
                    else:
                        edit_message(cid, msg_id, f"❌ No OTP found after 12 attempts.\n📱 <code>{phone}</code>\n\nTry sending SMS again and click Get OTP.", reply_markup=get_inline_buttons(phone, country, flag))
                
                elif data.startswith("block_"):
                    phone = data.replace("block_", "")
                    config = get_user_config(cid)
                    pid = sent_numbers.get(cid, {}).get(phone, {}).get("pid", "0257")
                    add_to_blacklist(phone, pid, config)
                    release(phone, pid, config)
                    answer_callback(cb_id, f"✅ {phone} blocked", alert=False)
                    delete_message(cid, msg_id)
                    if cid in sent_numbers and phone in sent_numbers[cid]:
                        del sent_numbers[cid][phone]
                
                elif data.startswith("cancel_"):
                    phone = data.replace("cancel_", "")
                    config = get_user_config(cid)
                    pid = sent_numbers.get(cid, {}).get(phone, {}).get("pid", "0257")
                    release(phone, pid, config)
                    answer_callback(cb_id, f"✅ {phone} released", alert=False)
                    delete_message(cid, msg_id)
                    if cid in sent_numbers and phone in sent_numbers[cid]:
                        del sent_numbers[cid][phone]
                
                continue
            
            if "message" not in u:
                continue
            
            msg = u["message"]
            cid = msg["chat"]["id"]
            text = msg.get("text", "")
            
            print(f"📨 {cid}: {text}")
            
            if cid == BACKUP_GROUP_ID:
                continue
            
            if not is_authorized(cid) and cid not in ADMIN_IDS:
                if text == "/start":
                    update_stats_user_started(cid)
                    welcome_text = """✨ Welcome to Durian World Bot ✨

👉 Contact Now For Access - @Rana1132
✡️ Join Now My Channel - @updaterange"""
                    send_msg(cid, welcome_text, reply_markup=WELCOME_BUTTON)
                else:
                    send_msg(cid, f"❌ You are not authorized.\nContact: @{ADMIN_USERNAME}")
                continue
            
            if cid not in user_data:
                user_data[cid] = {"countries": [], "single_country": None, "current_pid": "0257"}
            if cid not in sent_numbers:
                sent_numbers[cid] = {}
            if cid not in country_threads:
                country_threads[cid] = {}
            
            # ============ অ্যাডমিন সেশন চেক ============
            
            if cid in admin_session and admin_session[cid].get("waiting"):
                waiting_for = admin_session[cid]["waiting"]
                
                if waiting_for == "password":
                    if text == ADMIN_PASSWORD:
                        admin_session[cid] = {"authenticated": True, "waiting": None}
                        send_msg(cid, "✅ <b>Authentication Successful!</b>\n\nWelcome to Admin Panel.", ADMIN_KEYBOARD)
                    else:
                        admin_session[cid] = {"waiting": None}
                        send_msg(cid, "❌ <b>Wrong Password!</b>\n\nAccess denied.", MAIN_KEYBOARD)
                    continue
                
                elif waiting_for == "add_country":
                    parts = text.split()
                    if len(parts) >= 3:
                        code = parts[0]
                        name = " ".join(parts[1:-2]) if len(parts) > 3 else parts[1]
                        cuy = parts[-2] if len(parts) >= 3 else parts[1][:2].lower()
                        flag = parts[-1] if len(parts) >= 3 else "🌍"
                        add_new_country(code, name, cuy, flag)
                        send_msg(cid, f"✅ Country added!\n\n{name} {flag}\nCode: {code}\nCUY: {cuy}", ADMIN_KEYBOARD)
                    else:
                        send_msg(cid, "❌ Invalid format!\n\nUse: +999 CountryName cu flag\nExample: +966 Saudi Arabia sa 🇸🇦", ADMIN_KEYBOARD)
                    admin_session[cid]["waiting"] = None
                    continue
                
                elif waiting_for == "add_user_access":
                    try:
                        target_id = int(text)
                        if add_user_access(target_id):
                            send_msg(cid, f"✅ User {target_id} has been granted access!", USER_ACCESS_KEYBOARD)
                        else:
                            send_msg(cid, f"⚠️ User {target_id} already has access!", USER_ACCESS_KEYBOARD)
                    except:
                        send_msg(cid, "❌ Invalid user ID! Use number only.", USER_ACCESS_KEYBOARD)
                    admin_session[cid]["waiting"] = None
                    continue
                
                elif waiting_for == "remove_user_access":
                    try:
                        target_id = int(text)
                        if remove_user_access(target_id):
                            send_msg(cid, f"✅ User {target_id} access has been revoked!", USER_ACCESS_KEYBOARD)
                        else:
                            send_msg(cid, f"⚠️ User {target_id} does not have access!", USER_ACCESS_KEYBOARD)
                    except:
                        send_msg(cid, "❌ Invalid user ID! Use number only.", USER_ACCESS_KEYBOARD)
                    admin_session[cid]["waiting"] = None
                    continue
                
                elif waiting_for == "add_user_config":
                    parts = text.split()
                    if len(parts) >= 3:
                        try:
                            target_id = int(parts[0])
                            username = parts[1]
                            api_key = parts[2]
                            base_url = parts[3] if len(parts) > 3 else None
                            set_user_config(target_id, username, api_key, base_url)
                            send_msg(cid, f"✅ User config added/updated!\n\nUser ID: {target_id}\nUsername: {username}\nAPI Key: {api_key[:15]}...\n\nUser will use their own API balance.", USER_CONFIG_KEYBOARD)
                        except:
                            send_msg(cid, "❌ Invalid format!", USER_CONFIG_KEYBOARD)
                    else:
                        send_msg(cid, "❌ Invalid format!\n\nUse: user_id username api_key\nExample: 123456789 Aman2022 xxxxx", USER_CONFIG_KEYBOARD)
                    admin_session[cid]["waiting"] = None
                    continue
                
                elif waiting_for == "remove_user_config":
                    try:
                        user_input = text.strip()
                        numbers = re.findall(r'\d+', user_input)
                        if numbers:
                            target_id = int(numbers[0])
                            if remove_user_config(target_id):
                                send_msg(cid, f"✅ User {target_id} config has been removed successfully!", USER_CONFIG_KEYBOARD)
                            else:
                                send_msg(cid, f"⚠️ User {target_id} config not found!", USER_CONFIG_KEYBOARD)
                        else:
                            send_msg(cid, "❌ No valid user ID found! Please enter a numeric user ID.\nExample: 123456789", USER_CONFIG_KEYBOARD)
                    except Exception as e:
                        send_msg(cid, f"❌ Error: {str(e)}\nPlease enter a valid user ID.\nExample: 123456789", USER_CONFIG_KEYBOARD)
                    admin_session[cid]["waiting"] = None
                    continue
                
                elif waiting_for == "add_points":
                    try:
                        parts = text.split()
                        if len(parts) >= 2:
                            target_id = int(parts[0])
                            points = int(parts[1])
                            add_user_points(target_id, points)
                            send_msg(cid, f"✅ Added {points} points to User {target_id}!\nNew balance: {get_user_points(target_id)}", POINTS_KEYBOARD)
                        else:
                            send_msg(cid, "❌ Invalid format!\n\nUse: user_id points\nExample: 123456789 50", POINTS_KEYBOARD)
                    except:
                        send_msg(cid, "❌ Invalid format!\n\nUse: user_id points\nExample: 123456789 50", POINTS_KEYBOARD)
                    admin_session[cid]["waiting"] = None
                    continue
                
                elif waiting_for == "remove_points":
                    try:
                        parts = text.split()
                        if len(parts) >= 2:
                            target_id = int(parts[0])
                            points = int(parts[1])
                            current = get_user_points(target_id)
                            if current >= points:
                                set_user_points(target_id, current - points)
                                send_msg(cid, f"✅ Removed {points} points from User {target_id}!\nNew balance: {get_user_points(target_id)}", POINTS_KEYBOARD)
                            else:
                                send_msg(cid, f"⚠️ User {target_id} has only {current} points!\nCannot remove {points} points.", POINTS_KEYBOARD)
                        else:
                            send_msg(cid, "❌ Invalid format!\n\nUse: user_id points\nExample: 123456789 20", POINTS_KEYBOARD)
                    except:
                        send_msg(cid, "❌ Invalid format!\n\nUse: user_id points\nExample: 123456789 20", POINTS_KEYBOARD)
                    admin_session[cid]["waiting"] = None
                    continue
            
            # ============ কমান্ড ============
            
            if text == "/start":
                update_stats_user_started(cid)
                if is_admin(cid):
                    send_msg(cid, "✅ Bot is ready! Use the buttons below.", MAIN_KEYBOARD)
                elif is_authorized(cid):
                    send_msg(cid, "✅ Bot is ready! Use the buttons below.", MAIN_KEYBOARD)
                else:
                    welcome_text = """✨ Welcome to Durian World Bot ✨

👉 Contact Now For Access - @Rana1132
✡️ Join Now My Channel - @updaterange"""
                    send_msg(cid, welcome_text, reply_markup=WELCOME_BUTTON)
            
            elif text == "/admin" or text == "👑 Admin Panel":
                if is_admin(cid):
                    admin_session[cid] = {"waiting": "password"}
                    send_msg(cid, "🔐 <b>Admin Authentication Required</b>\n\nPlease enter the admin password:", MAIN_KEYBOARD)
                else:
                    send_msg(cid, "❌ You are not authorized to access Admin Panel.", MAIN_KEYBOARD)
            
            elif text == "💰 Balance":
                if is_admin(cid):
                    config = DEFAULT_CONFIG
                    balance = get_real_api_balance(config['username'], config['api_key'], config['base_url'])
                    if balance is not None:
                        send_msg(cid, f"💰 <b>Your Balance (Admin)</b>\n\n👤 Account: {config['username']}\n💎 Points: <code>{balance}</code>\n💸 Cost per OTP: <code>{OTP_COST}</code> points\n\nYou can get {balance // OTP_COST} more OTPs.", MAIN_KEYBOARD)
                    else:
                        send_msg(cid, f"💰 <b>Your Balance</b>\n\n❌ Could not fetch balance.\n💸 Cost per OTP: <code>{OTP_COST}</code> points", MAIN_KEYBOARD)
                elif has_user_config(cid):
                    config = get_user_config(cid)
                    balance = get_real_api_balance(config['username'], config['api_key'], config['base_url'])
                    if balance is not None:
                        if balance == 0:
                            send_msg(cid, f"💰 <b>Your Balance (from your API Panel)</b>\n\n💎 Points: <code>{balance}</code>\n💸 Cost per OTP: <code>{OTP_COST}</code> points\n\n⚠️ Your balance is 0!\n\n🔸 Recharge yourself: Login to your API panel\n🔸 Contact admin: @{ADMIN_USERNAME}", MAIN_KEYBOARD)
                        else:
                            send_msg(cid, f"💰 <b>Your Balance (from your API Panel)</b>\n\n💎 Points: <code>{balance}</code>\n💸 Cost per OTP: <code>{OTP_COST}</code> points\n\nYou can get {balance // OTP_COST} more OTPs.", MAIN_KEYBOARD)
                    else:
                        send_msg(cid, f"💰 <b>Your Balance</b>\n\n❌ Could not fetch balance. Please check your API configuration.\n💸 Cost per OTP: <code>{OTP_COST}</code> points", MAIN_KEYBOARD)
                else:
                    points = get_user_points(cid)
                    send_msg(cid, f"💰 <b>Your Balance</b>\n\n💎 Points: <code>{points}</code>\n💸 Cost per OTP: <code>{OTP_COST}</code> points\n\nYou can get {points // OTP_COST} more OTPs.", MAIN_KEYBOARD)
            
            elif text == "📊 Statistics":
                stats_text = get_statistics_text(cid, is_admin(cid))
                send_msg(cid, stats_text, MAIN_KEYBOARD)
            
            elif text == "➕ Add Country to Bot" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "➕ <b>Add New Country</b>\n\nFormat: <code>+999 CountryName cu flag</code>\n\n<b>Example:</b>\n<code>+966 Saudi Arabia sa 🇸🇦</code>\n<code>+962 Jordan jo 🇯🇴</code>\n\nEnter country details:", ADMIN_KEYBOARD)
                    admin_session[cid]["waiting"] = "add_country"
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "📋 All Countries" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    country_list = "\n".join([f"{c['flag']} {c['name']} ({c['code']}) - cuy: {c['cuy']}" for c in COUNTRIES.values()][:30])
                    total = len(COUNTRIES)
                    send_msg(cid, f"📋 <b>All Countries ({total})</b>\n\n{country_list}\n\n...and {total - 30} more countries.", ADMIN_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "👤 User Access Management" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "👤 <b>User Access Management</b>\n\nManage user permissions:", USER_ACCESS_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "👤 Add User Access" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "👤 <b>Add User Access</b>\n\nEnter user ID to grant access:\n\nExample: <code>123456789</code>\n\nUser will get 0 points initially.\nUse 'Points Management' to add points.", USER_ACCESS_KEYBOARD)
                    admin_session[cid]["waiting"] = "add_user_access"
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "📋 User Access List" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    users = get_all_authorized_users()
                    if users:
                        user_list = "\n".join([f"• {uid}" for uid in users])
                        send_msg(cid, f"📋 <b>Authorized Users ({len(users)})</b>\n\n{user_list}", USER_ACCESS_KEYBOARD)
                    else:
                        send_msg(cid, "📋 No authorized users yet.\n\nUse 'Add User Access' to add users.", USER_ACCESS_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "🗑️ Remove User Access" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "🗑️ <b>Remove User Access</b>\n\nEnter user ID to revoke access:\n\nExample: <code>123456789</code>", USER_ACCESS_KEYBOARD)
                    admin_session[cid]["waiting"] = "remove_user_access"
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "📁 User Config Management" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "📁 <b>User Config Management</b>\n\nManage user API configurations:", USER_CONFIG_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "⚙️ Add/Edit User Config" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "⚙️ <b>Add/Edit User Config</b>\n\nFormat: <code>user_id username api_key</code>\n\n<b>Example:</b>\n<code>123456789 Aman2022 S2E1cklMWXJBSXM2ODZFaWI5OW5lQT09</code>\n\nEnter user details:\n\n⚠️ Users added here will use their OWN API balance.", USER_CONFIG_KEYBOARD)
                    admin_session[cid]["waiting"] = "add_user_config"
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "🗑️ Remove User Config" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "🗑️ <b>Remove User Config</b>\n\nEnter user ID to remove config:\n\nExample: <code>123456789</code>", USER_CONFIG_KEYBOARD)
                    admin_session[cid]["waiting"] = "remove_user_config"
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "📋 All User Configs" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    configs = get_all_user_configs()
                    if configs:
                        config_list = "\n".join([f"• {uid}: {cfg['username']} - {cfg['api_key'][:15]}..." for uid, cfg in configs.items()])
                        send_msg(cid, f"📋 <b>All User Configs ({len(configs)})</b>\n\n{config_list}\n\n⚠️ These users use their OWN API balance.", USER_CONFIG_KEYBOARD)
                    else:
                        send_msg(cid, "📋 No user configs found.\n\nUse 'Add/Edit User Config' to add.", USER_CONFIG_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "💰 Points Management" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "💰 <b>Points Management</b>\n\n⚠️ This is for User Access Management users only.\nUsers with their own API config use their own balance.", POINTS_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "➕ Add Points" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "➕ <b>Add Points</b>\n\nFormat: <code>user_id points</code>\n\n<b>Example:</b>\n<code>123456789 500</code>\n\n⚠️ This adds points to User Access Management users only.", POINTS_KEYBOARD)
                    admin_session[cid]["waiting"] = "add_points"
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "➖ Remove Points" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "➖ <b>Remove Points</b>\n\nFormat: <code>user_id points</code>\n\n<b>Example:</b>\n<code>123456789 20</code>\n\n⚠️ This removes points from User Access Management users only.", POINTS_KEYBOARD)
                    admin_session[cid]["waiting"] = "remove_points"
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "📋 All Users Points" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    points_data = load_points()
                    if points_data:
                        points_list = "\n".join([f"• {uid}: {points} points" for uid, points in points_data.items()])
                        send_msg(cid, f"📋 <b>All Users Points</b>\n\n{points_list}\n\n⚠️ This shows only User Access Management users.", POINTS_KEYBOARD)
                    else:
                        send_msg(cid, "📋 No points data found.", POINTS_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "🔙 Admin Panel" and is_admin(cid):
                if admin_session.get(cid, {}).get("authenticated"):
                    send_msg(cid, "🔙 Back to Admin Panel:", ADMIN_KEYBOARD)
                else:
                    send_msg(cid, "❌ Please authenticate first.\nType /admin", MAIN_KEYBOARD)
            
            elif text == "🔙 Main Menu" and is_admin(cid):
                admin_session[cid] = {"authenticated": True, "waiting": None}
                send_msg(cid, "🔙 Back to main menu:", MAIN_KEYBOARD)
            
            # ============ ইউজার কমান্ড ============
            
            elif text == "➕ Add Countries":
                if not is_admin(cid):
                    if not has_user_config(cid):
                        if not has_sufficient_points(cid):
                            send_msg(cid, f"❌ <b>Insufficient Balance!</b>\n\nYour balance: {get_user_points(cid)} points\nNeed at least {OTP_COST} points to use the bot.\n\nContact admin to add points.", MAIN_KEYBOARD)
                            continue
                country_list = ", ".join(list(COUNTRIES.keys())[:20])
                send_msg(cid, f"➕ <b>Add countries</b>\n\nFormat: <code>Bangladesh, India, USA</code>\nor <code>Bangladesh India USA</code>\n\n<b>Examples:</b>\n{country_list}...\n\nEnter country names:", MAIN_KEYBOARD)
                user_data[cid]['waiting'] = "add_multiple"
            
            elif text == "📋 Selected Countries":
                if user_data[cid]['countries']:
                    clist = "\n".join([f"• {c}" for c in user_data[cid]['countries']])
                    send_msg(cid, f"📋 <b>Your selected countries:</b>\n{clist}\n\n<b>Total:</b> {len(user_data[cid]['countries'])}", MAIN_KEYBOARD)
                else:
                    send_msg(cid, "📋 No countries selected.\nPress '➕ Add Countries' to add.", MAIN_KEYBOARD)
            
            elif text == "❌ Remove Countries":
                if user_data[cid]['countries']:
                    kb = {"keyboard": [[f"❌ {c}"] for c in user_data[cid]['countries']] + [["🔙 Main Menu"]], "resize_keyboard": True}
                    send_msg(cid, "❌ <b>Select country to remove:</b>", kb)
                    user_data[cid]['waiting'] = "remove_country"
                else:
                    send_msg(cid, "📋 No countries to remove.", MAIN_KEYBOARD)
            
            elif text == "🚀 Start Watch":
                if not is_admin(cid):
                    if not has_user_config(cid):
                        if not has_sufficient_points(cid):
                            send_msg(cid, f"❌ <b>Insufficient Balance!</b>\n\nYour balance: {get_user_points(cid)} points\nNeed: {OTP_COST} points per OTP\n\nContact admin to add points.", MAIN_KEYBOARD)
                            continue
                if not user_data[cid]['countries']:
                    send_msg(cid, "❌ No countries selected!\nPress '➕ Add Countries' first.", MAIN_KEYBOARD)
                else:
                    if start_auto_watch(cid):
                        clist = ", ".join(user_data[cid]['countries'])
                        if has_user_config(cid):
                            send_msg(cid, f"🚀 <b>Watch Started!</b>\n\n<b>Countries:</b> {clist}\n<b>Mode:</b> Continuous (Never stops)\n<b>Status:</b> Running ✅\n<b>Note:</b> Points will be deducted from your API panel\n\nAll countries searching simultaneously!\nPress '🛑 Stop Watch' to stop.", MAIN_KEYBOARD)
                        else:
                            if is_admin(cid):
                                send_msg(cid, f"🚀 <b>Watch Started!</b>\n\n<b>Countries:</b> {clist}\n<b>Mode:</b> Continuous (Never stops)\n<b>Status:</b> Running ✅\n(Admin: No points deducted)\n\nAll countries searching simultaneously!\nPress '🛑 Stop Watch' to stop.", MAIN_KEYBOARD)
                            else:
                                send_msg(cid, f"🚀 <b>Watch Started!</b>\n\n<b>Countries:</b> {clist}\n<b>Mode:</b> Continuous (Never stops)\n<b>Status:</b> Running ✅\n<b>Your Balance:</b> {get_user_points(cid)} points\n\nAll countries searching simultaneously!\nPress '🛑 Stop Watch' to stop.", MAIN_KEYBOARD)
                    else:
                        send_msg(cid, "⚠️ Auto watch already running!", MAIN_KEYBOARD)
            
            elif text == "🛑 Stop Watch":
                if stop_auto_watch(cid):
                    send_msg(cid, "🛑 <b>Watch Stopped!</b>\n\nAll searches stopped.\nExisting numbers still active. Use Get OTP buttons.", MAIN_KEYBOARD)
                else:
                    send_msg(cid, "❌ No active watch to stop.", MAIN_KEYBOARD)
            
            elif text == "🔄 Switch Project":
                current = user_data[cid]['current_pid']
                kb = {"keyboard": [[f"{'✅ ' if current == '0257' else ''}📱 Project 0257 (Default)"], [f"{'✅ ' if current == '6003' else ''}🌍 Project 6003 (Extended)"], ["🔙 Main Menu"]], "resize_keyboard": True}
                send_msg(cid, f"🔄 <b>Switch Project</b>\n\n<b>Current:</b> {'Telegram Default' if current == '0257' else 'Telegram Extended'} ({current})\n\nSelect project:", kb)
                user_data[cid]['waiting'] = "switch_project"
            
            elif text == "📱 Single Number":
                if not is_admin(cid):
                    if not has_user_config(cid):
                        if not has_sufficient_points(cid):
                            send_msg(cid, f"❌ <b>Insufficient Balance!</b>\n\nYour balance: {get_user_points(cid)} points\nNeed: {OTP_COST} points\n\nContact admin to add points.", MAIN_KEYBOARD)
                            continue
                if user_data[cid]['single_country']:
                    country = find_country(user_data[cid]['single_country'])
                    if country:
                        config = get_user_config(cid)
                        send_msg(cid, f"⏳ Getting {country['name']} {country['flag']} number...")
                        pid = user_data[cid]['current_pid']
                        attempt = 0
                        while True:
                            attempt += 1
                            res = get_number_once(country['cuy'], pid, config)
                            if res.get('ok'):
                                phone = res['num']
                                update_stats_number_used(cid, country['name'])
                                msg_text = f"""<b>✅ New Number!</b>
<b>Number</b>: <code>{phone}</code>
<b>Country</b>: {country['name']} {country['flag']}
<b>Attempts</b>: {attempt}"""
                                result = send_msg(cid, msg_text, reply_markup=get_inline_buttons(phone, country['name'], country['flag']))
                                if result and 'result' in result:
                                    sent_numbers[cid][phone] = {
                                        "country": country['name'],
                                        "flag": country['flag'],
                                        "pid": pid,
                                        "msg_id": result['result']['message_id'],
                                        "otp_list": []
                                    }
                                break
                            time.sleep(3)
                    else:
                        send_msg(cid, "❌ Country not found!", MAIN_KEYBOARD)
                else:
                    send_msg(cid, "❌ No single country set!\nUse '🌍 Set Single Country' first.", MAIN_KEYBOARD)
            
            elif text == "🌍 Set Single Country":
                send_msg(cid, "🌍 <b>Set Single Country</b>\n\nType country name:\nExamples: Bangladesh, India, USA, UK, Germany", MAIN_KEYBOARD)
                user_data[cid]['waiting'] = "set_single"
            
            elif text == "📊 Report":
                active = "Yes ✅" if running_watches.get(cid, {}).get("active") else "No ❌"
                config = get_user_config(cid)
                if has_user_config(cid):
                    send_msg(cid, f"📊 <b>Report</b>\n\n👤 <b>Your Account:</b> {config['username']}\n📁 <b>Project:</b> {'Telegram Default' if user_data[cid]['current_pid'] == '0257' else 'Telegram Extended'} ({user_data[cid]['current_pid']})\n🎯 <b>Active Watch:</b> {active}\n🌍 <b>Selected Countries:</b> {len(user_data[cid]['countries'])}\n📱 <b>Numbers Received:</b> {len(sent_numbers.get(cid, {}))}\n💸 <b>Cost per OTP:</b> {OTP_COST} points (from your API panel)", MAIN_KEYBOARD)
                else:
                    points = get_user_points(cid)
                    send_msg(cid, f"📊 <b>Report</b>\n\n👤 <b>Your Account:</b> {config['username']}\n💰 <b>Balance:</b> {points} points\n📁 <b>Project:</b> {'Telegram Default' if user_data[cid]['current_pid'] == '0257' else 'Telegram Extended'} ({user_data[cid]['current_pid']})\n🎯 <b>Active Watch:</b> {active}\n🌍 <b>Selected Countries:</b> {len(user_data[cid]['countries'])}\n📱 <b>Numbers Received:</b> {len(sent_numbers.get(cid, {}))}", MAIN_KEYBOARD)
            
            elif text == "⚙️ Help":
                help_text = """Any Problem contact Now

👑 Admin: @rana1132
🆘 Support: @rana1132"""
                send_msg(cid, help_text, MAIN_KEYBOARD)
            
            elif text == "🔙 Main Menu":
                user_data[cid]['waiting'] = None
                send_msg(cid, "🔙 Main menu:", MAIN_KEYBOARD)
            
            elif text.startswith("📱 Project 0257") or text.startswith("✅ 📱 Project 0257"):
                user_data[cid]['current_pid'] = "0257"
                send_msg(cid, "✅ Switched to Project: Telegram Default (0257)", MAIN_KEYBOARD)
                user_data[cid]['waiting'] = None
            
            elif text.startswith("🌍 Project 6003") or text.startswith("✅ 🌍 Project 6003"):
                user_data[cid]['current_pid'] = "6003"
                send_msg(cid, "✅ Switched to Project: Telegram Extended (6003)", MAIN_KEYBOARD)
                user_data[cid]['waiting'] = None
            
            elif text.startswith("❌ ") and text != "❌ Remove Countries":
                cname = text.replace("❌ ", "")
                if cname in user_data[cid]['countries']:
                    user_data[cid]['countries'].remove(cname)
                    send_msg(cid, f"✅ {cname} removed from your list!", MAIN_KEYBOARD)
                user_data[cid]['waiting'] = None
            
            elif user_data[cid].get('waiting') == "add_multiple":
                found, not_found = parse_countries_input(text)
                if found:
                    for f in found:
                        if f not in user_data[cid]['countries']:
                            user_data[cid]['countries'].append(f)
                    msg = f"✅ <b>Countries Added</b>\n\n✅ Added: {', '.join(found)}\n"
                    if not_found:
                        msg += f"❌ Invalid: {', '.join(not_found)}\n"
                    msg += f"\n📊 Total: {len(user_data[cid]['countries'])}"
                    send_msg(cid, msg, MAIN_KEYBOARD)
                else:
                    send_msg(cid, f"❌ No valid countries found.\n\nTry: Bangladesh, India, USA, UK, Germany", MAIN_KEYBOARD)
                user_data[cid]['waiting'] = None
            
            elif user_data[cid].get('waiting') == "set_single":
                country = find_country(text)
                if country:
                    user_data[cid]['single_country'] = country['name']
                    send_msg(cid, f"✅ Single country set to: {country['name']} {country['flag']}", MAIN_KEYBOARD)
                else:
                    send_msg(cid, f"❌ '{text}' not found.\nTry: Bangladesh, India, USA", MAIN_KEYBOARD)
                user_data[cid]['waiting'] = None
            
            elif user_data[cid].get('waiting') == "switch_project":
                user_data[cid]['waiting'] = None
            
            elif user_data[cid].get('waiting') == "remove_country":
                user_data[cid]['waiting'] = None
            
            else:
                send_msg(cid, "❓ Please use the buttons below.", MAIN_KEYBOARD)
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        break
    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(5)