import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. إعداد الصفحة وتصميم الورقة التحريرية
# ==========================================
st.set_page_config(page_title="Diwan News Editor", layout="wide", page_icon="🇹🇳")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم الورقة الرسمية */
    .editorial-paper {
        background-color: #fff;
        padding: 40px;
        border-radius: 4px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-top: 6px solid #D95F18; /* هوية ديوان */
        font-size: 18px;
        line-height: 2.2;
        color: #111;
        white-space: pre-wrap;
    }
    
    .stButton>button {
        width: 100%; height: 65px; font-weight: bold; font-size: 16px;
        background-color: #0E738A; color: white; border: none; border-radius: 6px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #095c6e; }
    
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
def get_model():
    # نستخدم Pro 1.5 لأنه الأفضل في الحساب والالتزام بالتعليمات الدقيقة
    target = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for t in target:
            if t in available: return t
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. البرومبت "التونسي المحترف" (Tunisian Editorial Standards)
# ==========================================
TUNISIAN_EDITOR_PROMPT = """
أنت سكرتير تحرير خبير في "ديوان أف أم".
المهمة: تحرير مقال صحفي احترافي متكامل، مع الالتزام الصارم بقواعد "غرفة الأخبار التونسية".

📜 قواعد التحرير الملزمة (Editorial Rules):

1. **الهيكل (الهرم المقلوب):** ابدأ بالنتيجة النهائية أو الحدث الأهم مباشرة. لا تمهد بمقدمات تاريخية.
2. **الأسماء والألقاب:**
   - احذف تماماً كلمات المجاملة (السيد، السيدة، الفاضل، معالي).
   - الصيغة الوحيدة المقبولة: [الصفة الوظيفية] + [الاسم واللقب].
   - مثال: "أكد وزير الصحة علي المرابط..." (وليس السيد وزير الصحة).
3. **التقويم (الأشهر التونسية):**
   - استخدم الأسماء المعمول بها في تونس حصراً: (جانفي، فيفري، مارس، أفريل، ماي، جوان، جويلية، أوت، سبتمبر، أكتوبر، نوفمبر، ديسمبر).
   - ممنوع استخدام: (يناير، فبراير، كانون، تموز...).
4. **العملة (التحويل التلقائي):**
   - إذا ذكر النص مبلغاً بعملة أجنبية (دولار، يورو..)، يجب عليك إضافة ما يعادله بالدينار التونسي بين قوسين تقريباً.
   - مثال: "...بقيمة 100 مليون يورو (أي ما يناهز 330 مليون دينار تونسي)...".
5. **جودة الصياغة:**
   - استخدم روابط لغوية ذكية لربط الفقرات (كما في الصحافة المحترفة).
   - حافظ على الموضوعية والدقة.

التوقيع في البداية: **(تونس - ديوان أف أم)**
"""

# ==========================================
# 5. الواجهة
# ==========================================
st.title("🇹🇳 Diwan News Editor")
st.caption("نظام التحرير بمعايير الصحافة التونسية")

col_in, col_out = st.columns([1, 1.3])

with col_in:
    st.markdown("### 📥 النص الخام")
    input_text = st.text_area("ألصق النص:", height=600, placeholder="ضع النص هنا...")
    
    if st.button("✨ تحرير وتدقيق (تونسي 100%)"):
        if input_text:
            st.session_state.tn_edit = True
        else:
            st.warning("أدخل نصاً.")

with col_out:
    st.markdown("### 📰 المقال الجاهز")
    
    report_container = st.empty()
    
    if st.session_state.get('tn_edit') and input_text:
        try:
            model_name = get_model()
            
            # حرارة 0.7: تحافظ على سلاسة الأسلوب (Flow) مع الالتزام بالقواعد الجديدة
            config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 8192,
            }
            
            model = genai.GenerativeModel(model_name, generation_config=config)
            
            # Streaming Enabled
            response = model.generate_content(
                f"{TUNISIAN_EDITOR_PROMPT}\n\nالنص الخام:\n{input_text}",
                stream=True 
            )
            
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    report_container.markdown(f'<div class="editorial-paper">{full_text}</div>', unsafe_allow_html=True)
            
            st.caption("✅ تم تطبيق قواعد التحرير التونسية.")
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
