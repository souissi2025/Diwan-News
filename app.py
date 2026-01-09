import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(page_title="Diwan Smart Editor", layout="wide", page_icon="🎙️")

# ==========================================
# 2. التصميم
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    .stApp {
        background-color: #008CA0;
        font-family: 'Cairo', sans-serif;
    }
    
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}

    .header-container {
        display: flex; justify-content: center; align-items: center;
        margin-bottom: 30px; padding-top: 10px;
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

    div.stButton > button {
        width: 100%; height: 100px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.2);
        font-family: 'Cairo', sans-serif; font-size: 15px; font-weight: 700;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        display: flex; flex-direction: column;
        justify-content: center; align-items: center; gap: 8px;
        padding: 10px;
    }

    div.stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.1); color: white;
        backdrop-filter: blur(5px);
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-5px);
    }

    div.stButton > button[kind="primary"] {
        background-color: #ffffff !important; color: #D95F18 !important;
        border: none; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        transform: scale(1.05);
    }
    div.stButton > button p { font-size: 24px; margin-bottom: 5px; }

    .input-card {
        background-color: white; border-radius: 20px;
        padding: 25px; margin-top: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .section-label {
        color: #888; font-size: 12px; font-weight: 800;
        margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;
    }
    
    .result-card {
        background-color: #f0f4f9;
        border-radius: 20px;
        padding: 35px;
        margin-top: 20px;
        font-size: 18px; line-height: 2.2; color: #1f1f1f;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.02);
        border: 1px solid #e0e0e0;
        font-family: 'Cairo', sans-serif;
    }

    @keyframes pulse-orange {
        0% { box-shadow: 0 0 0 0 rgba(217, 95, 24, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(217, 95, 24, 0); }
        100% { box-shadow: 0 0 0 0 rgba(217, 95, 24, 0); }
    }
    
    .stButton button:active {
        animation: pulse-orange 1s;
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
# 3. الاتصال والموديل
# ==========================================

def setup_api():
    """إعداد API مع معالجة أفضل للأخطاء"""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        elif "GEMINI_API_KEY" in os.environ:
            api_key = os.environ["GEMINI_API_KEY"]
        else:
            st.error("⚠️ لم يتم العثور على مفتاح API. يرجى إضافته في ملف secrets.toml")
            st.stop()
        
        if not api_key or not api_key.startswith("AIza"):
            st.error("⚠️ مفتاح API غير صحيح. يجب أن يبدأ بـ AIza")
            st.stop()
        
        genai.configure(api_key=api_key)
        return True
        
    except Exception as e:
        st.error(f"❌ خطأ في إعداد API: {str(e)}")
        st.stop()
        return False

api_ready = setup_api()

def get_best_model():
    """الحصول على أفضل موديل متاح"""
    try:
        priority_models = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro', 
            'models/gemini-pro'
        ]
        
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except Exception:
            return 'models/gemini-1.5-flash'
        
        for priority in priority_models:
            if priority in available_models:
                return priority
        
        if available_models:
            return available_models[0]
        else:
            return 'models/gemini-1.5-flash'
            
    except Exception:
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

if 'page' not in st.session_state: 
    st.session_state.page = 'article'

def set_page(p): 
    st.session_state.page = p

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
        if st.button(f"{btn['icon']}\n{btn['label']}", key=btn['id'], 
                     type="primary" if active else "secondary", use_container_width=True):
            set_page(btn['id'])
            st.rerun()

# ==========================================
# 5. القواعد والبرومبت
# ==========================================

TUNISIAN_RULES = """
قواعد إلزامية (Tunisian Style):
1. التقويم: استخدم الأشهر التونسية (جانفي، فيفري، مارس، أفريل، ماي، جوان، جويلية، أوت، سبتمبر، أكتوبر، نوفمبر، ديسمبر).
2. الأسماء: حذف الألقاب (السيد/السيدة/المحترم) والاكتفاء بالصفة والاسم فقط.
3. العملة: ذكر المقابل بالدينار التونسي عند ورود مبالغ مالية.
4. التوقيع: ابدأ المقال بـ (تونس - ديوان أف أم).
5. الأسلوب: موضوعي، هرم مقلوب، لغة قوية وسلسة.
"""

ARTICLE_PROMPT = """
أنت محرر صحفي محترف في وكالة أنباء متخصصة، تمتلك خبرة عميقة في صياغة الأخبار وفق أعلى المعايير المهنية.

المهمة الرئيسية:
تحويل البلاغ/البيان المرفق إلى مقال إخباري احترافي متكامل يعكس جميع المعطيات الواردة بدقة ومهنية عالية، مع أسلوب سلس وجذاب.

معايير الصياغة الإلزامية:

1. البنية - الهرم المقلوب الصارم:
   - المقدمة (25-35 كلمة): تلخيص الخبر كاملاً - من؟ ماذا؟ متى؟ أين؟ لماذا؟ كيف؟
   - الفقرة الثانية: توضيح الحدث الرئيسي بتفاصيل إضافية
   - الفقرات التالية: التفاصيل الثانوية مرتبة تنازلياً حسب الأهمية
   - الخاتمة: معلومات سياقية أو خلفية إضافية (إن وُجدت في البلاغ)

2. الأسلوب اللغوي - أسلوب وكالات الأنباء:
   - لغة عربية فصحى واضحة ومباشرة - لا حشو ولا تكرار
   - جمل قصيرة ومتوسطة (12-18 كلمة للجملة)
   - فعل + فاعل + مفعول (ترتيب طبيعي وسلس)
   - تجنب الصفات المبالغة والتعابير الإنشائية
   - استخدام أفعال قوية ومحددة (أعلن، أكد، كشف، أشار، أوضح)
   - سلاسة في الانتقال بين الأفكار باستخدام روابط لغوية طبيعية

3. الموضوعية والحياد التام:
   - نقل الوقائع كما وردت دون إضافة أو حذف
   - عدم إبداء رأي أو استنتاج شخصي
   - تجنب الكلمات العاطفية أو المشحونة إلا إن وردت بنص البلاغ
   - نسبة التصريحات لأصحابها بدقة

4. الدقة الصحفية:
   - الالتزام الحرفي بكل الأرقام والتواريخ والأسماء
   - استخدام الألقاب والصفات كما وردت في البلاغ
   - التحقق من اتساق المعلومات داخل النص
   - عدم افتراض أي معلومة غير مذكورة

5. القواعد التونسية الخاصة (ديوان أف أم):
   - الأشهر: جانفي، فيفري، مارس، أفريل، ماي، جوان، جويلية، أوت، سبتمبر، أكتوبر، نوفمبر، ديسمبر
   - حذف ألقاب المجاملة (السيد/السيدة/المحترم) - فقط الصفة + الاسم
   - تحويل العملات الأجنبية للدينار التونسي (إن وُرد المبلغ)
   - التوقيع: بدء المقال بـ "تونس - ديوان أف أم"

6. التنسيق والشكل:
   - نص متصل واحد بدون عناوين فرعية
   - فقرات واضحة (كل فقرة فكرة واحدة - 3-5 جمل)
   - سطر فاصل بين الفقرات
   - عدم استخدام النقاط أو الترقيم العددي

المخرجات المطلوبة بالترتيب:

أولاً: العناوين المقترحة (3-5 عناوين)
قدّم 3 إلى 5 عناوين بديلة، كل عنوان:
   - مختصر (6-10 كلمات كحد أقصى)
   - يعكس جوهر الخبر بدقة
   - متنوع في الصياغة (مباشر، سؤالي، تشويقي)
   - بدون علامات تعجب أو استفهام إلا للضرورة
   
تنسيق العناوين:
العنوان 1: [النص]
العنوان 2: [النص]
العنوان 3: [النص]

ثانياً: المقال الصحفي الكامل
- ابدأ بـ "تونس - ديوان أف أم"
- نص متصل في فقرات متماسكة
- التزام صارم بكل المعايير أعلاه
- طول مناسب (200-400 كلمة حسب حجم البلاغ)

محظورات صارمة:
- إضافة معلومات خارج البلاغ
- الاستنتاج أو التفسير الشخصي
- استخدام عناوين فرعية داخل المقال
- الأسلوب الأدبي أو الإنشائي المبالغ
- الجمل الطويلة المعقدة (أكثر من 25 كلمة)
- التكرار أو الحشو اللغوي

الآن، ابدأ بتحويل البلاغ التالي إلى مقال صحفي احترافي:
"""

prompts = {
    "article": ARTICLE_PROMPT,
    "titles": f"المهمة: اقتراح 5 عناوين احترافية متنوعة.\n{TUNISIAN_RULES}",
    "flash": f"المهمة: موجز إخباري سريع ومكثف (أقل من 50 كلمة).\n{TUNISIAN_RULES}",
    "quotes": f"المهمة: استخراج وتنسيق أهم التصريحات.\n{TUNISIAN_RULES}",
    "event": f"المهمة: البحث عن السياق التاريخي لهذا الحدث.\n{TUNISIAN_RULES}",
    "audio": f"المهمة: تحرير النص المفرغ صوتياً ليصبح مقروءاً.\n{TUNISIAN_RULES}"
}

curr_mode = st.session_state.page
curr_prompt = prompts.get(curr_mode, prompts["article"])
curr_label = next((b['label'].replace('\n', ' ') for b in buttons_data if b['id'] == curr_mode), "صياغة المقال")

# ==========================================
# 6. منطقة العمل
# ==========================================

st.markdown(f'<div class="input-card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-label">📌 النص الخام (INPUT) - {curr_label}</div>', unsafe_allow_html=True)
input_text = st.text_area("input", height=200, label_visibility="collapsed", 
                           placeholder="أدخل النص هنا...")
st.markdown('</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1]) 
with c2:
    process_btn = st.button("✨ معالجة فورية ✨", type="primary", use_container_width=True)

if process_btn and input_text:
    
    with st.spinner('⏳ جاري تحليل النص وصياغته بذكاء...'):
        try:
            model_name = get_best_model()
            
            cfg = {
                "temperature": 0.7,
                "max_output_tokens": 8192,
                "top_p": 0.95,
                "top_k": 40
            }
            
            model = genai.GenerativeModel(model_name, generation_config=cfg)
            
            full_prompt = f"{curr_prompt}\n\nالنص الخام:\n{input_text}"
            
            st.markdown(f'<div class="section-label" style="margin-top:30px; color:white;">💎 النتيجة النهائية</div>', 
                       unsafe_allow_html=True)
            res_placeholder = st.empty()
            
            full_text = ""
            
            try:
                response = model.generate_content(full_prompt, stream=True)
                
                for chunk in response:
                    if hasattr(chunk, 'text') and chunk.text:
                        full_text += chunk.text
                        res_placeholder.markdown(
                            f'<div class="result-card">{full_text}</div>', 
                            unsafe_allow_html=True
                        )
                        
            except Exception:
                response = model.generate_content(full_prompt, stream=False)
                
                if response and hasattr(response, 'text'):
                    full_text = response.text
                    res_placeholder.markdown(
                        f'<div class="result-card">{full_text}</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.error("❌ لم يتم الحصول على استجابة من الذكاء الاصطناعي")
                    
        except Exception as e:
            st.error(f"❌ حدث خطأ: {str(e)}")
            
            with st.expander("📋 تفاصيل الخطأ (للمطورين)"):
                st.code(f"""
نوع الخطأ: {type(e).__name__}
الرسالة: {str(e)}
الموديل المستخدم: {model_name if 'model_name' in locals() else 'غير معروف'}
                """)

elif process_btn and not input_text:
    st.warning("⚠️ الرجاء إدخال نص أولاً!")

with st.sidebar:
    st.markdown("### ℹ️ معلومات التطبيق")
    st.info(f"**الموديل المستخدم:** {get_best_model()}")
    st.success("✅ API متصل بنجاح" if api_ready else "❌ خطأ في الاتصال")
    
    st.markdown("---")
    st.markdown("### 📖 كيفية الاستخدام")
    st.markdown("""
    1. اختر نوع المعالجة من الأزرار العلوية
    2. أدخل النص الخام في المربع
    3. اضغط على "معالجة فورية"
    4. انتظر النتيجة
    """)
