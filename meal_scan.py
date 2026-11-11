import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- GEMINI API AYARLARI ---
# Kendi Gemini API anahtarını buraya tırnak içinde yazmalısın.
# Örnek: GEMINI_API_KEY = "AIzaSyD-xxxxxxxxxxxx"
GEMINI_API_KEY = "AQ.Ab8RN6K_y2G2iYd_R6dfaiSAmSWPMu-gFgD1tCSMvn1Sa6kEvg" 
genai.configure(api_key=GEMINI_API_KEY)

def meal_scan_page():
    st.markdown("<p style='text-align:center; font-size:1.1rem;'>Yemeğinin fotoğrafını çek veya yükle, Nova içeriğini ve kalorisini tahmin etsin.</p>", unsafe_allow_html=True)
    
    upload_method = st.radio("Fotoğraf Ekleme Yöntemi:", ["Dosya Yükle", "Kameradan Çek"], horizontal=True)
    
    img_file = None
    if upload_method == "Kameradan Çek":
        img_file = st.camera_input("Yemeğini Çek")
    else:
        img_file = st.file_uploader("Yemek Fotoğrafı Yükle", type=["png", "jpg", "jpeg"])
        
    if img_file is not None:
        img = Image.open(img_file)
        st.image(img, caption="İncelenecek Fotoğraf", use_container_width=True)
        
        if st.button("🔍 Yapay Zeka ile Analiz Et", type="primary", use_container_width=True):
            with st.spinner("🤖 Nova yemeğini inceliyor, lütfen bekle..."):
                # Yapay zekaya ne yapması gerektiğini anlattığımız komut (Prompt)
                prompt = """
                Sen uzman bir diyetisyensin. Bu fotoğraftaki yemeği/yemekleri analiz et.
                Her bir malzemenin porsiyonunu tahmin et.
                Lütfen SADECE aşağıdaki JSON formatında, geçerli bir JSON objesi döndür.
                Başka hiçbir açıklama veya markdown karakteri (```json) yazma.
                
                Format:
                {
                    "items": [
                        {
                            "Yemek": "Yemek Adı",
                            "Kalori": 150.0,
                            "Protein (g)": 10.5,
                            "Karb. (g)": 20.0,
                            "Yağ (g)": 5.0
                        }
                    ]
                }
                """
                
                # Modeli başlat
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # --- İŞTE HATA KORUMA (TRY-EXCEPT) BLOĞU BURADA ---
                try:
                    response = model.generate_content([prompt, img])
                    
                    # Markdown temizliği (Bazen AI ```json ... ``` formatında yanıt verir)
                    response_text = response.text.replace("```json", "").replace("```", "").strip()
                    
                    # JSON metnini Python sözlüğüne çevir
                    data = json.loads(response_text)
                    
                    # Toplam kaloriyi hesapla
                    toplam_kalori = sum(item["Kalori"] for item in data["items"])
                    data["kcal"] = toplam_kalori
                    
                    return data
                    
                except json.JSONDecodeError:
                    st.error("⚠️ Yapay zeka fotoğrafı tam anlayamadı. Lütfen fotoğrafı daha net çekip tekrar dene.")
                    return None
                    
                except Exception as e:
                    # 503 High Demand (Sunucu Yoğunluğu) hatası gelirse uygulamayı çökertmeden uyarı ver
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        st.warning("🤖 Gemini yapay zeka sunucuları şu an çok yoğun. Lütfen 1-2 dakika sonra tekrar dene.")
                    else:
                        st.error(f"Beklenmeyen bir hata oluştu: {str(e)}")
                    return None
                    
    return None
