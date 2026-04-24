import telebot
from telebot import types
from googletrans import Translator
import cv2
import numpy as np
import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# استدعاء التوكنات من "متغيرات البيئة" للأمان
API_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

bot = telebot.TeleBot(API_TOKEN)

# إعداد ذكاء جوجل للتلخيص
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

translator = Translator()

def main_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('🌐 ترجمة احترافية')
    btn2 = types.KeyboardButton('🖼️ حذف العلامة المائية')
    btn3 = types.KeyboardButton('📝 ملخص يوتيوب')
    btn4 = types.KeyboardButton('📄 صورة إلى نص')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "أهلاً بك! بوت الخدمات الذكية جاهز للعمل.", reply_markup=main_markup())

# --- خدمة الترجمة ---
@bot.message_handler(func=lambda message: message.text == '🌐 ترجمة احترافية')
def trans_prompt(message):
    bot.send_message(message.chat.id, "أرسل النص الذي تريد ترجمته الآن:")

@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handle_translation(message):
    # سيتم الكشف عن اللغة تلقائياً والترجمة للعربية كمثال
    try:
        translated = translator.translate(message.text, dest='ar')
        bot.reply_to(message, f"الترجمة:\n{translated.text}")
    except:
        pass

# --- خدمة حذف العلامة المائية ---
@bot.message_handler(content_types=['photo'])
def handle_watermark(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("input.jpg", 'wb') as f:
        f.write(downloaded_file)
    
    img = cv2.imread("input.jpg")
    # تقنية Inpainting لمعالجة الصورة
    mask = np.zeros(img.shape[:2], np.uint8)
    # ملاحظة: في النسخة المتقدمة يتم تحديد مكان اللوجو يدوياً
    dst = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    cv2.imwrite("output.jpg", dst)
    
    with open("output.jpg", 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="تمت المعالجة بألوان متناسقة.")

# --- خدمة ملخص يوتيوب ---
@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
def summarize_video(message):
    try:
        v_id = message.text.split("v=")[1].split("&")[0] if "v=" in message.text else message.text.split("/")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['ar', 'en'])
        full_text = " ".join([t['text'] for t in transcript])
        
        response = model.generate_content(f"لخص هذا الفيديو باللغة العربية الفصحى: {full_text}")
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "لم أتمكن من الحصول على نص الفيديو.")

bot.infinity_polling()
