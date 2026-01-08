import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. التصميم الجمالي (UI/UX) - لوحة القيادة
# ==========================================
st.set_page_config(page_title="Diwan Newsroom OS", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        direction: rtl; 
        background-color: #f8f9fa;
    }
    
    /* تنسيق الأزرار كأيقونات تطبيقات */
    .stButton>button {
        width: 100%; 
        height: 90px; 
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        background-color: white;
        color: #333;
        font-size: 18px; 
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: #0E738A;
        color: #0E738A;
    }
    
    /* تنسيق ورقة النتيجة */
    .result-card {
        background-color: #fff;
        padding: 40px;
        border-radius: 15px;
        border-top: 6px solid #D95F18; /* برتقالي ديوان */
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        font-size: 18px;
        line-height: 2.2;
        color: #1a1a1a;
        margin-top: 20px;
        white-space: pre-wrap;
    }
    
    /* عناوين الأقسام */
    h1, h2, h3 { color: #0E738A; }
    
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
# 3. الموديل الذكي
# ==========================================
def get_model():
    target = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for t in target:
            if t in available: return t
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. الدستور التونسي (يُطبق على كل الأنماط)
# ==========================================
# هذه القواعد ستضاف أوتوماتيكياً لكل زر تضغطه
COMMON_RULES = """
🛑 قواعد التحرير الإلزامية (Tunisian Standards):
1. **الأسماء:** حذف الألقاب (السيد، السيدة) والاكتفاء بالصفة والاسم.
2. **التواريخ:** استخدام الأشهر التونسية حصراً (جانفي، فيفري، مارس، أفريل، ماي، جوان، جويلية، أوت، سبتمبر، أكتوبر، نوفمبر، ديسمبر).
3. **العملة:** عند ذكر عملة أجنبية، أضف فوراً المقابل التقريبي بالدينار التونسي بين قوسين.
4. **الأسلوب:** هرم مقلوب (الأهم أولاً)، لغة قوية، ربط ذكي بين الفقرات.
5. **التوقيع:** ابدأ بـ **(تونس - ديوان أف أم)**.
"""

# ==========================================
# 5. القوالب الخاصة بكل زر
# ==========================================
PROMPTS = {
    "article": f"""
    المهمة: تحرير "خبر إذاعي رئيسي" (Main News Article).
    {COMMON_RULES}
    - التنسيق: عنوان رئيسي + متن الخبر مقسم لفقرات مترابطة.
    """,
    
    "web": f"""
    المهمة: تحرير "مقال للموقع الإلكتروني" (Web/SEO).
    {COMMON_RULES}
    - العنوان: يجب أن يكون جذاباً جداً (Viral) ويحتوي على فعل.
    - الهيكل: فقرات قصيرة جداً (للموبايل).
    - في النهاية: اقترح 3 وسوم (Hashtags).
    """,
    
    "flash": f"""
    المهمة: صياغة "موجز أخبار" (Flash Info).
    {COMMON_RULES}
    - شرط إضافي: النص يجب أن يكون قصيراً جداً ومكثفاً (لا يتجاوز 60 كلمة).
    - جمل بسيطة للقراءة السريعة.
    """,
    
    "analysis": f"""
    المهمة: كتابة "ورقة تحليلية" (Background & Analysis).
    {COMMON_RULES}
    - اشرح خلفيات الحدث، السياق القانوني، وماذا يعني هذا القرار.
    - اربط الأحداث السابقة بالحالية.
    """,
    
    "titles": f"""
    المهمة: اقتراح "عناوين بديلة".
    {COMMON_RULES}
    - اقترح 5 عناوين متنوعة (رسمي، تساؤلي، مثير، اقتباس، عاجل).
    - لا تكتب مقالاً، فقط العناوين.
    """
}

# ==========================================
# 6. واجهة المستخدم (The Dashboard)
# ==========================================
st.title("🎙️ Diwan Newsroom OS")
st.caption("نظام التحرير الذكي المتكامل")

if 'selected_mode' not in st.session_state: st.session_state.selected_mode = None

# --- شبكة الأزرار (The Grid) ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📰 خبر رئيسي"): st.session_state.selected_mode = "article"
with col2:
    if st.button("🌐 ويب (SEO)"): st.session_state.selected_mode = "web"
with col3:
    if st.button("⚡ موجز"): st.session_state.selected_mode = "flash"
with col4:
    if st.button("🔍 تحليل"): st.session_state.selected_mode = "analysis"
with col5:
    if st.button("🏷️ عناوين"): st.session_state.selected_mode = "titles"

# --- منطقة العمل ---
st.markdown("---")

if st.session_state.selected_mode:
    # عرض اسم الوضع الحالي
    mode_names = {
        "article": "تحرير خبر رئيسي",
        "web": "مقال للموقع الإلكتروني",
        "flash": "موجز سريع",
        "analysis": "تحليل وسياق",
        "titles": "ورشة العناوين"
    }
    current_title = mode_names[st.session_state.selected_mode]
    
    st.subheader(f"📌 الوضع الحالي: {current_title}")
    
    # تقسيم الشاشة: مدخلات ومخرجات
    c_in, c_out = st.columns([1, 1.2])
    
    with c_in:
        input_text = st.text_area("النص الخام:", height=500, placeholder="ضع النص هنا...")
        run_btn = st.button(f"🚀 تنفيذ ({current_title})", type="primary")

    with c_out:
        result_placeholder = st.empty()
        
        if run_btn and input_text:
            try:
                # تحضير الموديل
                model_name = get_model()
                # حرارة 0.7 توازن ممتاز بين الإبداع والالتزام بالقواعد التونسية
                config = {"temperature": 0.7, "max_output_tokens": 8192}
                model = genai.GenerativeModel(model_name, generation_config=config)
                
                # جلب البرومبت المناسب
                final_prompt = PROMPTS[st.session_state.selected_mode]
                
                # التنفيذ (Streaming)
                response = model.generate_content(
                    f"{final_prompt}\n\nالنص الخام:\n{input_text}",
                    stream=True
                )
                
                # العرض المباشر
                full_text = ""
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        result_placeholder.markdown(f'<div class="result-card">{full_text}</div>', unsafe_allow_html=True)
                
                st.toast("✅ تمت المعالجة بنجاح", icon="🇹🇳")
                
            except Exception as e:
                st.error("حدث خطأ تقني.")
                st.write(e)
else:
    st.info("👈 اختر نوع التحرير من الأزرار أعلاه للبدء.")
