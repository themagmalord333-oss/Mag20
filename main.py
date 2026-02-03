import os
import asyncio
import json
from threading import Thread
from flask import Flask

from pyrogram import Client, filters, enums, idle
from pyrogram.errors import UserNotParticipant, UserAlreadyParticipant, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# ✅ NEW SESSION STRING (UPDATED)
SESSION_STRING = "BQI5Xz4AANa83p6zL0X6y2fP5eiMmu2yk9S-RAxCrgcrjGUZmMLhrbhMGyY1JJ7LdWIbEIEWymplxWx2kI2AgB10uVvXsovXavySVPt9heb_ViN6DBOkat12WVn0aciH2KJM0qyyfTZmC9QJlvxQwZZ9b6ncjFzMLEHF6cPgF4_xH9yN08S0s0t30bBo4CkjsRyHO-ImqryjeD0n9yiylcISTucBxQEpdInlDv80soVeF1KSlHj_KTd48fXlKJmhbXWdHdiN2bJKBAZzkFkT304UM4TN2PeztUW3wgnX6CMwz3GcWotmNuVJrFWKmN4I8U48tPmmhYvvPj6-deAlNekD2jwTrAAAAAFJSgVkAA"

# 🎯 TARGET SETTINGS (HIDDEN FROM USER)
TARGET_GROUP_LINK = "infobot_66"
TARGET_BOT_USERNAME = "Backupinfo69_bot"
FALLBACK_ID = -1003320004816 

# ✅ FOOTER (JSON ke Bahar)
NEW_FOOTER = "⚡ Designed & Powered by @MAGMAxRICH"

# --- 🔐 SECURITY SETTINGS ---
ALLOWED_GROUPS = [-1003387459132]
FSUB_CONFIG = [
    {"username": "Anysnapupdate", "link": "https://t.me/Anysnapupdate"},
    {"username": "Anysnapsupport", "link": "https://t.me/Anysnapsupport"}
]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- GLOBAL VARIABLE ---
RESOLVED_TARGET_ID = None 

# ==========================================
# 👇 FLASK SERVER
# ==========================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Database Server is Active."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# ==========================================

# --- HELPER FUNCTIONS ---
async def check_user_joined(client, user_id):
    missing = False
    for ch in FSUB_CONFIG:
        try:
            member = await client.get_chat_member(ch["username"], user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                missing = True
                break
        except UserNotParticipant:
            missing = True
            break
        except Exception:
            pass
    return not missing 

def get_fsub_buttons():
    buttons = []
    for ch in FSUB_CONFIG:
        buttons.append([InlineKeyboardButton(f"📢 Join {ch['username']}", url=ch['link'])])
    buttons.append([InlineKeyboardButton("✅ Check Subscription", callback_data="check_fsub")])
    return InlineKeyboardMarkup(buttons)

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 Access Denied! Authorization Required.", reply_markup=get_fsub_buttons())

    text = (
        "🔐 **DATABASE ACCESS TERMINAL**\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📱 `/num [number]` - Fetch Mobile Data\n"
        "🚗 `/vehicle [plate]` - Fetch RC Details\n"
        "🆔 `/aadhar [uid]` - Verify Identity\n"
        "👨‍👩‍👧‍👦 `/familyinfo [uid]` - Fetch Family Tree\n"
        "🔗 `/vnum [plate]` - Reverse Lookup\n"
        "📨 `/sms [number]` - Test Gateway\n\n"
        "💸 `/fam [id]` - FamPay Database\n\n"
        f"{NEW_FOOTER}"
    )
    await message.reply_text(text, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("check_fsub"))
async def check_fsub_callback(client, callback_query: CallbackQuery):
    if await check_user_joined(client, callback_query.from_user.id):
        await callback_query.message.delete()
        await show_dashboard(client, callback_query.message)
    else:
        await callback_query.answer("❌ Authorization Failed! Join Channels.", show_alert=True)

# --- MAIN LOGIC (STEALTH MODE) ---
COMMAND_LIST = ["num", "vehicle", "aadhar", "familyinfo", "vnum", "sms", "fam"]

@app.on_message(filters.command(COMMAND_LIST, prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    global RESOLVED_TARGET_ID
    
    if not RESOLVED_TARGET_ID:
        # User ko server error dikhayenge, "Target Group" nahi bolenge
        return await message.reply_text("❌ **Server Error:** Database connection failed. Contact Admin.")

    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 Unauthorized Access!", reply_markup=get_fsub_buttons())

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Input Error!**\nUsage: `/{message.command[0]} <value>`")

    # 🕵️‍♂️ FAKE STATUS MESSAGES (Lagna chahiye system khud dhoond raha hai)
    status_msg = await message.reply_text(f"🔍 **Connecting to Database...**")

    try:
        sent_req = await client.send_message(chat_id=RESOLVED_TARGET_ID, text=message.text)
        target_response = None

        for attempt in range(25):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(RESOLVED_TARGET_ID, limit=5):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    if log.reply_to_message_id == sent_req.id:
                        text_content = (log.text or log.caption or "").lower()
                        # Ignore "wait" messages but show user "Fetching"
                        ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading"]
                        if any(word in text_content for word in ignore_words):
                            await status_msg.edit(f"📂 **Fetching Records... ({attempt * 10}%)**")
                            break
                        target_response = log
                        break
            if target_response: break

        if not target_response:
            await status_msg.edit("❌ **Not Found:** No data exists in database.")
            return

        # Parsing
        raw_text = ""
        if target_response.document:
            await status_msg.edit("📂 **Decrypting File...**")
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        elif target_response.photo:
            raw_text = target_response.caption or ""
        elif target_response.text:
            raw_text = target_response.text

        if not raw_text or len(raw_text.strip()) < 5:
            await status_msg.edit("❌ **No Records Found.**")
            return

        # --- 🧹 STEALTH CLEANING (Source Chupana) ---
        clean_text = raw_text
        
        trash_list = [
            "⚡ Designed & Powered by @DuXxZx_info",
            "════════════════════════════════════",
            "====================",
            "MOBILE INFO REPORT", # Report header hata diya
            "Target:",           # Target number repeat hata diya
            "Generated:",        # Time stamp hata diya
            "--- Record",        # Record divider hata diya
            "★  CREDIT  ★",
            "@Backupinfo69_bot",
            "Join channel",
            "🔍 Lookup Services:",
            "/num [number]",       
            "/vehicle [plate]",
            "/aadhar [uid]",
            "/familyinfo [uid]",
            "/vnum [plate]",
            "/sms [number]",
            "/fam [id]",
            "Mobile Info",         
            "RC & Challan",
            "FamPay id to number Lookup"
        ]
        
        for trash in trash_list:
            clean_text = clean_text.replace(trash, "")
        
        # Remove lines starting with specific keywords if needed
        lines = []
        for line in clean_text.split('\n'):
            line = line.strip()
            # "Target:" ya "Generated:" wali lines agar bach gayi ho to hata do
            if not line: continue
            if line.startswith("Target:") or line.startswith("Generated:"): continue 
            lines.append(line)
            
        final_clean_text = "\n".join(lines)

        # --- 📝 FINAL OUTPUT (Looks like Raw Database) ---
        json_data = {
            "status": "success",
            "query": message.command[0],
            "input": message.command[1],
            "data": final_clean_text # Changed key from 'result' to 'data' (More professional)
        }
        
        formatted_output = (
            f"```json\n{json.dumps(json_data, indent=4, ensure_ascii=False)}\n```\n\n"
            f"{NEW_FOOTER}"
        )

        if len(formatted_output) > 4000:
            await message.reply_text(formatted_output[:4000])
            await message.reply_text(formatted_output[4000:])
        else:
            await message.reply_text(formatted_output)

        await status_msg.delete()

    except PeerIdInvalid:
        await status_msg.edit("⚠️ **System Busy... Retrying.**")
        await start_bot()
    except Exception as e:
        await status_msg.edit(f"❌ **System Error:** {str(e)}")

# --- STARTUP FIXER ---
async def start_bot():
    global RESOLVED_TARGET_ID
    print("🚀 Starting Database Interface...")
    if not app.is_connected:
        await app.start()
    
    # Internal Logs (User ko nahi dikhenge)
    print(f"🔄 Connecting to Backend Source: {TARGET_GROUP_LINK}")
    try:
        try:
            chat = await app.join_chat(TARGET_GROUP_LINK)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Connection Established! ID: {RESOLVED_TARGET_ID}")
        except UserAlreadyParticipant:
            chat = await app.get_chat(TARGET_GROUP_LINK)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Connection Verified. ID: {RESOLVED_TARGET_ID}")
        except Exception as e:
            print(f"⚠️ Direct Connect Failed ({e}), Switching to Backup ID...")
            RESOLVED_TARGET_ID = FALLBACK_ID
            
        await app.get_chat(RESOLVED_TARGET_ID)

    except Exception as e:
        print(f"❌ Error: {e}")
        RESOLVED_TARGET_ID = FALLBACK_ID

    print(f"🚀 System Ready! Backend ID: {RESOLVED_TARGET_ID}")
    await idle()
    await app.stop()

if __name__ == "__main__":
    keep_alive()
    app.run(start_bot())
