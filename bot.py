import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHANNEL_ID = "@mrxstory"

question = {
    "text": "Настоящий джентльмен никогда не снимает пиджак на официальном мероприятии.",
    "answer": "Правда",
    "explanation": "В классическом дресс-коде снимать пиджак считается дурным тоном — особенно до тех пор, пока это не сделал хозяин вечера.",
    "image": "https://i.imgur.com/x4svhYy.jpeg"
}

def send_card():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Правда", callback_data="answer_Правда"),
        types.InlineKeyboardButton("❌ Ложь", callback_data="answer_Ложь")
    )
    bot.send_photo(CHANNEL_ID, question["image"],
                   caption=f"🎩 *{question['text']}*\n\nОтветьте на вопрос:",
                   parse_mode="Markdown", reply_markup=markup)

def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

@bot.callback_query_handler(func=lambda call: True)
def handle_answer(call):
    user_id = call.from_user.id
    if is_user_subscribed(user_id):
        answer = call.data.split("_")[1]
        if answer == question["answer"]:
            text = f"✅ Верно! {question['explanation']}"
        else:
            text = f"❌ Мимо. {question['explanation']}"
        bot.answer_callback_query(call.id, text=text, show_alert=True)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/mrxstory"))
        bot.send_message(user_id, "Подпишитесь на канал, чтобы узнать правильный ответ!", reply_markup=markup)
        bot.answer_callback_query(call.id)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def hello():
    return "Бот работает", 200

if __name__ == "__main__":
    send_card()
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get("WEBHOOK_URL") + "/" + TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
