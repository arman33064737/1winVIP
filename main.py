import logging
import asyncio
import os
from threading import Thread
from flask import Flask
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)

# ================= লগিং =================
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= ফায়ারবেস কানেকশন (অরিজিনাল ফাইল মেথড) =================
# এটি আপনার 'firebase-key.json' ফাইল থেকে চাবিটি পড়বে, যা ১০০% সেফ
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://winbot-eea9a-default-rtdb.firebaseio.com/"
        })
    logger.info("✅ Firebase Connected Successfully!")
except Exception as e:
    logger.error(f"❌ Firebase Error: {e}")

# ================= কনফিগারেশন =================
BOT_TOKEN = "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q"
ADMIN_ID = 1146186608
REQUIRED_CHANNEL = -1001481593780
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# ================= ডাটাবেস ফাংশন =================
def save_user(user):
    try:
        ref = db.reference(f'users/{user.id}')
        if not ref.get():
            ref.set({'first_name': user.first_name, 'username': user.username or "N/A", 'id': user.id})
    except: pass

def get_users():
    try:
        ref = db.reference('users')
        users = ref.get()
        return list(users.keys()) if users else []
    except: return []

# ================= হ্যান্ডলারস =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user.id)
        is_member = member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: is_member = False
    
    if is_member:
        keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'),
                     InlineKeyboardButton("🇧🇩 বাংলা", callback_data='lang_bd')]]
        await update.message.reply_photo(photo=IMAGE_URL_WELCOME, caption="Please select your language:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join')]]
        await update.message.reply_text("⚠️ Join our channel first!", reply_markup=InlineKeyboardMarkup(keyboard))

async def language_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang
    
    text = "🚀 <b>Register Now!</b>\nUse promo <code>BLACK696</code>." if lang == 'en' else "🚀 <b>রেজিস্ট্রেশন করুন!</b>\nপ্রোমো কোড: <code>BLACK696</code>"
    keyboard = [[InlineKeyboardButton("🔗 Registration Link", url="https://bit.ly/3S0V67h")],
                [InlineKeyboardButton("✅ I have Registered", callback_data='verify_reg')]]
    
    await query.message.delete()
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=IMAGE_URL_REG, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

WAITING_FOR_ID = 0
async def verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = await query.message.reply_text("⏳ Checking synchronization... Please wait 5s.")
    await asyncio.sleep(5)
    await msg.delete()
    await query.message.reply_text("Please send your 9-digit Account ID:")
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_val = update.message.text
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚨 <b>New ID Submitted:</b> <code>{user_id_val}</code>", parse_mode='HTML')
    keyboard = [[InlineKeyboardButton("🎮 Open Hack Menu", callback_data='open_menu')]]
    await update.message.reply_photo(photo=IMAGE_URL_SUCCESS, caption="✅ <b>Verified!</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return ConversationHandler.END

async def hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("✈️ Aviator", web_app=WebAppInfo(url="https://aviatorbahohacker.fwh.is/"))],
                [InlineKeyboardButton("💣 Mines", web_app=WebAppInfo(url="https://mines-game-hack.netlify.app/"))]]
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=IMAGE_URL_HACK_MENU, caption="Select Game:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= অ্যাডমিন প্যানেল =================
BC_CONTENT, BC_LABEL, BC_LINK = range(1, 4)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_users()
    keyboard = [[InlineKeyboardButton("🔗 Button Broadcast", callback_data='admin_bc')]]
    await update.message.reply_text(f"🛠 <b>Admin Panel</b>\nUsers: {len(users)}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def bc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Send message (Text/Photo):")
    return BC_CONTENT

async def bc_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['bc_type'] = 'photo'; context.user_data['bc_file'] = update.message.photo[-1].file_id; context.user_data['bc_cap'] = update.message.caption
    else:
        context.user_data['bc_type'] = 'text'; context.user_data['bc_text'] = update.message.text
    await update.message.reply_text("Button Label:")
    return BC_LABEL

async def bc_get_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_label'] = update.message.text
    await update.message.reply_text("Button URL:")
    return BC_LINK

async def bc_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text; label = context.user_data['bc_label']; users = get_users()
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(label, url=url)]])
    for uid in users:
        try:
            if context.user_data['bc_type'] == 'photo': await context.bot.send_photo(uid, photo=context.user_data['bc_file'], caption=context.user_data['bc_cap'], reply_markup=markup)
            else: await context.bot.send_message(uid, text=context.user_data['bc_text'], reply_markup=markup)
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text("✅ Done!")
    return ConversationHandler.END

# ================= অটো ব্রডকাস্ট (৩ ঘণ্টা) =================
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text="🚀 <b>Reminder:</b> Check our latest signals!", parse_mode='HTML')
            await asyncio.sleep(0.05)
        except: pass

# ================= সার্ভার =================
app = Flask(__name__)
@app.route('/')
def home(): return "OK", 200
def run_srv(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run_srv, daemon=True).start()
    bot = ApplicationBuilder().token(BOT_TOKEN).build()
    bot.job_queue.run_repeating(auto_job, interval=10800, first=10)
    
    user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_start, pattern='^verify_reg$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('start', start)]
    )
    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(bc_start, pattern='^admin_bc$')],
        states={BC_CONTENT: [MessageHandler(filters.ALL, bc_get_content)], BC_LABEL: [MessageHandler(filters.TEXT, bc_get_label)], BC_LINK: [MessageHandler(filters.TEXT, bc_done)]},
        fallbacks=[CommandHandler('admin', admin_panel)]
    )
    
    bot.add_handler(CommandHandler('start', start)); bot.add_handler(CommandHandler('admin', admin_panel))
    bot.add_handler(user_conv); bot.add_handler(admin_conv)
    bot.add_handler(CallbackQueryHandler(language_select, pattern='^lang_'))
    bot.add_handler(CallbackQueryHandler(hack_menu, pattern='^open_menu$'))
    bot.add_handler(CallbackQueryHandler(start, pattern='^check_join$'))
    
    bot.run_polling()
