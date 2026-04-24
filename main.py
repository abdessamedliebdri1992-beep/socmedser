import telebot
from telebot import types
import google.generativeai as genai
import os

# --- الإعدادات (التوكنات الخاصة بك) ---
API_TOKEN = '8769168225:AAHaBx5_INz6kE0dR9LV6mQx0Ko-gIGP31E'
GEMINI_KEY = 'AIzaSyA2qLp82TZEiG_ueY1IAnVx_pj3km0hk6k'

bot = telebot.TeleBot(API_TOKEN)

# إعداد محرك الذكاء الاصطناعي (Gemini)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# القائمة الرئيسية
def main_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_ar = types.KeyboardButton('🇸🇦 ترجمة أي لغة إلى العربية')
    markup.add(btn_ar)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "أهلاً بك في بوت الترجمة الاحترافية.\nاضغط على الزر بالأسفل ثم أرسل أي نص سأقوم بترجمته فوراً.",
        reply_markup=main_markup()
    )

# حالة المستخدم (للتأكد أنه ضغط على الزر)
user_states = {}

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    cid = message.chat.id
    text = message.text

    if text == '🇸🇦 ترجمة أي لغة إلى العربية':
        user_states[cid] = 'waiting_for_text'
        bot.send_message(cid, "حسناً، أرسل الآن النص (بالإنجليزية، الفرنسية، أو غيرها) وسأحوله للعربية.")
    
    elif cid in user_states and user_states[cid] == 'waiting_for_text':
        # إظهار حالة "جاري الكتابة" لإعطاء انطباع احترافي
        bot.send_chat_action(cid, 'typing')
        
        try:
            # البرومبت المخصص للذكاء الاصطناعي لضمان جودة الترجمة
            prompt = (
                f"أنت مترجم محترف. قم بترجمة النص التالي إلى لغة عربية فصحى، بليغة، "
                f"ومناسبة للسياق. تجنب الترجمة الحرفية تماماً:\n\n{text}"
            )
            
            response = model.generate_content(prompt)
            
            # إرسال النتيجة للمستخدم
            bot.reply_to(message, response.text)
            
            # ملاحظة: لم نحذف الحالة هنا لكي يستطيع المستخدم إرسال نصوص متتالية وترجمتها مباشرة
        except Exception as e:
            bot.reply_to(message, "عذراً، حدث خطأ في معالجة الطلب. يرجى المحاولة لاحقاً.")
    else:
        bot.send_message(cid, "من فضلك اضغط على الزر أولاً لبدء الترجمة.", reply_markup=main_markup())

# تشغيل البوت باستمرار
print("البوت يعمل الآن...")
bot.infinity_polling()
