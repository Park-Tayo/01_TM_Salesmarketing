import streamlit as st
import pandas as pd
import openai  # OpenAI를 제대로 임포트합니다
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 설정
try:
    if 'OPENAI_API_KEY' in st.secrets:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
    else:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        
    if not openai_api_key:
        st.error('OpenAI API 키가 설정되지 않았습니다.')
        st.stop()
        
    client = openai.OpenAI(api_key=openai_api_key)  # OpenAI 클라이언트 초기화
except Exception as e:
    st.error(f'API 키 설정 중 오류가 발생했습니다: {str(e)}')
    st.stop()

# 페이지 설정
st.set_page_config(page_title="릴스 Q&A 챗봇", page_icon="🤖")

# 스크립트 데이터 로드
@st.cache_data
def load_script():
    df = pd.read_csv("릴스 강의_정리.csv", encoding='utf-8')
    return " ".join(df.iloc[:, 0].dropna().astype(str))

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 메인 함수
def main():
    st.title("💬 릴스 Q&A 챗봇")
    
    # 사이드바 안내 메시지 추가
    st.info("ℹ️ 좌측 상단의 메뉴(≡)를 클릭하시면 참고 자료와 문의처를 확인하실 수 있습니다.\n"
            "ℹ️ 채팅창에 질문을 입력하신 후 종이비행기 버튼을 클릭하시면 AI가 답변해드립니다.")
    
    # 대화 초기화 버튼
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
    
    # 스크립트 로드
    script = load_script()
    
    # 사이드바에 정보 표시
    with st.sidebar:
        st.header("AI 챗봇 정보")
        st.info("이 AI 챗봇은 「터지는 릴스 강의」 내용을 기반으로 답변합니다.")
        
        # 참고 페이지 링크 추가
        st.markdown("### 참고 자료")
        st.markdown("[📚 「한신그룹 - 터지는 릴스 자료」\n바로가기](https://smart-jumper-b33.notion.site/185312cc7a5980aaa201f0303e1f7c10)")
        
        # 구분선 추가
        st.divider()
        
        # 연락처 정보 추가
        st.markdown("### 문의하기")
        st.info("💡 문제가 발생하면 아래로 연락주세요\n\n📞 010-5752-2986")
    
    # 이전 대화 내용 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner('답변을 생성하고 있습니다...'):
                try:
                    messages = [
                        {"role": "system", "content": f"""
                        당신은 주어진 릴스 강의 내용만을 기반으로 답변하는 Q&A 전문가입니다.
                        
                        중요한 규칙:
                        1. 오직 제공된 릴스 강의에 있는 내용만 사용하여 답변하세요.
                        2. 릴스 강의에 관련 내용이 없다면 "죄송하지만 주어진 강의 내용에서 해당 질문에 대한 정보를 찾을 수 없습니다"라고 답변하세요.
                        3. 릴스 강의의 내용을 벗어나는 일반적인 조언이나 추측은 하지 마세요.
                        4. 답변할 때는 다음 형식을 따르세요:
                           • 핵심 답변을 먼저 간단히 제시
                           • 상세 내용은 번호를 매겨 구조화
                           • 중요한 부분은 **강조**
                           • 구분이 필요한 경우 단락을 나누어 작성
                        
                        스크립트 내용: {script}
                        """}
                    ]
                    messages.extend([
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ])
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",  # 모델명 수정
                        messages=messages,
                        temperature=0,
                        max_tokens=1000
                    )
                    
                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_response}
                    )
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 
