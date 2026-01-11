# AgroTime AI 🌾

AgroTime AI adalah sistem konsultan pertanian cerdas berbasis web yang mengintegrasikan prediksi hasil panen (menggunakan XGBoost) dengan antarmuka chat interaktif (menggunakan React & LLM).

Panduan ini akan membantu Anda menjalankan aplikasi secara lokal di komputer Anda.

## 📋 Prasyarat Sistem

Sebelum memulai, pastikan komputer Anda telah terinstal:

* **Python** (Versi 3.8 hingga 3.11 disarankan)
* **Node.js** (Versi 18+ disarankan untuk React 19)
* **npm** (Biasanya sudah terinstal otomatis bersama Node.js)

---

## 🚀 Langkah 1: Menjalankan Backend (Server)

Backend bertugas menangani logika prediksi AI, koneksi database, dan komunikasi dengan API DeepSeek.

1.  Buka terminal/command prompt.
2.  Masuk ke folder `backend`:
    ```bash
    cd backend
    ```

3.  (Opsional namun Disarankan) Buat dan aktifkan *Virtual Environment* agar library tidak tercampur:
    * **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    * **Mac/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

4.  Instal dependensi yang diperlukan (sesuai `requirements.txt`):
    ```bash
    pip install -r requirements.txt
    ```

5.  Jalankan server:
    ```bash
    python app.py
    ```

    > **Indikator Sukses:** Terminal akan menampilkan pesan *"SYSTEM READY"* dan *"Listening on http://0.0.0.0:5000"*. Biarkan terminal ini tetap terbuka.

---

## 💻 Langkah 2: Menjalankan Frontend (User Interface)

Frontend adalah tampilan website tempat pengguna berinteraksi dengan chatbot.

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

5.  Terminal akan menampilkan alamat lokal, biasanya:
    ```
    http://localhost:5173
    ```
    Buka alamat tersebut di browser Anda (Chrome/Edge/Firefox).
