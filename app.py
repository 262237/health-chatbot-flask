from flask import Flask, request, jsonify
from typing import Dict, List, Optional, Tuple
from datetime import datetime

app = Flask(__name__)

LANGS = ["en", "hi", "te", "kn", "ta"]

def guess_lang(text: str) -> str:
    if text is None:
        return "en"
    t = text.strip().lower()
    if len(t) == 0:
        return "en"
    hi_hints = ["namaste", "नमस्ते", "खांसी", "बुखार", "टीका", "टीकाकरण", "स्वास्थ्य"]
    te_hints = ["నమస్తే", "జ్వరం", "దగ్గు", "టీకా", "ఆరోగ్యం"]
    kn_hints = ["ನಮಸ್ಕಾರ", "ಜ್ವರ", "ಕೆಮ್ಮು", "ಲಸಿಕೆ", "ಆರೋಗ್ಯ"]
    ta_hints = ["வணக்கம்", "காய்ச்சல்", "இருமல்", "தடுப்பூசி", "ஆரோக்கியம்"]
    if any(ch in t for ch in "अआइईउऊएऐओऔकखगघचछजझटठडढतथदधनपफबभमयरलवशषसहािंीुूेैोौंः"):
        return "hi"
    if any(ch in t for ch in "అఆఇఈఉఊఎఏఐఒఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహాిీుూెేైొోౌంః"):
        return "te"
    if any(ch in t for ch in "ಅಆಇಈಉಊಎಏಐಒಓಔಕಖಗಘಙಚಛಜಝಞಟಠಡಢಣತಥದಧನಪಫಬಭಮಯರಲವಶಷಸಹಾಿೀುೂೃೆೇೈೊೋೌಂಃ"):
        return "kn"
    if any(ch in t for ch in "அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறஸஷஹாிீுூெேைொோௌம்ஂஃ"):
        return "ta"
    if any(w in t for w in hi_hints):
        return "hi"
    if any(w in t for w in te_hints):
        return "te"
    if any(w in t for w in kn_hints):
        return "kn"
    if any(w in t for w in ta_hints):
        return "ta"
    return "en"

class Intent(str):
    pass

INTENT_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "en": {
        "greet": ["hi", "hello", "hey", "namaste"],
        "preventive": ["prevention", "prevent", "wash", "mask", "avoid"],
        "symptoms": ["symptom", "fever", "cough", "cold", "headache"],
        "vaccine": ["vaccine", "vaccination", "schedule", "dose", "immunization"],
        "outbreak": ["outbreak", "alert", "cases", "disease spread"],
        "help": ["help", "menu"],
    },
    "hi": {
        "greet": ["नमस्ते", "नमस्कार", "हैलो"],
        "preventive": ["रोकथाम", "सावधानी", "मास्क", "हाथ", "धो"],
        "symptoms": ["लक्षण", "बुखार", "खांसी", "जुकाम", "सरदर्द"],
        "vaccine": ["टीका", "टीकाकरण", "खुराक", "शेड्यूल"],
        "outbreak": ["प्रकोप", "अलर्ट", "मामले", "फैल"],
        "help": ["मदद", "विकल्प"],
    },
    "te": {
        "greet": ["నమస్తే", "హలో"],
        "preventive": ["నివారణ", "మాస్క్", "కడుగు", "దూరం"],
        "symptoms": ["లక్షణాలు", "జ్వరం", "దగ్గు", "జలుబు", "తలనొప్పి"],
        "vaccine": ["టీకా", "టీకాకరణ", "డోస్", "షెడ్యూల్"],
        "outbreak": ["అలర్ట్", "కేసులు", "విస్తరణ"],
        "help": ["సహాయం", "మెను"],
    },
    "kn": {
        "greet": ["ನಮಸ್ಕಾರ", "ಹಲೋ"],
        "preventive": ["ತಡೆಗಟ್ಟುವಿಕೆ", "ಮಾಸ್ಕ್", "ಕೈ", "ತೊಳೆಯಿರಿ", "ಅಂತರ"],
        "symptoms": ["ಲಕ್ಷಣಗಳು", "ಜ್ವರ", "ಕೆಮ್ಮು", "ಶೀತ", "ತಲೆನೋವು"],
        "vaccine": ["ಲಸಿಕೆ", "ವೇಳಾಪಟ್ಟಿ", "ಡೋಸ್", "ಲಸಿಕಾಕರಣ"],
        "outbreak": ["ಎಚ್ಚರಿಕೆ", "ಕೇಸುಗಳು", "ಪ್ರಸರಣ"],
        "help": ["ಸಹಾಯ", "ಮೆನು"],
    },
    "ta": {
        "greet": ["வணக்கம்", "ஹலோ"],
        "preventive": ["தடுப்பு", "மாஸ்க்", "கைகளை", "கழுவ", "இடைவெளி"],
        "symptoms": ["அறிகுறிகள்", "காய்ச்சல்", "இருமல்", "சளி", "தலைவலி"],
        "vaccine": ["தடுப்பூசி", "அட்டவணை", "டோஸ்"],
        "outbreak": ["அலர்ட்", "பரவல்", "வழக்குகள்"],
        "help": ["உதவி", "மெனு"],
    },
}

RESPONSES: Dict[str, Dict[str, str]] = {
    "en": {
        "greet": "Hello! Ask me about prevention, symptoms, vaccines, or type 'alert'.",
        "preventive": "Wash hands, wear a mask in crowds, keep distance if sick, drink safe water.",
        "symptoms": "Watch for fever, cough, cold, headache. Seek a doctor for breathing issues.",
        "vaccine": "Send your age or a child's age to get a sample vaccination schedule.",
        "outbreak": "Current demo alert: Dengue risk is moderate. Remove stagnant water.",
        "help": "Try: prevention tips, symptoms, vaccine schedule, outbreak alerts.",
    },
    "hi": {
        "greet": "नमस्ते! रोकथाम, लक्षण, टीकाकरण या 'अलर्ट' लिखें।",
        "preventive": "हाथ धोएँ, भीड़ में मास्क पहनें, बीमार हों तो दूरी रखें, साफ पानी पिएँ।",
        "symptoms": "लक्षण: बुखार, खांसी, जुकाम, सिरदर्द। सांस में दिक्कत हो तो डॉक्टर से मिलें।",
        "vaccine": "अपनी या बच्चे की उम्र भेजें, मैं नमूना टीकाकरण शेड्यूल बताऊँगा।",
        "outbreak": "डेमो अलर्ट: डेंगू जोखिम मध्यम। रुका पानी हटाएँ।",
        "help": "पूछें: रोकथाम, लक्षण, टीकाकरण, प्रकोप अलर्ट।",
    },
    "te": {
        "greet": "నమస్తే! నివారణ, లక్షణాలు, టీకాలు లేదా 'అలర్ట్' అడగండి.",
        "preventive": "చేతులు కడగండి, గుంపుల్లో మాస్క్ ధరించండి, అనారోగ్యం ఉంటే దూరం పాటించండి, శుభ్రమైన నీరు తాగండి.",
        "symptoms": "లక్షణాలు: జ్వరం, దగ్గు, జలుబు, తలనొప్పి. శ్వాస ఇబ్బంది అయితే వైద్యుడిని సంప్రదించండి.",
        "vaccine": "వయస్సు పంపండి, నమూనా టీకా షెడ్యూల్ ఇస్తాను.",
        "outbreak": "డెమో అలర్ట్: డెంగ్యూ మోస్తరు ప్రమాదం. నిల్వ నీరు తొలగించండి.",
        "help": "ప్రశ్నలు: నివారణ, లక్షణాలు, టీకాలు, అలర్ట్స్.",
    },
    "kn": {
        "greet": "ನಮಸ್ಕಾರ! ತಡೆಗಟ್ಟುವಿಕೆ, ಲಕ್ಷಣಗಳು, ಲಸಿಕೆಗಳು ಅಥವಾ 'ಅಲರ್ಟ್' ಕೇಳಿ.",
        "preventive": "ಕೈ ತೊಳೆಯಿರಿ, ಗುಂಪಿನಲ್ಲಿ ಮಾಸ್ಕ್ ಧರಿಸಿ, ಅಸ್ವಸ್ಥರಾಗಿದ್ದರೆ ಅಂತರ ಕಾಯ್ದುಕೊಳ್ಳಿ, ಶುದ್ಧ ನೀರು ಕುಡಿಯಿರಿ.",
        "symptoms": "ಲಕ್ಷಣಗಳು: ಜ್ವರ, ಕೆಮ್ಮು, ಶೀತ, ತಲೆನೋವು. ಉಸಿರಾಟ ತೊಂದರೆ ಇದ್ದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "vaccine": "ನಿಮ್ಮ ವಯಸ್ಸು ಕಳುಹಿಸಿ, ಮಾದರಿ ಲಸಿಕೆ ವೇಳಾಪಟ್ಟಿ ನೀಡುತ್ತೇನೆ.",
        "outbreak": "ಡೆಮೋ ಎಚ್ಚರಿಕೆ: ಡೆಂಗ್ಯು ಮಧ್ಯಮ ಅಪಾಯ. ನಿಂತ ನೀರನ್ನು ತೆಗೆಯಿರಿ.",
        "help": "ಪ್ರಶ್ನೆಗಳು: ತಡೆಗಟ್ಟುವಿಕೆ, ಲಕ್ಷಣಗಳು, ಲಸಿಕೆ, ಅಲರ್ಟ್.",
    },
    "ta": {
        "greet": "வணக்கம்! தடுப்பு, அறிகுறிகள், தடுப்பூசி அல்லது 'அலர்ட்' கேளுங்கள்.",
        "preventive": "கைகளை கழுவுங்கள், கூட்டத்தில் மாஸ்க் அணியுங்கள், உடல்நலம் குன்றினால் இடைவெளி வைத்திருங்கள், சுத்தமான தண்ணீர் குடியுங்கள்.",
        "symptoms": "அறிகுறிகள்: காய்ச்சல், இருமல், சளி, தலைவலி. சுவாச சிரமம் இருந்தால் மருத்துவரை காணுங்கள்.",
        "vaccine": "வயதை அனுப்புங்கள், மாதிரி தடுப்பூசி அட்டவணை தருகிறேன்.",
        "outbreak": "டெமோ எச்சரிக்கை: டெங்கு மிதமான ஆபத்து. தங்கிய நீரை அகற்றுங்கள்.",
        "help": "கேள்விகள்: தடுப்பு, அறிகுறிகள், தடுப்பூசி, அலர்ட்.",
    },
}

MOCK_VACCINE_SCHEDULE = {
    "infant": [
        {"age": "6 weeks", "vaccine": "OPV, Penta, Rota"},
        {"age": "10 weeks", "vaccine": "OPV, Penta, Rota"},
        {"age": "14 weeks", "vaccine": "OPV, Penta, Rota"},
        {"age": "9-12 months", "vaccine": "Measles/Rubella"},
    ],
    "adult": [
        {"age": "Anytime", "vaccine": "Tetanus booster every 10 years"},
        {"age": ">= 60", "vaccine": "Flu, Pneumococcal (as advised)"},
    ],
}

SUBSCRIBERS: List[Tuple[str, str]] = []

def fetch_vaccination_schedule(age_years: int) -> List[Dict[str, str]]:
    if age_years <= 1:
        return MOCK_VACCINE_SCHEDULE["infant"]
    return MOCK_VACCINE_SCHEDULE["adult"]

def fetch_outbreak_alerts(pincode: Optional[str]) -> str:
    if pincode:
        return f"Outbreak update for {pincode}: Dengue risk is moderate. Remove stagnant water."
    return "Outbreak update: No major alerts currently. Stay safe!"

def format_vaccine_reply(lang: str, schedule: List[Dict[str, str]]) -> str:
    if lang not in RESPONSES:
        lang = "en"
    if lang == "en":
        lines = ["Sample vaccination schedule:"]
    elif lang == "hi":
        lines = ["नमूना टीकाकरण शेड्यूल:"]
    elif lang == "te":
        lines = ["నమూనా టీకా షెడ్యూల్:"]
    elif lang == "kn":
        lines = ["ಮಾದರಿ ಲಸಿಕೆ ವೇಳಾಪಟ್ಟಿ:"]
    else:
        lines = ["மாதிரி தடுப்பூசி அட்டவணை:"]
    for row in schedule:
        lines.append(f"- {row['age']}: {row['vaccine']}")
    return "".join(lines)

def send_message(phone: str, text: str) -> None:
    print(f"[SEND] to {phone}: {text}")

class BroadcastIn:
    def __init__(self, d: dict):
        self.message_en = d.get("message_en", "")
        self.message_hi = d.get("message_hi")
        self.message_te = d.get("message_te")
        self.message_kn = d.get("message_kn")
        self.message_ta = d.get("message_ta")

def handle_message(phone: str, text: str, pincode: Optional[str] = None, lang_in: Optional[str] = None):
    lang = lang_in if lang_in in LANGS else guess_lang(text)
    lang_map = INTENT_KEYWORDS.get(lang, INTENT_KEYWORDS["en"])
    t = (text or "").lower()
    intent = "help"
    for k_intent, kws in lang_map.items():
        for k in kws:
            if k in t:
                intent = k_intent
                break
        if intent != "help":
            break
    if len(t) <= 2:
        intent = "greet"
    reply = RESPONSES.get(lang, RESPONSES["en"]).get(intent, RESPONSES["en"]["help"])
    age = extract_age_years(text)
    if age is not None:
        schedule = fetch_vaccination_schedule(age)
        reply = format_vaccine_reply(lang, schedule)
    if intent == "outbreak":
        alert = fetch_outbreak_alerts(pincode)
        reply = reply + "" + alert
    send_message(phone, reply)
    return {"to": phone, "lang": lang, "intent": intent, "reply": reply}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    phone = str(data.get("phone", ""))
    text = str(data.get("text", ""))
    pincode = data.get("pincode")
    lang_in = data.get("lang")
    result = handle_message(phone=phone, text=text, pincode=pincode, lang_in=lang_in)
    return jsonify(result)

@app.route("/twilio", methods=["POST"])
def twilio_webhook():
    form = request.form or {}
    phone = form.get("WaId") or form.get("From", "").replace("whatsapp:", "")
    text = form.get("Body", "")
    pincode = None
    lang_in = None
    result = handle_message(phone=phone, text=text, pincode=pincode, lang_in=lang_in)
    return jsonify(result)

def extract_age_years(text: str) -> Optional[int]:
    if not text:
        return None
    t = text.lower()
    num = ""
    digits: List[str] = []
    for ch in t:
        if ch.isdigit():
            num += ch
        else:
            if num:
                digits.append(num)
                num = ""
    if num:
        digits.append(num)
    if not digits:
        return None
    try:
        val = int(digits[0])
        if 0 <= val <= 120:
            return val
    except Exception:
        return None
    return None

@app.route("/admin/broadcast", methods=["POST"])
def admin_broadcast():
    payload = BroadcastIn(request.get_json(force=True, silent=True) or {})
    messages = {
        "en": payload.message_en,
        "hi": payload.message_hi or payload.message_en,
        "te": payload.message_te or payload.message_en,
        "kn": payload.message_kn or payload.message_en,
        "ta": payload.message_ta or payload.message_en,
    }
    report: List[Dict[str, str]] = []
    for phone, lang in SUBSCRIBERS:
        text = messages.get(lang, payload.message_en)
        send_message(phone, text)
        report.append({"phone": phone, "lang": lang, "sent": "yes"})
    return jsonify({"count": len(report), "details": report})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
        "subscribers": len(SUBSCRIBERS),
        "langs": LANGS,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
from flask import Flask, request, jsonify
from typing import Dict, List, Optional, Tuple
from datetime import datetime

app = Flask(__name__)

LANGS = ["en", "hi", "te", "kn", "ta"]

def guess_lang(text: str) -> str:
    if text is None:
        return "en"
    t = text.strip().lower()
    if len(t) == 0:
        return "en"
    hi_hints = ["namaste", "नमस्ते", "खांसी", "बुखार", "टीका", "टीकाकरण", "स्वास्थ्य"]
    te_hints = ["నమస్తే", "జ్వరం", "దగ్గు", "టీకా", "ఆరోగ్యం"]
    kn_hints = ["ನಮಸ್ಕಾರ", "ಜ್ವರ", "ಕೆಮ್ಮು", "ಲಸಿಕೆ", "ಆರೋಗ್ಯ"]
    ta_hints = ["வணக்கம்", "காய்ச்சல்", "இருமல்", "தடுப்பூசி", "ஆரோக்கியம்"]
    if any(ch in t for ch in "अआइईउऊएऐओऔकखगघचछजझटठडढतथदधनपफबभमयरलवशषसहािंीुूेैोौंः"):
        return "hi"
    if any(ch in t for ch in "అఆఇఈఉఊఎఏఐఒఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహాిీుూెేైొోౌంః"):
        return "te"
    if any(ch in t for ch in "ಅಆಇಈಉಊಎಏಐಒಓಔಕಖಗಘಙಚಛಜಝಞಟಠಡಢಣತಥದಧನಪಫಬಭಮಯರಲವಶಷಸಹಾಿೀುೂೃೆೇೈೊೋೌಂಃ"):
        return "kn"
    if any(ch in t for ch in "அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறஸஷஹாிீுூெேைொோௌம்ஂஃ"):
        return "ta"
    if any(w in t for w in hi_hints):
        return "hi"
    if any(w in t for w in te_hints):
        return "te"
    if any(w in t for w in kn_hints):
        return "kn"
    if any(w in t for w in ta_hints):
        return "ta"
    return "en"

class Intent(str):
    pass

INTENT_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "en": {
        "greet": ["hi", "hello", "hey", "namaste"],
        "preventive": ["prevention", "prevent", "wash", "mask", "avoid"],
        "symptoms": ["symptom", "fever", "cough", "cold", "headache"],
        "vaccine": ["vaccine", "vaccination", "schedule", "dose", "immunization"],
        "outbreak": ["outbreak", "alert", "cases", "disease spread"],
        "help": ["help", "menu"],
    },
    "hi": {
        "greet": ["नमस्ते", "नमस्कार", "हैलो"],
        "preventive": ["रोकथाम", "सावधानी", "मास्क", "हाथ", "धो"],
        "symptoms": ["लक्षण", "बुखार", "खांसी", "जुकाम", "सरदर्द"],
        "vaccine": ["टीका", "टीकाकरण", "खुराक", "शेड्यूल"],
        "outbreak": ["प्रकोप", "अलर्ट", "मामले", "फैल"],
        "help": ["मदद", "विकल्प"],
    },
    "te": {
        "greet": ["నమస్తే", "హలో"],
        "preventive": ["నివారణ", "మాస్క్", "కడుగు", "దూరం"],
        "symptoms": ["లక్షణాలు", "జ్వరం", "దగ్గు", "జలుబు", "తలనొప్పి"],
        "vaccine": ["టీకా", "టీకాకరణ", "డోస్", "షెడ్యూల్"],
        "outbreak": ["అలర్ట్", "కేసులు", "విస్తరణ"],
        "help": ["సహాయం", "మెను"],
    },
    "kn": {
        "greet": ["ನಮಸ್ಕಾರ", "ಹಲೋ"],
        "preventive": ["ತಡೆಗಟ್ಟುವಿಕೆ", "ಮಾಸ್ಕ್", "ಕೈ", "ತೊಳೆಯಿರಿ", "ಅಂತರ"],
        "symptoms": ["ಲಕ್ಷಣಗಳು", "ಜ್ವರ", "ಕೆಮ್ಮು", "ಶೀತ", "ತಲೆನೋವು"],
        "vaccine": ["ಲಸಿಕೆ", "ವೇಳಾಪಟ್ಟಿ", "ಡೋಸ್", "ಲಸಿಕಾಕರಣ"],
        "outbreak": ["ಎಚ್ಚರಿಕೆ", "ಕೇಸುಗಳು", "ಪ್ರಸರಣ"],
        "help": ["ಸಹಾಯ", "ಮೆನು"],
    },
    "ta": {
        "greet": ["வணக்கம்", "ஹலோ"],
        "preventive": ["தடுப்பு", "மாஸ்க்", "கைகளை", "கழுவ", "இடைவெளி"],
        "symptoms": ["அறிகுறிகள்", "காய்ச்சல்", "இருமல்", "சளி", "தலைவலி"],
        "vaccine": ["தடுப்பூசி", "அட்டவணை", "டோஸ்"],
        "outbreak": ["அலர்ட்", "பரவல்", "வழக்குகள்"],
        "help": ["உதவி", "மெனு"],
    },
}

RESPONSES: Dict[str, Dict[str, str]] = {
    "en": {
        "greet": "Hello! Ask me about prevention, symptoms, vaccines, or type 'alert'.",
        "preventive": "Wash hands, wear a mask in crowds, keep distance if sick, drink safe water.",
        "symptoms": "Watch for fever, cough, cold, headache. Seek a doctor for breathing issues.",
        "vaccine": "Send your age or a child's age to get a sample vaccination schedule.",
        "outbreak": "Current demo alert: Dengue risk is moderate. Remove stagnant water.",
        "help": "Try: prevention tips, symptoms, vaccine schedule, outbreak alerts.",
    },
    "hi": {
        "greet": "नमस्ते! रोकथाम, लक्षण, टीकाकरण या 'अलर्ट' लिखें।",
        "preventive": "हाथ धोएँ, भीड़ में मास्क पहनें, बीमार हों तो दूरी रखें, साफ पानी पिएँ।",
        "symptoms": "लक्षण: बुखार, खांसी, जुकाम, सिरदर्द। सांस में दिक्कत हो तो डॉक्टर से मिलें।",
        "vaccine": "अपनी या बच्चे की उम्र भेजें, मैं नमूना टीकाकरण शेड्यूल बताऊँगा।",
        "outbreak": "डेमो अलर्ट: डेंगू जोखिम मध्यम। रुका पानी हटाएँ।",
        "help": "पूछें: रोकथाम, लक्षण, टीकाकरण, प्रकोप अलर्ट।",
    },
    "te": {
        "greet": "నమస్తే! నివారణ, లక్షణాలు, టీకాలు లేదా 'అలర్ట్' అడగండి.",
        "preventive": "చేతులు కడగండి, గుంపుల్లో మాస్క్ ధరించండి, అనారోగ్యం ఉంటే దూరం పాటించండి, శుభ్రమైన నీరు తాగండి.",
        "symptoms": "లక్షణాలు: జ్వరం, దగ్గు, జలుబు, తలనొప్పి. శ్వాస ఇబ్బంది అయితే వైద్యుడిని సంప్రదించండి.",
        "vaccine": "వయస్సు పంపండి, నమూనా టీకా షెడ్యూల్ ఇస్తాను.",
        "outbreak": "డెమో అలర్ట్: డెంగ్యూ మోస్తరు ప్రమాదం. నిల్వ నీరు తొలగించండి.",
        "help": "ప్రశ్నలు: నివారణ, లక్షణాలు, టీకాలు, అలర్ట్స్.",
    },
    "kn": {
        "greet": "ನಮಸ್ಕಾರ! ತಡೆಗಟ್ಟುವಿಕೆ, ಲಕ್ಷಣಗಳು, ಲಸಿಕೆಗಳು ಅಥವಾ 'ಅಲರ್ಟ್' ಕೇಳಿ.",
        "preventive": "ಕೈ ತೊಳೆಯಿರಿ, ಗುಂಪಿನಲ್ಲಿ ಮಾಸ್ಕ್ ಧರಿಸಿ, ಅಸ್ವಸ್ಥರಾಗಿದ್ದರೆ ಅಂತರ ಕಾಯ್ದುಕೊಳ್ಳಿ, ಶುದ್ಧ ನೀರು ಕುಡಿಯಿರಿ.",
        "symptoms": "ಲಕ್ಷಣಗಳು: ಜ್ವರ, ಕೆಮ್ಮು, ಶೀತ, ತಲೆನೋವು. ಉಸಿರಾಟ ತೊಂದರೆ ಇದ್ದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "vaccine": "ನಿಮ್ಮ ವಯಸ್ಸು ಕಳುಹಿಸಿ, ಮಾದರಿ ಲಸಿಕೆ ವೇಳಾಪಟ್ಟಿ ನೀಡುತ್ತೇನೆ.",
        "outbreak": "ಡೆಮೋ ಎಚ್ಚರಿಕೆ: ಡೆಂಗ್ಯು ಮಧ್ಯಮ ಅಪಾಯ. ನಿಂತ ನೀರನ್ನು ತೆಗೆಯಿರಿ.",
        "help": "ಪ್ರಶ್ನೆಗಳು: ತಡೆಗಟ್ಟುವಿಕೆ, ಲಕ್ಷಣಗಳು, ಲಸಿಕೆ, ಅಲರ್ಟ್.",
    },
    "ta": {
        "greet": "வணக்கம்! தடுப்பு, அறிகுறிகள், தடுப்பூசி அல்லது 'அலர்ட்' கேளுங்கள்.",
        "preventive": "கைகளை கழுவுங்கள், கூட்டத்தில் மாஸ்க் அணியுங்கள், உடல்நலம் குன்றினால் இடைவெளி வைத்திருங்கள், சுத்தமான தண்ணீர் குடியுங்கள்.",
        "symptoms": "அறிகுறிகள்: காய்ச்சல், இருமல், சளி, தலைவலி. சுவாச சிரமம் இருந்தால் மருத்துவரை காணுங்கள்.",
        "vaccine": "வயதை அனுப்புங்கள், மாதிரி தடுப்பூசி அட்டவணை தருகிறேன்.",
        "outbreak": "டெமோ எச்சரிக்கை: டெங்கு மிதமான ஆபத்து. தங்கிய நீரை அகற்றுங்கள்.",
        "help": "கேள்விகள்: தடுப்பு, அறிகுறிகள், தடுப்பூசி, அலர்ட்.",
    },
}

MOCK_VACCINE_SCHEDULE = {
    "infant": [
        {"age": "6 weeks", "vaccine": "OPV, Penta, Rota"},
        {"age": "10 weeks", "vaccine": "OPV, Penta, Rota"},
        {"age": "14 weeks", "vaccine": "OPV, Penta, Rota"},
        {"age": "9-12 months", "vaccine": "Measles/Rubella"},
    ],
    "adult": [
        {"age": "Anytime", "vaccine": "Tetanus booster every 10 years"},
        {"age": ">= 60", "vaccine": "Flu, Pneumococcal (as advised)"},
    ],
}

SUBSCRIBERS: List[Tuple[str, str]] = []

def fetch_vaccination_schedule(age_years: int) -> List[Dict[str, str]]:
    if age_years <= 1:
        return MOCK_VACCINE_SCHEDULE["infant"]
    return MOCK_VACCINE_SCHEDULE["adult"]

def fetch_outbreak_alerts(pincode: Optional[str]) -> str:
    if pincode:
        return f"Outbreak update for {pincode}: Dengue risk is moderate. Remove stagnant water."
    return "Outbreak update: No major alerts currently. Stay safe!"

def format_vaccine_reply(lang: str, schedule: List[Dict[str, str]]) -> str:
    if lang not in RESPONSES:
        lang = "en"
    if lang == "en":
        lines = ["Sample vaccination schedule:"]
    elif lang == "hi":
        lines = ["नमूना टीकाकरण शेड्यूल:"]
    elif lang == "te":
        lines = ["నమూనా టీకా షెడ్యూల్:"]
    elif lang == "kn":
        lines = ["ಮಾದರಿ ಲಸಿಕೆ ವೇಳಾಪಟ್ಟಿ:"]
    else:
        lines = ["மாதிரி தடுப்பூசி அட்டவணை:"]
    for row in schedule:
        lines.append(f"- {row['age']}: {row['vaccine']}")
    return "".join(lines)

def send_message(phone: str, text: str) -> None:
    print(f"[SEND] to {phone}: {text}")

class BroadcastIn:
    def __init__(self, d: dict):
        self.message_en = d.get("message_en", "")
        self.message_hi = d.get("message_hi")
        self.message_te = d.get("message_te")
        self.message_kn = d.get("message_kn")
        self.message_ta = d.get("message_ta")

def handle_message(phone: str, text: str, pincode: Optional[str] = None, lang_in: Optional[str] = None):
    lang = lang_in if lang_in in LANGS else guess_lang(text)
    lang_map = INTENT_KEYWORDS.get(lang, INTENT_KEYWORDS["en"])
    t = (text or "").lower()
    intent = "help"
    for k_intent, kws in lang_map.items():
        for k in kws:
            if k in t:
                intent = k_intent
                break
        if intent != "help":
            break
    if len(t) <= 2:
        intent = "greet"
    reply = RESPONSES.get(lang, RESPONSES["en"]).get(intent, RESPONSES["en"]["help"])
    age = extract_age_years(text)
    if age is not None:
        schedule = fetch_vaccination_schedule(age)
        reply = format_vaccine_reply(lang, schedule)
    if intent == "outbreak":
        alert = fetch_outbreak_alerts(pincode)
        reply = reply + "" + alert
    send_message(phone, reply)
    return {"to": phone, "lang": lang, "intent": intent, "reply": reply}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    phone = str(data.get("phone", ""))
    text = str(data.get("text", ""))
    pincode = data.get("pincode")
    lang_in = data.get("lang")
    result = handle_message(phone=phone, text=text, pincode=pincode, lang_in=lang_in)
    return jsonify(result)

@app.route("/twilio", methods=["POST"])
def twilio_webhook():
    form = request.form or {}
    phone = form.get("WaId") or form.get("From", "").replace("whatsapp:", "")
    text = form.get("Body", "")
    pincode = None
    lang_in = None
    result = handle_message(phone=phone, text=text, pincode=pincode, lang_in=lang_in)
    return jsonify(result)

def extract_age_years(text: str) -> Optional[int]:
    if not text:
        return None
    t = text.lower()
    num = ""
    digits: List[str] = []
    for ch in t:
        if ch.isdigit():
            num += ch
        else:
            if num:
                digits.append(num)
                num = ""
    if num:
        digits.append(num)
    if not digits:
        return None
    try:
        val = int(digits[0])
        if 0 <= val <= 120:
            return val
    except Exception:
        return None
    return None

@app.route("/admin/broadcast", methods=["POST"])
def admin_broadcast():
    payload = BroadcastIn(request.get_json(force=True, silent=True) or {})
    messages = {
        "en": payload.message_en,
        "hi": payload.message_hi or payload.message_en,
        "te": payload.message_te or payload.message_en,
        "kn": payload.message_kn or payload.message_en,
        "ta": payload.message_ta or payload.message_en,
    }
    report: List[Dict[str, str]] = []
    for phone, lang in SUBSCRIBERS:
        text = messages.get(lang, payload.message_en)
        send_message(phone, text)
        report.append({"phone": phone, "lang": lang, "sent": "yes"})
    return jsonify({"count": len(report), "details": report})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
        "subscribers": len(SUBSCRIBERS),
        "langs": LANGS,
    })
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/twilio", methods=["POST"])
def twilio_webhook():
    # get incoming message
    incoming_msg = (request.form.get("Body") or "").strip()

    # simple reply
    reply = f"You said: {incoming_msg}. Ask me about vaccines, symptoms, or type 'alert'."

    # build TwiML
    twiml = MessagingResponse()
    twiml.message(reply)

    # return XML
    return Response(str(twiml), mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
