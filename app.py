from datetime import datetime
import os
import sqlite3
from flask import Flask, jsonify, render_template_string, request, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def init_db():
  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()
  # დავამატეთ hotel_id ველი, რომ განვასხვავოთ სასტუმროები ერთმანეთისგან
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id TEXT NOT NULL,
            room_number TEXT NOT NULL,
            issue TEXT NOT NULL,
            photo_path TEXT,
            status TEXT DEFAULT 'ახალი',
            created_at TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()

# თარგმანების ლექსიკონი
TRANSLATIONS = {
    "en": {
        "title": "Hotel Service - Room",
        "header": "Room №",
        "sub": "Please let us know your request or issue:",
        "placeholder": (
            "For example: Need extra towels, or AC is not working..."
        ),
        "photo_label": "📸 Attach photo (optional):",
        "btn_send": "Send Request",
        "success": (
            "Request sent successfully! The manager is already working on it."
        ),
        "error": "Please enter a message!",
    },
    "es": {
        "title": "Servicio de Hotel - Habitación",
        "header": "Habitación №",
        "sub": "Por favor, háganos saber su solicitud o problema:",
        "placeholder": (
            "Por ejemplo: Necesito toallas adicionales o el aire"
            " acondicionado..."
        ),
        "photo_label": "📸 Adjuntar foto (opcional):",
        "btn_send": "Enviar Solicitud",
        "success": (
            "¡Solicitud enviada con éxito! El gerente ya está trabajando en"
            " ello."
        ),
        "error": "¡Por favor, escriba un mensaje!",
    },
    "ru": {
        "title": "Отельный сервис - Номер",
        "header": "Номер №",
        "sub": "Пожалуйста, сообщите о вашей просьбе или проблеме:",
        "placeholder": (
            "Например: Нужны дополнительные полотенца или не работает"
            " кондиционер..."
        ),
        "photo_label": "📸 Прикрепить фото (необязательно):",
        "btn_send": "Отправить",
        "success": (
            "Запрос успешно отправлен! Менеджер уже работает над этим."
        ),
        "error": "Пожалуйста, введите текст сообщения!",
    },
    "pl": {
        "title": "Obsługa hotelowa - Pokój",
        "header": "Pokój nr",
        "sub": "Daj nam znać, jaka jest Twoja prośba lub problem:",
        "placeholder": (
            "Na przykład: Potrzebuję dodatkowych ręczników lub klimatyzacja"
            " nie działa..."
        ),
        "photo_label": "📸 Dołącz zdjęcie (opcjonalnie):",
        "btn_send": "Wyślij zgłoszenie",
        "success": (
            "Zgłoszenie wysłane pomyślnie! Menedżer już nad tym pracuje."
        ),
        "error": "Proszę wpisać wiadomość!",
    },
    "fr": {
        "title": "Service Hôtel - Chambre",
        "header": "Chambre №",
        "sub": "Veuillez nous faire part de votre demande ou problème :",
        "placeholder": (
            "Par exemple : Besoin de serviettes supplémentaires ou la clim ne"
            " marche pas..."
        ),
        "photo_label": "📸 Joindre une photo (facultatif) :",
        "btn_send": "Envoyer la demande",
        "success": (
            "Demande envoyée avec succès ! Le responsable s'en occupe déjà."
        ),
        "error": "Veuillez entrer un message !",
    },
    "de": {
        "title": "Hotelservice - Zimmer",
        "header": "Zimmer №",
        "sub": "Bitte teilen Sie uns Ihr Anliegen oder Problem mit:",
        "placeholder": (
            "Zum Beispiel: Brauche zusätzliche Handtücher oder Klimaanlage"
            " kühlt nicht..."
        ),
        "photo_label": "📸 Foto anhängen (optional):",
        "btn_send": "Anfrage senden",
        "success": (
            "Anfrage erfolgreich gesendet! Der Manager kümmert sich darum."
        ),
        "error": "Bitte geben Sie eine Nachricht ein!",
    },
}


# სტუმრის გვერდი კონკრეტული სასტუმროსთვის და ოთახისთვის
@app.route("/hotel/<hotel_id>/room/<room_number>")
def room_page(hotel_id, room_number):
  lang = request.args.get("lang", "en")
  if lang not in TRANSLATIONS:
    lang = "en"
  t = TRANSLATIONS[lang]

  html_template = f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t['title']} {room_number}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; box-sizing: border-box; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }}
            .lang-switcher {{ display: flex; justify-content: center; gap: 5px; margin-bottom: 20px; flex-wrap: wrap; }}
            .lang-switcher a {{ text-decoration: none; padding: 5px 8px; border: 1px solid #ccc; border-radius: 5px; font-size: 13px; color: #333; background: #fff; }}
            .lang-switcher a.active {{ background: #007bff; color: white; border-color: #007bff; }}
            h2 {{ color: #333; margin-bottom: 5px; }}
            p {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
            textarea {{ width: 100%; height: 120px; padding: 10px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 15px; resize: none; font-family: Arial; box-sizing: border-box; }}
            .file-upload {{ margin-bottom: 15px; text-align: left; }}
            .file-upload label {{ display: block; font-size: 14px; color: #555; margin-bottom: 5px; }}
            input[type="file"] {{ width: 100%; font-size: 14px; }}
            button {{ background-color: #28a745; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; transition: 0.2s; }}
            button:hover {{ background-color: #218838; }}
            .success {{ color: green; font-weight: bold; display: none; margin-top: 15px; }}
            .error {{ color: red; font-size: 14px; margin-top: 10px; display: none; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="lang-switcher">
                <a href="?lang=en" class="{'active' if lang == 'en' else ''}">🇬🇧 EN</a>
                <a href="?lang=es" class="{'active' if lang == 'es' else ''}">🇪🇸 ES</a>
                <a href="?lang=ru" class="{'active' if lang == 'ru' else ''}">🇷🇺 RU</a>
                <a href="?lang=pl" class="{'active' if lang == 'pl' else ''}">🇵🇱 PL</a>
                <a href="?lang=fr" class="{'active' if lang == 'fr' else ''}">🇫🇷 FR</a>
                <a href="?lang=de" class="{'active' if lang == 'de' else ''}">🇩🇪 DE</a>
            </div>

            <h2>{t['header']} {room_number}</h2>
            <p>{t['sub']}</p>
            
            <textarea id="issueText" placeholder="{t['placeholder']}"></textarea>
            
            <div class="file-upload">
                <label for="photoInput">{t['photo_label']}</label>
                <input type="file" id="photoInput" accept="image/*" capture="environment">
            </div>

            <button onclick="sendRequest()">{t['btn_send']}</button>

            <div id="successMsg" class="success">{t['success']}</div>
            <div id="errorMsg" class="error">{t['error']}</div>
        </div>

        <script>
            const hotelId = "{hotel_id}";
            const roomNumber = "{room_number}";

            function sendRequest() {{
                const text = document.getElementById('issueText').value.trim();
                const photoInput = document.getElementById('photoInput');
                
                if(!text) {{
                    document.getElementById('errorMsg').style.display = 'block';
                    return;
                }}
                document.getElementById('errorMsg').style.display = 'none';

                const formData = new FormData();
                formData.append('hotel_id', hotelId);
                formData.append('room_number', roomNumber);
                formData.append('issue', text);
                
                if(photoInput.files.length > 0) {{
                    formData.append('photo', photoInput.files[0]);
                }}

                fetch('/api/request', {{
                    method: 'POST',
                    body: formData
                }})
                .then(response => response.json())
                .then(data => {{
                    if(data.status === 'success') {{
                        document.getElementById('successMsg').style.display = 'block';
                        document.getElementById('issueText').value = '';
                        document.getElementById('photoInput').value = '';
                        setTimeout(() => {{ document.getElementById('successMsg').style.display = 'none'; }}, 5000);
                    }}
                }})
                .catch(err => {{
                    alert('Error sending request. Please try again.');
                }});
            }}
        </script>
    </body>
    </html>
    """
  return html_template


@app.route("/api/request", methods=["POST"])
def api_request():
  hotel_id = request.form.get("hotel_id")
  room_number = request.form.get("room_number")
  issue = request.form.get("issue")
  created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  photo_filename = None
  if "photo" in request.files:
    photo = request.files["photo"]
    if photo.filename != "":
      ext = (
          photo.filename.rsplit(".", 1)[1].lower()
          if "." in photo.filename
          else "jpg"
      )
      photo_filename = (
          f"{hotel_id}_{room_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
      )
      photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO requests (hotel_id, room_number, issue, photo_path,"
      " created_at) VALUES (?, ?, ?, ?, ?)",
      (hotel_id, room_number, issue, photo_filename, created_at),
  )
  conn.commit()
  conn.close()

  return jsonify({"status": "success"})


@app.route("/uploads/<filename>")
def uploaded_file(filename):
  return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# მენეჯერის პანელი (სადაც ფილტრავს სასტუმროს მიხედვით: /manager?hotel=tbilisi-palace)
@app.route("/manager")
def manager_panel():
  hotel_filter = request.args.get("hotel", "")

  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()

  if hotel_filter:
    cursor.execute(
        "SELECT id, hotel_id, room_number, issue, photo_path, status,"
        " created_at FROM requests WHERE hotel_id = ? ORDER BY id DESC",
        (hotel_filter,),
    )
  else:
    cursor.execute(
        "SELECT id, hotel_id, room_number, issue, photo_path, status,"
        " created_at FROM requests ORDER BY id DESC"
    )

  rows = cursor.fetchall()
  conn.close()

  html_template = """
    <!DOCTYPE html>
    <html lang="ka">
    <head>
        <meta charset="UTF-8">
        <title>მენეჯერის პანელი - სასტუმროები</title>
        <style>
            body { font-family: Arial, sans-serif; background: #eef2f3; padding: 20px; }
            .container { max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; vertical-align: middle; }
            th { background-color: #007bff; color: white; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .badge { padding: 5px 10px; border-radius: 5px; background: #ffc107; font-weight: bold; font-size: 12px; }
            img.preview { width: 70px; height: 70px; object-fit: cover; border-radius: 5px; cursor: pointer; }
            img.preview:hover { opacity: 0.8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🏨 ყველა სასტუმროს შემოსული მოთხოვნები</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>სასტუმრო</th>
                    <th>ოთახი</th>
                    <th>აღწერა / პრობლემა</th>
                    <th>ფოტო</th>
                    <th>სტატუსი</th>
                    <th>დრო</th>
                </tr>
                {% for row in rows %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td><b>{{ row[1] }}</b></td>
                    <td>ოთახი {{ row[2] }}</td>
                    <td>{{ row[3] }}</td>
                    <td>
                        {% if row[4] %}
                            <a href="/uploads/{{ row[4] }}" target="_blank">
                                <img src="/uploads/{{ row[4] }}" class="preview" alt="ფოტო">
                            </a>
                        {% else %}
                            არ არის
                        {% endif %}
                    </td>
                    <td><span class="badge">{{ row[5] }}</span></td>
                    <td>{{ row[6] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
  return render_template_string(html_template, rows=rows)


if __name__ == "__main__":
  import os

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
