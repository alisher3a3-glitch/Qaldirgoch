import os
import threading
import sqlite3
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "3594418817"))
CHANNEL = os.getenv("CHANNEL", "@qaldirgoch_mobile")
ADMIN_USERNAME = "@AliSheR"
BOT_USERNAME = "@AiElonchibot"

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    exit(1)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, *args): pass

def run_dummy():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), Handler)
        print(f"Dummy server on {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy error: {e}")

threading.Thread(target=run_dummy, daemon=True).start()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

conn = sqlite3.connect('elonlar.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS elonlar
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              channel_message_id INTEGER,
              kategoriya TEXT,
              model TEXT,
              xotira TEXT,
              batareya TEXT,
              rangi TEXT,
              komplekt TEXT,
              narx TEXT,
              tavsif TEXT,
              manzil TEXT,
              tel TEXT,
              bezovta_vaqti TEXT,
              rasmlar TEXT,
              status TEXT)""")
conn.commit()

user_states = {}

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📢 E'lon berish", "📋 Mening e'lonlarim")
    kb.add("🤝 Hamkorlik", "🛡️ Ishonchli savdo")
    kb.add("☕ Choy chaqa")
    return kb

def kategoriya_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📱 Smartphone", "📞 Knopkali telefon")
    kb.add("🎧 Aksessuar", "⬅️ Orqaga")
    return kb

def contact_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Raqamni ulashish", request_contact=True))
    kb.add("✍️ Yozib kiritish", "⬅️ Orqaga")
    return kb

def tasdiqlash_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Tasdiqlash va kanalga yuborish", "❌ Bekor qilish")
    return kb

@bot.message_handler(commands=['start', 'cancel'])
def start(message):
    user_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, f"👋 Assalomu alaykum!\n\n📱 <b>{CHANNEL} kanali</b>\nHar e'londa 🛡️ Ishonchli savdo mavjud!\n\n👇 Tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🤝 Hamkorlik")
def hamkorlik(m):
    bot.send_message(m.chat.id, f"🤝 Hamkorlik: {ADMIN_USERNAME}", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛡️ Ishonchli savdo")
def ishonchli(m):
    bot.send_message(m.chat.id, "🛡️ <b>Admin orqali ishonchli savdo</b>\n\n1. @AliSheR ga yozasiz\n2. Tekshiriladi\n3. Pul adminda turadi\n4. Hammasi OK bo'lsa almashiladi", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "☕ Choy chaqa")
def choy(m):
    bot.send_message(m.chat.id, "☕ Ixtiyoriy: 9860 3501 4726 3700", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📢 E'lon berish")
def elon_berish(m):
    user_states[m.from_user.id] = {"step": "kategoriya", "data": {}, "photos": []}
    bot.send_message(m.chat.id, "📂 Qaysi tur?", reply_markup=kategoriya_menu())

@bot.message_handler(func=lambda m: m.text == "⬅️ Orqaga")
def orqaga(m):
    user_states.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, "Asosiy menyu:", reply_markup=main_menu())

def make_caption(data, sold=False):
    xotira_line = f"💾 Xotira: {data.get('xotira','—')}\n" if data.get('xotira') and data.get('xotira') != "—" else ""
    batareya_line = f"🔋 Batareya: {data.get('batareya','—')}\n" if data.get('batareya') and data.get('batareya') != "—" else ""
    sold_header = "✅ <b>SOTILDI!</b>\n\n" if sold else ""
    return f"""{sold_header}<b>{data['kategoriya']} — {data['model']}</b>

{xotira_line}{batareya_line}🎨 Rangi: {data['rangi']}
📦 Komplekt: {data['komplekt']}
💰 Narxi: {data['narx']}

📝 {data['tavsif']}

📍 {data['manzil']}
📞 {data['tel']}
⏰ {data['bezovta_vaqti']}

—————————————
🛡️ <b>ISHONCHLI SAVDO MAVJUD!</b>
Admin {ADMIN_USERNAME} orqali xavfsiz.

📢 {CHANNEL} | {BOT_USERNAME}
"""

@bot.message_handler(content_types=['text', 'contact', 'photo'])
def state_handler(message):
    uid = message.from_user.id
    if uid not in user_states:
        return
    st = user_states[uid]
    step = st["step"]
    data = st["data"]

    if step == "kategoriya":
        if message.text not in ["📱 Smartphone", "📞 Knopkali telefon", "🎧 Aksessuar"]:
            return
        data["kategoriya"] = message.text
        st["step"] = "model"
        bot.send_message(message.chat.id, "📱 Telefon modelini yozing:\nMisol: iPhone 13 Pro", reply_markup=types.ReplyKeyboardRemove())
        return

    if step == "model":
        data["model"] = message.text.strip()
        if "iphone" in data["model"].lower():
            st["step"] = "xotira"
            bot.send_message(message.chat.id, "💾 Xotirasi qancha?\nMisol: 128GB")
        else:
            data["xotira"] = "—"
            st["step"] = "rangi"
            bot.send_message(message.chat.id, "🎨 Rangi qanday?\nMisol: Qora")
        return

    if step == "xotira":
        data["xotira"] = message.text.strip()
        st["step"] = "batareya"
        bot.send_message(message.chat.id, "🔋 Batareya holati %?\nMisol: 85%")
        return

    if step == "batareya":
        data["batareya"] = message.text.strip()
        st["step"] = "rangi"
        bot.send_message(message.chat.id, "🎨 Rangi?")
        return

    if step == "rangi":
        data["rangi"] = message.text.strip()
        st["step"] = "komplekt"
        bot.send_message(message.chat.id, "📦 Komplekti?\nMisol: Karobka, zaryadnik")
        return

    if step == "komplekt":
        data["komplekt"] = message.text.strip()
        st["step"] = "narx"
        bot.send_message(message.chat.id, "💰 Narxi qancha?\nMisol: 3 500 000 so'm")
        return

    if step == "narx":
        data["narx"] = message.text.strip()
        st["step"] = "rasm"
        bot.send_message(message.chat.id, "📸 Endi telefon rasmlarini yuboring (10 tagacha).\nTayyor bo'lgach '✅ Tayyor' deb yozing:")
        return

    if step == "rasm":
        if message.content_type == 'photo':
            if len(st["photos"]) < 10:
                st["photos"].append(message.photo[-1].file_id)
                bot.send_message(message.chat.id, f"✅ {len(st['photos'])}/10 qabul qilindi. Yana yuboring yoki '✅ Tayyor' deb yozing.")
            else:
                bot.send_message(message.chat.id, "✅ 10 ta rasm bo'ldi. '✅ Tayyor' deb yozing.")
            return
        if message.text in ["✅ Tayyor", "Tayyor", "✅ Rasmlar tayyor", "✅"]:
            if not st["photos"]:
                bot.send_message(message.chat.id, "❗ Iltimos kamida 1 ta rasm yuboring!")
                return
            st["step"] = "tavsif"
            bot.send_message(message.chat.id, "📝 Telefon haqida qisqa tavsif yozing:\nMisol: Ideal holatda, hech qanday nuqsoni yo'q")
            return
        return

    if step == "tavsif":
        data["tavsif"] = message.text.strip()
        st["step"] = "manzil"
        bot.send_message(message.chat.id, "📍 Manzilingizni kiriting (masalan: Namangan sh, Chorsu):")
        return

    if step == "manzil":
        txt = message.text.strip()
        if len(txt) < 4 or txt.lower() in ["salom", "ha", "yoq", "yo'q", "hi", "hello", "assalom"]:
            bot.send_message(message.chat.id, "❗ Iltimos, haqiqiy manzil yozing!\nMasalan: Namangan sh, Chorsu")
            return
        data["manzil"] = txt
        st["step"] = "tel"
        bot.send_message(message.chat.id, "📞 Telefon raqamingizni tugma orqali yuboring:", reply_markup=contact_menu())
        return

    if step == "tel":
        if message.content_type == 'contact' and message.contact:
            data["tel"] = message.contact.phone_number
        else:
            if message.text == "✍️ Yozib kiritish":
                bot.send_message(message.chat.id, "📞 Raqamingizni yozing:\nMisol: +998901234567", reply_markup=types.ReplyKeyboardRemove())
                st["step"] = "tel_yozish"
                return
            txt = message.text.strip() if message.text else ""
            if len(txt) < 9 or txt.lower() in ["salom", "ha", "yoq", "yo'q", "hi"]:
                bot.send_message(message.chat.id, "❗ Iltimos, to'g'ri telefon raqam yozing yoki pastdagi tugmani bosing!\nMisol: +998901234567")
                return
            data["tel"] = txt
        st["step"] = "bezovta"
        bot.send_message(message.chat.id, "⏰ Qachon bezovta qilmaslik kerak?\nMisol: 22:00 dan keyin qo'ng'iroq qilmang", reply_markup=types.ReplyKeyboardRemove())
        return

    if step == "tel_yozish":
        txt = message.text.strip()
        if len(txt) < 9:
            bot.send_message(message.chat.id, "❗ Noto'g'ri raqam, qayta yozing:")
            return
        data["tel"] = txt
        st["step"] = "bezovta"
        bot.send_message(message.chat.id, "⏰ Bezovta vaqti?")
        return

    if step == "bezovta":
        data["bezovta_vaqti"] = message.text.strip()
        preview = make_caption(data)
        st["step"] = "tasdiqlash"
        try:
            if len(st["photos"]) == 1:
                bot.send_photo(message.chat.id, st["photos"][0], caption=preview)
            else:
                bot.send_media_group(message.chat.id, [types.InputMediaPhoto(fid, caption=preview if i==0 else "") for i, fid in enumerate(st["photos"])])
        except:
            bot.send_message(message.chat.id, preview)
        bot.send_message(message.chat.id, "👆 Shunday chiqadi. Tasdiqlaysizmi?", reply_markup=tasdiqlash_menu())
        return

    if step == "tasdiqlash":
        if message.text == "✅ Tasdiqlash va kanalga yuborish":
            caption = make_caption(data)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("📞 Sotuvchi bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
            markup.add(types.InlineKeyboardButton("🛡️ Admin orqali xavfsiz olish", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
            try:
                if len(st["photos"]) == 1:
                    sent = bot.send_photo(CHANNEL, st["photos"][0], caption=caption, reply_markup=markup)
                    ch_id = sent.message_id
                else:
                    msgs = bot.send_media_group(CHANNEL, [types.InputMediaPhoto(fid, caption=caption if i==0 else "") for i, fid in enumerate(st["photos"])])
                    bot.send_message(CHANNEL, f"☝️ {data['model']} - Bog'lanish:", reply_markup=markup)
                    ch_id = msgs[0].message_id
                c.execute("INSERT INTO elonlar (user_id, channel_message_id, kategoriya, model, xotira, batareya, rangi, komplekt, narx, tavsif, manzil, tel, bezovta_vaqti, rasmlar, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (uid, ch_id, data['kategoriya'], data['model'], data.get('xotira','—'), data.get('batareya','—'), data['rangi'], data['komplekt'], data['narx'], data['tavsif'], data['manzil'], data['tel'], data['bezovta_vaqti'], ",".join(st["photos"]), "active"))
                conn.commit()
                bot.send_message(message.chat.id, f"✅ E'loningiz {CHANNEL} kanaliga joylandi!", reply_markup=main_menu())
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Xato: {e}\nBotni kanalda admin qiling!", reply_markup=main_menu())
            user_states.pop(uid, None)
        else:
            bot.send_message(message.chat.id, "❌ Bekor qilindi.", reply_markup=main_menu())
            user_states.pop(uid, None)

@bot.message_handler(func=lambda m: m.text == "📋 Mening e'lonlarim")
def my(m):
    c.execute("SELECT id, model, narx, status, channel_message_id FROM elonlar WHERE user_id=? ORDER BY id DESC", (m.from_user.id,))
    rows = c.fetchall()
    if not rows:
        bot.send_message(m.chat.id, "📭 E'lonlaringiz yo'q", reply_markup=main_menu())
        return
    for eid, model, narx, status, chmid in rows:
        icon = "✅ SOTILDI" if status=="sold" else "🟢 Aktiv"
        kb = types.InlineKeyboardMarkup()
        if status=="active":
            kb.add(types.InlineKeyboardButton("✅ SOTILDI deb belgilash", callback_data=f"sold_{eid}_{chmid}"))
        bot.send_message(m.chat.id, f"{icon}\n📱 {model}\n💰 {narx}", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    if call.data.startswith("sold_"):
        _, eid, chmid = call.data.split("_")
        c.execute("UPDATE elonlar SET status='sold' WHERE id=?", (eid,))
        conn.commit()
        try:
            c.execute("SELECT kategoriya, model, xotira, batareya, rangi, komplekt, narx, tavsif, manzil, tel, bezovta_vaqti FROM elonlar WHERE id=?", (eid,))
            r = c.fetchone()
            if r:
                d = {"kategoriya":r[0],"model":r[1],"xotira":r[2],"batareya":r[3],"rangi":r[4],"komplekt":r[5],"narx":r[6],"tavsif":r[7],"manzil":r[8],"tel":r[9],"bezovta_vaqti":r[10]}
                bot.edit_message_caption(chat_id=CHANNEL, message_id=int(chmid), caption=make_caption(d, sold=True))
        except Exception as e:
            print(e)
        bot.answer_callback_query(call.id, "✅ Sotildi!")
        bot.send_message(call.message.chat.id, "🎉 Tabriklaymiz! E'lon SOTILDI deb belgilandi!\n☕ Ixtiyoriy choy chaqa: 9860350147263700")

print("Bot polling started... V3 FINAL")
bot.infinity_polling()
