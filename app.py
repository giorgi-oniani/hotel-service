from datetime import datetime
from functools import wraps
import sqlite3
from flask import Flask, Response, redirect, render_template_string, request, url_for

app = Flask(__name__)

# მენეჯერის პარამეტრები (შეგიძლია შეცვალო შენი სურვილისამებრ)
MANAGER_USER = "admin"
MANAGER_PASS = "saqartvelo@@@"


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
            service_type TEXT,
            message TEXT,
            status TEXT DEFAULT 'ახალი',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
  conn.commit()
  conn.close()


init_db()

# მომხმარებლის გვერდი (ლამაზი, თანამედროვე დიზაინით - Tailwind CSS)
USER_TEMPLATE = """
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>სასტუმროს ოთახის სერვისი</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col justify-between">
    <div class="max-w-md mx-auto p-6 w-full bg-white shadow-xl rounded-2xl my-auto mt-10">
        <div class="text-center mb-6">
            <span class="bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">სასტუმრო: {{ hotel_id }}</span>
            <h1 class="text-2xl font-bold mt-2 text-slate-900">ოთახი #{{ room_number }}</h1>
            <p class="text-sm text-slate-500 mt-1">რით შეგვიძლია დაგეხმაროთ დღეს?</p>
        </div>

        {% if success %}
        <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-center mb-6 animate-pulse">
            <p class="font-medium">მოთხოვნა წარმატებით გაიგზავნა! მალე დაგიკავშირდებით.</p>
        </div>
        {% endif %}

        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">სერვისის ტიპი</label>
                <select name="service_type" class="w-full border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-white">
                    <option value="ოთახის დალაგება">🧹 ოთახის დალაგება</option>
                    <option value="პირსახოცები / თეთრეული">🛏️ პირსახოცები / თეთრეული</option>
                    <option value="რუმ-სერვისი (კვება)">🍔 რუმ-სერვისი (კვება)</option>
                    <option value="ტექნიკური პრობლემა">🔧 ტექნიკური პრობლემა</option>
                    <option value="სხვა მოთხოვნა">💬 სხვა მოთხოვნა</option>
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">დამატებითი დეტალები</label>
                <textarea name="message" rows="4" placeholder="მოგვწერეთ დეტალურად..." class="w-full border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none"></textarea>
            </div>

            <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl transition duration-200 shadow-lg shadow-indigo-200">
                გაგზავნა
            </button>
        </form>
    </div>
    <footer class="text-center py-6 text-xs text-slate-400">
        Smart Hotel Service &copy; 2026
    </footer>
</body>
</html>
"""

# მენეჯერის პანელის შაბლონი (დაცული და თანამედროვე)
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
                            <th class="p-4">სერვისი</th>
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
                            <td class="p-4 text-slate-800">{{ req[3] }}</td>
                            <td class="p-4 text-slate-600">{{ req[4] }}</td>
                            <td class="p-4 text-slate-400 text-xs">{{ req[5] }}</td>
                            <td class="p-4">
                                <span class="bg-amber-100 text-amber-800 text-xs font-medium px-2.5 py-1 rounded-full">{{ req[6] }}</span>
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
  success = False
  if request.method == "POST":
    service_type = request.form.get("service_type")
    message = request.form.get("message")

    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO requests (hotel_id, room_number, service_type, message)"
        " VALUES (?, ?, ?, ?)",
        (hotel_id, room_number, service_type, message),
    )
    conn.commit()
    conn.close()
    success = True

  return render_template_string(
      USER_TEMPLATE,
      hotel_id=hotel_id,
      room_number=room_number,
      success=success,
  )


@app.route("/manager")
@requires_auth
def manager_panel():
  conn = sqlite3.connect("hotel.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, hotel_id, room_number, service_type, message, timestamp,"
      " status FROM requests ORDER BY id DESC"
  )
  reqs = cursor.fetchall()
  conn.close()

  return render_template_string(MANAGER_TEMPLATE, requests=reqs)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
