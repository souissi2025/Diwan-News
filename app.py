import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(page_title="Diwan Smart Editor", layout="wide", page_icon="🎙️")

# ==========================================
# 2. التصميم (Teal UI + Animations)
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
# 3. محرك الذكاء الاصطناعي (Stable Version)
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود.")

def generate_safe_content(prompt, input_text):
    """
    دالة آمنة تستخدم فقط الموديلات المستقرة (Version 1.5)
    وتبتعد عن الموديلات القديمة التي تسبب مشاكل
    """
    # قائمة الموديلات المضمونة فقط
    # 1. Flash: سريع ومجاني
    # 2. Pro: ذكي واحتياطي
    safe_models = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    last_error = None
    
    for model_name in safe_models:
        try:
            # إعداد الموديل
            gen_config = {"temperature": 0.7, "max_output_tokens": 8192}
            model = genai.GenerativeModel(model_name, generation_config=gen_config)
            
            # محاولة التوليد
            response = model.generate_content(f"{prompt}\n\nالنص الخام:\n{input_text}", stream=True)
            return response # نجاح
            
        except Exception as e:
            last_error = e
            time.sleep(1)
            continue
            
    # إذا فشل الاثنان (غالباً بسبب الحظر المؤقت 429)
    raise last_error

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

cols = st.columns(len(buttons_data))
for i, btn in enumerate(buttons_data):
    with cols[i]:
        active = (st.session_state.page == btn['id'])
        if st.button(f"{btn['icon']}\n{btn['label']}", key=btn['id'], type="primary" if active else "secondary", use_container_width=True):
            set_page(btn['id'])
            st.rerun()

# ==========================================
# 5. القواعد والبرومبت
# ==========================================
TUNISIAN_RULES = """
🛑 قواعد إلزامية (Tunisian Style):
1. التقويم: استخدم الأشهر التونسية (جانفي، فيفري...).
2. الأسماء: حذف الألقاب (السيد/السيدة) والاكتفاء بالصفة والاسم.
3. العملة: ذكر المقابل بالدينار التونسي.
4. التوقيع: ابدأ بـ (تونس - ديوان أف أم).
5. الأسلوب: موضوعي، هرم مقلوب، لغة قوية.
"""

prompts = {
    "article": f"المهمة: صياغة خبر إذاعي رئيسي متكامل.\n{TUNISIAN_RULES}",
    "titles": f"المهمة: اقتراح 5 عناوين احترافية متنوعة.\n{TUNISIAN_RULES}",
    "flash": f"المهمة: موجز إخباري سريع ومكثف (أقل من 50 كلمة).\n{TUNISIAN_RULES}",
    "quotes": f"المهمة: استخراج وتنسيق أهم التصريحات.\n{TUNISIAN_RULES}",
    "event": "المهمة: البحث عن السياق التاريخي لهذا الحدث.",
    "audio": f"المهمة: تحرير النص المفرغ صوتياً ليصبح مقروءاً.\n{TUNISIAN_RULES}"
}

curr_mode = st.session_state.page
curr_prompt = prompts.get(curr_mode, "")
curr_label = next((b['label'].replace('\n', ' ') for b in buttons_data if b['id'] == curr_mode), "")

# ==========================================
# 6. منطقة العمل
# ==========================================
st.markdown(f'<div class="input-card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-label">📌 النص الخام (INPUT) - {curr_label}</div>', unsafe_allow_html=True)
input_text = st.text_area("input", height=200, label_visibility="collapsed", placeholder="أدخل النص هنا...")
st.markdown('</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1]) 
with c2:
    process_btn = st.button("✨ معالجة فورية ✨", type="primary", use_container_width=True)

if process_btn and input_text:
    with st.spinner('⏳ جاري الاتصال...'):
        try:
            # استخدام الدالة الآمنة الجديدة
            response_stream = generate_safe_content(curr_prompt, input_text)
            
            st.markdown(f'<div class="section-label" style="margin-top:30px; color:white;">💎 النتيجة النهائية</div>', unsafe_allow_html=True)
            res_placeholder = st.empty()
            
            full_text = ""
            for chunk in response_stream:
                if chunk.text:
                    full_text += chunk.text
                    res_placeholder.markdown(f'<div class="result-card">{full_text}</div>', unsafe_allow_html=True)
                    
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ جميع الموديلات مشغولة (Quota Exceeded). يرجى الانتظار 40 ثانية.")
            elif "404" in str(e):
                st.error("⚠️ خطأ في اسم الموديل، تم استخدام القائمة الآمنة الآن.")
            else:
                st.error(f"حدث خطأ: {e}")

elif process_btn and not input_text:
    st.warning("⚠️ الرجاء إدخال نص أولاً!")
