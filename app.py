from datetime import datetime
from functools import wraps
import sqlite3
from flask import Flask, Response, redirect, render_template_string, request, url_for

app = Flask(__name__)

# მენეჯერის პარამეტრები
MANAGER_USER = "admin"
MANAGER_PASS = "saqartvelo123"


def check_auth(username, password):
  return username == MANAGER_USER and password == MANAGER_PASS


def authenticate():
  return Response(
      "არასწორი მონაცემები. გთხოვთ, შეიყვანოთ სწორი სახელი და პაროლი.",
      401,
      {"WWW-Authenticate": 'Basic realm="Login Required"'},
  )


def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
      return authenticate()
    return f(*args, **kwargs)

  return decorated


# ბაზის ინიციალიზაცია
def init_db():
  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id TEXT,
            room_number TEXT,
            message TEXT,
            status TEXT DEFAULT 'ახალი',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
  conn.commit()
  conn.close()


init_db()

# მრავალენოვანი ლექსიკონი (8 ენა)
TRANSLATIONS = {
    "es": {
        "title": "Servicio de Habitaciones",
        "hotel": "Hotel",
        "room": "Habitación",
        "subtitle": "Escriba su solicitud:",
        "success_msg": "¡Solicitud enviada con éxito! Nos pondremos en contacto.",
        "placeholder": "Ej: Necesito toallas adicionales...",
        "send_btn": "Enviar",
    },
    "ka": {
        "title": "სასტუმროს ოთახის სერვისი",
        "hotel": "სასტუმრო",
        "room": "ოთახი",
        "subtitle": "მოგვწერეთ თქვენი მოთხოვნა:",
        "success_msg": (
            "მოთხოვნა წარმატებით გაიგზავნა! მალე დაგიკავშირდებით."
        ),
        "placeholder": "მაგ: მჭირდება დამატებითი პირსახოცი...",
        "send_btn": "გაგზავნა",
    },
    "en": {
        "title": "Hotel Room Service",
        "hotel": "Hotel",
        "room": "Room",
        "subtitle": "Write your request below:",
        "success_msg": "Request sent successfully! We will contact you soon.",
        "placeholder": "E.g. Need extra towels...",
        "send_btn": "Send Request",
    },
    "ru": {
        "title": "Обслуживание номеров",
        "hotel": "Отель",
        "room": "Номер",
        "subtitle": "Напишите ваш запрос:",
        "success_msg": "Запрос успешно отправлен! Скоро мы с вами свяжемся.",
        "placeholder": "Напр: Нужно дополнительное полотенце...",
        "send_btn": "Отправить",
    },
    "fr": {
        "title": "Service d'étage",
        "hotel": "Hôtel",
        "room": "Chambre",
        "subtitle": "Écrivez votre demande:",
        "success_msg": "Demande envoyée avec succès! Nous vous contacterons.",
        "placeholder": "Ex: J'ai besoin de serviettes supplémentaires...",
        "send_btn": "Envoyer",
    },
    "de": {
        "title": "Zimmerservice",
        "hotel": "Hotel",
        "room": "Zimmer",
        "subtitle": "Schreiben Sie Ihre Anfrage:",
        "success_msg": (
            "Anfrage erfolgreich gesendet! Wir werden Sie kontaktieren."
        ),
        "placeholder": "Bsp: Ich brauche zusätzliche Handtücher...",
        "send_btn": "Senden",
    },
    "ar": {
        "title": "خدمة الغرف",
        "hotel": "الفندق",
        "room": "الغرفة",
        "subtitle": "اكتب طلبك أدناه:",
        "success_msg": "تم إرسال الطلب بنجاح! سنتواصل معك قريباً.",
        "placeholder": "مثال: أتاج مناشف إضافية...",
        "send_btn": "إرسال",
    },
    "tr": {
        "title": "Oda Servisi",
        "hotel": "Otel",
        "room": "Oda",
        "subtitle": "İsteğinizi aşağıya yazın:",
        "success_msg": (
            "İstek başarıyla gönderildi! Sizinle en kısa sürede"
            " iletişime geçeceğiz."
        ),
        "placeholder": "Örn: Ek havlu lazımdı...",
        "send_btn": "Gönder",
    },
}

# მომხმარებლის დიზაინი
USER_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" {% if lang == 'ar' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col justify-between">
    <div class="max-w-md mx-auto p-6 w-full bg-white shadow-xl rounded-2xl my-auto mt-6">
        
        <!-- ენების გადართვა (ესპანური პირველ ადგილზე) -->
        <div class="flex flex-wrap justify-center gap-1.5 mb-6 text-xs font-semibold">
            <a href="?lang=es" class="px-2 py-1 rounded-md {% if lang == 'es' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">ES</a>
            <a href="?lang=ka" class="px-2 py-1 rounded-md {% if lang == 'ka' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">KA</a>
            <a href="?lang=en" class="px-2 py-1 rounded-md {% if lang == 'en' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">EN</a>
            <a href="?lang=ru" class="px-2 py-1 rounded-md {% if lang == 'ru' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">RU</a>
            <a href="?lang=fr" class="px-2 py-1 rounded-md {% if lang == 'fr' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">FR</a>
            <a href="?lang=de" class="px-2 py-1 rounded-md {% if lang == 'de' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">DE</a>
            <a href="?lang=tr" class="px-2 py-1 rounded-md {% if lang == 'tr' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">TR</a>
            <a href="?lang=ar" class="px-2 py-1 rounded-md {% if lang == 'ar' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">AR</a>
        </div>

        <div class="text-center mb-6">
            <span class="bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">{{ t.hotel }}: {{ hotel_id }}</span>
            <h1 class="text-2xl font-bold mt-2 text-slate-900">{{ t.room }} #{{ room_number }}</h1>
            <p class="text-sm text-slate-500 mt-1">{{ t.subtitle }}</p>
        </div>

        {% if success %}
        <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-center mb-6 animate-pulse">
            <p class="font-medium">{{ t.success_msg }}</p>
        </div>
        {% endif %}

        <form method="POST" class="space-y-4">
            <div>
                <textarea name="message" rows="5" placeholder="{{ t.placeholder }}" required class="w-full border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none"></textarea>
            </div>

            <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl transition duration-200 shadow-lg shadow-indigo-200">
                {{ t.send_btn }}
            </button>
        </form>
    </div>
    <footer class="text-center py-6 text-xs text-slate-400">
        Smart Hotel Service &copy; 2026
    </footer>
</body>
</html>
"""

# მენეჯერის პანელის შაბლონი
MANAGER_TEMPLATE = """
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>მენეჯერის პანელი</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 min-h-screen p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-slate-900">🏨 მენეჯერის პანელი</h1>
            <span class="text-sm bg-emerald-100 text-emerald-800 font-medium px-3 py-1 rounded-full">სისტემა აქტიურია</span>
        </div>

        <div class="bg-white shadow-md rounded-2xl overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                            <th class="p-4">ID</th>
                            <th class="p-4">სასტუმრო</th>
                            <th class="p-4">ოთახი</th>
                            <th class="p-4">შეტყობინება</th>
                            <th class="p-4">დრო</th>
                            <th class="p-4">სტატუსი</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 text-sm">
                        {% for req in requests %}
                        <tr class="hover:bg-slate-50 transition">
                            <td class="p-4 font-medium text-slate-900">#{{ req[0] }}</td>
                            <td class="p-4 text-slate-700">{{ req[1] }}</td>
                            <td class="p-4 font-bold text-indigo-600">ოთახი {{ req[2] }}</td>
                            <td class="p-4 text-slate-800 font-medium">{{ req[3] }}</td>
                            <td class="p-4 text-slate-400 text-xs">{{ req[4] }}</td>
                            <td class="p-4">
                                <span class="bg-amber-100 text-amber-800 text-xs font-medium px-2.5 py-1 rounded-full">{{ req[5] }}</span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route("/hotel/<hotel_id>/room/<room_number>", methods=["GET", "POST"])
def room_service(hotel_id, room_number):
  # ნაგულისხმევ ენად მითითებულია ესპანური ('es')
  lang = request.args.get("lang", "es")
  if lang not in TRANSLATIONS:
    lang = "es"

  success = False
  if request.method == "POST":
    message = request.form.get("message")

    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO requests (hotel_id, room_number, message) VALUES (?, ?, ?)",
        (hotel_id, room_number, message),
    )
    conn.commit()
    conn.close()
    success = True

  return render_template_string(
      USER_TEMPLATE,
      hotel_id=hotel_id,
      room_number=room_number,
      success=success,
      t=TRANSLATIONS[lang],
      lang=lang,
  )


@app.route("/manager")
@requires_auth
def manager_panel():
  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, hotel_id, room_number, message, timestamp, status FROM"
      " requests ORDER BY id DESC"
  )
  reqs = cursor.fetchall()
  conn.close()

  return render_template_string(MANAGER_TEMPLATE, requests=reqs)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
