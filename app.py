# app.py
import streamlit as st
import json, os, time
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

    if menu == "📝 To-Do List":
        data = load_user_data(st.session_state.user)
        st.header("📋 To-Do List & Statistik")
        st.markdown("---")
        task = st.text_input("➕ Tambah tugas baru", key="new_task")
        if st.button("Tambahkan", key="add_task_btn"):
            data["tasks"].append({"task": task, "done": False})
            save_user_data(st.session_state.user, data)

        st.subheader("📌 Daftar Tugas")
        for i, t in enumerate(data["tasks"]):
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.write(f"- {t['task']}")
            with col2:
                if not t["done"]:
                    if st.button("Selesai", key=f"done_{i}"):
                        data["tasks"][i]["done"] = True
                        data["completed_tasks"] += 1
                        save_user_data(st.session_state.user, data)
                        st.rerun()

        st.markdown("---")
        st.subheader("📈 Statistik")
        total = len(data["tasks"])
        done = data["completed_tasks"]
        focus = data["focus_time_minutes"]
        progress = (done / total) * 100 if total else 0
        st.write(f"- Total tugas     : {total}")
        st.write(f"- Tugas selesai   : {done}")
        st.write(f"- Waktu fokus     : {focus} menit")
        st.progress(progress / 100)

        weekly = data.get("weekly_focus", {})
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        focus_values = [weekly.get(day, 0) for day in days]

        st.subheader("📅 Fokus Mingguan")
        # fig, ax = plt.subplots()
        # ax.bar(days, focus_values, color="skyblue")
        # ax.set_ylabel("Menit Fokus")
        # ax.set_title("Grafik Fokus per Hari")
        # plt.xticks(rotation=45)
        # st.pyplot(fig)
        # Buat dataframe untuk line chart
        # Buat dataframe untuk line chart
        import pandas as pd
        from datetime import datetime  # Import datetime here
        
        focus_data = pd.DataFrame({
            "Hari": days,
            "Menit Fokus": focus_values
        })
        
        # Tampilkan line chart dengan berbagai customisasi
        st.line_chart(
            focus_data.set_index("Hari"),
            height=400,
            use_container_width=True,
            color="#FF4B4B"  # Warna merah yang menarik
        )
        
        # Tambahkan metric untuk hari ini
        today_en = datetime.now().strftime("%A")  # English day name
        # Map English day names to Indonesian
        day_map = {
            "Monday": "Senin",
            "Tuesday": "Selasa",
            "Wednesday": "Rabu",
            "Thursday": "Kamis",
            "Friday": "Jumat",
            "Saturday": "Sabtu",
            "Sunday": "Minggu"
        }
        today_id = day_map.get(today_en, today_en)
        st.metric(
            label=f"Fokus Hari Ini ({today_id})",
            value=f"{weekly.get(today_id, 0)} menit"
        )

    elif menu == "⏳ Pomodoro":
        st.header("⏳ Pomodoro Fokus")
        duration = st.slider("Pilih durasi fokus (menit)", 5, 120, 25)

        if st.button("Mulai Fokus", key="start_pomodoro"):
            st.success("🧠 Fokus dimulai! Jangan buka media sosial dulu ya...")
            placeholder = st.empty()
            for i in range(duration * 60, 0, -1):
                mins, secs = divmod(i, 60)
                timer = f"{mins:02d}:{secs:02d}"
                placeholder.markdown(f"<h2 style='text-align: center;'>⏳ {timer}</h2>", unsafe_allow_html=True)
                time.sleep(1)

            st.success("✅ Sesi fokus selesai! Saatnya istirahat.")

            # Simpan ke data user
            data = load_user_data(st.session_state.user)
            data["focus_time_minutes"] += duration
            day = datetime.now().strftime("%A")
            data.setdefault("weekly_focus", {})
            data["weekly_focus"][day] = data["weekly_focus"].get(day, 0) + duration
            save_user_data(st.session_state.user, data)

    elif menu == "⏳ Pomodoro":
        st.header("⏳ Pomodoro Time")

        import datetime

        if not st.session_state.pomodoro_active:
            duration = st.slider("Durasi Pomodoro (menit)", 5, 60, 25)
            if st.button("▶️ Mulai Pomodoro"):
                st.session_state.pomodoro_active = True
                st.session_state.pomodoro_end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)
                st.success(f"Pomodoro dimulai selama {duration} menit! Jangan pindah menu ya 🙌")
                st.rerun()
        else:
            now = datetime.datetime.now()
            end = st.session_state.pomodoro_end_time
            remaining = (end - now).total_seconds()

            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                st.info(f"⏳ Waktu tersisa: {minutes:02d}:{seconds:02d}")
                st.write("📌 Fokus dulu, jangan pindah ke menu lain ya!")
                st.button("⏹️ Paksa Berhenti Pomodoro", on_click=lambda: st.session_state.update({
                    "pomodoro_active": False,
                    "pomodoro_end_time": None
                }))
                st.rerun()
            else:
                st.success("✅ Pomodoro selesai! Silakan lanjutkan aktivitasmu.")
                st.balloons()
                st.session_state.pomodoro_active = False
                st.session_state.pomodoro_end_time = None
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
