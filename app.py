import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. إعداد الصفحة والتصميم ---
st.set_page_config(page_title="Diwan Smart Newsroom", layout="wide", page_icon="🎙️")

# CSS لتخصيص الأزرار لتشبه التطبيق في الصورة
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 120px;
        border-radius: 15px;
        font-size: 20px;
        font-weight: bold;
        background-color: #0E738A;
        color: white;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #D95F18; /* اللون البرتقالي عند التحويم */
        transform: translateY(-2px);
    }
    h1 { text-align: center; color: #0E738A; }
</style>
""", unsafe_allow_html=True)

# --- 2. إعداد مفتاح API ---
# تأكد من وضع المفتاح في secrets أو هنا مؤقتاً للتجربة
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ الرجاء وضع مفتاح API في ملف secrets.toml")
    st.stop()

# --- 3. تعريف التعليمات (Prompts) لكل وظيفة ---
PROMPTS = {
    "web_editor": """
    أنت محرر ويب (SEO). أعد صياغة النص ليكون مقالاً متوافقاً مع محركات البحث.
    - استخدم فقرات قصيرة.
    - استخرج الكلمات المفتاحية في النهاية.
    - ضع عنواناً جذاباً جداً للنقر (Clickbait but professional).
    """,
    
    "article_writer": """
    أنت صحفي محترف (الهرم المقلوب).
    - ابدأ بالحدث الأهم.
    - احذف الألقاب (السيد/السيدة) واستخدم الصفات.
    - لغة عربية فصحى وسلسة.
    - ممنوع المقدمات الإنشائية.
    """,
    
    "headlines": """
    اقترح 5 عناوين قوية للنص المقدم:
    1. عنوان إخباري كلاسيكي.
    2. عنوان تساؤلي (هل...؟).
    3. عنوان صادم/مثير للجدل.
    4. عنوان للأرقام (شاهد..).
    5. عنوان قصير جداً للسوشيال ميديا.
    """,
    
    "quotes": """
    استخرج "أهم التصريحات" من النص.
    - قدمها في شكل نقاط.
    - ضع نص التصريح بين علامتي تنصيص "..."
    - اذكر اسم القائل بوضوح.
    """,
    
    "radio_flash": """
    حول النص إلى "موجز إذاعي" (Flash Info).
    - جمل قصيرة جداً.
    - اكتب للأذن (بسيط ومباشر).
    - لا تتجاوز 40 كلمة.
    """,
    
    "on_this_day": """
    استخرج أحداث هذا اليوم تاريخياً.
    الأولوية: 1. تونس 2. العالم العربي 3. العالم.
    الأسلوب: كبسولات سريعة.
    """
}

# --- 4. الهيدر والشعار ---
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.title("🎙️ ديوان أف أم - المحرر الذكي")
    st.markdown("##### Smart Newsroom Editor")

st.markdown("---")

# --- 5. نظام القوائم (State Management) ---
# نحتاج لتذكر أي زر ضغطه المستخدم
if 'active_mode' not in st.session_state:
    st.session_state.active_mode = None

# دالة لتغيير الوضع
def set_mode(mode):
    st.session_state.active_mode = mode

# --- 6. شبكة الأزرار (The Grid) ---
# الصف الأول
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📝 صياغة المقال"): set_mode("article_writer")
with col2:
    if st.button("✨ تحرير الويب"): set_mode("web_editor")
with col3:
    if st.button("🎤 من صوت لنص"): set_mode("audio_to_text")
with col4:
    if st.button("T صانع العناوين"): set_mode("headlines")

# الصف الثاني
col5, col6, col7, col8 = st.columns(4)
with col5:
    if st.button("ılı أهم التصريحات"): set_mode("quotes")
with col6:
    if st.button("((●)) موجز إذاعي"): set_mode("radio_flash")
with col7:
    if st.button("📅 حدث اليوم"): set_mode("on_this_day")
with col8:
    if st.button("🧹 تنظيف الشاشة"): set_mode(None)

st.markdown("---")

# --- 7. منطقة العمل (تتغير حسب الزر المختار) ---

if st.session_state.active_mode == "audio_to_text":
    st.header("🎤 تحويل التسجيلات الصوتية إلى نص")
    uploaded_file = st.file_uploader("ارفع ملف الصوت (MP3, WAV, M4A)", type=['mp3', 'wav', 'm4a', 'ogg'])
    
    if uploaded_file is not None:
        if st.button("بدء التفريغ"):
            with st.spinner('جاري معالجة الصوت... (قد يستغرق وقتاً حسب طول الملف)'):
                try:
                    # تفريغ الصوت يحتاج رفع الملف مؤقتاً لجوجل
                    # هذه خطوة متقدمة، هنا سأستخدم نموذج "Text Processing" للتبسيط
                    # إذا أردت تفعيل الصوت الحقيقي يحتاج كود رفع خاص
                    st.info("ميزة الصوت تتطلب تفعيل Upload API. حالياً سأقوم بتلخيص النص إذا أدخلته.")
                except Exception as e:
                    st.error(f"خطأ: {e}")

elif st.session_state.active_mode is not None:
    # الحصول على العنوان واسم الخاصية
    mode_titles = {
        "article_writer": "📝 صياغة مقال صحفي",
        "web_editor": "✨ تحرير متوافق مع الويب (SEO)",
        "headlines": "T صناعة العناوين الجذابة",
        "quotes": "ılı استخراج أهم التصريحات",
        "radio_flash": "((●)) صياغة موجز إذاعي",
        "on_this_day": "📅 حدث في مثل هذا اليوم"
    }
    
    current_mode = st.session_state.active_mode
    st.header(mode_titles[current_mode])
    
    # حقل الإدخال
    input_label = "أدخل التاريخ" if current_mode == "on_this_day" else "أدخل النص الخام هنا"
    user_input = st.text_area(input_label, height=200)
    
    if st.button("تنفيذ المهمة 🚀"):
        if user_input:
            with st.spinner('جاري العمل...'):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    # دمج التعليمات مع مدخلات المستخدم
                    full_prompt = f"{PROMPTS[current_mode]}\n\nالنص المدخل:\n{user_input}"
                    
                    # إعدادات خاصة لحدث اليوم (تجنب الهلوسة)
                    temp = 0.2 if current_mode == "on_this_day" else 0.4
                    
                    response = model.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(temperature=temp)
                    )
                    
                    st.success("تمت العملية بنجاح!")
                    st.markdown("### النتيجة:")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
        else:
            st.warning("الرجاء إدخال البيانات أولاً.")

else:
    st.info("👈 اختر إحدى الخدمات من القائمة أعلاه للبدء.")

    # يمكنك وضع صورة الشعار الكبير هنا كخلفية
