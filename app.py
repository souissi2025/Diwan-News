import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة والتصميم (CSS) ---
st.set_page_config(page_title="Diwan Editor Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم البطاقة للنتائج */
    .result-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-right: 6px solid #0E738A;
        margin-top: 25px;
        font-size: 16px;
        line-height: 1.9;
        color: #2c3e50;
        white-space: pre-wrap; /* يمنع قص النص */
    }
    
    .stButton>button {
        width: 100%; height: 60px; border-radius: 8px;
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
    st.error("⚠️ المفتاح مفقود من Settings.")
    st.stop()

# --- 3. البرومبت الصحفي ---
MY_PROMPT = """
أنت رئيس تحرير في "إذاعة ديوان أف أم".
المهمة: أعد صياغة النص التالي ليكون مادة صحفية احترافية.

القواعد:
1. صياغة قوية، إبداعية، وسلسة.
2. تجنب الحشو والتكرار.
3. حذف الألقاب والعبارات الإنشائية.
4. تقسيم النص لفقرات مريحة للقراءة.
"""

# --- 4. إعدادات الحرارة (الإبداع) ---
config = {
    "temperature": 0.85, # رفعنا النسبة لزيادة الإبداع
    "top_p": 0.95,
    "max_output_tokens": 2048,
}

# --- 5. الواجهة ---
st.title("🎙️ Diwan Smart Editor")
st.caption("Creative Mode (Temp: 0.85)")

c1, c2 = st.columns([3, 1])

with c1:
    input_text = st.text_area("النص الخام:", height=180, placeholder="أدخل النص هنا...")
    
    if st.button("🚀 صياغة إبداعية", type="primary"):
        if input_text:
            with st.spinner('جاري التحرير...'):
                try:
                    # محاولة الموديل الحديث (Flash)
                    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=config)
                    response = model.generate_content(f"{MY_PROMPT}\n\nالنص:\n{input_text}")
                    st.markdown(f'<div class="result-box">{response.text}</div>', unsafe_allow_html=True)
                
                except Exception as e1:
                    # فشل الحديث؟ ننتقل للقديم (Pro) تلقائياً
                    try:
                        model_old = genai.GenerativeModel('gemini-pro', generation_config=config)
                        response = model_old.generate_content(f"{MY_PROMPT}\n\nالنص:\n{input_text}")
                        st.markdown(f'<div class="result-box">{response.text}</div>', unsafe_allow_html=True)
                    except Exception as e2:
                        st.error(f"فشلت كل المحاولات. تأكد من تحديث المكتبة. الخطأ: {e1}")

with c2:
    st.info("💡 **الإعدادات:**\nتم رفع درجة الإبداع لضمان صياغة غير تقليدية.\nتم تحسين التصميم لعرض النص كاملاً.")
