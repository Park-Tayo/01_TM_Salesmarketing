import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 설정
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 페이지 설정
st.set_page_config(page_title="스크립트 Q&A 도우미", page_icon="🤖")

# 스크립트 데이터 로드
@st.cache_data
def load_script():
    df = pd.read_csv("스크립트_정리.csv", encoding='utf-8')
    return " ".join(df.iloc[:, 0].dropna().astype(str))

# 메인 함수
def main():
    st.title("💬 스크립트 Q&A 도우미")
    
    # 스크립트 로드
    script = load_script()
    
    # 사이드바에 시스템 프롬프트 표시 (선택사항)
    with st.sidebar:
        st.header("시스템 정보")
        st.info("이 AI는 인스타그램 마케팅 관련 스크립트 내용을 기반으로 답변합니다.")
    
    # 사용자 입력
    user_question = st.text_area("질문을 입력하세요:", height=100)
    
    if st.button("답변 받기"):
        if user_question:
            with st.spinner('답변을 생성하고 있습니다...'):
                try:
                    # ChatGPT API 호출
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": f"""
                            당신은 인스타그램 마케팅 전문가입니다. 
                            주어진 스크립트 내용을 기반으로 질문에 답변해주세요.
                            답변은 한국어로 해주시고, 가능한 스크립트의 내용을 인용하여 설명해주세요.
                            스크립트 내용: {script}
                            """},
                            {"role": "user", "content": user_question}
                        ],
                        temperature=0.7,
                        max_tokens=10000
                    )
                    
                    # 답변 표시
                    st.markdown("### 답변:")
                    st.write(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")
        else:
            st.warning("질문을 입력해주세요.")

if __name__ == "__main__":
    main() 