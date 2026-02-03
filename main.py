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

# ✅ SESSION STRING
SESSION_STRING = "BQI5Xz4AANa83p6zL0X6y2fP5eiMmu2yk9S-RAxCrgcrjGUZmMLhrbhMGyY1JJ7LdWIbEIEWymplxWx2kI2AgB10uVvXsovXavySVPt9heb_ViN6DBOkat12WVn0aciH2KJM0qyyfTZmC9QJlvxQwZZ9b6ncjFzMLEHF6cPgF4_xH9yN08S0s0t30bBo4CkjsRyHO-ImqryjeD0n9yiylcISTucBxQEpdInlDv80soVeF1KSlHj_KTd48fXlKJmhbXWdHdiN2bJKBAZzkFkT304UM4TN2PeztUW3wgnX6CMwz3GcWotmNuVJrFWKmN4I8U48tPmmhYvvPj6-deAlNekD2jwTrAAAAAFJSgVkAA"

# 🎯 TARGET SETTINGS
TARGET_GROUP_LINK = "infobot_66"
TARGET_BOT_USERNAME = "Backupinfo69_bot"
FALLBACK_ID = -1003320004816 

# ✅ NEW FOOTER (User Requested)
NEW_FOOTER = "⚡ Designed & Powered by @DuXxZx_info"

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
# 👇 FLASK KEEP-ALIVE
# ==========================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Bot is Running!"

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

# --- DASHBOARD (NEW MENU) ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 Access Denied! Join Channels first.", reply_markup=get_fsub_buttons())

    # ✅ User Defined Menu Layout
    text = (
        "🔍 **Lookup Services:**\n\n"
        "📱 `/num [number]` - Mobile Info\n"
        "🚗 `/vehicle [plate]` - RC & Challan\n"
        "🆔 `/aadhar [uid]` - Aadhaar Info\n"
        "👨‍👩‍👧‍👦 `/familyinfo [uid]` - Family List\n"
        "🔗 `/vnum [plate]` - Get Mobile from Vehicle\n"
        "📨 `/sms [number]` - SMS Service\n\n"
        "💸 `/fam [id]` - FamPay id to number Lookup\n\n"
        f"{NEW_FOOTER}"
    )
    await message.reply_text(text, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("check_fsub"))
async def check_fsub_callback(client, callback_query: CallbackQuery):
    if await check_user_joined(client, callback_query.from_user.id):
        await callback_query.message.delete()
        await show_dashboard(client, callback_query.message)
    else:
        await callback_query.answer("❌ Join channels first!", show_alert=True)

# --- MAIN LOGIC (UPDATED COMMANDS) ---
COMMAND_LIST = ["num", "vehicle", "aadhar", "familyinfo", "vnum", "sms", "fam"]

@app.on_message(filters.command(COMMAND_LIST, prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    global RESOLVED_TARGET_ID
    
    if not RESOLVED_TARGET_ID:
        return await message.reply_text("❌ **Error:** Target Group not connected. Contact Admin.")

    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 Access Denied!", reply_markup=get_fsub_buttons())

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

    status_msg = await message.reply_text(f"🔍 **Searching...**")

    try:
        # Forward command to target
        sent_req = await client.send_message(chat_id=RESOLVED_TARGET_ID, text=message.text)
        target_response = None

        # Wait loop
        for attempt in range(25):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(RESOLVED_TARGET_ID, limit=5):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    if log.reply_to_message_id == sent_req.id:
                        text_content = (log.text or log.caption or "").lower()
                        ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading"]
                        if any(word in text_content for word in ignore_words):
                            await status_msg.edit(f"⏳ **Processing... ({attempt+1})**")
                            break
                        target_response = log
                        break
            if target_response: break

        if not target_response:
            await status_msg.edit("❌ **Timeout:** Target bot ne reply nahi diya.")
            return

        # Parsing
        raw_text = ""
        if target_response.document:
            await status_msg.edit("📂 **Downloading...**")
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        elif target_response.photo:
            raw_text = target_response.caption or ""
        elif target_response.text:
            raw_text = target_response.text

        if not raw_text or len(raw_text.strip()) < 5:
            await status_msg.edit("❌ **No Data Found**")
            return

        # --- 🧹 CLEANING LOGIC (REMOVING MENU & TRASH) ---
        clean_text = raw_text
        
        # Ye sab text result se hata diya jayega
        trash_list = [
            "════════════════════════════════════",
            "★  CREDIT  ★",
            "@Backupinfo69_bot",
            "Join channel",
            "🔍 Lookup Services:",  # Removed Menu Title
            "/num [number]",       # Removed Commands from output
            "/vehicle [plate]",
            "/aadhar [uid]",
            "/familyinfo [uid]",
            "/vnum [plate]",
            "/sms [number]",
            "/fam [id]",
            "Mobile Info",         # Removed Descriptions
            "RC & Challan",
            "FamPay id to number Lookup"
        ]
        
        for trash in trash_list:
            clean_text = clean_text.replace(trash, "")
        
        # Remove Empty Lines
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        final_clean_text = "\n".join(lines)

        # --- 📝 JSON OUTPUT ---
        json_data = {
            "status": "success",
            "query": message.command[0],
            "input": message.command[1],
            "result": final_clean_text,
            "credits": NEW_FOOTER  # ✅ NEW FOOTER HERE
        }
        
        formatted_output = f"```json\n{json.dumps(json_data, indent=4, ensure_ascii=False)}\n```"

        if len(formatted_output) > 4000:
            await message.reply_text(formatted_output[:4000])
            await message.reply_text(formatted_output[4000:])
        else:
            await message.reply_text(formatted_output)

        await status_msg.delete()

    except PeerIdInvalid:
        await status_msg.edit("⚠️ **Refreshing... Try again.**")
        await start_bot()
    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

# --- STARTUP FIXER ---
async def start_bot():
    global RESOLVED_TARGET_ID
    print("🚀 Starting Bot...")
    if not app.is_connected:
        await app.start()
    
    print(f"🔄 Resolving Target: {TARGET_GROUP_LINK}")
    try:
        try:
            chat = await app.join_chat(TARGET_GROUP_LINK)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Joined! ID: {RESOLVED_TARGET_ID}")
        except UserAlreadyParticipant:
            chat = await app.get_chat(TARGET_GROUP_LINK)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Already Member. ID: {RESOLVED_TARGET_ID}")
        except Exception as e:
            print(f"⚠️ Link failed ({e}), using Fallback ID...")
            RESOLVED_TARGET_ID = FALLBACK_ID
            
        await app.get_chat(RESOLVED_TARGET_ID)

    except Exception as e:
        print(f"❌ Error: {e}")
        RESOLVED_TARGET_ID = FALLBACK_ID

    print(f"🚀 Bot Ready! Target ID: {RESOLVED_TARGET_ID}")
    await idle()
    await app.stop()

if __name__ == "__main__":
    keep_alive()
    app.run(start_bot())
