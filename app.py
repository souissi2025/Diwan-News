import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. إعداد الصفحة (أنيق ومريح للقراءة)
# ==========================================
st.set_page_config(page_title="Diwan Editor Pro", layout="wide", page_icon="✒️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم الورقة التحريرية */
    .editorial-paper {
        background-color: #fff;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.06);
        border-right: 6px solid #D95F18; /* لمسة ديوان */
        font-size: 18px;
        line-height: 2.2; /* تباعد مريح للأسطر */
        color: #222;
        white-space: pre-wrap;
    }
    
    .stButton>button {
        width: 100%; height: 65px; font-weight: bold; font-size: 16px;
        background: linear-gradient(to right, #2c3e50, #4ca1af); /* تدرج لوني فخم */
        color: white; border: none; border-radius: 6px;
        transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.9; }
    
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
def get_pro_model():
    target = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for t in target:
            if t in available: return t
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. البرومبت "الصحفي المخضرم" (Sophisticated Editor Prompt)
# ==========================================
# هذا البرومبت يطلب "الأناقة" في الصياغة مع "الصرامة" في المعلومات
EDITOR_PROMPT = """
أنت "سكرتير تحرير" خبير في إذاعة ديوان أف أم.
المهمة: إعادة صياغة النص الخام ليصبح مقالاً صحفياً متين الصياغة، سلس القراءة، ومحكماً.

🎯 التوجيهات الدقيقة (The Balance):
1. **حرية الصياغة:** مسموح لك بإضافة "روابط لغوية" وعبارات انتقالية (مثل: "وفي سياق متصل"، "مشدداً على أن"، "مما يعكس حرص...") لربط الأفكار وجعل النص يتدفق بسلاسة.
2. **قدسية الخبر:** لا تضف أي معلومة، رقم، تاريخ، أو اسم غير موجود في النص الأصلي. (جوّد الأسلوب ولا تغير الحقائق).
3. **الأسلوب:** استخدم لغة عربية "أنيقة" (Elegant) ورصينة. ابتعد عن الركاكة والجمل المتقطعة. اجعل القارئ يشعر أن وراء النص قلماً محترفاً.
4. **التوقيع:** ابدأ بـ: **(تونس - ديوان أف أم)**.

الشكل المطلوب:
نص متماسك، فقرات مترابطة، لغة قوية، دون عناوين فرعية كثيرة.
"""

# ==========================================
# 5. الواجهة (Streaming Enabled)
# ==========================================
st.title("✒️ Diwan Editor Pro")
st.caption("نظام الصياغة الصحفية الاحترافية (Flow & Accuracy)")

col_in, col_out = st.columns([1, 1.3])

with col_in:
    st.markdown("### 📥 النص الخام")
    input_text = st.text_area("ألصق النص:", height=600, placeholder="أدخل النص هنا...")
    
    if st.button("✨ تحرير وصياغة (بلمسة احترافية)"):
        if input_text:
            st.session_state.streaming_pro = True
        else:
            st.warning("أدخل نصاً.")

with col_out:
    st.markdown("### 📰 النص المُصاغ")
    
    report_container = st.empty()
    
    if st.session_state.get('streaming_pro') and input_text:
        try:
            model_name = get_pro_model()
            
            # درجة حرارة 0.7: المعادلة الذهبية
            # تسمح بجمال الأسلوب (Style) لكن تمنع الخيال الواسع (Hallucination)
            pro_config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 8192,
            }
            
            model = genai.GenerativeModel(model_name, generation_config=pro_config)
            
            response = model.generate_content(
                f"{EDITOR_PROMPT}\n\nالنص الخام:\n{input_text}",
                stream=True 
            )
            
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    report_container.markdown(f'<div class="editorial-paper">{full_text}</div>', unsafe_allow_html=True)
            
            st.caption("✅ تم التحرير.")
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
