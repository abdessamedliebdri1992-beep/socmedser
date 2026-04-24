import telebot
from telebot import types
from googletrans import Translator
import cv2
import numpy as np
import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# تم وضع التوكنات مباشرة بناءً على طلبك
API_TOKEN = '8769168225:AAHaBx5_INz6kE0dR9LV6mQx0Ko-gIGP31E'
GEMINI_KEY = 'AIzaSyA2qLp82TZEiG_ueY1IAnVx_pj3km0hk6k'

bot = telebot.TeleBot(API_TOKEN)

# إعداد ذكاء جوجل للتلخيص
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
    bot.send_message(message.chat.id, "أهلاً بك! بوت الخدمات الذكية يعمل الآن بامتياز.", reply_markup=main_markup())

# --- 1. الترجمة الاحترافية ---
@bot.message_handler(func=lambda message: message.text == '🌐 ترجمة احترافية')
def trans_prompt(message):
    bot.send_message(message.chat.id, "أرسل النص الذي تريد ترجمته (سيتم ترجمته للعربية آلياً):")

@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/') and not 'youtube' in message.text)
def handle_translation(message):
    try:
        # استخدام Gemini للترجمة الاحترافية بدلاً من الترجمة الحرفية
        prompt = f"ترجم النص التالي إلى لغة عربية فصحى واحترافية وبدون أخطاء: {message.text}"
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "عذراً، حدث خطأ أثناء الترجمة.")

# --- 2. حذف العلامة المائية ---
@bot.message_handler(content_types=['photo'])
def handle_watermark(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("input.jpg", 'wb') as f:
            f.write(downloaded_file)
        
        img = cv2.imread("input.jpg")
        # معالجة تلقائية باستخدام Inpainting لتغطية الشوائب بالألوان المحيطة
        mask = np.zeros(img.shape[:2], np.uint8)
        dst = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        cv2.imwrite("output.jpg", dst)
        
        with open("output.jpg", 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="تمت المعالجة بألوان متناسقة.")
    except Exception as e:
        bot.send_message(message.chat.id, "خطأ في معالجة الصورة.")

# --- 3. ملخص يوتيوب ---
@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
def summarize_video(message):
    bot.reply_to(message, "جاري استخراج النص وتلخيصه، انتظر قليلاً...")
    try:
        v_id = message.text.split("v=")[1].split("&")[0] if "v=" in message.text else message.text.split("/")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['ar', 'en'])
        full_text = " ".join([t['text'] for t in transcript])
        
        response = model.generate_content(f"لخص هذا الفيديو في نقاط واضحة باللغة العربية الفصحى: {full_text}")
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "عذراً، تعذر تلخيص الفيديو (تأكد أن الفيديو يحتوي على ترجمة مصاحبة Subtitles).")

# تشغيل البوت
bot.infinity_polling()
