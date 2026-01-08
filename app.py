import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. إعداد الصفحة وتصميم "غرفة الأخبار"
# ==========================================
st.set_page_config(page_title="Diwan News Wire", layout="wide", page_icon="📠")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم التقرير الإخباري الرسمي */
    .wire-report {
        background-color: #ffffff;
        padding: 40px;
        border: 1px solid #ccc;
        border-top: 6px solid #b30000; /* أحمر داكن (لون العاجل) */
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        font-size: 18px;
        line-height: 2;
        color: #000;
        white-space: pre-wrap;
    }
    
    .stButton>button {
        width: 100%; height: 60px; font-weight: bold; font-size: 16px;
        background-color: #2c3e50; color: white; border: none; border-radius: 4px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1a252f; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الاتصال
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود.")
    st.stop()

# ==========================================
# 3. الموديل (Pro 1.5)
# ==========================================
def get_news_model():
    # نستخدم Pro 1.5 لأنه الأفضل في الالتزام بالتعليمات المعقدة
    target = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for t in target:
            if t in available: return t
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. البرومبت "التقريري" (News Wire Prompt)
# ==========================================
# هذا هو السر: تعليمات صارمة بالموضوعية والابتعاد عن الإنشاء
AGENCY_PROMPT = """
أنت محرر أخبار في وكالة أنباء رسمية (مثل TAP أو Reuters).
المهمة: صياغة "تقرير إخباري" بناءً على النص الخام.

القواعد الصارمة (Style Guide):
1. **الموضوعية التامة:** استخدم لغة حيادية وجافة. ابتعد عن العاطفة والدراما (مثل: طعنة غادرة، سم، صدمة).
2. **الأفعال الخبرية:** استخدم أفعالاً مثل: (أكد، أشار، أوضح، اعتبر، شدد، صرح، أفاد).
3. **الهيكل:** ابدأ بأهم معلومة (Lead)، ثم التفاصيل، ثم السياق القانوني/الخلفية.
4. **التكثيف:** اختصر الجمل الطويلة.
5. **ممنوع:** لا تبدأ بـ "في بيان له" أو مقدمات ركيكة. ادخل في الخبر فوراً (مثال: أدان مجلس الصحافة...).

الهدف: نص جاهز للنشر في قسم "الأخبار الوطنية" بالموقع.
"""

# ==========================================
# 5. الواجهة
# ==========================================
st.title("📠 Diwan News Wire")
st.caption("نظام صياغة الأخبار الرسمية (نمط الوكالات)")

col_in, col_out = st.columns([1, 1.2])

with col_in:
    st.markdown("### 📥 البيان / المصدر")
    input_text = st.text_area("النص الخام:", height=500, placeholder="ضع نص البيان هنا...")
    
    if st.button("📝 صياغة تقرير إخباري (رسمي)"):
        if input_text:
            st.session_state.do_news = True
        else:
            st.warning("أدخل نصاً.")

with col_out:
    st.markdown("### 📰 التقرير الجاهز")
    
    if st.session_state.get('do_news') and input_text:
        with st.spinner('جاري الصياغة بأسلوب الوكالات...'):
            try:
                model_name = get_news_model()
                
                # السر هنا: حرارة منخفضة (0.4) تعني "التزام بالحقائق" و "صفر دراما"
                # الحرارة العالية (0.9) هي التي كانت تنتج النصوص الأدبية السابقة
                news_config = {
                    "temperature": 0.4, 
                    "top_p": 0.8,
                    "max_output_tokens": 2048,
                }
                
                model = genai.GenerativeModel(model_name, generation_config=news_config)
                
                response = model.generate_content(f"{AGENCY_PROMPT}\n\nالنص الخام:\n{input_text}")
                
                st.markdown(f'<div class="wire-report">{response.text}</div>', unsafe_allow_html=True)
                st.caption(f"تمت الصياغة بموديل: {model_name} | الإعداد: News Wire (Temp 0.4)")
                
            except Exception as e:
                st.error("حدث خطأ تقني.")
