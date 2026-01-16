# 🏥 Digital Medicine Assistant (DMA)

**Digital Medicine Assistant**, Python ve Tkinter kütüphaneleri kullanılarak geliştirilmiş, kullanıcıların kişisel sağlık verilerini takip etmelerini sağlayan kapsamlı bir masaüstü uygulamasıdır. Kullanıcı dostu arayüzü ile ilaç takibinden gebelik sürecine kadar birçok sağlık verisini kayıt altına alır ve yönetir.

## 🌟 Özellikler

Uygulama 4 ana modülden oluşmaktadır:

* **💊 İlaç & Vitamin Takibi:**
    * İlaç ve vitaminleri kaydetme.
    * Kullanım sıklığına göre (Günde 1-4 kez) otomatik saat planlama.
    * **Sesli ve Görsel Bildirim:** İlaç saati geldiğinde `winsound` ile sesli uyarı ve pop-up ekranı.
    * İçildi/İçilmedi durum takibi ve renkli listeleme.

* **🧬 Sağlık Özgeçmişi:**
    * Kişisel profil (Boy, Kilo, Kan Grubu vb.) yönetimi.
    * Kronik hastalıklar, geçirilmiş ameliyatlar ve alerjilerin detaylı seçimi ve kaydı.

* **🩸 Tansiyon & Şeker Takibi:**
    * Haftalık bazda (Pazartesi-Pazar) tansiyon (Büyük/Küçük) verilerinin takibi.
    * Açlık ve tokluk kan şekeri değerlerinin gün gün kaydedilmesi.

* **🤰 Gebe Takibi:**
    * Gebelik haftası, bebek cinsiyeti, tahmini boy/kilo takibi.
    * Obstetrik öykü (Gravida, Parite vb.) kaydı.
    * Aşı takvimi ve test sonuçlarının (Tetanoz, Şeker Yüklemesi vb.) izlenmesi.

## 🛠️ Teknik Detaylar

* **Dil:** Python 3.x
* **Arayüz (GUI):** Tkinter (ttk temaları ile modernize edilmiştir)
* **Veritabanı:** JSON (Veriler `med_data.json` dosyasında yerel olarak saklanır, kurulum gerektirmez).
* **Diğer Kütüphaneler:** `datetime`, `winsound` (Windows uyarı sesleri için), `os`.

## 🚀 Kurulum ve Çalıştırma

Proje standart Python kütüphanelerini kullanır, harici bir yükleme gerektirmez (Windows işletim sistemi önerilir).

1. Projeyi bilgisayarınıza indirin veya klonlayın:
   ```bash
   git clone [https://github.com/KULLANICI_ADIN/digital-medicine-assistant.git](https://github.com/KULLANICI_ADIN/digital-medicine-assistant.git)
