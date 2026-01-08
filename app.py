import streamlit as st
import google.generativeai as genai
import sys

st.set_page_config(page_title="Auto Test", layout="centered")
st.title("🔍 فحص تلقائي (Auto-Diagnostic)")

# 1. فحص نسخة المكتبة (هل التحديث نجح؟)
try:
    version = genai.__version__
    st.info(f"📦 نسخة المكتبة الحالية: {version}")
except:
    st.warning("⚠️ المكتبة قديمة جداً أو غير معروفة")

# 2. فحص المفتاح
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("✅ المفتاح سليم (Clé OK)")
except Exception as e:
    st.error(f"❌ مشكلة في المفتاح: {e}")
    st.stop()

# 3. محاولة الاتصال المباشر (بدون أزرار)
st.write("⏳ جاري محاولة الاتصال بـ Gemini Flash...")

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("هل تسمعني؟ أجب بكلمة واحدة.")
    
    st.success("🎉 نجح الاتصال! (Connexion Réussie)")
    st.markdown(f"### الرد: {response.text}")
    
except Exception as e:
    st.error("❌ فشل الاتصال. تفاصيل الخطأ:")
    st.code(e)
    
    # محاولة بديلة بموديل قديم
    st.write("🔄 جاري تجربة الموديل القديم (Gemini Pro)...")
    try:
        model_old = genai.GenerativeModel('gemini-pro')
        response_old = model_old.generate_content("Test")
        st.success("✅ الموديل القديم يعمل!")
        st.write(response_old.text)
    except:
        st.error("❌ حتى الموديل القديم لا يعمل.")
