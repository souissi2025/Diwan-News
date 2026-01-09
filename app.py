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
# 3. الاتصال والموديل - مُصحح للـ Free Tier
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
    """
    الحصول على أفضل موديل متاح في Free Tier
    حسب الجدول: Gemini 2.5 Pro (RPM: 2) أو Gemini 2.5 Flash (RPM: 10)
    """
    # الموديلات المتاحة في Free Tier فقط (من الجدول)
    free_tier_models = [
        'models/gemini-2.0-flash',      # RPM: 15, TPM: 1M - الأفضل مجاناً!
        'models/gemini-1.5-flash',      # RPM: 15, TPM: 250K
        'models/gemini-1.5-flash-latest',
        'models/gemini-1.5-pro',        # RPM: محدود جداً
        'models/gemini-1.5-pro-latest',
        'models/gemini-pro'             # احتياطي
    ]
    
    try:
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except Exception:
            return 'models/gemini-2.0-flash'
        
        # اختر أول موديل متاح من القائمة
        for model in free_tier_models:
            if model in available_models:
                return model
        
        # إذا لم يجد شيء، استخدم الافتراضي
        if available_models:
            return available_models[0]
        else:
            return 'models/gemini-2.0-flash'
            
    except Exception:
        return 'models/gemini-2.0-flash'

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
# 5. القواعد والبرومبت - النسخة الإبداعية
# ==========================================

TUNISIAN_RULES = """
المعايير التونسية الأساسية:
- الأشهر: جانفي، فيفري، مارس، أفريل، ماي، جوان، جويلية، أوت، سبتمبر، أكتوبر، نوفمبر، ديسمبر
- الأسماء: حذف ألقاب المجاملة (السيد/السيدة) واستخدام الصفة + الاسم
- العملة: تحويل للدينار التونسي عند الضرورة
- التوقيع: تونس - ديوان أف أم -
"""

ARTICLE_PROMPT = """
أنت صحفي محترف متمرس تجمع بين احترافية وكالات الأنباء العالمية وبراعة الكتاب المبدعين. لديك موهبة فريدة في تحويل البلاغات الجافة إلى مقالات صحفية آسرة تجذب القارئ وتحافظ على الدقة والمصداقية.

مهمتك: صياغة مقال إخباري احترافي وجذاب من البلاغ المرفق

فلسفة الصياغة:

أنت لست آلة نسخ - أنت فنان الكلمة الإخبارية. مهمتك تحويل المعلومات الخام إلى نص يمتع القارئ ويثري معرفته دون الإخلال بالحقائق.

المبادئ الأساسية (بدون قيود خانقة):

1. الدقة قبل كل شيء:
   - احتفظ بكل الحقائق والأرقام والأسماء والتواريخ كما وردت
   - لا تضف معلومات من خارج البلاغ
   - انسب كل معلومة لمصدرها بوضوح

2. الإبداع في التعبير:
   - لك الحرية الكاملة في إعادة صياغة الجمل بطريقة أجمل وأقوى
   - استخدم تنويعاً لغوياً ثرياً (مرادفات، تراكيب مختلفة)
   - اختر الكلمات الأكثر تأثيراً والأفعال الأقوى
   - تجنب الجفاف والرتابة - اجعل النص يتنفس

3. البنية الذكية:
   - ابدأ بأقوى معلومة في الفقرة الأولى (30-40 كلمة)
   - رتب المعلومات بذكاء من الأهم للمهم
   - اجعل كل فقرة تروي جزءاً من القصة
   - استخدم انتقالات سلسة وطبيعية بين الفقرات

4. اللغة الحية:
   - جمل متنوعة الطول (قصيرة للتشويق، متوسطة للشرح)
   - أفعال قوية ومعبرة: أعلن، كشف، أكد، شدد، كشف النقاب، أماط اللثام
   - تجنب الحشو والتكرار لكن لا تخف من الوصف الدقيق
   - اجعل اللغة أنيقة وسلسة دون تعقيد

5. اللمسة الفنية:
   - أضف سياقاً ذكياً يربط المعلومات ببعضها (من داخل البلاغ فقط)
   - استخدم روابط لغوية جميلة: "في هذا السياق"، "من جهة أخرى"، "وفي ذات الإطار"
   - اجعل النص يقرأ كقصة إخبارية متماسكة وليس نقاطاً منفصلة
   - العب بالإيقاع: تنوع في طول الجمل لخلق حيوية في النص

6. الموضوعية الذكية:
   - كن محايداً في نقل الحقائق لكن لا تكن مملاً
   - يمكنك إبراز أهمية الخبر دون مبالغة
   - استخدم اقتباسات مباشرة عندما تكون قوية ومؤثرة
   - الموضوعية لا تعني الجفاف

المعايير التونسية (ديوان أف أم):
- الأشهر التونسية: جانفي، فيفري، مارس، أفريل، ماي، جوان، جويلية، أوت، سبتمبر، أكتوبر، نوفمبر، ديسمبر
- حذف ألقاب المجاملة: استخدم الصفة + الاسم مباشرة
- تحويل العملات للدينار التونسي عند الحاجة
- التوقيع الإلزامي: "تونس - ديوان أف أم -"

التنسيق النهائي:
- نص متصل بدون عناوين فرعية
- فقرات واضحة منفصلة بسطر
- كل فقرة تحمل فكرة متكاملة (3-6 جمل)
- طول مثالي: 300-450 كلمة

المخرجات المطلوبة:

أولاً: 5 عناوين إبداعية

قدم 5 عناوين متنوعة، كل واحد يجذب بطريقة مختلفة:

1. عنوان مباشر قوي (فعل + معلومة رئيسية) - 7-10 كلمات
2. عنوان سؤالي يثير الفضول - 6-9 كلمات
3. عنوان رقمي مع تأثير - 7-10 كلمات
4. عنوان درامي يشد الانتباه - 8-12 كلمة
5. عنوان بتصريح أو اقتباس مباشر - 8-12 كلمة

ثانياً: المقال الكامل

ابدأ بـ: تونس - ديوان أف أم -

ثم اكتب المقال كاملاً بأسلوبك الإبداعي الاحترافي.

نماذج توضيحية:

مثال على أسلوب إبداعي صحيح:
"أعلن وزير الداخلية كمال الفقيه اليوم الجمعة بتونس عن إطلاق منظومة رقمية حديثة من شأنها تبسيط إجراءات استخراج وثائق الهوية وتخفيف العبء عن المواطنين. وكشف الوزير في تصريح صحفي أن هذه المنظومة الذكية ستدخل حيز التطبيق الفعلي مطلع فيفري المقبل في 24 معتمدية كمرحلة تجريبية أولى، قبل تعميمها على كامل التراب التونسي."

مثال على أسلوب ضعيف جاف:
"أعلن وزير الداخلية عن منظومة. المنظومة رقمية. ستبسط الإجراءات. ستدخل حيز التطبيق في فيفري."

ما يجب تجنبه:
- الأسلوب البيروقراطي الجاف
- التكرار الممل
- الجمل كلها بنفس الطول
- غياب الروح والحياة من النص
- المبالغة والتهويل غير المبرر
- إضافة معلومات من خارج البلاغ

حريتك الإبداعية تشمل:
- إعادة ترتيب المعلومات بذكاء
- اختيار أفضل الكلمات والتعابير
- خلق انسيابية وتماسك بين الأفكار
- إضافة سياق يربط المعلومات (من داخل البلاغ)
- استخدام أساليب بلاغية راقية (دون مبالغة)
- التلاعب بإيقاع النص لجعله أكثر حيوية

الآن، أطلق العنان لموهبتك الصحفية وحول البلاغ التالي إلى تحفة إخبارية:
"""

# باقي البرومبتات
prompts = {
    "article": ARTICLE_PROMPT,
    "titles": f"اقترح 5 عناوين إبداعية جذابة واحترافية للخبر التالي.\n{TUNISIAN_RULES}",
    "flash": f"اكتب موجزاً إخبارياً سريعاً وقوياً (40-50 كلمة) يلخص الخبر بأسلوب مشوق.\n{TUNISIAN_RULES}",
    "quotes": f"استخرج أهم التصريحات وقدمها بطريقة جذابة مع السياق.\n{TUNISIAN_RULES}",
    "event": f"ابحث عن السياق التاريخي واكتب فقرة غنية ومشوقة عن هذا الحدث.\n{TUNISIAN_RULES}",
    "audio": f"حول النص الصوتي المفرغ إلى مقال إخباري احترافي وجذاب.\n{TUNISIAN_RULES}"
}

curr_mode = st.session_state.page
curr_prompt = prompts.get(curr_mode, prompts["article"])
curr_label = next((b['label'].replace('\n', ' ') for b in buttons_data if b['id'] == curr_mode), "صياغة المقال")

# ==========================================
# 6. منطقة العمل - مع حماية من تجاوز الحصة
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
    
    with st.spinner('⏳ جاري الصياغة الإبداعية للنص...'):
        try:
            model_name = get_best_model()
            
            # إعدادات محسنة للإبداع
            cfg = {
                "temperature": 0.9,  # أعلى للإبداع
                "max_output_tokens": 4096,  # تقليل لتوفير الحصة
                "top_p": 0.95,
                "top_k": 50
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
                        
            except Exception as stream_error:
                # إذا فشل الـ streaming، استخدم الطريقة العادية
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
            error_msg = str(e)
            
            # معالجة خاصة لأخطاء تجاوز الحصة
            if "429" in error_msg or "quota" in error_msg.lower():
                st.error("⚠️ **تجاوزت الحصة المجانية اليومية!**")
                st.info("""
                **الحلول المتاحة:**
                
                1. **انتظر حتى منتصف الليل بتوقيت المحيط الهادئ** (الحصة تتجدد يومياً)
                
                2. **ترقية للخطة المدفوعة:**
                   - قم بربط بطاقة ائتمان في Google Cloud Console
                   - ستحصل على حدود أعلى بكثير (1000+ طلب/دقيقة)
                   
                3. **استخدم API key جديد** (إنشاء مشروع جديد)
                
                **حدودك الحالية (Free Tier):**
                - Gemini 2.0 Flash: 15 طلب/دقيقة، 200 طلب/يوم
                - Gemini 2.5 Pro: 2 طلب/دقيقة، 50 طلب/يوم
                
                [مراقبة الاستخدام](https://ai.dev/rate-limit) | [تفاصيل الأسعار](https://ai.google.dev/pricing)
                """)
            else:
                st.error(f"❌ حدث خطأ: {error_msg}")
            
            with st.expander("📋 تفاصيل الخطأ (للمطورين)"):
                st.code(f"""
نوع الخطأ: {type(e).__name__}
الرسالة: {error_msg}
الموديل المستخدم: {model_name if 'model_name' in locals() else 'غير معروف'}
                """)

elif process_btn and not input_text:
    st.warning("⚠️ الرجاء إدخال نص أولاً!")

# ==========================================
# 7. معلومات في الـ sidebar
# ==========================================
with st.sidebar:
    st.markdown("### ℹ️ معلومات التطبيق")
    current_model = get_best_model()
    st.info(f"**الموديل المستخدم:**\n{current_model}")
    
    if "2.0-flash" in current_model.lower():
        st.success("✅ أفضل موديل مجاني (15 RPM)")
    elif "flash" in current_model.lower():
        st.success("✅ موديل سريع (10-15 RPM)")
    else:
        st.warning("⚠️ موديل محدود (2 RPM)")
    
    st.success("✅ API متصل بنجاح" if api_ready else "❌ خطأ في الاتصال")
    
    st.markdown("---")
    st.markdown("### ⚡ حدود الاستخدام (Free)")
    st.markdown("""
    **Gemini 2.0 Flash:**
    - 15 طلب/دقيقة
    - 1M توكن/دقيقة
    - 200 طلب/يوم
    
    **Gemini 2.5 Pro:**
    - 2 طلب/دقيقة
    - 125K توكن/دقيقة
    - 50 طلب/يوم
    
    [مراقبة الاستخدام →](https://aistudio.google.com/apikey)
    """)
    
    st.markdown("---")
    st.markdown("### 🎨 الميزات الإبداعية")
    st.markdown("""
    ✓ صياغة إبداعية ذكية
    ✓ لغة حية وجذابة
    ✓ احترافية عالية
    ✓ تنوع في الأسلوب
    ✓ دقة في المعلومات
    """)
