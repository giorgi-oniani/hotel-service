from datetime import datetime
from functools import wraps
import sqlite3
from flask import Flask, Response, redirect, render_template_string, request, url_for

app = Flask(__name__)

# ავტორიზაცია
SUPER_USER = "superadmin"
SUPER_PASS = "super123"
MANAGER_USER = "admin"
MANAGER_PASS = "hotel123"


def check_super_auth(username, password):
  return username == SUPER_USER and password == SUPER_PASS


def check_manager_auth(username, password):
  return username == MANAGER_USER and password == MANAGER_PASS


def authenticate_super():
  return Response(
      "Unauthorized",
      401,
      {"WWW-Authenticate": 'Basic realm="Super Admin Required"'},
  )


def authenticate_manager():
  return Response(
      "Unauthorized",
      401,
      {"WWW-Authenticate": 'Basic realm="Manager Required"'},
  )


def requires_super_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_super_auth(auth.username, auth.password):
      return authenticate_super()
    return f(*args, **kwargs)

  return decorated


def requires_manager_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_manager_auth(auth.username, auth.password):
      return authenticate_manager()
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
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id TEXT,
            room_number TEXT,
            speed_score INTEGER,
            comfort_score INTEGER,
            recommend_score INTEGER,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
  conn.commit()
  conn.close()


init_db()

# 8 ენის ლექსიკონი
TRANSLATIONS = {
    "es": {
        "title": "Servicio de Habitaciones",
        "hotel": "Hotel",
        "room": "Habitación",
        "subtitle": "Escriba su solicitud:",
        "success_msg": "¡Solicitud enviada con éxito!",
        "placeholder": "Ej: Necesito toallas adicionales...",
        "send_btn": "Enviar Solicitud",
        "feedback_title": "Valore su estancia",
        "q1": "1. ¿Cómo califica la velocidad del servicio?",
        "q2": "2. ¿Qué tan limpio y cómodo estuvo el cuarto?",
        "q3": "3. ¿Recomendaría nuestro hotel?",
        "fb_placeholder": "Comentarios adicionales...",
        "fb_btn": "Enviar Valoración",
        "fb_success": "¡Gracias por su valoración!",
        "tab_service": "Servicio",
        "tab_feedback": "Valoración",
    },
    "ka": {
        "title": "სასტუმროს ოთახის სერვისი",
        "hotel": "სასტუმრო",
        "room": "ოთახი",
        "subtitle": "მოგვწერეთ თქვენი მოთხოვნა:",
        "success_msg": "მოთხოვნა წარმატებით გაიგზავნა!",
        "placeholder": "მაგ: მჭირდება დამატებითი პირსახოცი...",
        "send_btn": "მოთხოვნის გაგზავნა",
        "feedback_title": "შეაფასეთ თქვენი ყოფნა სასტუმროში",
        "q1": "1. როგორ შეაფასებდით მომსახურების სისწრაფეს?",
        "q2": "2. რამდენად კომფორტული და სუფთა იყო ოთახი?",
        "q3": "3. გვირჩევდით თუ არა მეგობრებს?",
        "fb_placeholder": "დამატებითი კომენტარი...",
        "fb_btn": "შეფასების გაგზავნა",
        "fb_success": "მადლობა შეფასებისთვის!",
        "tab_service": "სერვისი",
        "tab_feedback": "შეფასება",
    },
    "en": {
        "title": "Hotel Room Service",
        "hotel": "Hotel",
        "room": "Room",
        "subtitle": "Write your request below:",
        "success_msg": "Request sent successfully!",
        "placeholder": "E.g. Need extra towels...",
        "send_btn": "Send Request",
        "feedback_title": "Rate your stay",
        "q1": "1. How would you rate the service speed?",
        "q2": "2. How comfortable and clean was the room?",
        "q3": "3. Would you recommend us to friends?",
        "fb_placeholder": "Additional comments...",
        "fb_btn": "Submit Review",
        "fb_success": "Thank you for your feedback!",
        "tab_service": "Service",
        "tab_feedback": "Review",
    },
    "ru": {
        "title": "Обслуживание номеров",
        "hotel": "Отель",
        "room": "Номер",
        "subtitle": "Напишите ваш запрос:",
        "success_msg": "Запрос успешно отправлен!",
        "placeholder": "Напр: Нужно дополнительное полотенце...",
        "send_btn": "Отправить запрос",
        "feedback_title": "Оцените ваше пребывание",
        "q1": "1. Как вы оцениваете скорость обслуживания?",
        "q2": "2. Насколько комфортным и чистым был номер?",
        "q3": "3. Порекомендовали бы вы нас друзьям?",
        "fb_placeholder": "Дополнительные комментарии...",
        "fb_btn": "Отправить отзыв",
        "fb_success": "Спасибо за ваш отзыв!",
        "tab_service": "Сервис",
        "tab_feedback": "Отзыв",
    },
    "fr": {
        "title": "Service d'étage",
        "hotel": "Hôtel",
        "room": "Chambre",
        "subtitle": "Écrivez votre demande:",
        "success_msg": "Demande envoyée avec succès!",
        "placeholder": "Ex: J'ai besoin de serviettes...",
        "send_btn": "Envoyer la demande",
        "feedback_title": "Évaluez votre séjour",
        "q1": "1. Vitesse du service?",
        "q2": "2. Confort et propreté de la chambre?",
        "q3": "3. Recommanderiez-vous notre hôtel?",
        "fb_placeholder": "Commentaires...",
        "fb_btn": "Envoyer",
        "fb_success": "Merci pour votre avis!",
        "tab_service": "Service",
        "tab_feedback": "Avis",
    },
    "de": {
        "title": "Zimmerservice",
        "hotel": "Hotel",
        "room": "Zimmer",
        "subtitle": "Schreiben Sie Ihre Anfrage:",
        "success_msg": "Anfrage erfolgreich gesendet!",
        "placeholder": "Bsp: Handtücher benötigt...",
        "send_btn": "Anfrage senden",
        "feedback_title": "Bewerten Sie Ihren Aufenthalt",
        "q1": "1. Wie bewerten Sie die Servicegeschwindigkeit?",
        "q2": "2. Wie komfortabel und sauber war das Zimmer?",
        "q3": "3. Würden Sie uns weiterempfehlen?",
        "fb_placeholder": "Zusätzliche Kommentare...",
        "fb_btn": "Bewertung absenden",
        "fb_success": "Vielen Dank für Ihr Feedback!",
        "tab_service": "Service",
        "tab_feedback": "Bewertung",
    },
    "ar": {
        "title": "خدمة الغرف",
        "hotel": "الفندق",
        "room": "الغرفة",
        "subtitle": "اكتب طلبك أدناه:",
        "success_msg": "تم إرسال الطلب بنجاح!",
        "placeholder": "مثال: أتاج مناشف إضافية...",
        "send_btn": "إرسال الطلب",
        "feedback_title": "قيم إقامتك",
        "q1": "1. كيف تقيم سرعة الخدمة؟",
        "q2": "2. ما مدى راحة ونظافة الغرفة؟",
        "q3": "3. هل ترشحنا لأصدقائك؟",
        "fb_placeholder": "تعليقات إضافية...",
        "fb_btn": "إرسال التقييم",
        "fb_success": "شكرا لتقييمك!",
        "tab_service": "الخدمة",
        "tab_feedback": "التقييم",
    },
    "tr": {
        "title": "Oda Servisi",
        "hotel": "Otel",
        "room": "Oda",
        "subtitle": "İsteğinizi aşağıya yazın:",
        "success_msg": "İstek başarıyla gönderildi!",
        "placeholder": "Örn: Ek havlu lazımdı...",
        "send_btn": "İsteği Gönder",
        "feedback_title": "Konaklamanızı Değerlendirin",
        "q1": "1. Servis hızını nasıl buldunuz?",
        "q2": "2. Oda ne kadar rahat ve temizdi?",
        "q3": "3. Bizi başkalarına tavsiye eder misiniz?",
        "fb_placeholder": "Ek yorumlar...",
        "fb_btn": "Değerlendirmeyi Gönder",
        "fb_success": "Geri bildiriminiz için teşekkürler!",
        "tab_service": "Servis",
        "tab_feedback": "Değerlendirme",
    },
}

# სტუმრის მხარე (PWA მზაობით)
USER_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" {% if lang == 'ar' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.title }}</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#4f46e5">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col justify-between">
    <div class="max-w-md mx-auto p-6 w-full bg-white shadow-xl rounded-2xl my-auto mt-6">
        <div class="flex flex-wrap justify-center gap-1 mb-6 text-xs font-semibold">
            <a href="?lang=es{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'es' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇪🇸 ES</a>
            <a href="?lang=ka{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'ka' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇬🇪 KA</a>
            <a href="?lang=en{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'en' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇬🇧 EN</a>
            <a href="?lang=ru{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'ru' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇷🇺 RU</a>
            <a href="?lang=fr{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'fr' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇫🇷 FR</a>
            <a href="?lang=de{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'de' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇩🇪 DE</a>
            <a href="?lang=tr{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'tr' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇹🇷 TR</a>
            <a href="?lang=ar{% if active_tab == 'feedback' %}&tab=feedback{% endif %}" class="px-2 py-1 rounded-md {% if lang == 'ar' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-600{% endif %}">🇸🇦 AR</a>
        </div>
        <div class="flex border-b border-slate-200 mb-6 text-sm font-medium">
            <a href="?lang={{ lang }}&tab=service" class="w-1/2 text-center pb-2 border-b-2 {% if active_tab != 'feedback' %}border-indigo-600 text-indigo-600{% else %}border-transparent text-slate-400{% endif %}">{{ t.tab_service }}</a>
            <a href="?lang={{ lang }}&tab=feedback" class="w-1/2 text-center pb-2 border-b-2 {% if active_tab == 'feedback' %}border-indigo-600 text-indigo-600{% else %}border-transparent text-slate-400{% endif %}">{{ t.tab_feedback }}</a>
        </div>
        <div class="text-center mb-6">
            <span class="bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">{{ t.hotel }}: {{ hotel_id }}</span>
            <h1 class="text-2xl font-bold mt-2 text-slate-900">{{ t.room }} #{{ room_number }}</h1>
        </div>
        {% if active_tab == 'feedback' %}
            {% if success_fb %}
            <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-center mb-6">
                <p class="font-medium">{{ t.fb_success }}</p>
            </div>
            {% endif %}
            <form method="POST" action="?lang={{ lang }}&tab=feedback" class="space-y-4 text-xs">
                <div>
                    <label class="block font-medium text-slate-700 mb-1">{{ t.q1 }}</label>
                    <select name="speed" class="w-full border border-slate-300 rounded-lg p-2 bg-white">
                        <option value="5">⭐⭐⭐⭐⭐ (5/5)</option>
                        <option value="4">⭐⭐⭐⭐ (4/5)</option>
                        <option value="3">⭐⭐⭐ (3/5)</option>
                        <option value="2">⭐⭐ (2/5)</option>
                        <option value="1">⭐ (1/5)</option>
                    </select>
                </div>
                <div>
                    <label class="block font-medium text-slate-700 mb-1">{{ t.q2 }}</label>
                    <select name="comfort" class="w-full border border-slate-300 rounded-lg p-2 bg-white">
                        <option value="5">⭐⭐⭐⭐⭐ (5/5)</option>
                        <option value="4">⭐⭐⭐⭐ (4/5)</option>
                        <option value="3">⭐⭐⭐ (3/5)</option>
                        <option value="2">⭐⭐ (2/5)</option>
                        <option value="1">⭐ (1/5)</option>
                    </select>
                </div>
                <div>
                    <label class="block font-medium text-slate-700 mb-1">{{ t.q3 }}</label>
                    <select name="recommend" class="w-full border border-slate-300 rounded-lg p-2 bg-white">
                        <option value="5">დიახ, აუცილებლად / Yes</option>
                        <option value="3">ნეიტრალური / Neutral</option>
                        <option value="1">არა / No</option>
                    </select>
                </div>
                <div>
                    <textarea name="comment" rows="3" placeholder="{{ t.fb_placeholder }}" class="w-full border border-slate-300 rounded-lg p-2"></textarea>
                </div>
                <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 rounded-xl transition shadow-md">
                    {{ t.fb_btn }}
                </button>
            </form>
        {% else %}
            <p class="text-sm text-slate-500 text-center mb-4">{{ t.subtitle }}</p>
            {% if success_req %}
            <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-center mb-6 animate-pulse">
                <p class="font-medium">{{ t.success_msg }}</p>
            </div>
            {% endif %}
            <form method="POST" action="?lang={{ lang }}&tab=service" class="space-y-4">
                <div>
                    <textarea name="message" rows="5" placeholder="{{ t.placeholder }}" required class="w-full border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none"></textarea>
                </div>
                <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl transition duration-200 shadow-lg shadow-indigo-200">
                    {{ t.send_btn }}
                </button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

# მენეჯერის პანელი (QR გენერატორითა და შეკვეთების მართვით)
MANAGER_TEMPLATE = """
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>მენეჯერის პანელი</title>
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.1/build/qrcode.min.js"></script>
</head>
<body class="bg-slate-100 min-h-screen p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-slate-900">🏨 მენეჯერის პანელი</h1>
            <div class="flex gap-2">
                <a href="/super-admin" class="bg-slate-800 text-white text-xs px-3 py-2 rounded-xl font-medium">სუპერ ადმინი</a>
                <button onclick="generateQRs()" class="bg-indigo-600 text-white text-xs px-3 py-2 rounded-xl font-medium">🖨️ QR კოდების გენერაცია</button>
            </div>
        </div>

        <div class="bg-white shadow-md rounded-2xl overflow-hidden p-4 mb-8">
            <h2 class="text-lg font-bold text-slate-800 mb-4">შემოსული შეკვეთები</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                            <th class="p-3">ID</th>
                            <th class="p-3">სასტუმრო</th>
                            <th class="p-3">ოთახი</th>
                            <th class="p-3">შეტყობინება</th>
                            <th class="p-3">დრო</th>
                            <th class="p-3">სტატუსი</th>
                            <th class="p-3">მოქმედება</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 text-sm">
                        {% for req in requests %}
                        <tr class="hover:bg-slate-50 transition">
                            <td class="p-3 font-medium text-slate-900">#{{ req[0] }}</td>
                            <td class="p-3 text-slate-700">{{ req[1] }}</td>
                            <td class="p-3 font-bold text-indigo-600">ოთახი {{ req[2] }}</td>
                            <td class="p-3 text-slate-800 font-medium">{{ req[3] }}</td>
                            <td class="p-3 text-slate-400 text-xs">{{ req[4] }}</td>
                            <td class="p-3">
                                <span class="px-2.5 py-1 rounded-full text-xs font-semibold 
                                    {% if req[5] == 'ახალი' %}bg-amber-100 text-amber-800
                                    {% elif req[5] == 'მუშავდება' %}bg-blue-100 text-blue-800
                                    {% else %}bg-emerald-100 text-emerald-800{% endif %}">
                                    {{ req[5] }}
                                </span>
                            </td>
                            <td class="p-3 flex gap-1">
                                <a href="/manager/update/{{ req[0] }}/მუშავდება" class="bg-blue-50 text-blue-600 hover:bg-blue-100 px-2 py-1 rounded text-xs">მუშავდება</a>
                                <a href="/manager/update/{{ req[0] }}/შესრულებული" class="bg-emerald-50 text-emerald-600 hover:bg-emerald-100 px-2 py-1 rounded text-xs">დასრულება</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- QR კოდების გამოსატანი ზონა -->
        <div id="qr-container" class="bg-white shadow-md rounded-2xl p-6 hidden">
            <h2 class="text-lg font-bold text-slate-800 mb-4">ოთახების QR კოდები (დასაბეჭდად)</h2>
            <div id="qr-grid" class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center"></div>
        </div>
    </div>

    <script>
        function generateQRs() {
            const container = document.getElementById('qr-container');
            const grid = document.getElementById('qr-grid');
            container.classList.remove('hidden');
            grid.innerHTML = '';
            
            const hotelId = "tbilisi-hotel"; // შეგიძლიათ დინამიკურადაც შეიცვალოს
            for (let i = 101; i <= 108; i++) {
                const roomDiv = document.createElement('div');
                roomDiv.className = 'p-4 border border-slate-200 rounded-xl flex flex-col items-center bg-slate-50';
                roomDiv.innerHTML = `<p class="font-bold mb-2 text-slate-700">ოთახი ${i}</p><canvas id="qr-${i}"></canvas>`;
                grid.appendChild(roomDiv);

                const roomUrl = `${window.location.origin}/hotel/${hotelId}/room/${i}`;
                QRCode.toCanvas(document.getElementById(`qr-${i}`), roomUrl, { width: 120 }, function (error) {
                    if (error) console.error(error);
                });
            }
            window.print();
        }
    </script>
</body>
</html>
"""

# სუპერ ადმინის პანელი
SUPER_TEMPLATE = """
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>სუპერ ადმინის პანელი</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold">⚡ მთავარი მფლობელის პანელი (Super Admin)</h1>
            <a href="/manager" class="bg-indigo-600 text-white text-xs px-3 py-2 rounded-xl font-medium">მენეჯერის პანელზე გადასვლა</a>
        </div>
        <div class="bg-slate-800 shadow-lg rounded-2xl overflow-hidden p-6 mb-8 border border-slate-700">
            <h2 class="text-xl font-bold mb-4 text-amber-400">⭐ სტუმრების შეფასებები და გამოხმაურებები</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-sm">
                    <thead>
                        <tr class="bg-slate-700 text-slate-300 text-xs uppercase tracking-wider">
                            <th class="p-3">სასტუმრო</th>
                            <th class="p-3">ოთახი</th>
                            <th class="p-3">სისწრაფე</th>
                            <th class="p-3">კომფორტი</th>
                            <th class="p-3">რეკომენდაცია</th>
                            <th class="p-3">კომენტარი</th>
                            <th class="p-3">დრო</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-700">
                        {% for fb in feedbacks %}
                        <tr class="hover:bg-slate-750">
                            <td class="p-3">{{ fb[1] }}</td>
                            <td class="p-3 text-indigo-400 font-bold">ოთახი {{ fb[2] }}</td>
                            <td class="p-3">⭐ {{ fb[3] }}/5</td>
                            <td class="p-3">⭐ {{ fb[4] }}/5</td>
                            <td class="p-3">{{ fb[5] }}</td>
                            <td class="p-3 text-slate-300">{{ fb[6] }}</td>
                            <td class="p-3 text-slate-400 text-xs">{{ fb[7] }}</td>
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


@app.route("/manifest.json")
def manifest():
  manifest_data = {
      "name": "Smart Hotel Service",
      "short_name": "HotelApp",
      "start_url": "/",
      "display": "standalone",
      "background_color": "#f8fafc",
      "theme_color": "#4f46e5",
      "icons": [
          {
              "src": "https://cdn-icons-png.flaticon.com/512/3076/3076137.png",
              "sizes": "512x512",
              "type": "image/png",
          }
      ],
  }
  return app.response_class(
      response=str(manifest_data).replace("'", '"'),
      mimetype="application/json",
  )


@app.route("/sw.js")
def service_worker():
  sw_code = (
      "self.addEventListener('fetch', (e) => { e.respondWith(fetch(e.request));"
      " });"
  )
  return Response(sw_code, mimetype="application/javascript")


@app.route("/hotel/<hotel_id>/room/<room_number>", methods=["GET", "POST"])
def room_service(hotel_id, room_number):
  lang = request.args.get("lang", "es")
  if lang not in TRANSLATIONS:
    lang = "es"

  active_tab = request.args.get("tab", "service")
  success_req = False
  success_fb = False

  if request.method == "POST":
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    if active_tab == "feedback":
      speed = request.form.get("speed")
      comfort = request.form.get("comfort")
      recommend = request.form.get("recommend")
      comment = request.form.get("comment")
      cursor.execute(
          "INSERT INTO feedback (hotel_id, room_number, speed_score,"
          " comfort_score, recommend_score, comment) VALUES (?, ?, ?, ?, ?, ?)",
          (hotel_id, room_number, speed, comfort, recommend, comment),
      )
      success_fb = True
    else:
      message = request.form.get("message")
      cursor.execute(
          "INSERT INTO requests (hotel_id, room_number, message) VALUES (?, ?,"
          " ?)",
          (hotel_id, room_number, message),
      )
      success_req = True

    conn.commit()
    conn.close()

  return render_template_string(
      USER_TEMPLATE,
      hotel_id=hotel_id,
      room_number=room_number,
      success_req=success_req,
      success_fb=success_fb,
      t=TRANSLATIONS[lang],
      lang=lang,
      active_tab=active_tab,
  )


@app.route("/manager")
@requires_manager_auth
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


@app.route("/manager/update/<int:req_id>/<new_status>")
@requires_manager_auth
def update_status(req_id, new_status):
  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()
  cursor.execute(
      "UPDATE requests SET status = ? WHERE id = ?", (new_status, req_id)
  )
  conn.commit()
  conn.close()
  return redirect(url_for("manager_panel"))


@app.route("/super-admin")
@requires_super_auth
def super_admin_panel():
  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, hotel_id, room_number, speed_score, comfort_score,"
      " recommend_score, comment, timestamp FROM feedback ORDER BY id DESC"
  )
  feedbacks = cursor.fetchall()
  conn.close()
  return render_template_string(SUPER_TEMPLATE, feedbacks=feedbacks)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
