# app.py
import streamlit as st
import json, os
from datetime import time
from main import (
    hash_password, load_user_data, save_user_data,
    USER_FILE, USER_DATA_DIR, GROUP_DIR
)

# Setup folder
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(GROUP_DIR, exist_ok=True)
if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

# Auth functions
def login(username, password):
    users = json.load(open(USER_FILE))
    hashed = hash_password(password)
    return username if username in users and users[username] == hashed else None

def register(username, password):
    users = json.load(open(USER_FILE))
    if username in users:
        return False
    users[username] = hash_password(password)
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)
    return True

# Streamlit config
st.set_page_config("📚 Student Productivity App", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

# Cek apakah pomodoro sedang aktif
if "pomodoro_active" not in st.session_state:
    st.session_state.pomodoro_active = False
if "pomodoro_end_time" not in st.session_state:
    st.session_state.pomodoro_end_time = None

# Login & register UI
def auth_form():
    st.markdown("<h1 style='text-align: center;'>📚 Aplikasi Produktivitas Mahasiswa</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Registrasi"])

    with tab1:
        st.subheader("Masuk ke akun Anda")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_btn"):
            user = login(username, password)
            if user:
                st.success(f"Selamat datang, {user}!")
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Username atau password salah.")

    with tab2:
        st.subheader("Buat akun baru")
        username = st.text_input("Username baru", key="reg_user")
        password = st.text_input("Password baru", type="password", key="reg_pass")
        if st.button("Daftar", key="register_btn"):
            if register(username, password):
                st.success("Registrasi berhasil, silakan login.")
            else:
                st.error("Username sudah digunakan.")

# Dashboard UI
def dashboard():
    st.sidebar.title(f"📌 Menu - {st.session_state.user}")
    menu = st.sidebar.radio("Navigasi", ["📝 To-Do List", "⏳ Pomodoro", "🤝 Kolaborasi", "👤 Profil", "🚪 Logout"])

    # Jika sedang Pomodoro dan user bukan di menu Pomodoro → blokir
    if st.session_state.pomodoro_active and menu != "⏳ Pomodoro":
        st.warning("⛔ Kamu sedang menjalankan Pomodoro! Selesaikan dulu sebelum berpindah menu.")
        st.stop()

    # if menu == "📝 To-Do List":
    #     data = load_user_data(st.session_state.user)
    #     st.header("📋 To-Do List & Statistik")
    #     st.markdown("---")
    #     task = st.text_input("➕ Tambah tugas baru", key="new_task")
    #     if st.button("Tambahkan", key="add_task_btn"):
    #         data["tasks"].append({"task": task, "done": False})
    #         save_user_data(st.session_state.user, data)

    #     st.subheader("📌 Daftar Tugas")
    #     for i, t in enumerate(data["tasks"]):
    #         col1, col2 = st.columns([0.85, 0.15])
    #         with col1:
    #             st.write(f"- {t['task']}")
    #         with col2:
    #             if not t["done"]:
    #                 if st.button("Selesai", key=f"done_{i}"):
    #                     data["tasks"][i]["done"] = True
    #                     data["completed_tasks"] += 1
    #                     save_user_data(st.session_state.user, data)
    #                     st.rerun()

    #     st.markdown("---")
    #     st.subheader("📈 Statistik")
    #     total = len(data["tasks"])
    #     done = data["completed_tasks"]
    #     focus = data["focus_time_minutes"]
    #     progress = (done / total) * 100 if total else 0
    #     st.write(f"- Total tugas     : {total}")
    #     st.write(f"- Tugas selesai   : {done}")
    #     st.write(f"- Waktu fokus     : {focus} menit")
    #     st.progress(progress / 100)

    #     weekly = data.get("weekly_focus", {})
    #     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    #     focus_values = [weekly.get(day, 0) for day in days]

    #     st.subheader("📅 Fokus Mingguan")
    #     # fig, ax = plt.subplots()
    #     # ax.bar(days, focus_values, color="skyblue")
    #     # ax.set_ylabel("Menit Fokus")
    #     # ax.set_title("Grafik Fokus per Hari")
    #     # plt.xticks(rotation=45)
    #     # st.pyplot(fig)
    #     # Buat dataframe untuk line chart
    #     # Buat dataframe untuk line chart
    #     import pandas as pd
    #     from datetime import datetime  # Import datetime here
        
    #     focus_data = pd.DataFrame({
    #         "Hari": days,
    #         "Menit Fokus": focus_values
    #     })
        
    #     # Tampilkan line chart dengan berbagai customisasi
    #     st.line_chart(
    #         focus_data.set_index("Hari"),
    #         height=400,
    #         use_container_width=True,
    #         color="#FF4B4B"  # Warna merah yang menarik
    #     )
        
    #     # Tambahkan metric untuk hari ini
    #     today_en = datetime.now().strftime("%A")  # English day name
    #     # Map English day names to Indonesian
    #     day_map = {
    #         "Monday": "Senin",
    #         "Tuesday": "Selasa",
    #         "Wednesday": "Rabu",
    #         "Thursday": "Kamis",
    #         "Friday": "Jumat",
    #         "Saturday": "Sabtu",
    #         "Sunday": "Minggu"
    #     }
    #     today_id = day_map.get(today_en, today_en)
    #     st.metric(
    #         label=f"Fokus Hari Ini ({today_id})",
    #         value=f"{weekly.get(today_id, 0)} menit"
    #     )

    if menu == "📝 To-Do List":
        from datetime import datetime, date, time  # Tambahkan import time dari datetime
        import pandas as pd

        data = load_user_data(st.session_state.user)
        st.header("📋 To-Do List & Statistik")
        st.markdown("---")

        # Input tambah tugas + deadline
        task = st.text_input("➕ Tambah tugas baru", key="new_task")
        deadline_date = st.date_input("📅 Tanggal deadline", min_value=date.today(), key="deadline_date")
        deadline_time = st.time_input("🕒 Jam deadline", value=datetime.now().time().replace(hour=23, minute=59), key="deadline_time")
        deadline_dt = datetime.combine(deadline_date, deadline_time)
        
        if st.button("Tambahkan", key="add_task_btn") and task:
            data["tasks"].append({
                "task": task,
                "done": False,
                "deadline": deadline_dt.isoformat(),
                "completed_time": None
            })
            save_user_data(st.session_state.user, data)
            st.success("Tugas berhasil ditambahkan!")
            st.rerun()

        st.subheader("📌 Daftar Tugas")

        # Filter & sort
        sort_option = st.selectbox("🔃 Urutkan berdasarkan deadline:", ["Terdekat", "Terlama"], key="sort_deadline")

        # Konversi deadline ke datetime dan sort
        def get_deadline(task):
            try:
                return datetime.fromisoformat(task["deadline"])
            except:
                return datetime.max

        tasks_sorted = sorted(data["tasks"], key=get_deadline, reverse=(sort_option == "Terlama"))

        now = datetime.now()

        for i, t in enumerate(tasks_sorted):
            col1, col2 = st.columns([0.85, 0.15])
            deadline = datetime.fromisoformat(t["deadline"])

            with col1:
                deadline_str = deadline.strftime("%d-%m-%Y %H:%M")
                status_line = f"- {t['task']} (🕒 Deadline: {deadline_str})"

                if not t["done"] and now > deadline:
                    status_line += " ❗ **Terlambat!**"
                elif t["done"] and t["completed_time"]:
                    completed_time = datetime.fromisoformat(t["completed_time"])
                    if completed_time > deadline:
                        status_line += " ✅ (Selesai tapi terlambat)"
                    else:
                        status_line += " ✅ (Selesai tepat waktu)"
                st.markdown(status_line)

            with col2:
                if not t["done"]:
                    if st.button("Selesai", key=f"done_{i}_{t['task']}"):
                        t["done"] = True
                        t["completed_time"] = now.isoformat()
                        data["completed_tasks"] += 1
                        save_user_data(st.session_state.user, data)
                        st.rerun()

        st.markdown("---")

        # Statistik
        st.subheader("📈 Statistik")
        total = len(data["tasks"])
        done = data["completed_tasks"]
        focus = data["focus_time_minutes"]
        progress = (done / total) * 100 if total else 0

        st.write(f"- Total tugas     : {total}")
        st.write(f"- Tugas selesai   : {done}")
        st.write(f"- Waktu fokus     : {focus} menit")
        st.progress(progress / 100)

        # Di bagian Fokus Mingguan
        weekly = data.get("weekly_focus", {})
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Mapping konversi Indonesia -> Inggris
        day_translation = {
            "Senin": "Monday",
            "Selasa": "Tuesday",
            "Rabu": "Wednesday",
            "Kamis": "Thursday",
            "Jumat": "Friday",
            "Sabtu": "Saturday",
            "Minggu": "Sunday"
        }

        # Konversi key ke bahasa Inggris
        converted_weekly = {}
        for day_id, minutes in weekly.items():
            day_en = day_translation.get(day_id, day_id)
            converted_weekly[day_en] = minutes

        # Isi hari yang belum ada dengan 0
        focus_values = [converted_weekly.get(day, 0) for day in days_order]

        # Buat grafik
        focus_data = pd.DataFrame({
            "Hari": days_order,
            "Menit Fokus": focus_values
        })

        st.line_chart(
            focus_data.set_index("Hari"),
            height=400,
            use_container_width=True,
            color="#FF4B4B"
        )

        # Metric Hari Ini
        today_en = datetime.now().strftime("%A")
        day_map = {
            "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
            "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
        }

        today_id = day_map.get(today_en, today_en)
        st.metric(
            label=f"Fokus Hari Ini ({today_id})",
            value=f"{weekly.get(today_id, 0)} menit"
        )


    # elif menu == "⏳ Pomodoro":
    #     st.header("⏳ Pomodoro Fokus")
    #     duration = st.slider("Pilih durasi fokus (menit)", 5, 120, 25)

    #     if st.button("Mulai Fokus", key="start_pomodoro"):
    #         st.success("🧠 Fokus dimulai! Jangan buka media sosial dulu ya...")
    #         placeholder = st.empty()
    #         for i in range(duration * 60, 0, -1):
    #             mins, secs = divmod(i, 60)
    #             timer = f"{mins:02d}:{secs:02d}"
    #             placeholder.markdown(f"<h2 style='text-align: center;'>⏳ {timer}</h2>", unsafe_allow_html=True)
    #             time.sleep(1)

    #         st.success("✅ Sesi fokus selesai! Saatnya istirahat.")

    #         # Simpan ke data user
    #         data = load_user_data(st.session_state.user)
    #         data["focus_time_minutes"] += duration
    #         day = datetime.now().strftime("%A")
    #         data.setdefault("weekly_focus", {})
    #         data["weekly_focus"][day] = data["weekly_focus"].get(day, 0) + duration
    #         save_user_data(st.session_state.user, data)

    elif menu == "⏳ Pomodoro":
        st.header("⏳ Pomodoro Time")

        # Definisikan mapping hari di sini
        day_map = {
            "Monday": "Senin",
            "Tuesday": "Selasa",
            "Wednesday": "Rabu",
            "Thursday": "Kamis",
            "Friday": "Jumat",
            "Saturday": "Sabtu",
            "Sunday": "Minggu"
        }
        import time
        from datetime import datetime, timedelta
        # Inisialisasi state
        if 'pomodoro_active' not in st.session_state:
            st.session_state.pomodoro_active = False
        if 'pomodoro_start_time' not in st.session_state:
            st.session_state.pomodoro_start_time = datetime.now()
        if 'pomodoro_duration' not in st.session_state:
            st.session_state.pomodoro_duration = 25
        if 'last_update' not in st.session_state:
            st.session_state.last_update = 0

        # Fungsi untuk memulai Pomodoro
        def start_pomodoro():
            st.session_state.pomodoro_active = True
            st.session_state.pomodoro_start_time = datetime.now()
            st.session_state.last_update = 0

        # Fungsi untuk menghentikan Pomodoro
        def stop_pomodoro():
            if st.session_state.pomodoro_start_time:
                elapsed = datetime.now() - st.session_state.pomodoro_start_time
                elapsed_minutes = int(elapsed.total_seconds() / 60)
                
                if elapsed_minutes > 0:
                    data = load_user_data(st.session_state.user)
                    data["focus_time_minutes"] += elapsed_minutes
                    
                    today_en = datetime.now().strftime("%A")
                    today_id = day_map.get(today_en, today_en)
                    data.setdefault("weekly_focus", {})
                    data["weekly_focus"][today_id] = data["weekly_focus"].get(today_id, 0) + elapsed_minutes
                    save_user_data(st.session_state.user, data)
            
            st.session_state.pomodoro_active = False
            st.session_state.pomodoro_start_time = None

        if not st.session_state.pomodoro_active:
            st.session_state.pomodoro_duration = st.slider("Durasi Pomodoro (menit)", 1, 120, 25)
            if st.button("▶️ Mulai Pomodoro", on_click=start_pomodoro):
                pass
        else:
            if st.session_state.pomodoro_start_time is None:
                st.error("Error: Waktu mulai tidak valid")
                st.session_state.pomodoro_active = False
                st.rerun()
            
            now = datetime.now()
            elapsed = now - st.session_state.pomodoro_start_time
            remaining = st.session_state.pomodoro_duration * 60 - elapsed.total_seconds()
            
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                
                timer_placeholder = st.empty()
                timer_placeholder.info(f"⏳ Waktu tersisa: {minutes:02d}:{seconds:02d}")
                st.write("📌 Fokus dulu, jangan pindah ke menu lain ya!")
                
                if st.button("⏹️ Hentikan Pomodoro", on_click=stop_pomodoro):
                    pass
                
                # Gunakan time.sleep dari modul time, bukan datetime.time
                time.sleep(1)
                st.rerun()
            else:
                st.success("✅ Pomodoro selesai! Silakan istirahat sejenak.")
                st.balloons()
                
                data = load_user_data(st.session_state.user)
                data["focus_time_minutes"] += st.session_state.pomodoro_duration
                
                today_en = datetime.now().strftime("%A")
                today_id = day_map.get(today_en, today_en)
                data.setdefault("weekly_focus", {})
                data["weekly_focus"][today_id] = data["weekly_focus"].get(today_id, 0) + st.session_state.pomodoro_duration
                save_user_data(st.session_state.user, data)
                
                st.session_state.pomodoro_active = False
                st.session_state.pomodoro_start_time = None
                time.sleep(3)
                st.rerun()



    # elif menu == "🤝 Kolaborasi":
    #     st.header("🤝 Daftar Grup Kolaborasi")

    #     # Load all users (for validation)
    #     users = json.load(open(USER_FILE))

    #     # Ambil semua grup yang melibatkan user
    #     group_files = [f for f in os.listdir(GROUP_DIR) if f.endswith(".json")]
    #     user_groups = []
    #     for file in group_files:
    #         path = os.path.join(GROUP_DIR, file)
    #         with open(path, 'r') as f:
    #             group_data = json.load(f)
    #             if st.session_state.user in group_data.get("members", []):
    #                 user_groups.append((file.replace(".json", ""), group_data))

    #     if not user_groups:
    #         st.info("🚫 Kamu belum tergabung dalam grup mana pun.")
    #     else:
    #         for group_name, group in user_groups:
    #             with st.expander(f"📁 {group_name}"):
    #                 st.write(f"👥 Anggota: {', '.join(group['members'])}")

    #                 # Invite member section
    #                 st.subheader("➕ Undang Anggota Baru")
    #                 invite_user = st.text_input(f"Masukkan username untuk diundang ke '{group_name}'", key=f"invite_{group_name}")

    #                 if st.button(f"Undang {invite_user} ke {group_name}", key=f"invite_btn_{group_name}") and invite_user:
    #                     if invite_user in group["members"]:
    #                         st.warning(f"User '{invite_user}' sudah menjadi anggota grup.")
    #                     else:
    #                         if invite_user in users:
    #                             # User terdaftar, langsung invite
    #                             group["members"].append(invite_user)
    #                             with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
    #                                 json.dump(group, f, indent=4)
    #                             st.success(f"User '{invite_user}' berhasil diundang ke grup '{group_name}'.")
    #                             st.rerun()
    #                         else:
    #                             # User belum terdaftar, minta konfirmasi
    #                             confirm = st.checkbox(f"User '{invite_user}' tidak terdaftar. Tetap undang?")
    #                             if confirm:
    #                                 group["members"].append(invite_user)
    #                                 with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
    #                                     json.dump(group, f, indent=4)
    #                                 st.success(f"User '{invite_user}' berhasil diundang ke grup '{group_name}' meski belum terdaftar.")
    #                                 st.rerun()

    #                 # Progress bar grup
    #                 total_tasks = len(group["tasks"])
    #                 completed = sum(1 for t in group["tasks"] if t["done"])
    #                 progress = (completed / total_tasks) * 100 if total_tasks else 0
    #                 st.progress(progress / 100)
    #                 st.caption(f"Progress: {completed}/{total_tasks} tugas selesai")

    #                 # Tambah tugas grup
    #                 new_task = st.text_input(f"Tambah tugas di {group_name}", key=f"task_{group_name}")
    #                 if st.button(f"Tambahkan Tugas ke {group_name}", key=f"add_{group_name}"):
    #                     group["tasks"].append({"task": new_task, "by": st.session_state.user, "done": False})
    #                     with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
    #                         json.dump(group, f, indent=4)
    #                     st.success("✅ Tugas ditambahkan.")
    #                     st.rerun()

    #                 # Lihat tugas grup
    #                 for i, t in enumerate(group["tasks"]):
    #                     col1, col2 = st.columns([0.85, 0.15])
    #                     with col1:
    #                         st.write(f"- {t['task']} (oleh {t['by']})")
    #                     with col2:
    #                         if not t["done"] and st.button("Selesai", key=f"{group_name}_done_{i}"):
    #                             group["tasks"][i]["done"] = True
    #                             with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
    #                                 json.dump(group, f, indent=4)
    #                             st.rerun()

    #                 st.subheader("💬 Motivasi")
    #                 msg = st.text_area(f"Tulis pesan semangat untuk {group_name}", key=f"msg_{group_name}")
    #                 if st.button(f"Kirim Motivasi ke {group_name}", key=f"send_motivasi_{group_name}"):
    #                     group["motivations"].append({"from": st.session_state.user, "msg": msg})
    #                     with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
    #                         json.dump(group, f, indent=4)
    #                     st.success("Motivasi dikirim!")

    #                 for m in group["motivations"]:
    #                     st.info(f"{m['from']}: {m['msg']}")

    #     st.markdown("---")
    #     st.subheader("➕ Buat / Gabung Grup Baru")
    #     new_group_name = st.text_input("Nama grup baru / yang ingin kamu ikuti")
    #     if st.button("Gabung / Buat Grup"):
    #         group_path = os.path.join(GROUP_DIR, f"{new_group_name}.json")
    #         if os.path.exists(group_path):
    #             group = json.load(open(group_path))
    #             if st.session_state.user not in group["members"]:
    #                 group["members"].append(st.session_state.user)
    #         else:
    #             group = {"members": [st.session_state.user], "tasks": [], "motivations": []}
    #         with open(group_path, 'w') as f:
    #             json.dump(group, f, indent=4)
    #         st.success(f"Berhasil bergabung dengan grup '{new_group_name}'!")
    #         st.rerun()


    elif menu == "🤝 Kolaborasi":
        st.header("🤝 Daftar Grup Kolaborasi")

        users_all = list(json.load(open(USER_FILE)).keys())  # Semua username terdaftar

        # Cari grup yang melibatkan user
        group_files = [f for f in os.listdir(GROUP_DIR) if f.endswith(".json")]
        user_groups = []
        for file in group_files:
            path = os.path.join(GROUP_DIR, file)
            with open(path, 'r') as f:
                group_data = json.load(f)
                if st.session_state.user in group_data.get("members", []):
                    user_groups.append((file.replace(".json", ""), group_data))

        if not user_groups:
            st.info("🚫 Kamu belum tergabung dalam grup mana pun.")
        else:
            for group_name, group in user_groups:
                with st.expander(f"📁 {group_name} (Creator: {group.get('creator', 'unknown')})"):

                    st.write(f"👥 Anggota: {', '.join(group['members'])}")

                    # Progress bar grup
                    total_tasks = len(group["tasks"])
                    completed = sum(1 for t in group["tasks"] if t["done"])
                    progress = (completed / total_tasks) * 100 if total_tasks else 0
                    st.progress(progress / 100)
                    st.caption(f"Progress: {completed}/{total_tasks} tugas selesai")

                    # Tambah tugas grup
                    new_task = st.text_input(f"Tambah tugas di {group_name}", key=f"task_{group_name}")
                    if st.button(f"Tambahkan Tugas ke {group_name}", key=f"add_{group_name}"):
                        group["tasks"].append({"task": new_task, "by": st.session_state.user, "done": False})
                        with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
                            json.dump(group, f, indent=4)
                        st.success("✅ Tugas ditambahkan.")
                        st.rerun()

                    # Lihat tugas grup dan tombol selesai
                    for i, t in enumerate(group["tasks"]):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.write(f"- {t['task']} (oleh {t['by']})")
                        with col2:
                            if not t["done"] and st.button("Selesai", key=f"{group_name}_done_{i}"):
                                group["tasks"][i]["done"] = True
                                with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
                                    json.dump(group, f, indent=4)
                                st.rerun()

                    st.subheader("💬 Motivasi")
                    msg = st.text_area(f"Tulis pesan semangat untuk {group_name}", key=f"msg_{group_name}")
                    if st.button(f"Kirim Motivasi ke {group_name}", key=f"send_motivasi_{group_name}"):
                        group["motivations"].append({"from": st.session_state.user, "msg": msg})
                        with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
                            json.dump(group, f, indent=4)
                        st.success("Motivasi dikirim!")

                    for m in group["motivations"]:
                        st.info(f"{m['from']}: {m['msg']}")

                    # -------------------
                    # Bagian Invite Member (hanya creator yang bisa)
                    if group.get("creator") == st.session_state.user:
                        st.markdown("---")
                        st.subheader("➕ Undang Anggota Baru")
                        # Siapkan list user yang belum anggota
                        available_to_invite = [u for u in users_all if u not in group["members"]]

                        if available_to_invite:
                            invite_user = st.selectbox(
                                f"Pilih username untuk undang ke grup {group_name}",
                                options=available_to_invite,
                                key=f"invite_{group_name}"
                            )
                            if st.button(f"Undang anggota ke {group_name}", key=f"invite_btn_{group_name}"):
                                group["members"].append(invite_user)
                                with open(os.path.join(GROUP_DIR, f"{group_name}.json"), 'w') as f:
                                    json.dump(group, f, indent=4)
                                st.success(f"User '{invite_user}' berhasil ditambahkan ke grup {group_name}.")
                                st.rerun()
                        else:
                            st.info("Tidak ada user yang tersedia untuk diundang.")

        st.markdown("---")
        st.subheader("➕ Buat / Gabung Grup Baru")
        new_group_name = st.text_input("Nama grup baru / yang ingin kamu ikuti")
        if st.button("Gabung / Buat Grup"):
            group_path = os.path.join(GROUP_DIR, f"{new_group_name}.json")
            if os.path.exists(group_path):
                group = json.load(open(group_path))
                if st.session_state.user not in group["members"]:
                    group["members"].append(st.session_state.user)
            else:
                # Saat buat grup baru, simpan creator-nya juga
                group = {"creator": st.session_state.user, "members": [st.session_state.user], "tasks": [], "motivations": []}
            with open(group_path, 'w') as f:
                json.dump(group, f, indent=4)
            st.success(f"Berhasil bergabung dengan grup '{new_group_name}'!")
            st.rerun()


    elif menu == "👤 Profil":
        st.header("👤 Profil Pengguna")
        data = load_user_data(st.session_state.user)
        st.write(f"**Username:** {st.session_state.user}")
        st.write(f"**Total tugas:** {len(data['tasks'])}")
        st.write(f"**Tugas selesai:** {data['completed_tasks']}")
        st.write(f"**Total waktu fokus:** {data['focus_time_minutes']} menit")


    elif menu == "🚪 Logout":
        st.session_state.user = None
        st.rerun()

# Jalankan tampilan
if st.session_state.user:
    dashboard()
else:
    auth_form()
