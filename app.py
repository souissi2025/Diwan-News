import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة (Configuration) ---
st.set_page_config(page_title="Diwan Smart Newsroom", layout="wide", page_icon="🎙️")

# تصميم الأزرار (CSS)
st.markdown("""
<style>
    .stButton>button {
        width: 100%; height: 110px; border-radius: 12px;
        font-size: 20px; font-weight: bold; background-color: #0E738A; color: white;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #D95F18; border-color: white; transform: scale(1.02);
    }
    h1 { text-align: center; color: #0E738A; font-family: sans-serif; }
    .stSuccess { direction: rtl; font-size: 18px; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بالمفتاح (Connexion) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود (Clé manquante) - تأكد من Secrets")
    st.stop()

# --- 3. إعدادات الأمان (Sécurité) لمنع الحجب ---
safe = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# --- 4. التعليمات (Prompts) ---
PROMPTS = {
    "article": """أنت صحفي محترف في غرفة أخبار.
    المهمة: أعد صياغة النص التالي ليكون خبراً صحفياً متقناً.
    القواعد: 1. استخدم لغة عربية فصحى قوية. 2. احذف الألقاب واستبدلها بالصفات. 3. ابدأ بالأهم (الهرم المقلوب). 4. ضع عنواناً مقترحاً في البداية.""",
    
    "web": """أنت خبير SEO ومحرر ويب.
    المهمة: جهز هذا النص للنشر على الموقع الإلكتروني.
    القواعد: 1. فقرات قصيرة جداً. 2. استخرج 3 كلمات مفتاحية في النهاية. 3. صغ عنواناً جاذباً للنقر (Clickbait مهني).""",
    
    "flash": """أنت محرر نشرة موجزة (Flash Info).
    المهمة: حول الخبر إلى فقرة قصيرة جداً للمذيع.
    القواعد: 1. جمل قصيرة ومباشرة. 2. لا تتجاوز 40 كلمة. 3. اكتب للأذن وليس للعين.""",
    
    "titles": """اقترح 5 عناوين مختلفة لهذا الخبر:
    1. عنوان إخباري كلاسيكي.
    2. عنوان تساؤلي.
    3. عنوان صادم/مثير.
    4. عنوان يحتوي على أرقام.
    5. عنوان قصير للفيسبوك.""",
    
    "quotes": """استخرج "أهم التصريحات" فقط.
    ضعها في نقاط واضحة:
    - [الاسم]: "نص التصريح..." """,
    
    "history": """حدث في مثل هذا اليوم:
    ابحث في ذاكرتك التاريخية عن أحداث وقعت في هذا التاريخ.
    التركيز: 1. تونس 2. المغرب العربي 3. العالم.
    اكتبها بشكل موجز ومفيد."""
}

# --- 5. الواجهة (Interface) ---
st.title("🎙️ ديوان أف أم - المحرر الذكي")

if 'mode' not in st.session_state:
    st.session_state.mode = None

def set_mode(m): st.session_state.mode = m

# شبكة الأزرار
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📝 صياغة مقال"): set_mode("article")
    if st.button("T صانع العناوين"): set_mode("titles")
with c2:
    if st.button("✨ تحرير ويب"): set_mode("web")
    if st.button("((●)) موجز إذاعي"): set_mode("flash")
with c3:
    if st.button("ılı أهم التصريحات"): set_mode("quotes")
    if st.button("📅 حدث اليوم"): set_mode("history")

st.markdown("---")

# --- 6. التنفيذ (Exécution) ---
if st.session_state.mode:
    titles_map = {
        "article": "📝 صياغة مقال صحفي", "web": "✨ تحرير ويب (SEO)",
        "flash": "((●)) موجز إذاعي", "titles": "T اقتراح عناوين",
        "quotes": "ılı استخراج التصريحات", "history": "📅 حدث في مثل هذا اليوم"
    }
    
    current_mode = st.session_state.mode
    st.header(titles_map[current_mode])
    
    user_input = st.text_area("أدخل النص أو التاريخ هنا:", height=180)
    
    if st.button("🚀 تنفيذ (Exécuter)"):
        if user_input:
            with st.spinner('جاري المعالجة (En cours)...'):
                try:
                    # محاولة استخدام الموديل السريع Flash
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(
                        f"{PROMPTS[current_mode]}\n\nالنص:\n{user_input}",
                        safety_settings=safe
                    )
                    st.success("✅ النتيجة:")
                    st.markdown(response.text)
                    
                except Exception as e:
                    # في حال فشل Flash، نستخدم Pro تلقائياً كخطة بديلة
                    try:
                        st.warning("جاري التبديل للموديل البديل...")
                        model_backup = genai.GenerativeModel('gemini-1.5-pro')
                        response = model_backup.generate_content(
                            f"{PROMPTS[current_mode]}\n\nالنص:\n{user_input}",
                            safety_settings=safe
                        )
                        st.success("✅ النتيجة (Pro):")
                        st.markdown(response.text)
                    except Exception as e2:
                        st.error(f"خطأ في الاتصال: {e2}")
        else:
            st.warning("الرجاء إدخال النص أولاً.")
