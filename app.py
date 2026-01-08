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
    /* استيراد خط كايرو */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    
    /* 1. الخلفية العامة (Teal Background) */
    .stApp {
        background-color: #008CA0; /* لون الخلفية الفيروزي */
        font-family: 'Cairo', sans-serif;
    }
    
    /* إخفاء القوائم العلوية */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* 2. تصميم الهيدر (الشعار) */
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
        padding-top: 20px;
    }
    .logo-box {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 10px 40px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
        color: white;
        display: flex;
        align-items: center;
        gap: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .logo-text-main { font-size: 30px; font-weight: 800; }
    .logo-text-sub { font-size: 13px; opacity: 0.9; letter-spacing: 1px; }
    .orange-box {
        background-color: #D95F18;
        color: white;
        font-weight: bold;
        padding: 5px 15px;
        border-radius: 8px;
        font-size: 24px;
    }

    /* 3. تصميم الأزرار (Navigation) */
    div.stButton > button {
        width: 100%;
        height: 110px; /* زيادة الطول قليلاً ليناسب النص */
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        font-family: 'Cairo', sans-serif;
        font-size: 15px; /* حجم خط مناسب */
        font-weight: 700;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 8px;
        line-height: 1.2;
        padding: 10px;
    }

    /* الحالة العادية (غير نشط): شفاف */
    div.stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        backdrop-filter: blur(5px);
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.25);
    }

    /* الحالة النشطة (Active): أبيض ونص برتقالي */
    div.stButton > button[kind="primary"] {
        background-color: #ffffff !important;
        color: #D95F18 !important;
        border: none;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        transform: translateY(-5px);
    }
    
    /* تكبير الأيقونات */
    div.stButton > button p {
        font-size: 26px; 
        margin-bottom: 5px;
    }

    /* 4. صندوق المحتوى (Input Card) */
    .input-card {
        background-color: white;
        border-radius: 25px;
        padding: 30px;
        margin-top: 30px;
        min-height: 450px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    .input-label {
        color: #888;
        font-size: 13px;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: right;
        letter-spacing: 0.5px;
    }
    
    /* تحسين منطقة النص */
    .stTextArea textarea {
        background-color: #f7f9fc;
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 20px;
        font-size: 16px;
        color: #333;
    }
    .stTextArea textarea:focus {
        border-color: #D95F18;
        box-shadow: 0 0 0 1px #D95F18;
    }
    
    /* ضبط المسافات بين الأعمدة */
    [data-testid="column"] { padding: 0 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. الهيدر (الشعار)
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

# ==========================================
# 4. منطق التنقل والأزرار
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'article' # الافتراضي

def set_page(page_name):
    st.session_state.page = page_name

# تعريف الأزرار بالتسميات الحرفية من الصورة
# الترتيب في القائمة: من اليسار إلى اليمين (حسب ظهورها في الشاشة)
buttons_data = [
    {"id": "event", "label": "حدث في مثل\nهذا اليوم", "icon": "📅"},
    {"id": "quotes", "label": "أهم التصريحات", "icon": "💬"},
    {"id": "flash", "label": "موجز إذاعي", "icon": "📻"},
    {"id": "audio", "label": "من صوت لنص", "icon": "🎙️"},
    {"id": "titles", "label": "صانع العناوين", "icon": "T"},
    {"id": "web", "label": "تحرير الويب", "icon": "✨"},
    {"id": "article", "label": "صياغة المقال", "icon": "📄"},
]

# رسم الأزرار
cols = st.columns(len(buttons_data))

for i, btn in enumerate(buttons_data):
    with cols[i]:
        is_active = (st.session_state.page == btn['id'])
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(f"{btn['icon']}\n{btn['label']}", key=btn['id'], type=btn_type, use_container_width=True):
            set_page(btn['id'])
            st.rerun()

# ==========================================
# 5. منطق المعالجة (Gemini)
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    pass # سيتم التعامل مع الخطأ عند التنفيذ

# البرومبتات المخصصة لكل زر (مع الالتزام بالمعايير التونسية)
TUNISIAN_RULES = """
قواعد التحرير التونسية:
1. استخدم الأشهر التونسية (جانفي، فيفري...).
2. احذف الألقاب (السيد/السيدة).
3. حول العملات للدينار التونسي.
4. ابدأ بـ (تونس - ديوان أف أم).
"""

prompts = {
    "article": f"أنت صحفي. أعد صياغة النص ليكون خبراً رئيسياً متكاملاً.\n{TUNISIAN_RULES}",
    "web": f"أنت محرر ويب. أعد صياغة النص لموقع إلكتروني (SEO) مع عنوان جذاب وفقرات قصيرة.\n{TUNISIAN_RULES}",
    "titles": f"اقترح 5 عناوين احترافية متنوعة (رسمي، فيسبوك، تساؤلي).\n{TUNISIAN_RULES}",
    "flash": f"لخص النص في موجز إخباري سريع لا يتجاوز 50 كلمة.\n{TUNISIAN_RULES}",
    "quotes": f"استخرج أهم التصريحات الواردة في النص على لسان أصحابها.\n{TUNISIAN_RULES}",
    "event": f"ابحث في السياق التاريخي: ماذا حدث في مثل هذا اليوم مرتبطاً بموضوع النص أو التاريخ المذكور؟",
    "audio": f"قم بتحسين النص المفرغ صوتياً (تصحيح الأخطاء وتحويله لنص مقروء).\n{TUNISIAN_RULES}"
}

curr_mode = st.session_state.page
curr_prompt = prompts.get(curr_mode, "")
curr_label = next((b['label'].replace('\n', ' ') for b in buttons_data if b['id'] == curr_mode), "")

# ==========================================
# 6. منطقة العمل (Input Card)
# ==========================================
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown(f'<div class="input-label">📎 المصدر (INPUT DATA) - {curr_label}</div>', unsafe_allow_html=True)

with st.container():
    # مربع النص
    input_text = st.text_area("input_area", height=200, label_visibility="collapsed", placeholder="أدخل النص أو رؤوس الأقلام هنا...")
    
    # فاصل وزر التنفيذ
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4])
    with c1:
        run_btn = st.button("🚀 معالجة فورية", type="primary", key="run_main")

    # عرض النتائج
    if run_btn and input_text:
        st.markdown("---")
        with st.spinner('جاري المعالجة الذكية...'):
            try:
                # استخدام Gemini Pro 1.5 أو المتوفر
                model = genai.GenerativeModel('gemini-pro') 
                response = model.generate_content(f"{curr_prompt}\n\nالنص الخام:\n{input_text}")
                
                # عرض النتيجة بتنسيق نظيف
                st.markdown(f"""
                <div style="font-size:18px; line-height:2.2; color:#333; white-space: pre-wrap;">
                {response.text}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error("حدث خطأ في الاتصال، يرجى المحاولة مجدداً.")

st.markdown('</div>', unsafe_allow_html=True)
