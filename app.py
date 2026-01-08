import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة والتصميم (CSS) ---
st.set_page_config(page_title="Diwan Editor Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* صندوق النتيجة الجمالي */
    .result-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-right: 8px solid #0E738A;
        margin-top: 25px;
        font-size: 16px;
        line-height: 1.8;
        color: #2c3e50;
        white-space: pre-wrap;
    }
    
    .stButton>button {
        width: 100%; height: 60px; border-radius: 10px;
        font-weight: bold; background-color: #f8f9fa; border: 1px solid #ddd;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0E738A; color: white; border-color: #0E738A;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بالمفتاح ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود.")
    st.stop()

# --- 3. البرومبت (ضع نصك هنا) ---
# يمكنك تعديل هذا النص بما يناسبك
MY_PROMPT = """
أنت صحفي محترف (Editor-in-Chief) في إذاعة ديوان أف أم.
مهمتك: إعادة صياغة النص الخام التالي ليصبح خبراً إذاعياً احترافياً وجذاباً.

القواعد الصارمة:
1. استخدم لغة عربية فصحى قوية وسلسة (السهل الممتنع).
2. تجنب التكرار والحشو (مثل: تم، قام، الجدير بالذكر).
3. استبدل الألقاب بالصفات الوظيفية.
4. ابدأ بالمعلومة الأهم (Lead).
5. اجعل النص مقسماً لفقرات قصيرة.
"""

# --- 4. إعدادات الموديل (رفع الحرارة) ---
# هنا قمنا برفع الحرارة إلى 0.8 لزيادة الإبداع وجودة الصياغة
generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 2000,
}

# --- 5. الواجهة ---
st.title("🎙️ Diwan Smart Editor")
st.caption("الإصدار الاحترافي (High Creativity Mode)")

col_input, col_help = st.columns([3, 1])

with col_input:
    input_text = st.text_area("النص الخام:", height=180, placeholder="أدخل النص هنا...")
    
    if st.button("🚀 صياغة إبداعية (تنفيذ)", type="primary"):
        if input_text:
            with st.spinner('جاري الصياغة بلمسة إبداعية...'):
                try:
                    # اختيار الموديل مع تطبيق إعدادات الحرارة
                    model = genai.GenerativeModel(
                        model_name='gemini-1.5-flash',
                        generation_config=generation_config
                    )
                    
                    full_prompt = f"{MY_PROMPT}\n\nالنص:\n{input_text}"
                    response = model.generate_content(full_prompt)
                    
                    # عرض النتيجة
                    st.markdown(f'<div class="result-box">{response.text}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    # محاولة احتياطية
                    try:
                        model_old = genai.GenerativeModel('gemini-pro', generation_config=generation_config)
                        response = model_old.generate_content(full_prompt)
                        st.markdown(f'<div class="result-box">{response.text}</div>', unsafe_allow_html=True)
                    except:
                         st.error(f"خطأ تقني: {e}")
        else:
            st.warning("الرجاء كتابة نص أولاً.")

with col_help:
    st.info("🔥 **ملاحظة:**\nتم رفع درجة 'إبداع الموديل' (Temperature) إلى 0.8 للحصول على صياغة أقل جموداً وأكثر احترافية.")
