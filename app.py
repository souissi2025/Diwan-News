import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. إعداد الصفحة وتصميم العرض
# ==========================================
st.set_page_config(page_title="Diwan Newsroom", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم منطقة النتيجة لتبدو كورقة تحرير */
    .news-paper {
        background-color: #fff;
        padding: 40px;
        border: 1px solid #ddd;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        font-size: 18px;
        line-height: 2;
        color: #000;
    }
    
    .stButton>button {
        width: 100%; height: 60px; font-weight: bold; 
        background-color: #0E738A; color: white; border: none;
        border-radius: 8px; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #0b5e70; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
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
# 3. دالة ضمان العمل (تجاوز الأخطاء)
# ==========================================
def get_working_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # ترتيب الأفضلية للصياغة القوية
        priority = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for p in priority:
            if p in available: return p
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. "المحرك التحريري" (السر في الصياغة الاحترافية)
# ==========================================
# هنا وضعت تعليمات صارمة جداً لضمان الجودة
EDITORIAL_PROMPT = """
أنت "كبير المحررين" (Senior Editor) في مؤسسة "ديوان أف أم".
المهمة: تحويل النص الخام المدخل إلى مادة إخبارية مكتملة، رصينة، وجاهزة للنشر.

⚠️ قائمة الممنوعات (Strictly Forbidden):
1. يمنع تماماً استخدام مقدمات المحادثة (مثل: "حسناً"، "إليك النص"، "بصفتي..").
2. يمنع استخدام عبارات الحشو الصحفي القديمة (مثل: "مما لا شك فيه"، "الجدير بالذكر"، "تجدر الإشارة").
3. يمنع استخدام صيغ المبني للمجهول الضعيفة (مثل: "تم الذهاب") واستبدلها بالفعل المباشر (مثل: "ذهب").
4. لا تضع خاتمة إنشائية (مثل: "وفي الختام نأمل...").

✅ معايير الصياغة الاحترافية (Guidelines):
1. العنوان: صغ عنواناً إخبارياً ذكياً (فعل + فاعل) لا يتجاوز 8 كلمات.
2. المقدمة (Lead): ابدأ بأقوى معلومة في النص تجيب عن (من؟ وماذا؟).
3. الجسم: رتب التفاصيل حسب الأهمية (الهرم المقلوب).
4. اللغة: عربية فصحى حديثة (White Arabic)، قوية، خالية من التعقيد، وسلسة القراءة.
5. التنسيق: افصل بين الفقرات بشكل واضح.

النتيجة المطلوبة: الخبر فقط (العنوان + المتن).
"""

# ==========================================
# 5. الواجهة
# ==========================================
st.title("🎙️ Diwan Newsroom Pro")
st.caption("نظام التحرير الصحفي المتقدم")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 النص الخام")
    input_text = st.text_area("ضع مسودة الخبر هنا:", height=450, placeholder="أدخل النقاط الرئيسية أو النص العشوائي...")
    
    if st.button("✨ تحرير وتدقيق احترافي"):
        if input_text:
            st.session_state.processing = True
        else:
            st.warning("الرجاء إدخال نص.")

with col2:
    st.markdown("### 📰 النص المعدل (النتيجة)")
    
    # حاوية النتيجة
    if st.session_state.get('processing') and input_text:
        with st.spinner('جاري تطبيق المعايير التحريرية...'):
            try:
                # إعداد الموديل
                model_name = get_working_model()
                # حرارة 0.6 تعطي توازناً مثالياً بين الإبداع والالتزام بالقواعد
                model = genai.GenerativeModel(model_name, generation_config={"temperature": 0.6})
                
                # المعالجة
                full_request = f"{EDITORIAL_PROMPT}\n\nالنص للمعالجة:\n{input_text}"
                response = model.generate_content(full_request)
                
                # عرض النتيجة بتنسيق الورقة الصحفية
                st.markdown(f'<div class="news-paper">{response.text}</div>', unsafe_allow_html=True)
                
                # زر نسخ سريع
                st.code(response.text, language=None)
                st.caption("✅ تمت الصياغة وفق معايير ديوان أف أم.")
                
            except Exception as e:
                st.error("حدث خطأ في الاتصال، حاول مجدداً.")
    else:
        st.info("النتيجة ستظهر هنا بعد المعالجة.")
