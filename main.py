import logging
import asyncio
import os
import sys
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

# ================= লগিং সেটআপ =================
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= কনফিগারেশন =================
# আপনার দেওয়া টোকেন ও আইডি
BOT_TOKEN = "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q"
ADMIN_ID = 1146186608
REQUIRED_CHANNEL = -1001481593780
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# মিডিয়া লিঙ্কসমূহ
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# ================= ফায়ারবেস কানেকশন (ফাইল পদ্ধতি) =================
# এটি আপনার 'firebase-key.json' ফাইলটি খুঁজে বের করবে
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://winbot-eea9a-default-rtdb.firebaseio.com/"
        })
    logger.info("✅ Firebase Connected Successfully from File!")
except Exception as e:
    logger.error(f"❌ Firebase Critical Error: {e}")
    # ফাইল না পাওয়া গেলে বা ভুল থাকলে বট বন্ধ হয়ে যাবে যাতে আপনি লগ দেখে ঠিক করতে পারেন
    sys.exit(1)

# ================= ডাটাবেস ফাংশন =================
def save_user(user):
    try:
        ref = db.reference(f'users/{user.id}')
        if not ref.get():
            ref.set({
                'first_name': user.first_name,
                'username': user.username or "N/A",
                'id': user.id
            })
    except: pass

def get_all_users():
    try:
        ref = db.reference('users')
        users = ref.get()
        return list(users.keys()) if users else []
    except: return []

# ================= হ্যান্ডলারস =================
async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    if await check_membership(user.id, context):
        keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'), 
                     InlineKeyboardButton("🇧🇩 বাংলা", callback_data='lang_bd')]]
        await update.message.reply_photo(photo=IMAGE_URL_WELCOME, caption="Select Language / ভাষা নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))
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

# আইডি ভেরিফাই (৫ সেকেন্ড ওয়েট)
WAITING_FOR_ID = 0
async def verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = await query.message.reply_text("⏳ Verifying sync... 5s")
    await asyncio.sleep(5)
    await msg.delete()
    await query.message.reply_text("Please send your 9-digit Account ID:")
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_val = update.message.text
    # অ্যাডমিনকে জানানো
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚨 <b>ID Submitted:</b> <code>{user_id_val}</code>", parse_mode='HTML')
    
    keyboard = [[InlineKeyboardButton("🎮 Open Hack Menu", callback_data='open_hack')]]
    await update.message.reply_photo(photo=IMAGE_URL_SUCCESS, caption="✅ <b>Verified!</b> Account linked.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return ConversationHandler.END

async def hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("✈️ Aviator", web_app=WebAppInfo(url="https://aviatorbahohacker.fwh.is/"))], 
                [InlineKeyboardButton("💣 Mines", web_app=WebAppInfo(url="https://mines-game-hack.netlify.app/"))]]
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=IMAGE_HACK_MENU, caption="Select Game:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= অ্যাডমিন প্যানেল (ব্রডকাস্ট) =================
BC_CONTENT, BC_LABEL, BC_LINK = range(1, 4)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_all_users()
    keyboard = [[InlineKeyboardButton("🔗 Button Broadcast", callback_data='admin_bc')]]
    await update.message.reply_text(f"🛠 <b>Admin Panel</b>\nTotal Users: {len(users)}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def bc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Send message to broadcast (Text/Photo):")
    return BC_CONTENT

async def bc_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['bc_type'] = 'photo'
        context.user_data['bc_file'] = update.message.photo[-1].file_id
        context.user_data['bc_cap'] = update.message.caption
    else:
        context.user_data['bc_type'] = 'text'
        context.user_data['bc_text'] = update.message.text
    await update.message.reply_text("Enter Button Label:")
    return BC_LABEL

async def bc_get_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_label'] = update.message.text
    await update.message.reply_text("Enter Button URL:")
    return BC_LINK

async def bc_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    label = context.user_data['bc_label']
    users = get_all_users()
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(label, url=url)]])
    
    count = 0
    for uid in users:
        try:
            if context.user_data['bc_type'] == 'photo':
                await context.bot.send_photo(uid, photo=context.user_data['bc_file'], caption=context.user_data['bc_cap'], reply_markup=markup)
            else:
                await context.bot.send_message(uid, text=context.user_data['bc_text'], reply_markup=markup)
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"✅ Sent to {count} users.")
    return ConversationHandler.END

# ================= অটো ব্রডকাস্ট (৩ ঘণ্টা পর পর) =================
async def auto_broadcast_job(context: ContextTypes.DEFAULT_TYPE):
    users = get_all_users()
    text = "🚀 <b>New Hack Update!</b>\nচেক করুন আমাদের নতুন সিগন্যাল এবং প্রফিট করুন।\n\n[3-Hour Reminder]"
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text, parse_mode='HTML')
            await asyncio.sleep(0.05)
        except: pass

# ================= ওয়েব সার্ভার (Render/Railway Port Binding) =================
server = Flask(__name__)
@server.route('/')
def home(): return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# ================= মেইন =================
if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # অটো মেসেজ ৩ ঘণ্টা (১০৮০০ সেকেন্ড)
    application.job_queue.run_repeating(auto_broadcast_job, interval=10800, first=10)

    # কনভারসেশন হ্যান্ডলারস
    user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_start, pattern='^verify_reg$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('start', start)],
        allow_reentry=True
    )
    
    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(bc_start, pattern='^admin_bc$')],
        states={
            BC_CONTENT: [MessageHandler(filters.ALL & ~filters.COMMAND, bc_get_content)],
            BC_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bc_get_label)],
            BC_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, bc_done)],
        },
        fallbacks=[CommandHandler('admin', admin_panel)]
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(user_conv)
    application.add_handler(admin_conv)
    application.add_handler(CallbackQueryHandler(language_select, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(hack_menu, pattern='^open_hack$'))
    application.add_handler(CallbackQueryHandler(start, pattern='^check_join$'))

    print("Bot is polling...")
    application.run_polling()
