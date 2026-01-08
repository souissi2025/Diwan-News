import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(page_title="Diwan Smart Editor", layout="wide", page_icon="🎙️")

# ==========================================
# 2. التصميم (Teal UI)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    .stApp { background-color: #008CA0; font-family: 'Cairo', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* الهيدر */
    .header-container {
        display: flex; justify-content: center; align-items: center;
        margin-bottom: 30px; padding-top: 10px;
    }
    .logo-box {
        background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px);
        padding: 10px 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2);
        color: white; display: flex; align-items: center; gap: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .logo-text-main { font-size: 30px; font-weight: 800; }
    .logo-text-sub { font-size: 13px; opacity: 0.9; letter-spacing: 1px; }
    .orange-box {
        background-color: #D95F18; color: white; font-weight: bold;
        padding: 5px 15px; border-radius: 8px; font-size: 24px;
    }

    /* الأزرار */
    div.stButton > button {
        width: 100%; height: 100px; border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.2);
        font-family: 'Cairo', sans-serif; font-size: 15px; font-weight: 700;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 8px;
        padding: 10px;
    }
    div.stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.1); color: white; backdrop-filter: blur(5px);
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.25); transform: translateY(-5px);
    }
    div.stButton > button[kind="primary"] {
        background-color: #ffffff !important; color: #D95F18 !important;
        border: none; box-shadow: 0 10px 25px rgba(0,0,0,0.2); transform: scale(1.05);
    }
    div.stButton > button p { font-size: 24px; margin-bottom: 5px; }

    /* المدخلات والمخرجات */
    .input-card {
        background-color: white; border-radius: 20px; padding: 25px;
        margin-top: 20px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .section-label {
        color: #888; font-size: 12px; font-weight: 800;
        margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;
    }
    .result-card {
        background-color: #f0f4f9; border-radius: 20px; padding: 35px; margin-top: 20px;
        font-size: 18px; line-height: 2.2; color: #1f1f1f; white-space: pre-wrap;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.02); border: 1px solid #e0e0e0;
        font-family: 'Cairo', sans-serif;
    }
    
    .stTextArea textarea {
        background-color: #f8f9fa; border: 1px solid #e0e0e0;
        border-radius: 12px; padding: 15px; font-size: 16px; color: #333;
    }
    .stTextArea textarea:focus { border-color: #D95F18; outline: none; }
    [data-testid="column"] { padding: 0 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. دالة الاستكشاف التلقائي للموديل
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود.")

def get_working_model():
    """
    تكتشف الموديل المتاح تلقائياً لتجنب أخطاء 404
    """
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # الترتيب: فلاش -> برو
        for m in available_models:
            if 'gemini-1.5-flash' in m: return m
        
        for m in available_models:
            if 'gemini-1.5-pro' in m: return m
            
        if available_models:
            return available_models[0]
            
    except Exception:
        return 'models/gemini-1.5-flash'

    return 'models/gemini-1.5-flash'

# ==========================================
# 4. الهيدر والأزرار
# ==========================================
st.markdown("""
<div class="header-container">
    <div class="logo-box">
        <div class="orange-box">D</div>
        <div>
            <div class="logo-text-main">ديوان أف أم</div>
            <div class="logo-text-sub">SMART NEWSROOM EDITOR</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'article'
def set_page(p): st.session_state.page = p

buttons_data = [
    {"id": "event", "label": "حدث في مثل\nهذا اليوم", "icon": "📅"},
    {"id": "quotes", "label": "أهم التصريحات", "icon": "💬"},
    {"id": "flash", "label": "موجز إذاعي", "icon": "📻"},
    {"id": "audio", "label": "من صوت لنص", "icon": "🎙️"},
    {"id": "titles", "label": "صانع العناوين", "icon": "T"},
    {"id": "article", "label": "صياغة المقال", "icon": "📄"},
]

cols = st.columns(len(buttons
