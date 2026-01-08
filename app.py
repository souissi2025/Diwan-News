import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. تصميم الموقع وغرفة العناوين
# ==========================================
st.set_page_config(page_title="Diwan Web Editor + Titles", layout="wide", page_icon="🌐")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم المقال */
    .article-box {
        background-color: #fff;
        padding: 40px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    
    .article-title {
        color: #111; font-size: 24px; font-weight: 900;
        margin-bottom: 15px; line-height: 1.4;
        border-bottom: 2px solid #D95F18; padding-bottom: 15px;
    }
    
    .article-body {
        font-size: 17px; line-height: 1.9; color: #333;
        white-space: pre-wrap;
    }
    
    /* تصميم صندوق مقترحات العناوين */
    .titles-box {
        background-color: #f0f7f9; /* لون سماوي فاتح */
        padding: 25px;
        border-radius: 8px;
        border-right: 5px solid #0E738A;
        font-size: 16px;
        color: #0E738A;
    }
    .titles-header {
        font-weight: bold; font-size: 18px; margin-bottom: 10px; display: block;
    }

    .stButton>button {
        width: 100%; height: 65px; font-weight: bold; font-size: 16px;
        background-color: #D95F18; color: white; border: none; border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #bf4d0f; }
    
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
def get_best_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for p in priority:
            if p in available: return p
        if available: return available[0]
    except: pass
    return 'gemini-pro'

# ==========================================
# 4. البرومبت المطور (مع ورشة العناوين)
# ==========================================
WEB_PROMPT = """
أنت رئيس تحرير القسم الرقمي في موقع "ديوان أف أم".
المهمة: تحويل النص الخام إلى مقال ويب احترافي + اقتراح عناوين بديلة.

الجزء الأول: المقال (The Article)
1. اكتب عنواناً رئيسياً للمقال في البداية.
2. اكتب المقال بأسلوب شيق، فقرات قصيرة (للموبايل)، ولغة عصرية.
3. اربط الأحداث بذكاء (Context).

الجزء الثاني: ورشة العناوين (Title Workshop)
بعد نهاية المقال، ضع فاصلاً ثم اقترح 5 عناوين بديلة احترافية جداً للأنماط التالية:
1. 🎯 **عنوان SEO:** (دقيق ويحتوي كلمات مفتاحية لمحركات البحث).
2. 🔥 **عنوان فيسبوك:** (مثير للجدل أو العاطفة لزيادة التفاعل).
3. ❓ **عنوان تساؤلي:** (يثير فضول القارئ).
4. 💬 **عنوان اقتباس:** (أقوى جملة قيلت في النص).
5. ⚡ **عنوان عاجل:** (قصير جداً ومباشر للتنبيهات).

تنسيق الإجابة المطلوب:
[العنوان الرئيسي]
[نص المقال...]
---
[قائمة العناوين المقترحة]
"""

# ==========================================
# 5. الواجهة
# ==========================================
st.title("🌐 Diwan Web Publisher")
st.caption("محرر المقالات + مولد العناوين الذكي")

col_in, col_out = st.columns([1, 1.3])

with col_in:
    st.markdown("##### 📄 النص الخام")
    input_text = st.text_area("ألصق البيان أو النص:", height=600, placeholder="أدخل النص هنا...")
    
    if st.button("✨ تحرير المقال + اقتراح العناوين"):
        if input_text:
            st.session_state.run_web_titles = True
        else:
            st.warning("أدخل نصاً أولاً.")

with col_out:
    st.markdown("##### 💻 المعاينة (المقال + العناوين)")
    
    if st.session_state.get('run_web_titles') and input_text:
        with st.spinner('جاري صياغة المقال وعصر الذهن للعناوين...'):
            try:
                model_name = get_best_model()
                # حرارة 0.85 للحصول على عناوين إبداعية وغير تقليدية
                model = genai.GenerativeModel(model_name, generation_config={"temperature": 0.85})
                
                response = model.generate_content(f"{WEB_PROMPT}\n\nالنص الخام:\n{input_text}")
                
                # فصل المقال عن العناوين (باستخدام الفاصل الذي طلبناه في البرومبت)
                if "---" in response.text:
                    parts = response.text.split("---")
                    article_part = parts[0]
                    titles_part = parts[1]
                else:
                    article_part = response.text
                    titles_part = "لم يتم توليد عناوين منفصلة، طالع النص أعلاه."

                # عرض المقال في صندوق أبيض
                st.markdown(f"""
                <div class="article-box">
                    <div class="article-body">{article_part}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض العناوين المقترحة في صندوق ملون منفصل
                st.markdown(f"""
                <div class="titles-box">
                    <span class="titles-header">💡 مقترحات عناوين بديلة:</span>
                    {titles_part}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error("حدث خطأ تقني.")
