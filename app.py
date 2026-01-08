import streamlit as st
import google.generativeai as genai
import os

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Diwan Smart Newsroom", layout="wide", page_icon="🎙️")
st.markdown("""
<style>
    .stButton>button {
        width: 100%; height: 70px; border-radius: 10px;
        font-size: 16px; font-weight: bold; background-color: #f0f2f6; color: #31333F;
        border: 1px solid #d6d6d6;
    }
    .stButton>button:hover { background-color: #ffe0b2; border-color: #ff8c00; color: #ff8c00; }
    h1 { color: #0E738A; }
    .stSuccess { background-color: #e8f5e9; border-right: 5px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بالمفتاح ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود (GEMINI_API_KEY).")
    st.stop()

# --- 3. دالة اكتشاف الموديل (Auto-Discovery) ---
def get_best_model():
    """
    هذه الدالة تبحث عن أي موديل متاح في حسابك وتستخدمه.
    تتجاوز خطأ 404 بالبحث عن الاسم الصحيح.
    """
    # قائمة الموديلات المفضلة بالترتيب
    preferred_order = [
        "gemini-1.5-pro",
        "gemini-1.5-flash", 
        "gemini-1.0-pro", 
        "gemini-pro"
    ]
    
    available_models = []
    try:
        # جلب القائمة من جوجل
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # تنظيف الاسم (حذف models/)
                name = m.name.replace('models/', '')
                available_models.append(name)
    except:
        pass

    # اختيار الأفضل
    chosen_model = "gemini-pro" # احتياطي أخير
    
    if available_models:
        # هل يوجد واحد من المفضلين؟
        for p in preferred_order:
            if p in available_models:
                chosen_model = p
                break
        # إذا لم نجد المفضل، نأخذ أول واحد متاح وخلاص
        if chosen_model == "gemini-pro" and available_models:
            chosen_model = available_models[0]
            
    return chosen_model

# --- 4. التعليمات الصحفية ---
SYS_INSTRUCTIONS = """
أنت رئيس تحرير في "إذاعة ديوان أف أم".
القواعد:
1. موضوعية تامة وحذف الآراء الشخصية.
2. أسلوب صحفي (الهرم المقلوب).
3. لغة عربية قوية ومباشرة.
4. حذف الألقاب والعبارات الإنشائية.
"""

PROMPTS = {
    "article": "المهمة: خبر إذاعي رئيسي. ابدأ بمقدمة قوية تجيب عن الأسئلة الخمسة. فقرات قصيرة.",
    "web": "المهمة: مقال ويب (SEO). عنوان جذاب، كلمات مفتاحية في البداية، وخاتمة تفاعلية.",
    "flash": "المهمة: موجز صوتي (Flash). جمل قصيرة جداً للمذيع. لا تتجاوز 40 كلمة.",
    "titles": "المهمة: اقترح 5 عناوين (كلاسيكي، تساؤلي، مثير، اقتباس، فيسبوك).",
    "quotes": "المهمة: استخرج التصريحات المباشرة فقط: [الاسم]: النص.",
    "analysis": "المهمة: تحليل سياسي/اجتماعي. ضع الخبر في سياقه واشرح دلالاته."
}

# --- 5. الواجهة ---
st.title("🎙️ Diwan Smart Newsroom")

if 'mode' not in st.session_state: st.session_state.mode = "article"
def set_mode(m): st.session_state.mode = m

# الأزرار
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📝 خبر إذاعي"): set_mode("article")
    if st.button("🔍 تحليل"): set_mode("analysis")
with c2:
    if st.button("🌐 ويب (SEO)"): set_mode("web")
    if st.button("🏷️ عناوين"): set_mode("titles")
with c3:
    if st.button("⚡ موجز (Flash)"): set_mode("flash")
    if st.button("💬 تصريحات"): set_mode("quotes")

st.markdown("---")
st.subheader(f"📌 {st.session_state.mode}")

# الفورم والتنفيذ
with st.form("news_form"):
    text_input = st.text_area("أدخل النص هنا:", height=200)
    submitted = st.form_submit_button("🚀 تنفيذ")
    
    if submitted and text_input:
        with st.spinner('جاري البحث عن الموديل وتنفيذ الطلب...'):
            try:
                # 1. اكتشاف الموديل
                model_name = get_best_model()
                
                # 2. تجهيز الموديل
                model = genai.GenerativeModel(model_name)
                
                # 3. التنفيذ
                full_prompt = f"{SYS_INSTRUCTIONS}\n\n{PROMPTS[st.session_state.mode]}\n\nالنص:\n{text_input}"
                response = model.generate_content(full_prompt)
                
                # 4. النتيجة
                st.success(f"✅ تم التحرير (الموديل: {model_name})")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ خطأ تقني: {e}")
                st.write("حاول تحديث الصفحة (Reboot App) لتفعيل المكتبة الجديدة.")
