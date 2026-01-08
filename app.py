import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(page_title="Diwan Smart Editor", layout="wide", page_icon="🎙️")

# ==========================================
# 2. التصميم المطابق للصورة (CSS High-End)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    
    /* الخلفية الفيروزية */
    .stApp {
        background-color: #008CA0;
        font-family: 'Cairo', sans-serif;
    }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* الهيدر */
    .header-container {
        display: flex; justify-content: center; align-items: center;
        margin-bottom: 30px; padding-top: 20px;
    }
    .logo-box {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 10px 40px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
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
        width: 100%; height: 110px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        font-family: 'Cairo', sans-serif; font-size: 15px; font-weight: 700;
        transition: all 0.3s ease; display: flex; flex-direction: column;
        justify-content: center; align-items: center; gap: 8px;
        line-height: 1.2; padding: 10px;
    }

    /* زر غير نشط */
    div.stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.1); color: white;
        backdrop-filter: blur(5px);
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.25);
    }

    /* زر نشط */
    div.stButton > button[kind="primary"] {
        background-color: #ffffff !important; color: #D95F18 !important;
        border: none; box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        transform: translateY(-5px);
    }
    
    div.stButton > button p { font-size: 26px; margin-bottom: 5px; }

    /* كارد الإدخال */
    .input-card {
        background-color: white; border-radius: 25px;
        padding: 30px; margin-top: 30px; min-height: 450px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    .input-label {
        color: #888; font-size: 13px; font-weight: bold;
        margin-bottom: 15px; text-align: right;
    }
    
    /* النتيجة */
    .result-text {
        font-size: 18px; line-height: 2.2; color: #333;
        white-space: pre-wrap; margin-top: 20px;
        border-top: 1px solid #eee; padding-top: 20px;
    }

    .stTextArea textarea {
        background-color: #f7f9fc; border: 1px solid #eee;
        border-radius: 12px; padding: 20px; font-size: 16px; color: #333;
    }
    [data-testid="column"] { padding: 0 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. دالة الاتصال الذكي (الحل الجذري للخطأ)
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("المفتاح مفقود.")

def get_best_model():
    """تبحث عن أفضل موديل متاح لتجنب أخطاء الاتصال"""
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # ترتيب الأفضلية: 1.5 Pro (العبقري) -> 1.5 Flash (السريع) -> Pro (القديم)
        priority = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for p in priority:
            if p in available: return p
        if available: return available[0]
    except: pass
    return 'gemini-pro' # احتياطي أخير

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
    {"id": "web", "label": "تحرير الويب", "icon": "✨"},
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
# 5. القواعد التونسية والبرومبت
# ==========================================
TUNISIAN_RULES = """
🛑 قواعد إلزامية (Tunisian Style):
1. التقويم: استخدم الأشهر التونسية (جانفي، فيفري، مارس...).
2. الأسماء: حذف الألقاب (السيد/السيدة).
3. العملة: ذكر المقابل بالدينار التونسي.
4. التوقيع: ابدأ بـ (تونس - ديوان أف أم).
5. الأسلوب: موضوعي، هرم مقلوب، لغة قوية.
"""

prompts = {
    "article": f"المهمة: صياغة خبر إذاعي رئيسي متكامل.\n{TUNISIAN_RULES}",
    "web": f"المهمة: مقال للموقع الإلكتروني (SEO) بعنوان جذاب وفقرات قصيرة.\n{TUNISIAN_RULES}",
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
# 6. منطقة العمل (التنفيذ الآمن)
# ==========================================
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown(f'<div class="input-label">📎 المصدر (INPUT DATA) - {curr_label}</div>', unsafe_allow_html=True)

with st.container():
    input_text = st.text_area("input", height=200, label_visibility="collapsed", placeholder="أدخل النص هنا...")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 معالجة فورية", type="primary", key="go"):
        if input_text:
            # مكان عرض النتيجة
            res_box = st.empty()
            
            try:
                # 1. اختيار الموديل الآمن (لتفادي الخطأ)
                model_name = get_best_model()
                
                # 2. إعدادات (Streaming + Heat)
                # حرارة 0.7 توازن بين الإبداع والقواعد
                cfg = {"temperature": 0.7, "max_output_tokens": 8192}
                model = genai.GenerativeModel(model_name, generation_config=cfg)
                
                # 3. التنفيذ بالبث المباشر (لمنع الانقطاع)
                response = model.generate_content(
                    f"{curr_prompt}\n\nالنص الخام:\n{input_text}", 
                    stream=True
                )
                
                # 4. التجميع والعرض
                full_text = ""
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        res_box.markdown(f'<div class="result-text">{full_text}</div>', unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"حدث خطأ تقني: {e}")
                st.caption("تأكد من تحديث requirements.txt إذا استمر الخطأ.")

st.markdown('</div>', unsafe_allow_html=True)
