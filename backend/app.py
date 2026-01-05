from flask import Flask, request, jsonify
from flask_cors import CORS
from prediction_engine import CropPredictor
import requests
import datetime
import difflib 
import re
from waitress import serve 

app = Flask(__name__)
CORS(app)

print("Initializing AI Engine...")
engine = CropPredictor()

# --- 1. GLOBAL MEMORY ---
SESSION_MEMORY = {"crop": None, "province": None}

# --- 2. CONFIGURATION ---
STOPWORDS = {
    'kapan', 'waktu', 'terbaik', 'bagus', 'menanam', 'tanam', 'di', 'adalah', 'yang', 'untuk', 
    'prediksi', 'hasil', 'panen', 'berapa', 'bisa', 'gak', 'tidak', 'ya', 'tolong', 'jelaskan', 
    'gimana', 'hari', 'bulan', 'tahun', 'tanggal', 'saat', 'ini', 'itu', 'mungkin', 'saya',
    'mau', 'ingin', 'tanya', 'optimal', 'paling', 'cocok', 'daerah', 'apakah', 'kalau', 'jika', 
    'misal', 'sebaiknya', 'rekomendasi', 'tterbaik', 'kpan', 'dimana', 'lokasi', 'tempat', 'kota', 'provinsi'
}

CROP_ALIASES = {}
for crop_key in engine.duration_lookup.keys():
    clean_key = crop_key.lower().strip()
    CROP_ALIASES[clean_key] = crop_key 
    if '/' in clean_key:
        for part in clean_key.split('/'):
            CROP_ALIASES[part.strip()] = crop_key

CITY_TO_PROVINCE = {
    # SUMATERA
    'banda aceh': 'aceh', 'sabang': 'aceh', 'lhokseumawe': 'aceh', 'langsa': 'aceh', 'subulussalam': 'aceh', 
    'aceh besar': 'aceh', 'pidie': 'aceh', 'bireuen': 'aceh', 'aceh utara': 'aceh', 'aceh timur': 'aceh', 
    'aceh barat': 'aceh', 'aceh tengah': 'aceh', 'aceh selatan': 'aceh', 'aceh tenggara': 'aceh',
    'medan': 'sumatera utara', 'binjai': 'sumatera utara', 'pematangsiantar': 'sumatera utara', 
    'sibolga': 'sumatera utara', 'tanjungbalai': 'sumatera utara', 'tebingtinggi': 'sumatera utara', 
    'padangsidimpuan': 'sumatera utara', 'gunungsitoli': 'sumatera utara', 'deli serdang': 'sumatera utara', 
    'karo': 'sumatera utara', 'langkat': 'sumatera utara', 'asahan': 'sumatera utara', 'simalungun': 'sumatera utara',
    'tapanuli': 'sumatera utara', 'labuhanbatu': 'sumatera utara', 'nias': 'sumatera utara', 'samosir': 'sumatera utara',
    'padang': 'sumatera barat', 'bukittinggi': 'sumatera barat', 'payakumbuh': 'sumatera barat', 
    'pariaman': 'sumatera barat', 'solok': 'sumatera barat', 'sawahlunto': 'sumatera barat', 
    'padang panjang': 'sumatera barat', 'agam': 'sumatera barat', 'tanah datar': 'sumatera barat', 
    'limapuluh kota': 'sumatera barat', 'pasaman': 'sumatera barat', 'mentawai': 'sumatera barat',
    'pekanbaru': 'riau', 'dumai': 'riau', 'kampar': 'riau', 'bengkalis': 'riau', 'siak': 'riau', 
    'indragiri': 'riau', 'rokan': 'riau', 'pelalawan': 'riau', 'kuantan singingi': 'riau',
    'jambi': 'jambi', 'sungai penuh': 'jambi', 'batanghari': 'jambi', 'bungo': 'jambi', 'kerinci': 'jambi', 
    'merangin': 'jambi', 'muaro jambi': 'jambi', 'sarolangun': 'jambi', 'tanjung jabung': 'jambi',
    'palembang': 'sumatera selatan', 'prabumulih': 'sumatera selatan', 'pagar alam': 'sumatera selatan', 
    'lubuklinggau': 'sumatera selatan', 'banyuasin': 'sumatera selatan', 'empat lawang': 'sumatera selatan', 
    'lahat': 'sumatera selatan', 'muara enim': 'sumatera selatan', 'musi': 'sumatera selatan', 
    'ogan': 'sumatera selatan', 'penukal': 'sumatera selatan',
    'bengkulu': 'bengkulu', 'rejang lebong': 'bengkulu', 'mukomuko': 'bengkulu', 'seluma': 'bengkulu', 'kaur': 'bengkulu',
    'bandar lampung': 'lampung', 'metro': 'lampung', 'lampung barat': 'lampung', 'lampung selatan': 'lampung', 
    'lampung tengah': 'lampung', 'lampung timur': 'lampung', 'lampung utara': 'lampung', 'mesuji': 'lampung', 
    'pesawaran': 'lampung', 'pringsewu': 'lampung', 'tanggamus': 'lampung', 'tulang bawang': 'lampung', 'way kanan': 'lampung',
    'pangkalpinang': 'kepulauan bangka belitung', 'bangka': 'kepulauan bangka belitung', 'belitung': 'kepulauan bangka belitung',
    'tanjungpinang': 'kepulauan riau', 'batam': 'kepulauan riau', 'bintan': 'kepulauan riau', 
    'karimun': 'kepulauan riau', 'natuna': 'kepulauan riau', 'lingga': 'kepulauan riau', 'anambas': 'kepulauan riau',

    # JAWA
    'jakarta': 'dki jakarta', 'jakarta pusat': 'dki jakarta', 'jakarta utara': 'dki jakarta', 
    'jakarta barat': 'dki jakarta', 'jakarta selatan': 'dki jakarta', 'jakarta timur': 'dki jakarta', 
    'kepulauan seribu': 'dki jakarta',
    'bandung': 'jawa barat', 'bekasi': 'jawa barat', 'bogor': 'jawa barat', 'depok': 'jawa barat', 
    'cimahi': 'jawa barat', 'tasikmalaya': 'jawa barat', 'banjar': 'jawa barat', 'sukabumi': 'jawa barat', 
    'cirebon': 'jawa barat', 'cianjur': 'jawa barat', 'garut': 'jawa barat', 'indramayu': 'jawa barat', 
    'karawang': 'jawa barat', 'kuningan': 'jawa barat', 'majalengka': 'jawa barat', 'pangandaran': 'jawa barat', 
    'purwakarta': 'jawa barat', 'subang': 'jawa barat', 'sumedang': 'jawa barat', 'ciamis': 'jawa barat',
    'semarang': 'jawa tengah', 'surakarta': 'jawa tengah', 'solo': 'jawa tengah', 'salatiga': 'jawa tengah', 
    'magelang': 'jawa tengah', 'pekalongan': 'jawa tengah', 'tegal': 'jawa tengah', 'banjarnegara': 'jawa tengah', 
    'banyumas': 'jawa tengah', 'purwokerto': 'jawa tengah', 'batang': 'jawa tengah', 'blora': 'jawa tengah', 
    'boyolali': 'jawa tengah', 'brebes': 'jawa tengah', 'cilacap': 'jawa tengah', 'demak': 'jawa tengah', 
    'grobogan': 'jawa tengah', 'jepara': 'jawa tengah', 'karanganyar': 'jawa tengah', 'kebumen': 'jawa tengah', 
    'kendal': 'jawa tengah', 'klaten': 'jawa tengah', 'kudus': 'jawa tengah', 'pati': 'jawa tengah', 
    'pemalang': 'jawa tengah', 'purbalingga': 'jawa tengah', 'purworejo': 'jawa tengah', 'rembang': 'jawa tengah', 
    'sragen': 'jawa tengah', 'sukoharjo': 'jawa tengah', 'temanggung': 'jawa tengah', 'wonogiri': 'jawa tengah', 
    'wonosobo': 'jawa tengah',
    'yogyakarta': 'di yogyakarta', 'jogja': 'di yogyakarta', 'bantul': 'di yogyakarta', 'sleman': 'di yogyakarta', 
    'kulon progo': 'di yogyakarta', 'gunungkidul': 'di yogyakarta', 'wonosari': 'di yogyakarta',
    'surabaya': 'jawa timur', 'malang': 'jawa timur', 'madiun': 'jawa timur', 'kediri': 'jawa timur', 
    'mojokerto': 'jawa timur', 'blitar': 'jawa timur', 'pasuruan': 'jawa timur', 'probolinggo': 'jawa timur', 
    'batu': 'jawa timur', 'bangkalan': 'jawa timur', 'banyuwangi': 'jawa timur', 'bojonegoro': 'jawa timur', 
    'bondowoso': 'jawa timur', 'gresik': 'jawa timur', 'jember': 'jawa timur', 'jombang': 'jawa timur', 
    'lamongan': 'jawa timur', 'lumajang': 'jawa timur', 'magetan': 'jawa timur', 'nganjuk': 'jawa timur', 
    'ngawi': 'jawa timur', 'pacitan': 'jawa timur', 'pamekasan': 'jawa timur', 'ponorogo': 'jawa timur', 
    'sampang': 'jawa timur', 'sidoarjo': 'jawa timur', 'situbondo': 'jawa timur', 'sumenep': 'jawa timur', 
    'trenggalek': 'jawa timur', 'tuban': 'jawa timur', 'tulungagung': 'jawa timur',
    'serang': 'banten', 'cilegon': 'banten', 'tangerang': 'banten', 'tangerang selatan': 'banten', 
    'lebak': 'banten', 'pandeglang': 'banten',

    # BALI & NUSA TENGGARA
    'denpasar': 'bali', 'badung': 'bali', 'bangli': 'bali', 'buleleng': 'bali', 'gianyar': 'bali', 
    'jembrana': 'bali', 'karangasem': 'bali', 'klungkung': 'bali', 'tabanan': 'bali', 'ubud': 'bali', 
    'canggu': 'bali', 'kuta': 'bali',
    'mataram': 'nusa tenggara barat', 'bima': 'nusa tenggara barat', 'dompu': 'nusa tenggara barat', 
    'lombok': 'nusa tenggara barat', 'lombok barat': 'nusa tenggara barat', 'lombok tengah': 'nusa tenggara barat', 
    'lombok timur': 'nusa tenggara barat', 'lombok utara': 'nusa tenggara barat', 'sumbawa': 'nusa tenggara barat',
    'kupang': 'nusa tenggara timur', 'alor': 'nusa tenggara timur', 'belu': 'nusa tenggara timur', 
    'ende': 'nusa tenggara timur', 'flores': 'nusa tenggara timur', 'manggarai': 'nusa tenggara timur', 
    'ngada': 'nusa tenggara timur', 'rote': 'nusa tenggara timur', 'sikka': 'nusa tenggara timur', 
    'sumba': 'nusa tenggara timur', 'timor tengah': 'nusa tenggara timur',

    # KALIMANTAN
    'pontianak': 'kalimantan barat', 'singkawang': 'kalimantan barat', 'sambas': 'kalimantan barat', 
    'bengkayang': 'kalimantan barat', 'ketapang': 'kalimantan barat', 'sintang': 'kalimantan barat', 
    'kapuas hulu': 'kalimantan barat', 'kubu raya': 'kalimantan barat',
    'palangkaraya': 'kalimantan tengah', 'barito': 'kalimantan tengah', 'kapuas': 'kalimantan tengah', 
    'kotawaringin': 'kalimantan tengah', 'seruyan': 'kalimantan tengah',
    'banjarmasin': 'kalimantan selatan', 'banjarbaru': 'kalimantan selatan', 'banjar': 'kalimantan selatan', 
    'barito kuala': 'kalimantan selatan', 'tanah bumbu': 'kalimantan selatan', 'tanah laut': 'kalimantan selatan', 
    'kotabaru': 'kalimantan selatan', 'tabalong': 'kalimantan selatan',
    'samarinda': 'kalimantan timur', 'balikpapan': 'kalimantan timur', 'bontang': 'kalimantan timur', 
    'kutai': 'kalimantan timur', 'berau': 'kalimantan timur', 'paser': 'kalimantan timur', 
    'mahakam ulu': 'kalimantan timur',
    'tarakan': 'kalimantan utara', 'bulungan': 'kalimantan utara', 'malinau': 'kalimantan utara', 
    'nunukan': 'kalimantan utara', 'tana tidung': 'kalimantan utara',

    # SULAWESI
    'manado': 'sulawesi utara', 'bitung': 'sulawesi utara', 'tomohon': 'sulawesi utara', 
    'kotamobagu': 'sulawesi utara', 'minahasa': 'sulawesi utara', 'bolaang mongondow': 'sulawesi utara', 
    'sangihe': 'sulawesi utara',
    'gorontalo': 'gorontalo', 'boalemo': 'gorontalo', 'bone bolango': 'gorontalo', 'pohuwato': 'gorontalo',
    'palu': 'sulawesi tengah', 'donggala': 'sulawesi tengah', 'poso': 'sulawesi tengah', 'toli-toli': 'sulawesi tengah', 
    'banggai': 'sulawesi tengah', 'morowali': 'sulawesi tengah', 'parigi moutong': 'sulawesi tengah',
    'mamuju': 'sulawesi barat', 'majene': 'sulawesi barat', 'mamasa': 'sulawesi barat', 'polewali mandar': 'sulawesi barat',
    'makassar': 'sulawesi selatan', 'parepare': 'sulawesi selatan', 'palopo': 'sulawesi selatan', 
    'bantaeng': 'sulawesi selatan', 'barru': 'sulawesi selatan', 'bone': 'sulawesi selatan', 
    'bulukumba': 'sulawesi selatan', 'enrekang': 'sulawesi selatan', 'gowa': 'sulawesi selatan', 
    'jeneponto': 'sulawesi selatan', 'luwu': 'sulawesi selatan', 'maros': 'sulawesi selatan', 
    'pinrang': 'sulawesi selatan', 'sinjai': 'sulawesi selatan', 'soppeng': 'sulawesi selatan', 
    'takalar': 'sulawesi selatan', 'tana toraja': 'sulawesi selatan', 'wajo': 'sulawesi selatan',
    'kendari': 'sulawesi tenggara', 'bau-bau': 'sulawesi tenggara', 'bombana': 'sulawesi tenggara', 
    'buton': 'sulawesi tenggara', 'kolaka': 'sulawesi tenggara', 'konawe': 'sulawesi tenggara', 
    'muna': 'sulawesi tenggara', 'wakatobi': 'sulawesi tenggara',

    # MALUKU & PAPUA
    'ambon': 'maluku', 'tual': 'maluku', 'buru': 'maluku', 'aru': 'maluku', 'seram': 'maluku', 'maluku tengah': 'maluku',
    'ternate': 'maluku utara', 'tidore': 'maluku utara', 'halmahera': 'maluku utara', 'sula': 'maluku utara',
    'jayapura': 'papua', 'keerom': 'papua', 'sarmi': 'papua', 'biak': 'papua', 'yapen': 'papua',
    'manokwari': 'papua barat', 'fakfak': 'papua barat', 'kaimana': 'papua barat', 'teluk bintuni': 'papua barat',
    'sorong': 'papua barat daya', 'raja ampat': 'papua barat daya',
    'merauke': 'papua selatan', 'boven digoel': 'papua selatan', 'mappi': 'papua selatan', 'asmat': 'papua selatan',
    'nabire': 'papua tengah', 'mimika': 'papua tengah', 'timika': 'papua tengah', 'paniai': 'papua tengah', 
    'puncak jaya': 'papua tengah', 'dogiyai': 'papua tengah', 'intan jaya': 'papua tengah',
    'wamena': 'papua pegunungan', 'jayawijaya': 'papua pegunungan', 'yahukimo': 'papua pegunungan', 
    'tolikara': 'papua pegunungan'
}


DEEPSEEK_API_KEY = "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"
DEEPSEEK_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "deepseek/deepseek-r1-0528:free"

def get_deepseek_advice(user_query, context_text, missing_info=False):
    if not DEEPSEEK_API_KEY: return "AI Advice Unavailable."
    if missing_info:
        prompt = f"""User: "{user_query}"\nSistem: "{context_text}"\nTugas: Minta user melengkapi data TANAMAN atau LOKASI."""
    else:
        prompt = f"""
        Anda ahli pertanian. User bertanya: "{user_query}"
        Konteks: {context_text}
        Jawab to the point. Gunakan poin (-). Sisipkan  jika relevan.
        """
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
        data = response.json()
        if 'choices' in data: return data['choices'][0]['message']['content']
    except: return "Maaf, AI sedang sibuk."

def extract_entities(text):
    if not text: return None, None
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    found_crop, found_prov = None, None
    
    # 1. Location Detection
    for city, prov in CITY_TO_PROVINCE.items():
        if city in clean_text: 
            found_prov = prov
            print(f"DEBUG: Mapped City '{city}' to Province '{prov}'") # <-- DEBUG RESTORED
            break
    if not found_prov:
        for prov in engine.soil_lookup.keys():
            if prov.lower() in clean_text: 
                found_prov = prov
                break

    # 2. Crop Detection
    all_aliases = sorted(CROP_ALIASES.keys(), key=len, reverse=True)
    for alias in all_aliases:
        if re.search(r'\b' + re.escape(alias) + r'\b', clean_text): 
            found_crop = CROP_ALIASES[alias]
            break
            
    if not found_crop:
        words = clean_text.split()
        for word in words:
            if len(word) < 3 or word in STOPWORDS: continue 
            matches = difflib.get_close_matches(word, all_aliases, n=1, cutoff=0.8)
            if matches: 
                found_crop = CROP_ALIASES[matches[0]]
                print(f"DEBUG: Fuzzy Matched Typo '{word}' -> '{matches[0]}'") # <-- DEBUG RESTORED
                break
    return found_crop, found_prov

def parse_date(query):
    today = datetime.date.today()
    
    # 0. Handle Relative Dates (Besok/Lusa/Minggu Depan)
    if 'besok' in query:
        d = today + datetime.timedelta(days=1)
        print(f"DEBUG: Relative Date 'Besok' -> {d}")
        return d.isoformat()
    if 'lusa' in query:
        d = today + datetime.timedelta(days=2)
        print(f"DEBUG: Relative Date 'Lusa' -> {d}")
        return d.isoformat()
    if 'minggu depan' in query:
        d = today + datetime.timedelta(weeks=1)
        return d.isoformat()

    # 1. Look for explicit Year
    year_match = re.search(r'\b(20\d{2})\b', query)
    year = int(year_match.group(1)) if year_match else None
    
    # 2. Look for Day
    day = 1
    numbers = re.findall(r'\b(\d{1,2})\b', query)
    # Filter numbers that are likely days (1-31) and not the year part
    valid_days = [int(n) for n in numbers if int(n) <= 31 and str(n) not in (str(year) if year else "")]
    if valid_days: day = valid_days[0]

    # 3. Look for Month
    months = {'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12, 'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
    
    found_month = None
    for m_name, m_num in months.items():
        if m_name in query.lower():
            found_month = m_num
            break
            
    if found_month:
        target_year = year if year else today.year
        # If no year specified and month is in past, assume next year
        if not year and found_month < today.month:
            target_year += 1
        return datetime.date(target_year, found_month, day).isoformat()
            
    return today.isoformat()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    query = data.get('query', '').lower()
    
    # Reset Memory
    if any(w in query for w in ['reset', 'ulang', 'hapus']):
        SESSION_MEMORY['crop'], SESSION_MEMORY['province'] = None, None
        return jsonify({"result_text": "Reset", "ai_message": "Oke, memori direset."})

    # Extract Entities
    new_crop, new_prov = extract_entities(query)
    if new_crop: SESSION_MEMORY['crop'] = new_crop
    if new_prov: SESSION_MEMORY['province'] = new_prov
    
    final_crop = SESSION_MEMORY['crop']
    final_prov = SESSION_MEMORY['province']
    
    print(f"DEBUG: Context -> Crop: {final_crop}, Prov: {final_prov}") # <-- DEBUG RESTORED

    # General Knowledge Check
    if any(w in query for w in ['bagaimana', 'cara', 'tips']) and not final_prov:
        if not final_crop: return jsonify({"result_text": "Butuh Info", "ai_message": get_deepseek_advice(query, "No Crop Detected", True)})
        return jsonify({"result_text": "Info Umum", "ai_message": get_deepseek_advice(query, f"Tentang {final_crop}")})

    # Missing Info Check
    if not final_crop or not final_prov:
        missing = []
        if not final_crop: missing.append("Tanaman")
        if not final_prov: missing.append("Lokasi")
        return jsonify({"result_text": "Butuh Info", "ai_message": get_deepseek_advice(query, f"Missing: {missing}. Have: Crop={final_crop}, Loc={final_prov}", True)})

    # --- MAIN LOGIC ---
    is_optimization = any(w in query for w in ['kapan', 'terbaik', 'optimal'])
    
    if is_optimization:
        best_date, best_yield = engine.find_best_planting_time(final_crop, final_prov)
        avg = engine.get_baseline_yield(final_crop, final_prov)
        diff = ((best_yield - avg)/avg)*100
        result_text = f"REKOMENDASI MODEL (365 Hari):\nTanaman: {final_crop}\nLokasi: {final_prov.title()}\nTanggal Tanam Terbaik: {best_date}\nEstimasi: {best_yield:.2f} Ton/Ha (+{diff:.1f}%)."
    else:
        # 1. Parse Date (Includes Besok/Lusa logic)
        planting_date_str = parse_date(query)
        planting_date = datetime.date.fromisoformat(planting_date_str)
        today = datetime.date.today()
        
        print(f"DEBUG: Prediction Date -> {planting_date_str}") # <-- DEBUG RESTORED

        # 2. Predict Yield
        pred_yield = engine.predict_yield(final_crop, final_prov, planting_date_str)
        
        # 3. Calculate Status
        duration = engine.duration_lookup.get(final_crop, 90)
        harvest_date = planting_date + datetime.timedelta(days=duration)
        
        if planting_date < today:
            days_elapsed = (today - planting_date).days
            if days_elapsed < duration:
                progress = (days_elapsed / duration) * 100
                status_msg = f"🌱 **Status: Sedang Tumbuh** (Hari ke-{days_elapsed}).\n⏳ Progress: {progress:.1f}%. Panen sekitar {harvest_date}."
            else:
                status_msg = f"🌾 **Status: Siap Panen / Sudah Lewat**.\nSeharusnya panen sekitar {harvest_date}."
        else:
            status_msg = f"🗓️ **Perencanaan**: Jika tanam {planting_date_str}, panen sekitar {harvest_date}."

        result_text = (
            f"ANALISIS SPESIFIK:\n"
            f"Tanaman: {final_crop}\n"
            f"Lokasi: {final_prov.title()}\n"
            f"Tanggal Tanam: {planting_date_str}\n"
            f"Estimasi Hasil: {pred_yield:.2f} Ton/Ha\n\n"
            f"{status_msg}"
        )

    ai_response = get_deepseek_advice(query, result_text)
    return jsonify({"result_text": result_text, "ai_message": ai_response})

if __name__ == '__main__':
    print("-------------------------------------------------------")
    print(" SYSTEM READY: Debug Logs Restored ")
    print(" Listening on http://0.0.0.0:5000")
    print("-------------------------------------------------------")
    serve(app, host='0.0.0.0', port=5000, threads=6)