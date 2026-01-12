import google.generativeai as genai

# 여기에 님의 Gemini API 키를 넣으세요
genai.configure(api_key="AIzaSyDc9KG-b2_ogiEiPGC8AMz4wMUIwu7P_Wc")

print("📋 사용 가능한 모델 목록:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")