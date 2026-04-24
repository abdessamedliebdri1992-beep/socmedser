import telebot
from telebot import types
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# --- الإعدادات الخاصة بك ---
API_TOKEN = '8769168225:AAHaBx5_INz6kE0dR9LV6mQx0Ko-gIGP31E'
MISTRAL_API_KEY = 'Y4UUIW4EaWIv2i7ZrNYICRgYMYS7vTHb'

bot = telebot.TeleBot(API_TOKEN)
client = MistralClient(api_key=MISTRAL_API_KEY)

# القائمة الرئيسية
def main_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_ar = types.KeyboardButton('🇸🇦 ترجمة أي لغة إلى العربية')
    markup.add(btn_ar)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "أهلاً بك! بوت الترجمة الاحترافية المدعوم بـ Mistral AI جاهز.\nاضغط على الزر بالأسفل ثم أرسل النص.",
        reply_markup=main_markup()
    )

# تخزين حالة المستخدم
user_states = {}

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    cid = message.chat.id
    text = message.text

    if text == '🇸🇦 ترجمة أي لغة إلى العربية':
        user_states[cid] = 'waiting_text'
        bot.send_message(cid, "حسناً، أرسل النص الآن (الإنجليزية، الفرنسية، إلخ) وسأحوله للعربية فوراً.")
    
    elif cid in user_states and user_states[cid] == 'waiting_text':
        bot.send_chat_action(cid, 'typing')
        try:
            # صياغة الطلب لـ Mistral
            instruction = (
                "You are a professional translator. Translate the following text into "
                "pure, eloquent, and natural-sounding Arabic. Do not provide literal translation: "
            )
            
            messages = [
                ChatMessage(role="user", content=f"{instruction}\n\n{text}")
            ]
            
            # تنفيذ الترجمة باستخدام موديل mistral-medium (أو mistral-tiny للسرعة)
            chat_response = client.chat(
                model="mistral-medium",
                messages=messages,
            )
            
            result = chat_response.choices[0].message.content
            bot.reply_to(message, result)
            
        except Exception as e:
            # تنبيه في حال وجود مشكلة في المفتاح أو الخدمة
            bot.reply_to(message, f"عذراً، حدث خطأ في الاتصال بـ Mistral. تأكد من رصيد الحساب أو المحاولة لاحقاً.")
            print(f"Error: {e}")
    else:
        bot.send_message(cid, "من فضلك اضغط على الزر أولاً لبدء الترجمة.", reply_markup=main_markup())

# تشغيل البوت
print("Mistral Bot is running...")
bot.infinity_polling()
