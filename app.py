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

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 메인 함수
def main():
    st.title("💬 스크립트 Q&A 도우미")
    
    # 스크립트 로드
    script = load_script()
    
    # 사이드바에 시스템 프롬프트 표시 (선택사항)
    with st.sidebar:
        st.header("시스템 정보")
        st.info("이 AI는 인스타그램 마케팅 관련 스크립트 내용을 기반으로 답변합니다.")
        
        # 대화 초기화 버튼
        if st.button("대화 초기화"):
            st.session_state.messages = []
            st.rerun()
    
    # 이전 대화 내용 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner('답변을 생성하고 있습니다...'):
                try:
                    messages = [
                        {"role": "system", "content": f"""
                        당신은 인스타그램 마케팅 전문가입니다. 
                        주어진 스크립트 내용을 기반으로 질문에 답변해주세요.
                        답변은 한국어로 해주시고, 가능한 스크립트의 내용을 인용하여 설명해주세요.
                        스크립트 내용: {script}
                        """}
                    ]
                    # 이전 대화 내용 포함
                    messages.extend([
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ])
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0,
                        max_tokens=1000
                    )
                    
                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    
                    # 어시스턴트 메시지 저장
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_response}
                    )
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 