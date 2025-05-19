import json, os, hashlib, time
from datetime import datetime

DATA_FOLDER = 'data'
USER_FILE = os.path.join(DATA_FOLDER, 'users.json')
USER_DATA_DIR = os.path.join(DATA_FOLDER, 'user_data')
GROUP_DIR = os.path.join(DATA_FOLDER, 'groups')

# Buat folder jika belum ada
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(GROUP_DIR, exist_ok=True)
if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

# === Utility Functions ===
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_data(username):
    path = os.path.join(USER_DATA_DIR, f"{username}.json")
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({"tasks": [], "focus_time_minutes": 0, "completed_tasks": 0, "weekly_focus": {}}, f)
    with open(path, 'r') as f:
        return json.load(f)

def save_user_data(username, data):
    path = os.path.join(USER_DATA_DIR, f"{username}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# === Authentication ===
def login():
    users = json.load(open(USER_FILE))
    username = input("👤 Username: ")
    password = input("🔑 Password: ")
    hashed = hash_password(password)
    if username in users and users[username] == hashed:
        print(f"✅ Selamat datang kembali, {username}!")
        return username
    else:
        print("❌ Username atau password salah.")
        return None

def register():
    users = json.load(open(USER_FILE))
    username = input("🆕 Buat username: ")
    if username in users:
        print("❗ Username sudah digunakan.")
        return None
    password = input("🔑 Buat password: ")
    users[username] = hash_password(password)
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)
    print(f"✅ Akun {username} berhasil dibuat!")
    return username

def auth_menu():
    while True:
        print("""
🔐 LOGIN SISTEM
1. Login
2. Registrasi
3. Keluar
        """)
        choice = input("Pilih (1-3): ")
        if choice == '1':
            user = login()
            if user:
                return user
        elif choice == '2':
            user = register()
            if user:
                return user
        elif choice == '3':
            exit()
        else:
            print("❌ Pilihan tidak valid.")

# === To-Do & Statistik ===
def todo_menu(username):
    data = load_user_data(username)
    while True:
        print(f"""
📝 TO-DO LIST - {username}
1. Tambah tugas
2. Lihat tugas
3. Tandai tugas selesai
4. Statistik
5. Kembali
        """)
        choice = input("Pilih: ")
        if choice == '1':
            task = input("Masukkan nama tugas: ")
            data["tasks"].append({"task": task, "done": False})
            save_user_data(username, data)
            print("✅ Tugas ditambahkan!")
        elif choice == '2':
            if not data["tasks"]:
                print("📭 Tidak ada tugas.")
            for i, t in enumerate(data["tasks"]):
                status = "✅" if t["done"] else "❌"
                print(f"{i+1}. {t['task']} [{status}]")
        elif choice == '3':
            for i, t in enumerate(data["tasks"]):
                status = "✅" if t["done"] else "❌"
                print(f"{i+1}. {t['task']} [{status}]")
            idx = int(input("Tugas mana yang selesai (nomor): ")) - 1
            if 0 <= idx < len(data["tasks"]):
                data["tasks"][idx]["done"] = True
                data["completed_tasks"] += 1
                save_user_data(username, data)
                print("🎉 Tugas ditandai selesai!")
        elif choice == '4':
            total = len(data["tasks"])
            done = data["completed_tasks"]
            focus = data["focus_time_minutes"]
            progress = (done / total) * 100 if total else 0
            print(f"""
        📊 STATISTIK
        - Total tugas      : {total}
        - Tugas selesai    : {done}
        - Fokus (menit)    : {focus}
        - Progress         : {progress:.2f}%
            """)

            print("Grafik Fokus Mingguan (menit):")
            weekly = data.get("weekly_focus", {})
            max_focus = max(weekly.values(), default=1)
            scale = max_focus // 25 or 1  # setiap █ mewakili ~1-25 menit

            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                dur = weekly.get(day, 0)
                bar = "█" * (dur // scale) if dur > 0 else ""
                print(f"{day:<9}: {bar} {dur}")
        elif choice == '5':
            break

# === Pomodoro ===
def pomodoro_timer(username):
    data = load_user_data(username)
    try:
        duration = int(input("Masukkan durasi sesi fokus (menit): "))
    except ValueError:
        print("❌ Input tidak valid.")
        return
    print(f"⏳ Fokus selama {duration} menit dimulai...")
    time.sleep(duration * 60)  # Ganti ke time.sleep(3) untuk versi cepat
    data["focus_time_minutes"] += duration

    # Update grafik mingguan
    day = datetime.now().strftime("%A")
    if "weekly_focus" not in data:
        data["weekly_focus"] = {}
    data["weekly_focus"][day] = data["weekly_focus"].get(day, 0) + duration

    save_user_data(username, data)
    print("✅ Sesi fokus selesai! Saatnya istirahat.")

# === Group Collaboration ===
def group_menu(username):
    print("\n🤝 MENU GRUP")
    group_name = input("Masukkan nama grup yang ingin kamu masuki/buat: ")
    group_path = os.path.join(GROUP_DIR, f"{group_name}.json")
    if not os.path.exists(group_path):
        group = {"members": [username], "tasks": [], "motivations": []}
    else:
        group = json.load(open(group_path))
        if username not in group["members"]:
            group["members"].append(username)

    def save_group():
        with open(group_path, 'w') as f:
            json.dump(group, f, indent=4)

    save_group()

    while True:
        print(f"""
🤝 GRUP: {group_name}
1. Tambah tugas grup
2. Lihat semua tugas & progress
3. Kirim pesan motivasi
4. Lihat motivasi dari teman
5. Kembali
        """)
        choice = input("Pilih: ")
        if choice == '1':
            task = input("Tugas grup: ")
            group["tasks"].append({"task": task, "by": username, "done": False})
            save_group()
            print("✅ Tugas grup ditambahkan.")
        elif choice == '2':
            for t in group["tasks"]:
                status = "✅" if t["done"] else "❌"
                print(f"- {t['task']} [{status}] (oleh {t['by']})")
        elif choice == '3':
            msg = input("Tulis pesan semangat: ")
            group["motivations"].append({"from": username, "msg": msg})
            save_group()
            print("💬 Pesan semangat dikirim!")
        elif choice == '4':
            print("\n💌 Motivasi dari teman:")
            for m in group["motivations"]:
                print(f"- {m['from']}: {m['msg']}")
        elif choice == '5':
            break

# === Main Dashboard ===
def user_dashboard(username):
    while True:
        print(f"""
📌 DASHBOARD {username}
1. To-Do List & Statistik
2. Pomodoro Timer
3. Grup Kolaborasi
4. Logout
        """)
        choice = input("Pilih menu: ")
        if choice == '1':
            todo_menu(username)
        elif choice == '2':
            pomodoro_timer(username)
        elif choice == '3':
            group_menu(username)
        elif choice == '4':
            break

if __name__ == '__main__':
    user = auth_menu()
    user_dashboard(user)
