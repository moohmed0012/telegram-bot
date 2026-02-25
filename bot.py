import datetime
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8450802969:AAEX6WzC-yM4ZwvHOdDaZE-Xb6vUpTPYmHE"
ADMIN_IDS = [5894877058, 77098280]

groups = [
    ["Group A", "Group B"],
    ["Group C", "Group D"],
    ["Group E"]
]

user_data_store = {}
submissions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(groups, resize_keyboard=True)
    await update.message.reply_text("اختر الكروب الخاص بك:", reply_markup=keyboard)
    user_data_store[update.message.from_user.id] = {"state": "choosing_group"}

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data_store:
        await update.message.reply_text("اكتب /start للبدء")
        return

    state = user_data_store[user_id]["state"]

    if state == "choosing_group":
        if text in ["Group A", "Group B", "Group C", "Group D", "Group E"]:
            user_data_store[user_id]["group"] = text
            user_data_store[user_id]["state"] = "waiting_for_name"
            await update.message.reply_text("اكتب اسمك الثلاثي:")
        else:
            await update.message.reply_text("اختر من الأزرار فقط.")

    elif state == "waiting_for_name":
        user_data_store[user_id]["name"] = text
        user_data_store[user_id]["state"] = "waiting_for_file"
        await update.message.reply_text("الآن أرسل مشروعك كملف (PDF أو ZIP).")

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_data_store:
        await update.message.reply_text("اكتب /start أولاً")
        return

    if user_data_store[user_id]["state"] != "waiting_for_file":
        await update.message.reply_text("أكمل الخطوات أولاً")
        return

    file = update.message.document
    extension = file.file_name.split(".")[-1].lower()
    allowed = ["pdf", "zip", "rar"]

    if extension not in allowed:
        await update.message.reply_text("نوع ملف غير مسموح ❌")
        return

    group = user_data_store[user_id]["group"]
    name = user_data_store[user_id]["name"]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_edit = user_id in submissions

    caption_text = f"""
📥 تسليم {'معدل' if is_edit else 'جديد'}
👤 الاسم: {name}
📂 المجموعة: {group}
🆔 ID الطالب: {user_id}
⏰ الوقت: {now}
"""

    for admin in ADMIN_IDS:
        await context.bot.send_document(
            chat_id=admin,
            document=file.file_id,
            caption=caption_text
        )

    submissions[user_id] = {
        "name": name,
        "group": group,
        "time": now
    }

    await update.message.reply_text(
        "تم تحديثك ✅" if is_edit else "تم استلام مشروعك ✅"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.Document.ALL, receive_file))

if __name__ == "__main__":
    print("Bot is starting...")
    app.run_polling()
