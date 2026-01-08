import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# --- 1. إعداد الصفحة والستايل ---
st.set_page_config(page_title="Diwan Newsroom Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    .stButton>button {
        width: 100%; height: 70px; border-radius: 10px;
        font-size: 16px; font-weight: bold; background-color: #f0f2f6; color: #31333F;
        border: 1px solid #d6d6d6;
    }
    .stButton>button:hover { background-color: #ffe0b2; border-color: #ff8c00; color: #ff8c00; }
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stTextArea textarea { font-size: 16px; font-family: 'Courier New', monospace; }
    .stSuccess { background-color: #e8f5e9; border-right: 5px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بالمفتاح ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود (GEMINI_API_KEY).")
    st.stop()

# --- 3. دالة المعالجة الآمنة (The Safe Handler) ---
def generate_content_safe(full_prompt, temperature):
    """
    تحاول هذه الدالة استخدام الموديل الأقوى (Pro)، 
    وإذا فشلت تنتقل تلقائياً للموديل الأسرع (Flash) دون إظهار خطأ للمستخدم.
    """
    
    # المحاولة الأولى: الموديل الأقوى (Gemini 1.5 Pro)
    try:
        model_pro = genai.GenerativeModel('gemini-1.5-pro', generation_config={"temperature": temperature})
        response = model_pro.generate_content(full_prompt)
        return response.text, "Gemini 1.5 Pro (الجودة القصوى)"
    except Exception:
        # المحاولة الثانية: الموديل السريع (Gemini 1.5 Flash) - خطة بديلة
        try:
            model_flash = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": temperature})
            response = model_flash.generate_content(full_prompt)
            return response.text, "Gemini 1.5 Flash (السرعة)"
        except Exception as e:
            # إذا فشل الاثنان
            return f"عذراً، حدث خطأ تقني غير متوقع: {e}", "Error"

# --- 4. هندسة الأوامر (الصحفية) ---
SYS_INSTRUCTIONS = """
أنت رئيس تحرير خبير في "إذاعة ديوان أف أم".
الدور: إعادة صياغة النصوص لتكون مواد إخبارية احترافية وجاهزة للبث والنشر.
القواعد الذهبية:
1. الموضوعية: احذف آراء الكاتب، العواطف، والمبالغات.
2. الهيكل: ابدأ بالمعلومة الأهم (الهرم المقلوب).
3. اللغة: عربية فصحى إعلامية قوية، موجزة، وخالية من الحشو.
4. التنسيق: استخدم فقرات قصيرة جداً.
"""

PROMPTS = {
    "article": """
    المهمة: خبر إذاعي رئيسي (Main News).
    - الصياغة: ابدأ بـ Lead قوي يجيب عن الأسئلة الخمسة.
    - الأسلوب: سردي، متماسك، وجدي.
    - الطول: متوسط (يغطي التفاصيل المهمة دون إطالة).
    """,
    
    "web": """
    المهمة: مقال للموقع الإلكتروني (SEO).
    - العنوان: يجب أن يكون جذاباً جداً (Viral) لكن صادقاً.
    - المتن: فقرات قصيرة (لا تتجاوز 3 أسطر للفقرة).
    - الكلمات المفتاحية: ضمن أهم الكلمات في أول فقرة.
    - الخاتمة: أضف 3 وسوم (Hashtags) مقترحة.
    """,
    
    "flash": """
    المهمة: موجز (Flash Info).
    - الموجه: للمذيع (للقراءة الصوتية).
    - القواعد: جمل قصيرة وبسيطة. ابتعد عن الجمل المعقدة.
    - الطول: أقصى حد 40 كلمة.
    """,
    
    "titles": """
    المهمة: توليد عناوين. اقترح 5 خيارات:
    1. كلاسيكي.
    2. تساؤلي.
    3. مثير (Clickbait نظيف).
    4. اقتباس.
    5. قصير جداً (للسوشيال ميديا).
    """,
    
    "quotes": """
    المهمة: استخراج التصريحات.
    - استخرج الكلام المباشر فقط.
    - نسقه كالتالي:
    * [الاسم/الصفة]: "النص..."
    """,
    
    "analysis": """
    المهمة: زاوية تحليلية (Context).
    - ضع الخبر في سياقه العام.
    - اربطه بالأحداث السابقة.
    - ما دلالات هذا الحدث؟
    """
}

# --- 5. الواجهة الجانبية ---
with st.sidebar:
    st.header("⚙️ إعدادات المحرر")
    creativity = st.slider("درجة التصرف (Creativity)", 0.0, 1.0, 0.3)
    st.info("💡 نصيحة: للترجمة الحرفية قلل الدرجة، وللصياغة الإبداعية ارفعها.")

# --- 6. الواجهة الرئيسية ---
st.title("🎙️ Diwan Smart Newsroom")

if 'mode' not in st.session_state: st.session_state.mode = "article"
def set_mode(m): st.session_state.mode = m

# الأزرار
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📝 خبر إذاعي"): set_mode("article")
    if st.button("🔍 تحليل وسياق"): set_mode("analysis")
with col2:
    if st.button("🌐 ويب (SEO)"): set_mode("web")
    if st.button("🏷️ عناوين"): set_mode("titles")
with col3:
    if st.button("⚡ موجز (Flash)"): set_mode("flash")
    if st.button("💬 تصريحات"): set_mode("quotes")

st.markdown("---")

# العنوان المتغير
titles_display = {
    "article": "📝 تحرير خبر إذاعي", "web": "🌐 تحرير للموقع (SEO)",
    "flash": "⚡ صياغة موجز", "titles": "🏷️ توليد عناوين",
    "quotes": "💬 استخراج التصريحات", "analysis": "🔍 تحليل وسياق"
}
curr = st.session_state.mode
st.subheader(f"{titles_display[curr]}")

# نموذج العمل
with st.form("editor_form"):
    text_input = st.text_area("أدخل النص هنا:", height=250)
    submitted = st.form_submit_button("🚀 معالجة النص")
    
    if submitted and text_input:
        with st.spinner('جاري التحرير...'):
            
            # تجهيز الطلب
            full_prompt = f"""
            {SYS_INSTRUCTIONS}
            ---
            {PROMPTS[curr]}
            ---
            النص الأصلي:
            {text_input}
            """
            
            # التنفيذ عبر الدالة الآمنة
            result_text, model_used = generate_content_safe(full_prompt, creativity)
            
            # عرض النتيجة
            if model_used == "Error":
                st.error(result_text)
            else:
                st.success("✅ النتيجة النهائية:")
                st.markdown(result_text)
                st.caption(f"تمت المعالجة بواسطة: {model_used}")
