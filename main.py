# أضف هذا الزر إلى قائمة الأزرار في دالة main_markup
def main_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_ar = types.KeyboardButton('🇸🇦 ترجمة إلى العربية')
    # ... بقية الأزرار ...
    markup.add(btn_ar)
    return markup

# أضف هذا الجزء داخل دالة handle_all_messages لمعالجة الضغط على الزر
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    cid = message.chat.id
    text = message.text

    if text == '🇸🇦 ترجمة إلى العربية':
        user_state[cid] = 'translate_to_ar'
        bot.send_message(cid, "أرسل النص بأي لغة (فرنسية، إنجليزية، صينية...) وسأحوله للعربية فوراً:")

    elif cid in user_state and user_state[cid] == 'translate_to_ar':
        try:
            # استخدام برومبت مخصص لضمان الفصاحة
            prompt = f"قم بترجمة النص التالي إلى لغة عربية فصحى بأسلوب بليغ وواضح، مع الحفاظ على المعنى الأصلي بدقة: {text}"
            response = model.generate_content(prompt)
            
            bot.reply_to(message, f"**الترجمة العربية:**\n\n{response.text}", parse_mode="Markdown")
            # لا نحذف الحالة هنا إذا كنت تريد ترجمة عدة نصوص متتالية، أو احذفها للعودة للقائمة
            # del user_state[cid] 
        except Exception as e:
            bot.reply_to(message, "عذراً، حدث خطأ أثناء محاولة الترجمة.")
