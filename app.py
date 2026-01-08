import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. إعداد الصفحة (Google Studio Style)
# ==========================================
st.set_page_config(page_title="Diwan AI Studio", layout="wide", page_icon="✨")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* محاكاة تصميم النتيجة في جوجل ستوديو */
    .studio-result {
        background-color: #f0f4f9; /* لون خلفية جوجل */
        padding: 35px;
        border-radius: 12px;
        border: none;
        font-size: 17px;
        line-height: 2;
        color: #1f1f1f;
        white-space: pre-wrap;
    }
    
    .stButton>button {
        width: 100%; height: 60px; font-weight: bold; font-size: 16px;
        background-color: #0b57d0; /* أزرق جوجل */
        color: white; border: none; border-radius: 25px; /* حواف دائرية */
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #0842a0; box-shadow: 0 4px 12px rgba(11, 87, 208, 0.3); }
    
    /* عناوين */
    h1, h2, h3 { color: #1f1f1f; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الاتصال
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود.")
    st.stop()

# ==========================================
# 3. إعداد الموديل "العبقري" (Pro 1.5 Only)
# ==========================================
def get_studio_model():
    # نبحث تحديداً عن موديلات Pro لأنها المسؤولة عن الصياغة الذكية
    # الفلاش Flash سريع لكنه "سطحي"، البرو Pro "عميق"
    target_models = ['models/gemini-1.5-pro', 'models/gemini-1.5-pro-latest', 'models/gemini-pro']
    
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for t in target_models:
            if t in available: return t
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. البرومبت "المفتوح" (بدون قيود خانقة)
# ==========================================
# هذا البرومبت يمنحه الحرية التي يجدها في جوجل ستوديو
STUDIO_PROMPT = """
أنت كاتب صحفي مبدع ومحترف من الطراز الرفيع.
لديك نص خام، والمطلوب منك إعادة صياغته ليصبح **مقالاً استثنائياً** لموقع "ديوان أف أم".

أريدك أن تستخدم ذكاءك في:
1. **المبادرة:** لا تترجم حرفياً، بل افهم المعنى وأعد صياغته بأسلوبك القوي.
2. **الربط:** اربط الأحداث ببعضها لتصنع قصة متماسكة.
3. **اللغة:** استخدم مفردات غنية، عميقة، ومؤثرة (ابتعد عن السطحية).
4. **العنوان:** ضع عنواناً ذكياً جداً في البداية.

النص ليس مجرد كلمات، بل هو "قضية". اكتبه بروح المسؤولية والاحترافية.
"""

# ==========================================
# 5. الواجهة
# ==========================================
st.title("✨ Diwan AI Studio")
st.caption("نسخة مطابقة لجودة Google AI Studio (Gemini 1.5 Pro)")

col_input, col_output = st.columns([1, 1.2])

with col_input:
    st.markdown("### 📄 النص الأصلي")
    input_text = st.text_area("مساحة العمل:", height=500, placeholder="ضع النص هنا واتركه يبدع...")
    
    if st.button("✨ تشغيل (Generate)"):
        if input_text:
            st.session_state.run_studio = True
        else:
            st.warning("الرجاء إدخال نص.")

with col_output:
    st.markdown("### 💎 النتيجة")
    
    if st.session_state.get('run_studio') and input_text:
        with st.spinner('جاري المعالجة بموديل Pro 1.5 (High Creativity)...'):
            try:
                # 1. الموديل: نستخدم Pro حصراً
                model_name = get_studio_model()
                
                # 2. الإعدادات: نفس إعدادات Google Studio الافتراضية
                # Temperature 0.9 = إبداع عالي ومبادرة
                studio_config = {
                    "temperature": 0.9,
                    "top_p": 1.0,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                
                model = genai.GenerativeModel(model_name, generation_config=studio_config)
                
                # 3. التوليد
                response = model.generate_content(f"{STUDIO_PROMPT}\n\nالنص الأصلي:\n{input_text}")
                
                # 4. العرض بتصميم ستوديو
                st.markdown(f'<div class="studio-result">{response.text}</div>', unsafe_allow_html=True)
                
                # إظهار الموديل المستخدم للتأكد
                st.caption(f"⚡ Model: {model_name} | Temp: 0.9")
                
            except Exception as e:
                st.error("حدث خطأ في الاتصال.")
                st.write(e)
