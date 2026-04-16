import logging
import asyncio
import os
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
from telegram.error import BadRequest, Forbidden

# ================= CONFIGURATION =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1146186608"))
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# --- MEDIA LINKS ---
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

LOGO_AVIATOR = "https://i.ibb.co/PZBBDv85/images-9.jpg"
LOGO_MINES = "https://i.ibb.co/MDVxth7x/images-8.jpg"
LOGO_PENALTY = "https://i.ibb.co/5WzBdWX4/hqdefault.jpg"
LOGO_KING_THIMBLES = "https://i.ibb.co/8LYwvg1j/maxresdefault.jpg"

LINK_AVIATOR = "https://aviatorgameadmin.netlify.app/"
LINK_MINES = "https://mines-game-hack.netlify.app/"
LINK_PENALTY = "https://pnalteaybot.netlify.app/"
LINK_KING_THIMBLES = "https://kingthimblesbot.netlify.app/"
HOW_TO_USE_LINK = "https://youtube.com/@sunny_bro11?si=gYfOtXnKayCkZloF"

USER_FILE = "users.txt"

# --- STATES ---
WAITING_FOR_ID = 0
BROADCAST_SIMPLE, BTN_BC_CONTENT, BTN_BC_LABEL, BTN_BC_LINK, BC_AUTO_SIGNAL = range(1, 6)

# --- LANGUAGES ---
LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning Money', 'reg_btn': 'Registration Link', 'verify_btn': '✅ I have Registered', 'ask_id': 'Please send your 9-digit Account ID:', 'analyzing': '🔄 Verifying...', 'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'How to use', 'help_btn': 'Help', 'select_game': 'Select a game:'},
    'hi': {'name': '🇮🇳 Hindi', 'earn_btn': 'पैसे कमाना शुरू करें', 'reg_btn': 'पंजीकरण', 'verify_btn': '✅ मैंने पंजीकरण किया है', 'ask_id': 'अपनी 9-अंकीय आईडी भेजें:', 'analyzing': '🔄 जांच की जा رہی ہے...', 'success_msg': '✅ <b>खाता सत्यापित!</b>', 'play_btn': 'हैक के साथ खेलें', 'guide_btn': 'उपयोग कैसे करें', 'help_btn': 'मदদ', 'select_game': 'गेम चुनें:'},
    'bd': {'name': '🇧🇩 Bangla', 'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন লিংক', 'verify_btn': '✅ রেজিস্ট্রেশন সম্পন্ন', 'ask_id': 'আপনার ৯ ডিজিটের আইডি দিন:', 'analyzing': '🔄 যাচাই করা হচ্ছে...', 'success_msg': '✅ <b>একাউন্ট ভেরিফাইড!</b>', 'play_btn': 'হ্যাক দিয়ে খেলুন', 'guide_btn': 'কিভাবে ব্যবহার করবেন', 'help_btn': 'সাহায্য', 'select_game': 'গেম সিলেক্ট করুন:'}
}

# ================= DB FUNCTIONS =================
def save_user(user_id):
    users = get_users()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f: f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USER_FILE): return []
    with open(USER_FILE, "r") as f: return [line.strip() for line in f.readlines() if line.strip()]

# ================= UTILS =================
async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: return False

async def send_lang_menu(update, context):
    kb = [[InlineKeyboardButton(v['name'], callback_data=f'lang_{k}') for k in list(LANGUAGES.keys())[i:i+2]] for i in range(0, len(LANGUAGES), 2)]
    msg = "Hello! Please select your language:"
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=InlineKeyboardMarkup(kb))

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    if await check_membership(user_id, context):
        await send_lang_menu(update, context)
    else:
        kb = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)], [InlineKeyboardButton("✅ Joined", callback_data='check_join')]]
        await context.bot.send_message(chat_id=user_id, text="⚠️ Please join our channel first!", reply_markup=InlineKeyboardMarkup(kb))
    return ConversationHandler.END

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang
    lang_data = LANGUAGES.get(lang, LANGUAGES['en'])
    kb = [[InlineKeyboardButton(lang_data['earn_btn'], callback_data='start_earning')]]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_WELCOME, caption=f"Language: {lang_data['name']}", reply_markup=InlineKeyboardMarkup(kb))

async def start_earning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('selected_lang', 'en')
    ld = LANGUAGES.get(lang, LANGUAGES['en'])
    txt = "<b>Step 1: Register</b>\nCreate new account with promo code: <b>BLACK110</b>\n\n<b>Step 2: Verify</b>\nClick below."
    kb = [[InlineKeyboardButton(ld['reg_btn'], url="https://1wezue.com/casino")], [InlineKeyboardButton(ld['verify_btn'], callback_data='verify_reg')]]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_REG, caption=txt, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))

async def verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    lang = context.user_data.get('selected_lang', 'en')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=LANGUAGES[lang]['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_text = update.message.text
    lang = context.user_data.get('selected_lang', 'en')
    ld = LANGUAGES[lang]
    
    # Notify Admin
    await context.bot.send_message(ADMIN_ID, f"🔔 <b>New User Verified!</b>\nID: {user_id_text}\nTG: {update.effective_user.id}", parse_mode='HTML')
    
    kb = [[InlineKeyboardButton(ld['play_btn'], callback_data='play_hack')], [InlineKeyboardButton(ld['guide_btn'], url=HOW_TO_USE_LINK)]]
    await update.message.reply_photo(photo=IMAGE_URL_SUCCESS, caption=ld['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))
    return ConversationHandler.END

async def hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    kb = [
        [InlineKeyboardButton("✈️ Aviator", callback_data='game_aviator'), InlineKeyboardButton("💣 Mines", callback_data='game_mines')],
        [InlineKeyboardButton("⚽ Penalty", callback_data='game_penalty'), InlineKeyboardButton("👑 King Thimbles", callback_data='game_king_thimbles')]
    ]
    await update.callback_query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_HACK_MENU, caption="Choose Game:", reply_markup=InlineKeyboardMarkup(kb))

async def game_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game = query.data
    links = {'game_aviator': (LINK_AVIATOR, LOGO_AVIATOR, "Aviator"), 'game_mines': (LINK_MINES, LOGO_MINES, "Mines"), 'game_penalty': (LINK_PENALTY, LOGO_PENALTY, "Penalty"), 'game_king_thimbles': (LINK_KING_THIMBLES, LOGO_KING_THIMBLES, "King Thimbles")}
    url, logo, name = links[game]
    kb = [[InlineKeyboardButton(f"📱 Open {name} Hack", web_app=WebAppInfo(url=url))], [InlineKeyboardButton("🔙 Back", callback_data='play_hack')]]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=logo, caption=f"<b>{name} Hack Ready!</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))

# ================= ADMIN LOGIC (FIXED) =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_users()
    kb = [
        [InlineKeyboardButton("📝 Simple Broadcast", callback_data='adm_bc_simple')],
        [InlineKeyboardButton("🔗 Button Broadcast", callback_data='adm_bc_btn')],
        [InlineKeyboardButton("✨ Signal Broadcast", callback_data='adm_bc_signal')],
        [InlineKeyboardButton("❌ Close", callback_data='adm_close')]
    ]
    await update.message.reply_text(f"👑 <b>Admin Panel</b>\nTotal Users: {len(users)}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Action Cancelled.")
    return ConversationHandler.END

# Broadcast Actions
async def bc_simple_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Send message or photo for broadcast (or /cancel):")
    return BROADCAST_SIMPLE

async def do_simple_bc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    success = 0
    for uid in users:
        try:
            if update.message.photo: await context.bot.send_photo(uid, update.message.photo[-1].file_id, caption=update.message.caption)
            else: await context.bot.send_message(uid, update.message.text)
            success += 1
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"✅ Sent to {success} users.")
    return ConversationHandler.END

async def bc_btn_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Step 1: Send the message/photo content:")
    return BTN_BC_CONTENT

async def bc_btn_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['tmp_bc'] = ('photo', update.message.photo[-1].file_id, update.message.caption)
    else:
        context.user_data['tmp_bc'] = ('text', update.message.text, None)
    await update.message.reply_text("Step 2: Send Button Label (e.g. Join Now):")
    return BTN_BC_LABEL

async def bc_btn_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tmp_label'] = update.message.text
    await update.message.reply_text("Step 3: Send Button URL:")
    return BTN_BC_LINK

async def do_btn_bc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    label = context.user_data['tmp_label']
    type, content, cap = context.user_data['tmp_bc']
    users = get_users()
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(label, url=url)]])
    success = 0
    for uid in users:
        try:
            if type == 'photo': await context.bot.send_photo(uid, content, caption=cap, reply_markup=kb)
            else: await context.bot.send_message(uid, content, reply_markup=kb)
            success += 1
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"✅ Sent to {success} users.")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation Handlers
    user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_start, pattern='^verify_reg$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(bc_simple_start, pattern='^adm_bc_simple$'),
            CallbackQueryHandler(bc_btn_start, pattern='^adm_bc_btn$')
        ],
        states={
            BROADCAST_SIMPLE: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, do_simple_bc)],
            BTN_BC_CONTENT: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, bc_btn_content)],
            BTN_BC_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bc_btn_label)],
            BTN_BC_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, do_btn_bc)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(admin_conv)
    app.add_handler(user_conv)
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('admin', admin_panel))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern='^lang_'))
    app.add_handler(CallbackQueryHandler(start_earning, pattern='^start_earning$'))
    app.add_handler(CallbackQueryHandler(hack_menu, pattern='^play_hack$'))
    app.add_handler(CallbackQueryHandler(game_select, pattern='^game_'))
    app.add_handler(CallbackQueryHandler(start, pattern='^check_join$'))
    app.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.message.delete(), pattern='^adm_close$'))

    print("Bot started...")
    app.run_polling()
