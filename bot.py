from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from persiantools.jdatetime import JalaliDate
import ollama  # Import the ollama library directly


#  Add your keys here
TELEGRAM_TOKEN = '8300310340:AAHX1hVfEG-U5P1CE0AjGMItpGZXwWWcNeI'

OLLAMA_MODEL = "mistral"  # Default model that works for most cases


def query_ollama(prompt):
    try:
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
            options={'temperature': 1}
        )
        return response['response'].strip()
    except Exception as e:
        print(f"Ollama error: {e}")
        return "❌ خطا در پردازش درخواست. لطفاً بعداً تلاش کنید."

async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        today = JalaliDate.today()
        months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                 "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
        persian_month_name = months[today.month - 1]

        await update.message.reply_text(f"🔍 در حال جستجوی مناسبت‌های ماه {persian_month_name}...")

        prompt = f"show '{persian_month_name}' in Persian, formatted as 'date: event' then at the end of the messegae propose and suggest some very creative ideas for doing special activities or campaigns for an ngo company who takes care of children with low social level, you can even suggest campaigns or ideas to raise fund for this ngo event named IMA"
        
        response_text = query_ollama(prompt)
        
        if not response_text or "❌" in response_text:
            await update.message.reply_text("⚠️ متأسفانه اطلاعات مناسبت‌ها در دسترس نیست.")
            return

        # Format the response
        formatted_lines = []
        for line in response_text.split('\n'):
            if ':' in line:
                date, event = line.split(':', 1)
                formatted_lines.append(f"• {date.strip()}: {event.strip()}")
        
        if not formatted_lines:
            await update.message.reply_text(f"مناسبت رسمی‌ای در ماه {persian_month_name} یافت نشد.")
            return

        reply_msg = f"📅 مناسبت‌های ماه {persian_month_name}:\n\n" + "\n".join(formatted_lines[:8])
        await update.message.reply_text(reply_msg)

    except Exception as e:
        print(f"Handler error: {e}")
        await update.message.reply_text("⚠️ خطایی در پردازش درخواست رخ داد.")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("Error: Telegram token not set!")
        print("Please set TELEGRAM_TOKEN environment variable")
        sys.exit(1)
    
    print(f"🤖 ربات آماده با مدل ...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("month", month_handler))
    app.run_polling()