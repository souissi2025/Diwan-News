import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة وتصميم الهوية البصرية ---
st.set_page_config(page_title="Diwan Newsroom Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    /* تحسين الخطوط والألوان لتشبه برامج التحرير الاحترافية */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    .stButton>button {
        width: 100%; height: 60px; border-radius: 8px;
        font-size: 16px; font-weight: bold; 
        background-color: #f8f9fa; color: #1f1f1f; border: 1px solid #ddd;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0E738A; color: white; border-color: #0E738A;
    }
    
    /* تنسيق النتائج */
    .report-box {
        padding: 20px; border-radius: 10px; background-color: #ffffff;
        border-right: 5px solid #0E738A; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-top: 20px; color: #000;
    }
    .stTextArea textarea { font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بالمفتاح ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ المفتاح مفقود (GEMINI_API_KEY).")
    st.stop()

# --- 3. البحث عن أفضل موديل متاح (تجاوز الأخطاء) ---
def get_model_config(creativity):
    # إعدادات التوليد لزيادة الجودة
    config = genai.types.GenerationConfig(
        temperature=creativity, # التحكم في الإبداع
        top_p=0.95,
        top_k=64,
        max_output_tokens=2000,
    )
    
    # البحث عن الموديل
    model_name = "gemini-1.5-flash" # الافتراضي السريع
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # نفضل البرو إذا وجدناه
        if "models/gemini-1.5-pro" in models: model_name = "gemini-1.5-pro"
        elif "models/gemini-1.5-flash" in models: model_name = "gemini-1.5-flash"
        elif "models/gemini-pro" in models: model_name = "gemini-pro"
        elif models: model_name = models[0].replace('models/', '')
    except:
        pass
        
    return genai.GenerativeModel(model_name, generation_config=config), model_name

# --- 4. "عقل" الصحفي: التعليمات الصارمة ---
SYSTEM_PROMPT = """
أنت "رئيس تحرير" مخضرم في إذاعة "ديوان أف أم".
مهمتك: تحويل النصوص الخام إلى مواد صحفية احترافية للنشر فوراً.

⛔ الممنوعات (Blacklist):
1. لا تبدأ بكلمات ضعيفة مثل: "قام"، "تم"، "في إطار"، "الجدير بالذكر".
2. احذف الألقاب التفخيمية (معالي، سيادة، السيد) واكتفِ بالصفة والاسم.
3. تجنب المبني للمجهول (تم افتتاح) واستخدم المبني للمعلوم (افتتح الوزير).
4. لا تستخدم مقدمات إنشائية ومحسنات بديعية. ادخل في الخبر فوراً.

✅ الأسلوب المطلوب (Style):
- لغة عربية فصحى حديثة (White Arabic) مفهومة وقوية.
- جمل قصيرة ورشيقة (فعل + فاعل + مفعول به).
- الهرم المقلوب: الأهم فالمهم.
"""

# تعليمات المهام الخاصة
TASK_PROMPTS = {
    "article": """
    🔴 المهمة: صياغة خبر إذاعي (Radio News Report).
    - العنوان: اقترح عنواناً إخبارياً قوياً.
    - المقدمة (Lead): يجب أن تجيب عن (من، ماذا، متى، أين) في أول 20 كلمة.
    - الجسم: فقرتان تشرحان التفاصيل والخلفية.
    - النبرة: جادة، موضوعية، إخبارية.
    """,
    
    "web": """
    🌐 المهمة: مقال للموقع الإلكتروني (SEO Optimized).
    - العنوان: (Clicky & Viral) جذاب جداً للنقر، يحفز الفضول لكن صادق.
    - الهيكل: فقرات قصيرة جداً (سطرين كحد أقصى).
    - الكلمات المفتاحية: ضمن أهم 3 كلمات بحثية في الفقرة الأولى.
    - الخاتمة: "للمزيد من التفاصيل" + 3 وسوم (Hashtags).
    """,
    
    "flash": """
    ⚡ المهمة: موجز (Flash Info) للمذيع.
    - اكتب "للأذن" وليس "للعين".
    - جمل بسيطة جداً. تجنب الأرقام المعقدة.
    - الحد الأقصى: 40 كلمة فقط.
    """,
    
    "titles": """
    🏷️ المهمة: ورشة عناوين. اقترح 5 بدائل متنوعة:
    1. عنوان كلاسيكي (وصفي).
    2. عنوان تساؤلي (يثير الجدل).
    3. عنوان اقتباس (تصريح قوي).
    4. عنوان عاجل (قصير جداً).
    5. عنوان "سوشيال ميديا" (خفيف وجذاب).
    """,
    
    "analysis": """
    🔍 المهمة: زاوية تحليلية (Context & Background).
    - لا تذكر الخبر فقط، بل اشرح "ماذا يعني هذا؟".
    - اربط الحدث بسياقه السياسي أو الاجتماعي في تونس.
    - استشرف المستقبل: "ما الخطوة القادمة المتوقعة؟".
    """
}

# --- 5. الواجهة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("⚙️ غرفة التحكم")
    
    # التحكم في الإبداع
    tone = st.select_slider(
        "نبرة الصياغة (Tone):",
        options=["دقيق ورسمي", "متوازن", "إبداعي وجريء"],
        value="متوازن"
    )
    
    # ترجمة النبرة إلى أرقام
    temp_map = {"دقيق ورسمي": 0.2, "متوازن": 0.5, "إبداعي وجريء": 0.8}
    selected_temp = temp_map[tone]
    
    st.info("💡 نصيحة: للأخبار السياسية اختر 'دقيق'، وللمنوعات والويب اختر 'إبداعي'.")
    st.divider()
    st.caption("Developed for Diwan FM")

# --- 6. الواجهة الرئيسية ---
st.title("🎙️ Diwan Newsroom Suite")
st.caption("نظام التحرير الذكي المعزز - الإصدار 2.0")

if 'mode' not in st.session_state: st.session_state.mode = "article"
def set_mode(m): st.session_state.mode = m

# شريط الأدوات
c1, c2, c3, c4, c5 = st.columns(5)
with c1: 
    if st.button("📝 خبر رئيسي"): set_mode("article")
with c2:
    if st.button("🌐 ويب (SEO)"): set_mode("web")
with c3:
    if st.button("⚡ موجز"): set_mode("flash")
with c4:
    if st.button("🏷️ عناوين"): set_mode("titles")
with c5:
    if st.button("🔍 تحليل"): set_mode("analysis")

# منطقة العمل
current_task = st.session_state.mode
task_names = {"article": "تحرير خبر إذاعي", "web": "تحرير للويب", "flash": "موجز سريع", "titles": "توليد عناوين", "analysis": "تحليل وسياق"}

st.markdown(f"### 📌 {task_names[current_task]}")

with st.form("editor"):
    text_input = st.text_area("أدخل النص الخام، البيان، أو رؤوس الأقلام:", height=250, placeholder="ضع النص هنا...")
    
    col_sub, col_info = st.columns([1, 4])
    with col_sub:
        submitted = st.form_submit_button("🚀 تحرير الآن")
    
    if submitted and text_input:
        with st.spinner('جاري استدعاء رئيس التحرير الرقمي...'):
            try:
                # 1. إعداد الموديل
                model, m_name = get_model_config(selected_temp)
                
                # 2. بناء الأمر المركب
                full_prompt = f"""
                {SYSTEM_PROMPT}
                ---
                التعليمات الخاصة:
                {TASK_PROMPTS[current_task]}
                ---
                النص المراد تحريره:
                {text_input}
                """
                
                # 3. التنفيذ
                response = model.generate_content(full_prompt)
                
                # 4. العرض بتنسيق جميل
                st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                
                # توثيق تقني خفي
                st.toast(f"تمت المعالجة باستخدام {m_name} | الحرارة: {selected_temp}", icon="✅")
                
            except Exception as e:
                st.error("حدث خطأ غير متوقع. حاول تقليل طول النص أو تغيير النبرة.")
                st.code(e)
