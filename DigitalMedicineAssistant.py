import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import winsound
import json
import os

# --- MODELLER ---

class UserProfile:
    def __init__(self, name, gender, age, blood, weight, height):
        self.name = name.upper()
        self.gender = gender
        # Cinsiyete göre hitap belirleme
        self.title = "BEY" if gender == "Erkek" else "HANIM"
        self.age = age
        self.blood = blood
        self.weight = weight
        self.height = height

    def to_dict(self):
        return {
            "name": self.name, "gender": self.gender, "age": self.age,
            "blood": self.blood, "weight": self.weight, "height": self.height
        }

class Medicine:
    def __init__(self, name_dosage, freq_text, intake):
        self.name_dosage = name_dosage
        self.frequency = freq_text
        self.intake_condition = intake 

    def to_dict(self):
        return {"name_dosage": self.name_dosage, "frequency": self.frequency, "intake_condition": self.intake_condition}

class MedicationReminder:
    def __init__(self, medicine, time_str, status="Bekliyor"):
        self.medicine = medicine
        self.time = time_str
        self.status = status

    def to_dict(self):
        return {
            "medicine": self.medicine.to_dict(),
            "time": self.time,
            "status": self.status
        }

# --- ANA UYGULAMA ---

class DigitalMedicineAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Medicine Assistant Pro v10.0 (Ultimate Edition)")
        self.root.state('zoomed')
        self.root.configure(bg="#F3E5F5")

        self.db_file = "med_data.json"
        self.current_email = None
        self.user = None
        self.reminders = []
        self.is_logged_in = False
        
        # Veri Saklama Değişkenleri (Bellek)
        self.saved_history = {
            "chronic": [],
            "surgery": [],
            "allergy": []
        }
        self.saved_vitals = {}
        self.saved_pregnancy = {}

        self.lila_dark = "#7B1FA2" 
        self.lila_main = "#9C27B0" 
        self.lila_light = "#E1BEE7" 

        # --- LİSTELER (GÜNCELLENDİ) ---
        self.med_only_list = [
            "Arveles (25mg)", "Parol (500mg)", "Apranax (550mg)", "Lansor (30mg)", "Coraspin (100mg)",
            "Glifor (1000mg)", "Augmentin (1000mg)", "Cipralex (10mg)", "Nexium (40mg)", "Euthyrox (50mcg)",
            "Majezik (100mg)", "Dikloron (75mg)", "Buscopan (10mg)", "Xanax (0.5mg)", "Atarax (25mg)",
            "Amoklavin", "Klavunat", "Duphalac", "Xarelto", "Ecopirin", "Lipitor", "Crestor", "Beloc ZOK",
            "Co-Diovan", "Exforge", "Norvasc", "Vasoxen", "Lustral", "Passiflora", "Tylolhot", "DİĞER"
        ]
        
        self.vitamin_only_list = [
            "D Vitamini (Damla/Hap)", "B12 Vitamini", "C Vitamini", "Multivitamin", "Omega 3 (Balık Yağı)",
            "Magnezyum", "Demir Hapı (Ferro)", "Kalsiyum", "Çinko", "Biotin", "Folik Asit", "Probiyotik",
            "Kolajen", "Glukozamin", "Ginseng", "DİĞER"
        ]

        # Genişletilmiş Listeler
        self.chronic_list = [
            "Hipertansiyon", "Diyabet (Tip 1)", "Diyabet (Tip 2)", "Astım", "KOAH", "Hipotiroidi", 
            "Hipertiroidi", "Migren", "Anemi", "Romatizma", "Kalp Yetmezliği", "Epilepsi", 
            "Böbrek Yetmezliği", "Gastrit/Ülser", "DİĞER"
        ]
        self.surgery_list = [
            "Bypass", "Kalp Kapakçığı", "Beyin Tümörü", "Anevrizma Cerrahisi", "Stent", "Apandisit",
            "Sezaryen", "Safra Kesesi", "Fıtık Ameliyatı", "Bademcik", "Katarakt", "Prostat", "DİĞER"
        ]
        self.allergy_list = [
            "Penisilin", "Aspirin", "Sülfonamid", "Polen", "Lateks", "Arı Zehri",
            "Yer Fıstığı", "Süt/Laktoz", "Yumurta", "Deniz Ürünleri", "Toz Akarı", "Kedi/Köpek Tüyü", "DİĞER"
        ]

        self.setup_styles()
        self.load_database()
        self.show_auth_screen()

    # --- VERİTABANI ---
    def load_database(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.db_data = json.load(f)
            except:
                self.db_data = {}
        else:
            self.db_data = {}

    def save_to_database(self):
        if self.current_email and self.user:
            # UI'daki güncel verileri çekmeye çalış, yoksa hafızadakini kullan
            vitals = self.get_vitals_ui_data() if hasattr(self, 'vital_vars') else self.saved_vitals
            pregnancy = self.get_pregnancy_ui_data() if hasattr(self, 'preg_vars') else self.saved_pregnancy
            
            # Sağlık geçmişi UI açıksa oradan al, değilse hafızadan
            history = self.saved_history 
            if hasattr(self, 'history_lbs'): # Eğer UI oluşturulmuşsa listboxlardan güncelini al
                history = self.get_history_from_ui()

            user_save_data = {
                "password": self.current_password,
                "profile": self.user.to_dict(),
                "reminders": [r.to_dict() for r in self.reminders],
                "history_data": history,
                "vitals_data": vitals,
                "pregnancy_data": pregnancy
            }
            self.db_data[self.current_email] = user_save_data
            
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump(self.db_data, f, ensure_ascii=False, indent=4)
            print("Veriler Kaydedildi.")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#F3E5F5", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[20, 10], background="#E1BEE7")
        style.map("TNotebook.Tab", background=[("selected", "#9C27B0")], foreground=[("selected", "white")])
        style.map("TCombobox", fieldbackground=[("readonly", "white")], selectbackground=[("readonly", "#9C27B0")])

    # --- GİRİŞ / KAYIT EKRANI ---
    def show_auth_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg="#F3E5F5")
        
        self.auth_frame = tk.Frame(self.root, bg="#F3E5F5")
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.auth_tabs = ttk.Notebook(self.auth_frame)
        self.auth_tabs.pack(fill="both", expand=True)

        self.tab_login = tk.Frame(self.auth_tabs, bg="white", padx=40, pady=40)
        self.tab_register = tk.Frame(self.auth_tabs, bg="white", padx=40, pady=40)

        self.auth_tabs.add(self.tab_login, text="  GİRİŞ YAP  ")
        self.auth_tabs.add(self.tab_register, text="  KAYDOL  ")

        # GİRİŞ
        tk.Label(self.tab_login, text="HOŞGELDİNİZ", font=("Segoe UI", 18, "bold"), fg=self.lila_dark, bg="white").pack(pady=(0, 20))
        self.l_email = self.create_auth_entry(self.tab_login, "E-Posta:")
        self.l_pass = self.create_auth_entry(self.tab_login, "Şifre:", show="*")
        tk.Button(self.tab_login, text="GİRİŞ YAP", command=self.perform_login, bg=self.lila_main, fg="white", font=("bold", 12), bd=0, pady=10, width=20).pack(pady=20)

        # KAYIT (Cinsiyet Eklendi)
        tk.Label(self.tab_register, text="YENİ HESAP", font=("Segoe UI", 18, "bold"), fg=self.lila_dark, bg="white").pack(pady=(0, 20))
        self.r_name = self.create_auth_entry(self.tab_register, "Ad Soyad:")
        
        tk.Label(self.tab_register, text="Cinsiyet:", bg="white", font=("bold", 9)).pack(anchor="w")
        self.r_gender = ttk.Combobox(self.tab_register, values=["Kadın", "Erkek"], state="readonly", font=("Segoe UI", 11), width=28)
        self.r_gender.pack(pady=(2, 15)); self.r_gender.set("Kadın")

        self.r_email = self.create_auth_entry(self.tab_register, "E-Posta:")
        self.r_pass = self.create_auth_entry(self.tab_register, "Şifre:", show="*")
        tk.Button(self.tab_register, text="KAYDOL", command=self.perform_register, bg="#E91E63", fg="white", font=("bold", 12), bd=0, pady=10, width=20).pack(pady=20)

    def create_auth_entry(self, parent, label, show=None):
        tk.Label(parent, text=label, bg="white", font=("bold", 9)).pack(anchor="w")
        e = tk.Entry(parent, font=("Segoe UI", 11), bd=1, relief="solid", show=show, width=30)
        e.pack(pady=(2, 15)); return e

    def perform_login(self):
        email = self.l_email.get().strip()
        password = self.l_pass.get().strip()
        if not email or not password: messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun."); return

        if email in self.db_data:
            if self.db_data[email]["password"] == password:
                self.load_user_data(email, password)
            else: messagebox.showerror("Hata", "Şifre yanlış!")
        else: messagebox.showerror("Hata", "Kayıt bulunamadı.")

    def perform_register(self):
        name = self.r_name.get().strip().upper()
        email = self.r_email.get().strip()
        password = self.r_pass.get().strip()
        gender = self.r_gender.get()

        if not name or not email or not password: messagebox.showwarning("Uyarı", "Tüm alanlar zorunludur."); return
        if email in self.db_data: messagebox.showerror("Hata", "E-posta zaten kayıtlı."); return

        new_user = UserProfile(name, gender, "30", "A+", "60", "165")
        self.db_data[email] = {
            "password": password,
            "profile": new_user.to_dict(),
            "reminders": [],
            "history_data": {"chronic": [], "surgery": [], "allergy": []},
            "vitals_data": {},
            "pregnancy_data": {}
        }
        with open(self.db_file, "w", encoding="utf-8") as f: json.dump(self.db_data, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Başarılı", "Kayıt oluşturuldu! Giriş yapabilirsiniz."); self.auth_tabs.select(self.tab_login)

    def load_user_data(self, email, password):
        saved_user = self.db_data[email]
        self.current_email = email
        self.current_password = password
        
        p_data = saved_user["profile"]
        # Profil oluşturulurken cinsiyet veritabanından, başlık otomatik hesaplanır
        self.user = UserProfile(p_data["name"], p_data["gender"], p_data["age"], p_data["blood"], p_data["weight"], p_data["height"])
        
        self.reminders = []
        for r in saved_user.get("reminders", []):
            med = Medicine(r["medicine"]["name_dosage"], r["medicine"]["frequency"], r["medicine"]["intake_condition"])
            self.reminders.append(MedicationReminder(med, r["time"], r["status"]))
        
        self.saved_history = saved_user.get("history_data", {"chronic": [], "surgery": [], "allergy": []})
        self.saved_vitals = saved_user.get("vitals_data", {})
        self.saved_pregnancy = saved_user.get("pregnancy_data", {})
        
        self.is_logged_in = True; self.auth_frame.destroy(); self.setup_main_ui(); self.check_clock_loop()

    # --- ANA ARAYÜZ ---
    def setup_main_ui(self):
        header = tk.Frame(self.root, bg=self.lila_dark, height=90); header.pack(fill="x")
        tk.Button(header, text="🔒 GÜVENLİ ÇIKIŞ", command=self.logout_user, bg="#D32F2F", fg="white", font=("bold", 10), bd=0, padx=10, pady=5).pack(side="right", padx=(5, 20), pady=25)
        tk.Button(header, text="💾 KAYDET", command=self.manual_save, bg="white", fg=self.lila_dark, font=("bold", 10), bd=0, padx=10, pady=5).pack(side="right", padx=5, pady=25)
        
        # HİTAPLI BAŞLIK
        tk.Label(header, text=f"HOŞGELDİNİZ, {self.user.name} {self.user.title}", font=("Segoe UI", 20, "bold"), fg="white", bg=self.lila_dark).pack(pady=25)

        self.tabs = ttk.Notebook(self.root); self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        self.tab_med = tk.Frame(self.tabs, bg="#F3E5F5"); self.tab_profile = tk.Frame(self.tabs, bg="#F3E5F5"); self.tab_vitals = tk.Frame(self.tabs, bg="#F3E5F5"); self.tab_preg = tk.Frame(self.tabs, bg="#F3E5F5")
        
        self.tabs.add(self.tab_med, text=" 💊 İLAÇ & VİTAMİN "); self.tabs.add(self.tab_profile, text=" 🧬 SAĞLIK ÖZGEÇMİŞİ "); self.tabs.add(self.tab_vitals, text=" 🩸 TANSİYON & ŞEKER "); self.tabs.add(self.tab_preg, text=" 🤰 GEBE TAKİBİ ")
        self.build_med_tab(); self.build_profile_tab(); self.build_vitals_tab(); self.build_pregnancy_tab()

    def logout_user(self):
        if messagebox.askyesno("Çıkış", "Çıkmak istiyor musunuz? Veriler kaydedilecek."):
            self.save_to_database(); self.is_logged_in = False; self.current_email = None; self.user = None; self.show_auth_screen()

    def manual_save(self):
        self.save_to_database(); messagebox.showinfo("Başarılı", "Tüm veriler kaydedildi.")

    def build_med_tab(self):
        left = tk.Frame(self.tab_med, bg="white", padx=25, pady=20, highlightbackground=self.lila_main, highlightthickness=1); left.place(relx=0.02, rely=0.05, relwidth=0.45, relheight=0.9)
        tk.Label(left, text="Kategori:", bg="white", font=("bold", 10)).pack(anchor="w")
        self.type_select = ttk.Combobox(left, values=["İlaç", "Vitamin/Takviye"], state="readonly"); self.type_select.pack(fill="x", pady=5); self.type_select.set("İlaç"); self.type_select.bind("<<ComboboxSelected>>", self.update_sub_list)
        self.sel_med = self.create_combo(left, "Ad Seçin:", self.med_only_list)
        self.sel_freq = self.create_combo(left, "Sıklık:", ["Günde 1 Kez", "Günde 2 Kez (12s)", "Günde 3 Kez (8s)", "Günde 4 Kez (6s)"])
        self.sel_intake = self.create_combo(left, "Durum:", ["Aç Karnına", "Tok Karnına", "Farketmez"])
        t_f = tk.Frame(left, bg="white"); t_f.pack(fill="x", pady=5)
        self.sel_h = ttk.Combobox(t_f, values=[f"{i:02d}" for i in range(24)], width=5, state="readonly"); self.sel_h.pack(side="left"); self.sel_h.set("08")
        self.sel_m = ttk.Combobox(t_f, values=[f"{i:02d}" for i in range(60)], width=5, state="readonly"); self.sel_m.pack(side="left", padx=5); self.sel_m.set("00")
        tk.Button(left, text="HATIRLATICI OLUŞTUR", command=self.smart_plan, bg=self.lila_main, fg="white", font=("bold", 12), bd=0, pady=10).pack(fill="x", pady=20)
        right = tk.Frame(self.tab_med, bg="white", padx=15, pady=15, highlightbackground=self.lila_main, highlightthickness=1); right.place(relx=0.5, rely=0.05, relwidth=0.48, relheight=0.9)
        self.list_area = tk.Frame(right, bg="white"); self.list_area.pack(fill="both", expand=True); self.refresh_list()

    def update_sub_list(self, event):
        self.sel_med['values'] = self.vitamin_only_list if self.type_select.get() == "Vitamin/Takviye" else self.med_only_list
        self.sel_med.set("Seçiniz...")

    def build_profile_tab(self):
        canvas = tk.Canvas(self.tab_profile, bg="#F3E5F5", highlightthickness=0); sb = ttk.Scrollbar(self.tab_profile, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg="#F3E5F5"); sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))); canvas.create_window((0, 0), window=sf, anchor="nw", width=1200)
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        
        # Profil Alanı
        p_frame = tk.Frame(sf, bg="white", padx=20, pady=10); p_frame.pack(fill="x", pady=5, padx=20)
        tk.Label(p_frame, text="Kişisel Bilgiler", font=("bold", 12), bg="white", fg=self.lila_dark).pack(anchor="w")
        grid_f = tk.Frame(p_frame, bg="white"); grid_f.pack(fill="x", pady=5)
        
        tk.Label(grid_f, text="Yaş:", bg="white").grid(row=0, column=0); self.e_age = tk.Entry(grid_f, width=5); self.e_age.grid(row=0, column=1); self.e_age.insert(0, self.user.age)
        tk.Label(grid_f, text="Kilo:", bg="white").grid(row=0, column=2); self.e_weight = tk.Entry(grid_f, width=5); self.e_weight.grid(row=0, column=3); self.e_weight.insert(0, self.user.weight)
        tk.Label(grid_f, text="Boy:", bg="white").grid(row=0, column=4); self.e_height = tk.Entry(grid_f, width=5); self.e_height.grid(row=0, column=5); self.e_height.insert(0, self.user.height)
        tk.Label(grid_f, text="Kan:", bg="white").grid(row=0, column=6); self.e_blood = ttk.Combobox(grid_f, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"], width=5); self.e_blood.grid(row=0, column=7); self.e_blood.set(self.user.blood)
        tk.Label(grid_f, text="Cinsiyet:", bg="white").grid(row=0, column=8); self.e_gen = ttk.Combobox(grid_f, values=["Erkek", "Kadın"], width=7); self.e_gen.grid(row=0, column=9); self.e_gen.set(self.user.gender)
        tk.Button(p_frame, text="PROFİLİ GÜNCELLE", bg=self.lila_light, command=self.update_profile_data).pack(pady=5)

        # Hastalıklar - Listbox Gelişmiş Kayıt
        self.history_lbs = {} # Listbox referanslarını tutar
        
        list_defs = [
            ("Kronik Hastalıklar", self.chronic_list, "chronic"),
            ("Ameliyatlar", self.surgery_list, "surgery"),
            ("Alerjiler", self.allergy_list, "allergy")
        ]

        for title, data, key in list_defs:
            f = tk.Frame(sf, bg="white", padx=20, pady=10); f.pack(fill="x", pady=5, padx=20)
            tk.Label(f, text=title, font=("bold", 12), bg="white", fg=self.lila_dark).pack(anchor="w")
            lb = tk.Listbox(f, selectmode="multiple", height=6, selectbackground=self.lila_main)
            for d in data: lb.insert(tk.END, d)
            lb.pack(fill="x", pady=5)
            self.history_lbs[key] = lb
            
            # Kayıtlı verileri geri yükle (Seçili hale getir)
            saved_items = self.saved_history.get(key, [])
            for i, item in enumerate(data):
                if item in saved_items: lb.selection_set(i)

            tk.Button(f, text="LİSTEYİ KAYDET", bg=self.lila_light, command=self.manual_save).pack(anchor="e")

    def update_profile_data(self):
        self.user.age = self.e_age.get(); self.user.weight = self.e_weight.get(); self.user.height = self.e_height.get()
        self.user.blood = self.e_blood.get(); self.user.gender = self.e_gen.get()
        self.user.title = "BEY" if self.user.gender == "Erkek" else "HANIM"
        self.manual_save()

    def get_history_from_ui(self):
        history = {}
        for key, lb in self.history_lbs.items():
            history[key] = [lb.get(i) for i in lb.curselection()]
        return history

    def build_vitals_tab(self):
        f = tk.Frame(self.tab_vitals, bg="white", padx=20, pady=20); f.pack(fill="both", expand=True, padx=20, pady=20)
        days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        self.vital_vars = {} 
        tk.Label(f, text="🩸 HAFTALIK TANSİYON TAKİBİ", font=("bold", 12), fg="red", bg="white").pack()
        b_grid = tk.Frame(f, bg="white"); b_grid.pack(pady=10)
        for i, d in enumerate(days):
            b = tk.Frame(b_grid, bg="#FFF5F5", padx=8, pady=8, highlightthickness=1, highlightbackground="red"); b.grid(row=0, column=i, padx=5); tk.Label(b, text=d, bg="#FFF5F5").pack()
            cb_b = ttk.Combobox(b, values=[f"{x} B" for x in range(300, 30, -1)], width=7); cb_b.pack(); self.vital_vars[f"tansiyon_buyuk_{d}"] = cb_b
            if f"tansiyon_buyuk_{d}" in self.saved_vitals: cb_b.set(self.saved_vitals[f"tansiyon_buyuk_{d}"])
            cb_k = ttk.Combobox(b, values=[f"{x} K" for x in range(200, 20, -1)], width=7); cb_k.pack(); self.vital_vars[f"tansiyon_kucuk_{d}"] = cb_k
            if f"tansiyon_kucuk_{d}" in self.saved_vitals: cb_k.set(self.saved_vitals[f"tansiyon_kucuk_{d}"])
            
        tk.Label(f, text="🍬 HAFTALIK ŞEKER TAKİBİ", font=("bold", 12), fg="blue", bg="white").pack(pady=(20,0))
        s_grid = tk.Frame(f, bg="white"); s_grid.pack(pady=10)
        for i, d in enumerate(days):
            b = tk.Frame(s_grid, bg="#E3F2FD", padx=8, pady=8, highlightthickness=1, highlightbackground="blue"); b.grid(row=0, column=i, padx=5); tk.Label(b, text=d, bg="#E3F2FD").pack()
            cb_ac = ttk.Combobox(b, values=[f"{x} Aç" for x in range(600, 10, -5)], width=7); cb_ac.pack(); self.vital_vars[f"seker_ac_{d}"] = cb_ac
            if f"seker_ac_{d}" in self.saved_vitals: cb_ac.set(self.saved_vitals[f"seker_ac_{d}"])
            cb_tok = ttk.Combobox(b, values=[f"{x} Tok" for x in range(600, 10, -5)], width=7); cb_tok.pack(); self.vital_vars[f"seker_tok_{d}"] = cb_tok
            if f"seker_tok_{d}" in self.saved_vitals: cb_tok.set(self.saved_vitals[f"seker_tok_{d}"])
        tk.Button(f, text="DEĞERLERİ KAYDET", bg="#2196F3", fg="white", font=("bold", 12), command=self.manual_save).pack(pady=20)

    def get_vitals_ui_data(self):
        return {k: v.get() for k, v in self.vital_vars.items()}

    def build_pregnancy_tab(self):
        canvas = tk.Canvas(self.tab_preg, bg="white", highlightthickness=0); sb = ttk.Scrollbar(self.tab_preg, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg="white", padx=20, pady=20); sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))); canvas.create_window((0, 0), window=sf, anchor="nw", width=1300)
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        
        self.preg_vars = {} 
        g1 = tk.LabelFrame(sf, text=" 🤰 GEBELİK VE BEBEK BİLGİLERİ ", font=("bold", 12), bg="#FDF2F9", fg="#C2185B", padx=20, pady=15); g1.pack(fill="x", pady=10)
        row1 = tk.Frame(g1, bg="#FDF2F9"); row1.pack(fill="x", pady=5)
        
        def create_s_c(p, k, v, w=10): 
            c = ttk.Combobox(p, values=v, width=w); self.preg_vars[k]=c; 
            if k in self.saved_pregnancy: c.set(self.saved_pregnancy[k])
            return c
        def create_s_e(p, k, w=8): 
            e = tk.Entry(p, width=w); self.preg_vars[k]=e; 
            if k in self.saved_pregnancy: e.insert(0, self.saved_pregnancy[k])
            return e

        tk.Label(row1, text="Hafta:", bg="#FDF2F9").pack(side="left"); create_s_c(row1, "hafta", [f"{x}. Hafta" for x in range(1, 43)]).pack(side="left", padx=10)
        tk.Label(row1, text="Cinsiyet:", bg="#FDF2F9").pack(side="left", padx=10); create_s_c(row1, "cinsiyet", ["Erkek", "Kız", "Belirsiz"]).pack(side="left")
        row2 = tk.Frame(g1, bg="#FDF2F9"); row2.pack(fill="x", pady=5)
        tk.Label(row2, text="Tahmini Boy (cm):", bg="#FDF2F9").pack(side="left"); create_s_e(row2, "boy").pack(side="left", padx=5)
        tk.Label(row2, text="Tahmini Kilo (gr):", bg="#FDF2F9").pack(side="left", padx=15); create_s_e(row2, "kilo").pack(side="left")

        g2 = tk.LabelFrame(sf, text=" 🧬 OBSTETRİK ÖYKÜ ", font=("bold", 12), bg="white", fg=self.lila_dark, padx=20, pady=15); g2.pack(fill="x", pady=10)
        row3 = tk.Frame(g2, bg="white"); row3.pack(fill="x")
        for k, (l, v) in {"gravida": ("Gravida (Toplam Gebelik Sayısı):", 15), "parite": ("Parite(Doğum Sayısı):", 15), "abortus": ("Abortus(Düşük Sayısı):", 10), "yasayan": ("Yaşayan:", 15)}.items():
            tk.Label(row3, text=l, bg="white").pack(side="left", padx=5); c = ttk.Combobox(row3, values=[x for x in range(v+1)], width=4); c.pack(side="left", padx=10); self.preg_vars[k]=c
            if k in self.saved_pregnancy: c.set(self.saved_pregnancy[k])

        g3 = tk.LabelFrame(sf, text=" 💉 AŞI TAKİBİ VE TESTLER ", font=("bold", 12), bg="#F3E5F5", fg=self.lila_dark, padx=20, pady=15); g3.pack(fill="x", pady=10)
        for t in ["Tetanoz Aşısı", "Grip Aşısı", "Smear Testi", "HPV Taraması"]:
            row = tk.Frame(g3, bg="#F3E5F5"); row.pack(fill="x", pady=2); tk.Label(row, text=t, width=20, anchor="w", bg="#F3E5F5").pack(side="left")
            c = ttk.Combobox(row, values=["Yapıldı", "Yapılmadı", "Normal", "Pozitif", "Negatif"], width=12); c.pack(side="left", padx=10); k=t.replace(" ", "_"); self.preg_vars[k]=c
            if k in self.saved_pregnancy: c.set(self.saved_pregnancy[k])
        tk.Button(sf, text="GEBELİK BİLGİLERİNİ KAYDET", bg="#C2185B", fg="white", font=("bold", 12), command=self.manual_save).pack(pady=20)

    def get_pregnancy_ui_data(self): return {k: v.get() for k, v in self.preg_vars.items()}
    def create_combo(self, parent, label, values): tk.Label(parent, text=label, bg="white", font=("bold")).pack(anchor="w"); c = ttk.Combobox(parent, values=values, state="readonly"); c.pack(fill="x", pady=5); c.set("Seçiniz..."); return c
    
    def smart_plan(self):
        name, freq, h, m = self.sel_med.get(), self.sel_freq.get(), self.sel_h.get(), self.sel_m.get()
        if "Seçiniz" in name: return
        start = datetime.datetime.now().replace(hour=int(h), minute=int(m))
        count, step = 1, 0
        if "2 Kez" in freq: count, step = 2, 12
        elif "3 Kez" in freq: count, step = 3, 8
        elif "4 Kez" in freq: count, step = 4, 6
        for i in range(count):
            t = (start + datetime.timedelta(hours=i*step)).strftime("%H:%M")
            self.reminders.append(MedicationReminder(Medicine(name, freq, ""), t))
        self.manual_save(); self.refresh_list()

    def refresh_list(self):
        for w in self.list_area.winfo_children(): w.destroy()
        for r in sorted(self.reminders, key=lambda x: x.time):
            row = tk.Frame(self.list_area, bg="#F8FAFC", pady=5, highlightthickness=1, highlightbackground="#E2E8F0"); row.pack(fill="x", pady=2)
            lbl = f"⏰ {r.time} | {r.medicine.name_dosage.upper()}"; c = "#10B981" if r.status == "İçildi" else ("#EF4444" if r.status == "İçilmedi" else "#1E293B")
            tk.Label(row, text=lbl, font=("bold", 11), bg="#F8FAFC", fg=c).pack(side="left", padx=10)
            tk.Button(row, text="İÇİLDİ", bg="#10B981", fg="white", command=lambda x=r: self.set_status(x, "İçildi")).pack(side="right", padx=5)
            tk.Button(row, text="İÇİLMEDİ", bg="#EF4444", fg="white", command=lambda x=r: self.set_status(x, "İçilmedi")).pack(side="right")

    def set_status(self, rem, stat): rem.status = stat; self.manual_save(); self.refresh_list()
    def check_clock_loop(self):
        if not self.is_logged_in: return
        now = datetime.datetime.now().strftime("%H:%M")
        for r in self.reminders:
            if r.time == now and r.status == "Bekliyor":
                winsound.Beep(1000, 1000); win = tk.Toplevel(self.root); win.geometry("500x350"); win.configure(bg=self.lila_dark); win.attributes("-topmost", True)
                tk.Label(win, text=f"🔔 {r.medicine.name_dosage.upper()} VAKTİ", font=("bold", 20), bg=self.lila_dark, fg="white").pack(pady=40)
                tk.Label(win, text="İlacınızı içmeyi unutmayınız.", font=("Arial", 16), bg=self.lila_dark, fg="white").pack(); tk.Button(win, text="TAMAM", command=win.destroy, bg="white", fg=self.lila_dark).pack(pady=30)
        self.root.after(30000, self.check_clock_loop)

if __name__ == "__main__":
    root = tk.Tk(); app = DigitalMedicineAssistant(root); root.mainloop()