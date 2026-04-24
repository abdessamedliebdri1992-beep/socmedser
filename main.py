import telebot
from telebot import types
import cv2
import numpy as np
import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from PIL import Image
import pytesseract

# المفاتيح الخاصة بك
API_TOKEN = '8769168225:AAHaBx5_INz6kE0dR9LV6mQx0Ko-gIGP31E'
GEMINI_KEY = 'AIzaSyA2qLp82TZEiG_ueY1IAnVx_pj3km0hk6k'

bot = telebot.TeleBot(API_TOKEN)

# إعداد Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

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
    bot.send_message(message.chat.id, "مرحباً بك! اختر الخدمة التي تريدها:", reply_markup=main_markup())

# مخزن مؤقت لحالة المستخدم
user_state = {}

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    cid = message.chat.id
    text = message.text

    if text == '🌐 ترجمة احترافية':
        user_state[cid] = 'waiting_for_translate'
        bot.send_message(cid, "أرسل النص الذي تريد ترجمته باحترافية الآن:")
    
    elif text == '🖼️ حذف العلامة المائية':
        user_state[cid] = 'waiting_for_watermark'
        bot.send_message(cid, "أرسل الصورة التي تحتوي على العلامة المائية.")

    elif text == '📝 ملخص يوتيوب':
        user_state[cid] = 'waiting_for_yt'
        bot.send_message(cid, "أرسل رابط فيديو اليوتيوب الآن:")

    elif text == '📄 صورة إلى نص':
        user_state[cid] = 'waiting_for_ocr'
        bot.send_message(cid, "أرسل صورة تحتوي على نص واضح.")

    # معالجة النصوص بناءً على الحالة
    elif cid in user_state:
        if user_state[cid] == 'waiting_for_translate':
            try:
                response = model.generate_content(f"ترجم النص التالي للعربية باحترافية وسياق طبيعي: {text}")
                bot.reply_to(message, response.text)
                del user_state[cid]
            except:
                bot.reply_to(message, "حدث خطأ في الاتصال بالذكاء الاصطناعي.")
        
        elif user_state[cid] == 'waiting_for_yt' and ('youtube' in text or 'youtu.be' in text):
            try:
                v_id = text.split("v=")[1].split("&")[0] if "v=" in text else text.split("/")[-1]
                transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['ar', 'en'])
                full_text = " ".join([t['text'] for t in transcript])
                response = model.generate_content(f"لخص هذا الفيديو في نقاط باللغة العربية: {full_text}")
                bot.reply_to(message, response.text)
                del user_state[cid]
            except:
                bot.reply_to(message, "تعذر استخراج نص الفيديو.")

# معالجة الصور (لحذف العلامة أو OCR)
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    cid = message.chat.id
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("input.jpg", 'wb') as f:
        f.write(downloaded_file)

    if cid in user_state and user_state[cid] == 'waiting_for_ocr':
        try:
            # استخدام Gemini لتحويل الصورة لنص (أدق من الطرق التقليدية)
            img = Image.open("input.jpg")
            response = model.generate_content(["استخرج النص الموجود في هذه الصورة بدقة وبنفس لغته:", img])
            bot.reply_to(message, response.text)
        except:
            bot.reply_to(message, "فشل استخراج النص من الصورة.")
    
    else: # الحالة الافتراضية حذف العلامة المائية
        img = cv2.imread("input.jpg")
        mask = np.zeros(img.shape[:2], np.uint8)
        dst = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        cv2.imwrite("output.jpg", dst)
        with open("output.jpg", 'rb') as photo:
            bot.send_photo(cid, photo, caption="تمت المعالجة بنجاح.")

bot.infinity_polling()
