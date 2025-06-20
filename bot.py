from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 Токен и ID владельца (подставлены вручную)
BOT_TOKEN = "8187999524:AAG8gpdIZ_-wltHFAxT9KeWwKDaIZSSibRk"
OWNER_ID = 1295958989

# Словарь для отслеживания ожидания уточняющего вопроса
user_waiting_question = {}

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [["✅ Заинтересовал товар"]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Здравствуйте!\n\n"
        "Вы можете ознакомиться с нашими товарами по одной из ссылок:\n"
        "🔹 [Витрина 1](https://t.me/loftconstruction)\n"
        "🔹 [Витрина 2](https://t.me/MagicTablesUz)\n\n"
        "Если что-то заинтересовало — нажмите кнопку ниже 👇",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# Обработка кнопки "Заинтересовал товар"
async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "✅ Заинтересовал товар":
        contact_button = KeyboardButton("📞 Оставить контакт", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
        await update.message.reply_text(
            "Отлично! Пожалуйста, нажмите кнопку ниже, чтобы отправить контакт.\n"
            "Наш оператор свяжется с вами в ближайшее время!",
            reply_markup=keyboard
        )

# Обработка контакта от пользователя
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    name = contact.first_name or "Не указано"
    phone = contact.phone_number or "Нет номера"

    # Отправка владельцу
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"📩 Новый клиент!\nИмя: {name}\nТелефон: {phone}"
    )

    user_id = update.effective_user.id
    user_waiting_question[user_id] = True

    await update.message.reply_text(
        "Спасибо! Мы уже получили вашу заявку 😊\n"
        "Если у вас есть вопросы или пожелания — напишите их сюда:"
    )

# Обработка уточняющих сообщений от клиента
async def followup_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_waiting_question.get(user_id):
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📨 Уточнение от клиента:\n{text}"
        )
        await update.message.reply_text("Всё передано оператору! Спасибо 🙌")
        user_waiting_question[user_id] = False
    else:
        await update.message.reply_text(
            "Если у вас есть вопросы или детали по заказу — можете писать сюда 📝"
        )

# Запуск бота
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("✅ Заинтересовал товар"), ask_contact))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, followup_question))
app.run_polling()
