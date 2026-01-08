import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Diwan Smart Newsroom", layout="wide", page_icon="🎙️")

# CSS لتحسين المظهر
st.markdown("""
<style>
    .stButton>button {
        width: 100%; height: 100px; border-radius: 10px;
        font-size: 18px; font-weight: bold; background-color: #0E738A; color: white;
    }
    .stButton>button:hover { background-color: #D95F18; border-color: white; }
    h1 { text-align: center; color: #0E738A; }
</style>
""", unsafe_allow_html=True)

# --- 2. التحقق من المفتاح ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ مفتاح API مفقود! تأكد من وضعه في Secrets.")
    st.stop()

# --- 3. التعليمات (PROMPTS) ---
PROMPTS = {
    "article_writer": "أنت صحفي محترف. أعد صياغة النص كخبر صحفي (الهرم المقلوب). احذف الألقاب واستخدم الصفات. لغة عربية قوية.",
    "web_editor": "أنت خبير SEO. أعد صياغة النص للموقع الإلكتروني. فقرات قصيرة، كلمات مفتاحية، وعنوان جذاب.",
    "headlines": "اقترح 5 عناوين قوية (إخباري، تساؤلي، مثير، رقمي، فيسبوك).",
    "quotes": "استخرج أهم التصريحات في شكل نقاط مع ذكر القائل.",
    "radio_flash": "حول النص لموجز إذاعي (40 كلمة كحد أقصى) للكلام المنطوق.",
    "on_this_day": "حدث في مثل هذا اليوم (تونس أولاً، ثم العالم). باختصار."
}

# --- 4. الواجهة ---
st.title("🎙️ ديوان أف أم - المحرر الذكي")
st.markdown("---")

# إدارة الأزرار
if 'active_mode' not in st.session_state:
    st.session_state.active_mode = None

def set_mode(mode):
    st.session_state.active_mode = mode

# شبكة الأزرار
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📝 صياغة مقال"): set_mode("article_writer")
    if st.button("T صانع العناوين"): set_mode("headlines")
with col2:
    if st.button("✨ تحرير ويب (SEO)"): set_mode("web_editor")
    if st.button("((●)) موجز إذاعي"): set_mode("radio_flash")
with col3:
    if st.button("ılı أهم التصريحات"): set_mode("quotes")
    if st.button("📅 حدث اليوم"): set_mode("on_this_day")

st.markdown("---")

# --- 5. منطقة العمل ---
if st.session_state.active_mode:
    titles = {
        "article_writer": "📝 صياغة مقال صحفي",
        "web_editor": "✨ تحرير ويب (SEO)",
        "headlines": "T مقترحات عناوين",
        "quotes": "ılı استخراج التصريحات",
        "radio_flash": "((●)) موجز إذاعي",
        "on_this_day": "📅 حدث في مثل هذا اليوم"
    }
    
    mode = st.session_state.active_mode
    st.header(titles[mode])
    
    # حقل الإدخال
    input_text = st.text_area("أدخل النص أو التاريخ هنا:", height=200)
    
    if st.button("🚀 تنفيذ المهمة"):
        if input_text:
            with st.spinner('جاري العمل بسرعة...'):
                try:
                    # هنا التغيير المهم: استخدام نموذج FLASH السريع
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    response = model.generate_content(
                        f"{PROMPTS[mode]}\n\nالنص:\n{input_text}"
                    )
                    st.success("تم!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
        else:
            st.warning("الرجاء إدخال النص.")
