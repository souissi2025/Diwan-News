import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Diwan Smart Editor", layout="wide", page_icon="🎙️")

# تصميم الأزرار
st.markdown("""
<style>
    .stButton>button {
        width: 100%; height: 80px; border-radius: 12px;
        font-size: 18px; font-weight: bold; background-color: #0E738A; color: white;
    }
    .stButton>button:hover { background-color: #D95F18; border-color: white; }
    h1 { color: #0E738A; }
</style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بالمفتاح ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود (Clé manquante)")
    st.stop()

# --- 3. التعليمات ---
PROMPTS = {
    "article": "أنت صحفي محترف. أعد صياغة النص كخبر صحفي (الهرم المقلوب). احذف الألقاب. لغة عربية قوية.",
    "web": "أنت خبير SEO. أعد صياغة النص للويب. فقرات قصيرة، كلمات مفتاحية، وعنوان جذاب.",
    "flash": "حول الخبر إلى موجز إذاعي قصير جداً (للمذيع). جمل قصيرة. لا تتجاوز 40 كلمة.",
    "titles": "اقترح 5 عناوين قوية (إخباري، تساؤلي، مثير، رقمي، فيسبوك).",
    "quotes": "استخرج أهم التصريحات في نقاط: - [الاسم]: النص.",
    "history": "حدث في مثل هذا اليوم (تونس، ثم العالم). باختصار."
}

# --- 4. الواجهة ---
st.title("🎙️ ديوان أف أم - المحرر الذكي")

# حفظ الوضع المختار
if 'mode' not in st.session_state:
    st.session_state.mode = "article" # الوضع الافتراضي

def set_mode(m): st.session_state.mode = m

# أزرار اختيار الخدمة
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

# --- 5. منطقة العمل (داخل Form لضمان الاستقرار) ---
titles_map = {
    "article": "📝 صياغة مقال صحفي", "web": "✨ تحرير ويب (SEO)",
    "flash": "((●)) موجز إذاعي", "titles": "T اقتراح عناوين",
    "quotes": "ılı استخراج التصريحات", "history": "📅 حدث في مثل هذا اليوم"
}

current_mode = st.session_state.mode
st.header(titles_map[current_mode])

# >> هنا الحل السحري: استخدام st.form <<
with st.form("my_form"):
    text_input = st.text_area("أدخل النص أو التاريخ هنا:", height=200)
    
    # زر الإرسال داخل الفورم
    submitted = st.form_submit_button("🚀 تنفيذ المهمة (Exécuter)")
    
    if submitted:
        if not text_input:
            st.warning("الرجاء إدخال نص.")
        else:
            st.info("⏳ جاري الاتصال... (En cours)")
            try:
                # استخدام Flash للسرعة
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                response = model.generate_content(
                    f"{PROMPTS[current_mode]}\n\nالنص:\n{text_input}"
                )
                
                # التحقق من وجود رد قبل طباعته
                if response.text:
                    st.success("✅ تمت العملية:")
                    st.markdown(response.text)
                else:
                    st.error("⚠️ وصل الرد فارغاً (قد يكون بسبب فلاتر المحتوى).")
                    
            except Exception as e:
                # طباعة الخطأ بوضوح
                st.error(f"❌ حدث خطأ: {e}")
                # محاولة ثانية بالموديل القديم إذا فشل الجديد
                try:
                    st.warning("🔄 محاولة بالموديل الاحتياطي...")
                    model_pro = genai.GenerativeModel('gemini-1.5-pro')
                    response_pro = model_pro.generate_content(
                        f"{PROMPTS[current_mode]}\n\nالنص:\n{text_input}"
                    )
                    st.markdown(response_pro.text)
                except:
                    pass
