import time
import telebot

TOKEN = '8170642575:AAGan_GxI21GU7hAU4ktRDZRfI4sqRmAOHY'
ADMIN_IDS = [6840212721, 7545364150, 6327194120, 5128118019]

bot = telebot.TeleBot(TOKEN)
current_join_message = {"type": "text", "content": "Merhaba! Gruba katılma isteğiniz alındı."}

def is_admin(user_id):
    return user_id in ADMIN_IDS

@bot.message_handler(commands=['yap'])
def set_join_message(message):
    global current_join_message
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Bu komutu kullanma yetkiniz yok!")
        return

    caption = message.text.replace('/yap', '', 1).strip()
    # Yanıtlanan mesajı kontrol et (medya/metin ayarı)
    if message.reply_to_message:
        replied = message.reply_to_message
        if replied.text:
            msg_type, content = "text", replied.text
            current_join_message = {"type": msg_type, "content": content}
            bot.reply_to(message, "✅ Katılım mesajı başarıyla güncellendi!")
            return
        elif replied.photo:
            msg_type, content = "photo", replied.photo[-1].file_id
        elif replied.document:
            msg_type, content = "document", replied.document.file_id
        elif replied.video:
            msg_type, content = "video", replied.video.file_id
        else:
            bot.reply_to(message, "Bu medya türü desteklenmiyor.")
            return

        # Medya + caption destekli
        current_join_message = {
            "type": msg_type,
            "content": content,
            "caption": caption if caption else None
        }
        bot.reply_to(message, "✅ Katılım mesajı başarıyla güncellendi (medya + mesaj)!")
    else:
        if not caption:
            bot.reply_to(message, "Lütfen bir mesaj yazın veya bir mesaja yanıt verin.")
            return
        current_join_message = {"type": "text", "content": caption}
        bot.reply_to(message, "✅ Katılım mesajı başarıyla güncellendi!")

@bot.chat_join_request_handler()
def handle_chat_join_request(message):
    try:
        msg = current_join_message
        if msg["type"] == "text":
            bot.send_message(message.from_user.id, msg["content"])
        elif msg["type"] == "photo":
            bot.send_photo(message.from_user.id, msg["content"], caption=msg.get("caption"))
        elif msg["type"] == "document":
            bot.send_document(message.from_user.id, msg["content"], caption=msg.get("caption"))
        elif msg["type"] == "video":
            bot.send_video(message.from_user.id, msg["content"], caption=msg.get("caption"))
        else:
            bot.send_message(message.from_user.id, "Katılım mesajı gönderilemiyor.")
    except Exception as e:
        print(f"Error: {e}")

if name == "__main__":
    while True:
        try:
            print("Bot çalışıyor...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            time.sleep(5)
