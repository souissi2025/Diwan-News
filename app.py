import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Diwan Newsroom", layout="wide", page_icon="🎙️")
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
    st.error("⚠️ المفتاح مفقود.")
    st.stop()

# --- 3. دالة ذكية لاختيار الموديل المتاح ---
def get_working_model():
    # قائمة أسماء نحاول معها بالترتيب
    candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    # محاولة تجربة الأسماء المعروفة
    return genai.GenerativeModel("gemini-1.5-flash") # نجرب الفلاش كخيار أول

# --- 4. التعليمات ---
PROMPTS = {
    "article": "أنت صحفي محترف. أعد صياغة النص كخبر صحفي (الهرم المقلوب). احذف الألقاب. لغة عربية قوية.",
    "web": "أنت خبير SEO. أعد صياغة النص للويب. فقرات قصيرة، كلمات مفتاحية، وعنوان جذاب.",
    "flash": "حول الخبر إلى موجز إذاعي قصير جداً (للمذيع). جمل قصيرة. لا تتجاوز 40 كلمة.",
    "titles": "اقترح 5 عناوين قوية (إخباري، تساؤلي، مثير، رقمي، فيسبوك).",
    "quotes": "استخرج أهم التصريحات في نقاط: - [الاسم]: النص.",
    "history": "حدث في مثل هذا اليوم (تونس، ثم العالم). باختصار."
}

# --- 5. الواجهة ---
st.title("🎙️ ديوان أف أم - المحرر الذكي")

if 'mode' not in st.session_state: st.session_state.mode = "article"
def set_mode(m): st.session_state.mode = m

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

titles_map = {
    "article": "📝 صياغة مقال صحفي", "web": "✨ تحرير ويب (SEO)",
    "flash": "((●)) موجز إذاعي", "titles": "T اقتراح عناوين",
    "quotes": "ılı استخراج التصريحات", "history": "📅 حدث في مثل هذا اليوم"
}
current_mode = st.session_state.mode
st.header(titles_map[current_mode])

# الفورم والتنفيذ
with st.form("my_form"):
    text_input = st.text_area("أدخل النص أو التاريخ:", height=200)
    submitted = st.form_submit_button("🚀 تنفيذ المهمة")
    
    if submitted:
        if not text_input:
            st.warning("أدخل نصاً.")
        else:
            st.info("⏳ جاري البحث عن أفضل موديل وتنفيذ الطلب...")
            
            try:
                # 1. أولاً: نحاول الحصول على قائمة الموديلات المتاحة لك فعلياً
                available_models = []
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_models.append(m.name)
                except:
                    pass
                
                # 2. اختيار موديل من القائمة
                chosen_model_name = ""
                if available_models:
                    # نفضل الفلاش إذا وجدناه
                    if 'models/gemini-1.5-flash' in available_models:
                        chosen_model_name = 'gemini-1.5-flash'
                    elif 'models/gemini-pro' in available_models:
                        chosen_model_name = 'gemini-pro'
                    else:
                        # نأخذ أول واحد متاح وخلاص
                        chosen_model_name = available_models[0].replace('models/', '')
                else:
                    # إذا فشل البحث، نستخدم الفلاش كحل أخير
                    chosen_model_name = 'gemini-1.5-flash'

                # 3. التنفيذ بالموديل المختار
                # st.write(f"Testing Model: {chosen_model_name}") # للتجربة
                
                model = genai.GenerativeModel(chosen_model_name)
                response = model.generate_content(
                    f"{PROMPTS[current_mode]}\n\nالنص:\n{text_input}"
                )
                st.success(f"✅ تم (باستخدام {chosen_model_name}):")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ فشلت كل المحاولات. الخطأ: {e}")
                # طباعة القائمة للمساعدة في التشخيص
                st.write("الموديلات المتاحة في حسابك هي:")
                try:
                    for m in genai.list_models():
                        st.code(m.name)
                except:
                    st.write("غير قادر على جلب القائمة.")
