#!/usr/bin/env python3
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ↓ Senin değerlerin ↓
BOT_TOKEN      = "7936867639:AAFITAN5LtyzwLFsbJ1W-spNAprCV94ZxLM"
BOT_USERNAME   = "goygoyitiraf_bot"
ADMIN_GROUP_ID = -1002532660895
CHANNEL_ID     = -1001679841226
CHANNEL_GROUP  = "https://t.me/goygoy_itiraf"

# Durum saklama
awaiting_confession = set()
pending = {}

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    keyboard = [
        [
            {"text": "✅ İtiraf Et", "callback_data": "start_confess"},
            {"text": "❌ Vazgeç",  "callback_data": "start_cancel"}
        ],
        [
            {"text": "📺 İtiraf Kanalımız", "url": CHANNEL_GROUP}
        ]
    ]
    reply_markup = {"inline_keyboard": keyboard}

    await update.message.reply_text(
        "👋 Merhaba! İtiraf etmek istersen önce “İtiraf Et” butonuna tıkla.\n\n"
        "Kanalımıza göz atmak istersen “İtiraf Kanalımız” butonuna tıklayabilirsin.",
        reply_markup=reply_markup
    )

async def start_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()
    await cq.edit_message_reply_markup(None)

    if cq.data == "start_confess":
        awaiting_confession.add(cq.from_user.id)
        await cq.message.reply_text("✍️ Lütfen itiraf metnini yazın:")
    else:
        await cq.message.reply_text(
            "❌ İtiraf etmekten vazgeçildi. Etmek istersen /start komutunu kullanabilirsiniz."
        )

async def confession_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private" or not update.message.text:
        return

    user_id = update.effective_user.id
    if user_id not in awaiting_confession:
        return

    text = update.message.text.strip()
    awaiting_confession.remove(user_id)

    keyboard = [
        [
            {"text": "✅ Onayla", "callback_data": f"onay_{update.message.message_id}"},
            {"text": "❌ Reddet", "callback_data": f"reddet_{update.message.message_id}"}
        ]
    ]
    reply_markup = {"inline_keyboard": keyboard}

    sent = await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=(
            f"📢 <b>Yeni İtiraf:</b>\n\n"
            f"{text}\n\n"
            f"👤 İtiraf Eden: {update.effective_user.mention_html()}"
        ),
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    pending[sent.message_id] = (user_id, text)
    await update.message.reply_text("🙌 İtirafınız yöneticilere iletildi, teşekkürler.")

async def decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()

    action, _ = cq.data.split("_", 1)
    msg_id = cq.message.message_id

    if msg_id not in pending:
        return await cq.answer("Bu itiraf zaten işlenmiş.", show_alert=True)

    user_id, text = pending.pop(msg_id)

    if action == "onay":
        html = (
            f"💬 <b>Yeni İtiraf:</b>\n\n"
            f"{text}\n\n"
            f'<a href="https://t.me/{BOT_USERNAME}?start">✒️İtiraf etmek için buraya tıkla!</a>\n\n'
            f'<a href="{CHANNEL_GROUP}">👥 İtiraf Grubuna gitmek için Buraya Tıkla!</a>'
        )
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=html,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await cq.edit_message_reply_markup(None)
        await cq.answer("İtiraf onaylandı ve kanala gönderildi.")
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="Üzgünüm, itirafınız uygun bulunmadı ve paylaşılmadı."
        )
        await cq.edit_message_reply_markup(None)
        await cq.answer("İtiraf reddedildi.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    # Eskimiş callback-query hatasını görmezden gel
    if isinstance(error, BadRequest) and "too old" in str(error).lower():
        return
    # Diğer hataları logla
    print(f"Unhandled error: {error!r}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(start_cb_handler, pattern="^start_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, confession_handler))
    app.add_handler(CallbackQueryHandler(decision_handler, pattern="^(onay|reddet)_"))

    # Global error handler
    app.add_error_handler(error_handler)

    print("Bot çalışıyor…")
    app.run_polling()

if __name__ == "__main__":
    main()
