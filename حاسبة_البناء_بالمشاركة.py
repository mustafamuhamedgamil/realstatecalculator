import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import os

st.set_page_config(page_title="برنامج البناء بالمشاركة", layout="wide")
st.title("🏗️ برنامج البناء بالمشاركة - قائمة المراجعة والحاسبة")

# --- قائمة المراجعة ---
st.header("✅ قائمة المراجعة")
checklist_items = [
    "صورة من عقد الملكية (موثق)",
    "خلو الأرض من أي نزاعات قضائية",
    "مطابقة المساحة",
    "دراسة سعر المتر في المنطقة",
    "معرفة المنافسين",
    "تحديد نسبة المشاركة",
    "تحديد التزامات كل طرف",
    "مدة التنفيذ وموعد التسليم",
    "حل النزاعات",
    "توثيق العقد",
    "استخراج التراخيص كاملة",
    "تعيين مهندس استشاري",
    "مراجعة التصميمات",
    "تقدير تكلفة الإنشاء",
    "إضافة احتياطي 10-15%",
    "تحديد مصدر التمويل",
    "اختيار مقاول",
    "جدول زمني محدد",
    "متابعة الجودة",
    "تحديد سعر المتر النهائي",
    "حساب مصاريف الأمن والصيانة",
    "إضافة مصاريف التراخيص",
    "تحديد المقدم والأقساط",
    "تحديد الفائدة السنوية",
    "تجهيز جدول دفع",
    "تصميم كتالوج",
    "خطة تسويق",
    "بند خدمة ما بعد البيع",
    "صياغة عقد بيع",
    "بند تسليم الوحدة",
    "إيصالات استلام",
    "طرق الدفع",
    "تعيين حارس/بواب",
    "خطة صيانة دورية",
    "ميزانية الأمن والصيانة"
]

completed_items = []
for item in checklist_items:
    checked = st.checkbox(item)
    if checked:
        completed_items.append(item)

# --- الحاسبة ---
st.header("📊 الحاسبة")
سعر_المتر = st.number_input("سعر المتر:", min_value=0.0, value=20000.0, step=500.0)
مساحة_الشقة = st.number_input("مساحة الشقة (متر مربع):", min_value=0.0, value=150.0, step=10.0)
عدد_الشقق_في_الدور = st.number_input("عدد الشقق في الدور:", min_value=1, value=4, step=1)
عدد_الادوار = st.number_input("عدد الأدوار:", min_value=1, value=6, step=1)
اجمالي_عدد_الشقق = عدد_الشقق_في_الدور * عدد_الادوار
سعر_الوحدة = سعر_المتر * مساحة_الشقة
اجمالي_الايرادات = اجمالي_عدد_الشقق * سعر_الوحدة

تكلفة_البناء = st.number_input("إجمالي تكلفة البناء (جنيه):", min_value=0.0, value=30816000.0, step=100000.0)

مرتب_الحارس = st.number_input("مرتب الحارس (شهريًا):", min_value=0.0, value=5000.0, step=500.0)
صيانة_دورية = st.number_input("الصيانة الدورية (شهريًا):", min_value=0.0, value=4000.0, step=500.0)
خدمات_مشتركة = st.number_input("مصاريف الخدمات المشتركة (شهريًا):", min_value=0.0, value=2000.0, step=500.0)
ادارة_العقار = st.number_input("إدارة العقار (شهريًا):", min_value=0.0, value=3000.0, step=500.0)
اجمالي_الامن_والصيانة_السنوي = (مرتب_الحارس + صيانة_دورية + خدمات_مشتركة + ادارة_العقار) * 12
التكلفة_لكل_شقة = اجمالي_الامن_والصيانة_السنوي / اجمالي_عدد_الشقق

صافي_الربح = اجمالي_الايرادات - تكلفة_البناء
نسبة_المطور = st.number_input("نسبة المطور (%):", min_value=0, max_value=100, value=50, step=5)
حصة_المطور = صافي_الربح * (نسبة_المطور / 100)
حصة_المالك = صافي_الربح - حصة_المطور

مقدم_الحجز_نسبة = st.number_input("نسبة المقدم (%):", min_value=0, max_value=100, value=25, step=5)
مقدم_الحجز = سعر_الوحدة * (مقدم_الحجز_نسبة / 100)
باقي_المبلغ = سعر_الوحدة - مقدم_الحجز
نسبة_الفائدة_سنويا = st.number_input("نسبة الفائدة السنوية (%):", min_value=0.0, max_value=30.0, value=10.0, step=0.5)
مدة_التنفيذ = st.number_input("مدة التنفيذ (شهور):", min_value=1, max_value=60, value=24, step=1)
الفائدة_السنوية = باقي_المبلغ * (نسبة_الفائدة_سنويا / 100)
اجمالي_الفائدة = الفائدة_السنوية * (مدة_التنفيذ / 12)
اجمالي_المستحق = باقي_المبلغ + اجمالي_الفائدة
القسط_الشهري = اجمالي_المستحق / مدة_التنفيذ

# --- زرار تحميل PDF ---
if st.button("📄 حفظ النتائج كـ PDF"):
    pdf_file = "نتائج_البناء_بالمشاركة.pdf"
    c = canvas.Canvas(pdf_file, pagesize=(595, 842))
    
    font_path = "arial.ttf"  # تأكد من وجود الخط في نفس المسار
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("Arabic", font_path))
        c.setFont("Arabic", 14)
    else:
        c.setFont("Helvetica", 14)

    def draw_arabic_text(c, x, y, text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        c.drawRightString(x, y, bidi_text)  # من اليمين لليسار

    y = 800
    draw_arabic_text(c, 550, y, "نتائج البناء بالمشاركة:")

    y -= 20
    draw_arabic_text(c, 550, y, "✅ قائمة المراجعة:")
    y -= 20
    for item in checklist_items:
        status = "✔️" if item in completed_items else "❌"
        draw_arabic_text(c, 550, y, f"{status} {item}")
        y -= 15
        if y < 100:
            c.showPage()
            y = 800

    y -= 10
    draw_arabic_text(c, 550, y, "📊 الحاسبة:")
    y -= 20
    draw_arabic_text(c, 550, y, f"إجمالي عدد الشقق: {اجمالي_عدد_الشقق}")
    y -= 15
    draw_arabic_text(c, 550, y, f"سعر الوحدة: {سعر_الوحدة:,.0f} جنيه")
    y -= 15
    draw_arabic_text(c, 550, y, f"إجمالي الإيرادات: {اجمالي_الايرادات:,.0f} جنيه")
    y -= 15
    draw_arabic_text(c, 550, y, f"صافي الربح: {صافي_الربح:,.0f} جنيه")
    y -= 15
    draw_arabic_text(c, 550, y, f"حصة المطور: {حصة_المطور:,.0f} جنيه")
    y -= 15
    draw_arabic_text(c, 550, y, f"حصة المالك: {حصة_المالك:,.0f} جنيه")
    y -= 15
    draw_arabic_text(c, 550, y, f"إجمالي الأمن والصيانة: {اجمالي_الامن_والصيانة_السنوي:,.0f} جنيه")
    y -= 15
    draw_arabic_text(c, 550, y, f"القسط الشهري: {القسط_الشهري:,.0f} جنيه")
    
    c.save()

    with open(pdf_file, "rb") as f:
        st.download_button("📥 تحميل PDF", f, file_name=pdf_file)
