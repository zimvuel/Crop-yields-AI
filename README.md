# AgroTime AI 🌾

AgroTime AI adalah sistem konsultan pertanian cerdas berbasis web yang mengintegrasikan prediksi hasil panen dengan antarmuka chatbot.
Panduan ini akan membantu menjalankan aplikasi secara lokal.

## 📋 Prasyarat Sistem

* **Python** (Versi 3.8 hingga 3.11 disarankan)
* **Node.js** (Versi 18+ disarankan untuk React 19)
* **npm** (atau Node.js)

---

## 🚀 Langkah 1: Menjalankan Backend

1.  Buka terminal/command prompt.
2.  Masuk ke folder `backend`:
    ```bash
    cd backend
    ```
3.  Instal dependensi yang diperlukan (sesuai `requirements.txt`):
    ```bash
    pip install -r requirements.txt
    ```

4.  Jalankan server:
    ```bash
    python app.py
    ```

    > **Indikator Sukses:** Terminal akan menampilkan pesan *"SYSTEM READY"* dan *"Listening on http://0.0.0.0:5000"*. Biarkan terminal ini tetap terbuka.

---

## 💻 Langkah 2: Menjalankan Frontend

1.  Buka terminal **baru** (jangan tutup terminal backend).
2.  Masuk ke folder `frontend`:
    ```bash
    cd frontend
    ```

3.  Instal dependensi React dan Tailwind (sesuai `package.json`):
    ```bash
    npm install
    ```

4.  Jalankan mode pengembangan:
    ```bash
    npm run dev
    ```

5.  Terminal akan menampilkan alamat lokal:
    ```
    http://localhost:5173
    ```
    Buka alamat tersebut di browser (Chrome/Edge/Firefox).
