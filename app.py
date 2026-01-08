import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. إعداد الصفحة (تصميم رسمي نظيف)
# ==========================================
st.set_page_config(page_title="Diwan News Wire", layout="wide", page_icon="📠")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم التقرير الرسمي */
    .wire-report {
        background-color: #ffffff;
        padding: 35px;
        border: 1px solid #e0e0e0;
        border-top: 5px solid #0E738A; /* لون ديوان الرسمي */
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        font-size: 18px;
        line-height: 2.1;
        color: #111;
        white-space: pre-wrap;
    }
    
    /* تحسين الأزرار */
    .stButton>button {
        width: 100%; height: 60px; font-weight: bold; font-size: 16px;
        background-color: #2c3e50; color: white; border: none; border-radius: 6px;
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
# 3. الموديل
# ==========================================
def get_news_model():
    # الأولوية للموديلات القادرة على الالتزام بالتعليمات الصارمة
    target = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for t in target:
            if t in available: return t
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. البرومبت "المحاكي" (TAP Style without TAP Name)
# ==========================================
AGENCY_PROMPT = """
أنت محرر أول في قسم الأخبار بإذاعة "ديوان أف أم".
المهمة: صياغة تقرير إخباري رسمي جداً، يحاكي بدقة أسلوب وكالات الأنباء الرسمية (مثل وكالة تونس أفريقيا للأنباء)، ولكن بهوية الإذاعة.

⛔ تعليمات صارمة (Strict Rules):
1. **الأسلوب:** جاف، موضوعي، مباشر، خالي تماماً من العواطف والمحسنات البديعية.
2. **الهوية:** ابدأ النص وجوباً بـ: **(تونس/المنطقة - ديوان أف أم)**.
3. **الممنوعات:** يُمنع منعاً باتاً كتابة "(وات)" أو "TAP" أو ذكر اسم الوكالة الرسمية. نحن نحاكي الأسلوب فقط ولا ننتحل الصفة.
4. **الأفعال المعتمدة:** استخدم حصرياً أفعالاً مثل: (أفاد، أعلن، اعتبر، شدّد، أشار، جدّد، أوضح).
5. **الهيكلة:**
   - الفقرة الأولى: تلخيص دقيق للحدث/القرار (دون مقدمات).
   - الفقرات التالية: تفاصيل القرار والمواقف.
   - الفقرة الأخيرة: السياق القانوني أو الخلفية (إن وجدت).

النتيجة المطلوبة: نص رصين، دقيق، وكامل.
"""

# ==========================================
# 5. الواجهة (مع البث المباشر Streaming)
# ==========================================
st.title("📠 Diwan News Wire")
st.caption("نظام التحرير الإخباري الرسمي")

col_in, col_out = st.columns([1, 1.2])

with col_in:
    st.markdown("### 📥 النص / البيان")
    input_text = st.text_area("ألصق النص هنا:", height=550, placeholder="ضع نص البيان أو المعلومات الخام...")
    
    if st.button("📝 صياغة رسمية (نمط الوكالات)"):
        if input_text:
            st.session_state.streaming = True
        else:
            st.warning("أدخل نصاً.")

with col_out:
    st.markdown("### 📰 التقرير الجاهز")
    
    # حاوية فارغة للعرض المباشر
    report_container = st.empty()
    
    if st.session_state.get('streaming') and input_text:
        try:
            model_name = get_news_model()
            
            # إعدادات الرسمية (حرارة منخفضة جداً 0.3) لضمان عدم "التأليف"
            news_config = {
                "temperature": 0.3,
                "top_p": 0.8,
                "max_output_tokens": 8192, # حد أقصى مرتفع جداً لمنع الانقطاع
            }
            
            model = genai.GenerativeModel(model_name, generation_config=news_config)
            
            # تشغيل البث المباشر
            response = model.generate_content(
                f"{AGENCY_PROMPT}\n\nالنص الخام:\n{input_text}",
                stream=True 
            )
            
            # تجميع النص وعرضه
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    # تحديث النص في كل لحظة
                    report_container.markdown(f'<div class="wire-report">{full_text}</div>', unsafe_allow_html=True)
            
            st.caption("✅ تمت الصياغة.")
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة: {e}")
