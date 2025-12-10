import google.generativeai as genai

# --- APNI KEY YAHAN DAALO ---
GOOGLE_API_KEY = "AIzaSyBvbX3VL1Qk33U-DdGYTq8TO2GRFl2fCiE"

genai.configure(api_key=GOOGLE_API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"AVAILABLE MODEL: {m.name}")
except Exception as e:
    print(f"Error: {e}")