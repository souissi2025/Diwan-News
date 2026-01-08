import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. التصميم البصري (نظيف واحترافي)
# ==========================================
st.set_page_config(page_title="Diwan Creative Editor", layout="wide", page_icon="✒️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* صندوق النتيجة الاحترافي */
    .creative-box {
        background-color: #ffffff;
        padding: 35px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); /* ظل ناعم */
        border-right: 6px solid #D95F18; /* اللون البرتقالي المميز */
        font-size: 17px;
        line-height: 2.1;
        color: #2c3e50;
        white-space: pre-wrap;
    }
    
    /* تحسين زر التنفيذ */
    .stButton>button {
        width: 100%; height: 65px; border-radius: 10px;
        font-size: 18px; font-weight: 800; 
        background: linear-gradient(90deg, #0E738A 0%, #095c6e 100%);
        color: white; border: none; transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(14, 115, 138, 0.3);
    }
    
    /* إخفاء العناصر المزعجة */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الاتصال بالمفتاح
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود.")
    st.stop()

# ==========================================
# 3. إعداد الموديل "الفنان" (High Creativity)
# ==========================================
def get_creative_model():
    # نحاول استخدام البرو 1.5 لأنه الأفضل في الصياغة الأدبية
    # إذا لم يعمل، ننتقل للفلاش، ثم القديم
    priorities = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for p in priorities:
            if p in available: return p
        if available: return available[0]
    except: pass
    
    return 'gemini-pro' # الملاذ الأخير

# ==========================================
# 4. البرومبت الذكي (Smart Initiative Prompt)
# ==========================================
# هذا البرومبت يعطي الحرية للموديل ليتصرف بذكاء
CREATIVE_PROMPT = """
أنت "كبير كتاب المحتوى" (Senior Copywriter) في ديوان أف أم.
لديك الحرية الكاملة في إعادة صياغة النص بأسلوبك الخاص.

المطلوب منك ليس مجرد تصحيح، بل "إعادة خلق" للنص (Re-creation):
1. 💡 **المبادرة الذكية:** افهم الفكرة الجوهرية للنص وأعد كتابتها بأسلوب جذاب يشد القارئ/المستمع.
2. 🎨 **التفنن اللغوي:** استخدم مفردات غنية، تعبيرات قوية، وابتعد عن الركاكة.
3. 🔗 **التماسك:** اربط الأفكار بسلاسة بحيث تكون قصة متكاملة وليست جملاً متقاطعة.
4. 🎙️ **الروح:** اجعل للنص "شخصية" (Character) واضحة، تناسب خبراً إذاعياً مهماً.

ملاحظة: لا تضع مقدمات (مثل: إليك النص).. ابدأ بالإبداع فوراً.
"""

# ==========================================
# 5. الواجهة (تقسيم الشاشة)
# ==========================================
st.title("✒️ Diwan Smart Editor")
st.caption("نسخة الإبداع والمبادرة الذكية (High Creativity Mode)")

col_in, col_out = st.columns([1, 1.2]) # العمود الأيسر (النتيجة) أعرض قليلاً

with col_in:
    st.markdown("### 📝 النص الأصلي")
    input_text = st.text_area("مساحة الكتابة:", height=450, placeholder="ضع الأفكار أو النص هنا واترك الباقي عليّ...")
    
    # مسافة
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("✨ إبداع وتطوير النص"):
        if input_text:
            st.session_state.do_process = True
        else:
            st.toast("اكتب شيئاً أولاً!", icon="✍️")

with col_out:
    st.markdown("### 💎 النص المطور")
    
    if st.session_state.get('do_process') and input_text:
        with st.spinner('جاري التفنن في الصياغة...'):
            try:
                # 1. إعداد الموديل
                model_name = get_creative_model()
                
                # إعدادات الحرارة 0.9 = قمة الإبداع
                config = {"temperature": 0.9, "top_p": 1, "max_output_tokens": 2048}
                model = genai.GenerativeModel(model_name, generation_config=config)
                
                # 2. التوليد
                response = model.generate_content(f"{CREATIVE_PROMPT}\n\nالنص الأصلي:\n{input_text}")
                
                # 3. عرض النتيجة (مرة واحدة فقط وبشكل جميل)
                st.markdown(f'<div class="creative-box">{response.text}</div>', unsafe_allow_html=True)
                
                # تنظيف الحالة لمنع التكرار عند التحديث
                # st.session_state.do_process = False 
                
            except Exception as e:
                st.error("حدث خطأ تقني. حاول تقليل النص قليلاً.")
                st.caption(f"Error details: {e}")
