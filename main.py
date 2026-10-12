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
        self.wfile.write(b"Bot V6 running")
    def log_message(self, *args):
        pass

def run_dummy():
    port = int(os.environ.get("PORT", 10000))
    try:
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()
    except:
        pass

threading.Thread(target=run_dummy, daemon=True).start()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

conn = sqlite3.connect('elonlar.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS elonlar
             (id INTEGER PRIMARY KEY, user_id INTEGER, channel_message_id INTEGER,
              kategoriya TEXT, model TEXT, xotira TEXT, batareya TEXT, rangi TEXT,
              komplekt TEXT, narx TEXT, tavsif TEXT, manzil TEXT, tel TEXT,
              bezovta_vaqti TEXT, rasmlar TEXT, status TEXT)""")
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

def tasdiq_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Tasdiqlash va kanalga yuborish", "❌ Bekor qilish")
    return kb

def rasm_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Tayyor")
    return kb

@bot.message_handler(commands=['start', 'cancel'])
def start(m):
    user_states.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, f"👋 Assalomu alaykum!\n\n📱 <b>{CHANNEL}</b> kanali boti\n\n👇 Menudan tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["🤝 Hamkorlik", "🛡️ Ishonchli savdo", "☕ Choy chaqa", "⬅️ Orqaga"])
def info(m):
    if m.text == "🤝 Hamkorlik":
        bot.send_message(m.chat.id, f"🤝 Reklama va hamkorlik uchun: {ADMIN_USERNAME}", reply_markup=main_menu())
    elif m.text == "🛡️ Ishonchli savdo":
        bot.send_message(m.chat.id, "🛡️ <b>Ishonchli savdo:</b>\n\n1. @AliSheR ga ikkala taraf yozadi\n2. Telefon tekshiriladi\n3. Pul adminda turadi\n4. Hammasi joyida bo'lsa almashiladi", reply_markup=main_menu())
    elif m.text == "☕ Choy chaqa":
        bot.send_message(m.chat.id, "☕ Rahmat! 9860350147263700 (Alisher)", reply_markup=main_menu())
    else:
        user_states.pop(m.from_user.id, None)
        bot.send_message(m.chat.id, "Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📢 E'lon berish")
def elon(m):
    user_states[m.from_user.id] = {"step": "kategoriya", "data": {}, "photos": []}
    bot.send_message(m.chat.id, "📂 Qaysi turdagi telefon?", reply_markup=kategoriya_menu())

def make_caption(d, sold=False):
    sold_top = "✅ <b>SOTILDI!</b>\n" if sold else ""
    xotira = ""
    if d.get('xotira') and d['xotira'] != "—":
        xotira = f"💾 Xotira: {d['xotira']}\n"
    batareya = ""
    bval = d.get('batareya', '—')
    if bval and bval != "—":
        if any(k in d.get('model','').lower() for k in ["iphone", "ayfon", "айфон"]):
            batareya = f"🔋 Yomkost: {bval}\n"
        else:
            batareya = f"🔋 Batareya: {bval}\n"
    model_tag = "#" + d['model'].replace(' ', '_').replace('-', '_')[:20]
    manzil_first = d['manzil'].split()[0].replace(',', '').replace(' ', '_')
    manzil_tag = "#" + manzil_first
    return f"{sold_top}<b>📱 {d['kategoriya']} — {d['model']}</b>\n{xotira}{batareya}🎨 Rangi: {d['rangi']}\n📦 Komplekt: {d['komplekt']}\n💰 <b>Narxi: {d['narx']}</b>\n📝 {d['tavsif']}\n📍 Manzil: {d['manzil']}\n📞 Tel: {d['tel']}\n⏰ {d['bezovta_vaqti']}\n——————————\n🛡️ <b>ISHONCHLI SAVDO MAVJUD</b>\nAdmin {ADMIN_USERNAME} orqali xavfsiz xarid\n📢 {CHANNEL} | {BOT_USERNAME}\n{model_tag} {manzil_tag}"

@bot.message_handler(content_types=['text', 'contact', 'photo'])
def handler(message):
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
        bot.send_message(message.chat.id, "📱 Modelini yozing:\nMisol: iPhone 14", reply_markup=types.ReplyKeyboardRemove())
        return

    if step == "model":
        txt = message.text.strip()
        if len(txt) < 2:
            bot.send_message(message.chat.id, "❗ Modelni to'liq yozing!")
            return
        data["model"] = txt
        if any(k in txt.lower() for k in ["iphone", "ayfon", "айфон"]):
            st["step"] = "xotira"
            bot.send_message(message.chat.id, "💾 Xotirasi? (Misol: 128GB)")
        else:
            data["xotira"] = "—"
            st["step"] = "rangi"
            bot.send_message(message.chat.id, "🎨 Rangi? (Misol: Qora)")
        return

    if step == "xotira":
        data["xotira"] = message.text.strip()
        st["step"] = "batareya"
        bot.send_message(message.chat.id, "🔋 Yomkost nechi %? (Misol: 85%)")
        return

    if step == "batareya":
        data["batareya"] = message.text.strip()
        st["step"] = "rangi"
        bot.send_message(message.chat.id, "🎨 Rangi? (Misol: Qora)")
        return

    if step == "rangi":
        data["rangi"] = message.text.strip()
        st["step"] = "komplekt"
        bot.send_message(message.chat.id, "📦 Komplekt nima bor? (Misol: Karobka, kabel)")
        return

    if step == "komplekt":
        data["komplekt"] = message.text.strip()
        st["step"] = "narx"
        bot.send_message(message.chat.id, "💰 Narxi? (Misol: 7 000 000 so'm)")
        return

    if step == "narx":
        data["narx"] = message.text.strip()
        st["step"] = "rasm"
        bot.send_message(message.chat.id, "📸 Telefon rasmlarini yuboring (1-10 ta).", reply_markup=rasm_menu())
        return

    if step == "rasm":
        if message.content_type == 'photo':
            if len(st["photos"]) < 10:
                st["photos"].append(message.photo[-1].file_id)
                bot.send_message(message.chat.id, f"✅ {len(st['photos'])} ta qabul qilindi.", reply_markup=rasm_menu())
            else:
                bot.send_message(message.chat.id, "10 ta bo'ldi, pastdagi ✅ Tayyor ni bosing.", reply_markup=rasm_menu())
            return
        if message.text == "✅ Tayyor":
            if not st["photos"]:
                bot.send_message(message.chat.id, "❗ Kamida 1 ta rasm kerak!", reply_markup=rasm_menu())
                return
            st["step"] = "tavsif"
            bot.send_message(message.chat.id, "📝 Tavsif yozing:\nMisol: Ideal holatda, karobka hujjatlari bor, aybi yo'q", reply_markup=types.ReplyKeyboardRemove())
            return
        return

    if step == "tavsif":
        txt = message.text.strip()
        if len(txt) < 5:
            bot.send_message(message.chat.id, "❗ Tavsifni batafsilroq yozing (kamida 5 harf)")
            return
        data["tavsif"] = txt
        st["step"] = "manzil"
        bot.send_message(message.chat.id, "📍 Manzilni yozing:\nMisol: Namangan sh, Chorsu")
        return

    if step == "manzil":
        txt = message.text.strip()
        if len(txt) < 4 or txt.lower() in ["salom", "ha", "yoq", "hi", "hello", "assalom"]:
            bot.send_message(message.chat.id, "❗ Haqiqiy manzil yozing!\nMisol: Namangan sh")
            return
        data["manzil"] = txt
        st["step"] = "tel"
        bot.send_message(message.chat.id, "📞 Telefon raqamingizni yuboring:", reply_markup=contact_menu())
        return

    if step == "tel":
        if message.content_type == 'contact':
            data["tel"] = message.contact.phone_number
        else:
            if message.text == "✍️ Yozib kiritish":
                bot.send_message(message.chat.id, "📞 Raqamni +998 bilan yozing:\n+998913437333", reply_markup=types.ReplyKeyboardRemove())
                st["step"] = "tel_yozish"
                return
            txt = (message.text or "").strip()
            if len(txt) < 9 or txt.lower() in ["salom", "ha"]:
                bot.send_message(message.chat.id, "❗ To'g'ri raqam yozing!\nMisol: +998913437333")
                return
            data["tel"] = txt
        st["step"] = "bezovta"
        bot.send_message(message.chat.id, "⏰ Qachon qo'ng'iroq qilmaslik kerak?\nMisol: 22:00 dan keyin qo'ng'iroq qilmang", reply_markup=types.ReplyKeyboardRemove())
        return

    if step == "tel_yozish":
        txt = message.text.strip()
        if len(txt) < 9:
            bot.send_message(message.chat.id, "❗ Noto'g'ri raqam!")
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
                bot.send_photo(message.chat.id, st["photos"][0], caption=preview, parse_mode="HTML")
            else:
                bot.send_media_group(message.chat.id, [types.InputMediaPhoto(f, caption=preview if i==0 else "", parse_mode="HTML") for i,f in enumerate(st["photos"])])
                bot.send_message(message.chat.id, "👆 Yuqoridagi kabi chiqadi")
        except Exception as e:
            bot.send_message(message.chat.id, f"{preview}\n\n(e:{e})", parse_mode="HTML")
        bot.send_message(message.chat.id, "Tasdiqlaysizmi?", reply_markup=tasdiq_menu())
        return

    if step == "tasdiqlash":
        if message.text == "✅ Tasdiqlash va kanalga yuborish":
            cap = make_caption(data)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("📞 Sotuvchi bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
            markup.add(types.InlineKeyboardButton("🛡️ Admin orqali xavfsiz olish", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
            try:
                if len(st["photos"]) == 1:
                    sent = bot.send_photo(CHANNEL, st["photos"][0], caption=cap, reply_markup=markup, parse_mode="HTML")
                    ch_id = sent.message_id
                else:
                    msgs = bot.send_media_group(CHANNEL, [types.InputMediaPhoto(f, caption=cap if i==0 else "", parse_mode="HTML") for i,f in enumerate(st["photos"])])
                    bot.send_message(CHANNEL, f"☝️ {data['model']} — Bog'lanish uchun:", reply_markup=markup)
                    ch_id = msgs[0].message_id
                c.execute("INSERT INTO elonlar (user_id, channel_message_id, kategoriya, model, xotira, batareya, rangi, komplekt, narx, tavsif, manzil, tel, bezovta_vaqti, rasmlar, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (uid, ch_id, data['kategoriya'], data['model'], data.get('xotira','—'), data.get('batareya','—'), data['rangi'], data['komplekt'], data['narx'], data['tavsif'], data['manzil'], data['tel'], data['bezovta_vaqti'], ",".join(st["photos"]), "active"))
                conn.commit()
                bot.send_message(message.chat.id, f"✅ {CHANNEL} ga joylandi!", reply_markup=main_menu())
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Xato: {e}\nBotni kanalda admin qiling!", reply_markup=main_menu())
            user_states.pop(uid, None)
        else:
            bot.send_message(message.chat.id, "❌ Bekor qilindi.", reply_markup=main_menu())
            user_states.pop(uid, None)

@bot.message_handler(func=lambda m: m.text == "📋 Mening e'lonlarim")
def my(m):
    c.execute("SELECT id, model, narx, status, channel_message_id FROM elonlar WHERE user_id=? ORDER BY id DESC LIMIT 10", (m.from_user.id,))
    rows = c.fetchall()
    if not rows:
        bot.send_message(m.chat.id, "📭 E'lon yo'q", reply_markup=main_menu())
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
                bot.edit_message_caption(chat_id=CHANNEL, message_id=int(chmid), caption=make_caption(d, sold=True), parse_mode="HTML")
        except:
            pass
        bot.answer_callback_query(call.id, "✅ Sotildi!")
        bot.send_message(call.message.chat.id, "✅ SOTILDI deb belgilandi!")

print("Bot V6 FIXED started - yomkost, tayyor knopka, no empty lines")
bot.infinity_polling()
