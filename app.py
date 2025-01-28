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
st.set_page_config(page_title="릴스 강의 Q&A 챗봇", page_icon="🤖")

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
    st.title("💬 릴스 강의 Q&A 챗봇")
    
    # 대화 초기화 버튼을 타이틀 바로 아래로 이동
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
    
    # 스크립트 로드
    script = load_script()
    
    # 사이드바에 정보 표시
    with st.sidebar:
        st.header("AI 챗봇 정보")
        st.info("이 AI 챗봇은 <터지는 릴스> 강의 내용을 기반으로 답변합니다.")
        
        # 참고 페이지 링크 추가
        st.markdown("### 참고 페이지")
        st.markdown("[📚 <한신그룹 - 터지는 릴스 자료> 바로가기](https://smart-jumper-b33.notion.site/185312cc7a5980aaa201f0303e1f7c10)")
        
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
                        4. 답변할 때는 릴스 강의의 어떤 부분을 참고했는지 명시하면서 설명해주세요.
                        5. 답변 후에는 다음 형식으로 자체 검증 결과를 추가해주세요:
                           
                           [검증 결과]
                           - 답변 정확도: (0-100%)
                           - 참고한 강의 내용: (구체적인 부분 명시)
                           - 강의 내용 범위 준수 여부: (예/아니오)
                        
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
