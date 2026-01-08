import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Test Connexion", layout="centered")
st.title("🛠️ فحص الاتصال (Test)")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("✅ المفتاح موجود (Clé trouvée)")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ خطأ في المفتاح: {e}")
    st.stop()

input_text = st.text_area("أدخل كلمة للتجربة:", height=100)
if st.button("تجربة (Test)"):
    if input_text:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(input_text)
            st.info("الرد من جوجل:")
            st.write(response.text)
        except Exception as e:
            st.error(f"❌ الخطأ هو: {e}")