import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. التصميم الجمالي (CSS) - حل مشكلة البتر
# ==========================================
st.set_page_config(page_title="Diwan Editor Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* صندوق النتائج الاحترافي */
    .result-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-right: 6px solid #0E738A;
        margin-top: 25px;
        font-size: 16px;
        line-height: 1.8;
        color: #2c3e50;
        white-space: pre-wrap; /* يمنع قص النص */
    }
    
    .stButton>button {
        width: 100%; height: 60px; border-radius: 8px;
        font-weight: bold; background-color: #f8f9fa; border: 1px solid #ddd;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0E738A; color: white; border-color: #0E738A;
    }
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
# 3. الوظيفة الذكية: البحث عن الموديل (تمنع خطأ 404)
# ==========================================
def get_working_model():
    """
    هذه الدالة لا تخمن الاسم، بل تبحث في القائمة الحقيقية للموديلات
    وتعيد أول موديل صالح للعمل لتجنب الأخطاء.
    """
    try:
        # جلب قائمة الموديلات المتاحة فعلياً من جوجل
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # ترتيب الأولويات: نحاول الحديث أولاً، ثم القديم
        priority_list = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-1.0-pro',
            'models/gemini-pro'
        ]
        
        # اختيار الأفضل الموجود في القائمة
        for priority in priority_list:
            if priority in available_models:
                return priority
        
        # إذا لم نجد المفضلات، نأخذ أول واحد متاح وخلاص
        if available_models:
            return available_models[0]
            
    except:
        pass
    
    # شبكة أمان أخيرة (اسم الموديل الكلاسيكي)
    return 'gemini-pro'

# ==========================================
# 4. البرومبت والإعدادات
# ==========================================
MY_PROMPT = """
أنت رئيس تحرير محترف في إذاعة ديوان أف أم.
المهمة: أعد صياغة النص الخام التالي ليصبح خبراً إذاعياً جذاباً.

القواعد:
1. صياغة إبداعية، سلسة، وقوية (السهل الممتنع).
2. حذف الحشو (تم، قام، الجدير بالذكر).
3. حذف الألقاب والعبارات الإنشائية.
4. تقسيم النص لفقرات واضحة.
"""

# رفع درجة الإبداع
config = {
    "temperature": 0.8,
    "max_output_tokens": 2048,
}

# ==========================================
# 5. الواجهة والتنفيذ
# ==========================================
st.title("🎙️ Diwan Smart Editor")
st.caption("Auto-Detect Model System")

col_input, col_info = st.columns([3, 1])

with col_input:
    input_text = st.text_area("النص الخام:", height=180, placeholder="أدخل النص هنا...")
    
    if st.button("🚀 معالجة النص (تنفيذ)", type="primary"):
        if input_text:
            with st.spinner('جاري البحث عن الموديل المناسب والصياغة...'):
                try:
                    # 1. اكتشاف الموديل الصالح
                    model_name = get_working_model()
                    
                    # 2. إنشاء الموديل
                    model = genai.GenerativeModel(model_name, generation_config=config)
                    
                    # 3. التوليد
                    response = model.generate_content(f"{MY_PROMPT}\n\nالنص:\n{input_text}")
                    
                    # 4. العرض
                    st.markdown(f'<div class="result-box">{response.text}</div>', unsafe_allow_html=True)
                    st.toast(f"تم استخدام الموديل: {model_name}", icon="✅")
                    
                except Exception as e:
                    st.error(f"حدث خطأ غير متوقع: {e}")
                    st.info("نصيحة: جرب تقليل طول النص قليلاً.")
        else:
            st.warning("الرجاء إدخال نص.")

with col_info:
    st.success("✅ النظام يعمل")
    st.caption("يقوم النظام تلقائياً باختيار الموديل المتوفر في الخادم لتجنب أخطاء الاتصال.")
