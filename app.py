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

def verify_response(script, question, answer):
    try:
        verification = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                당신은 엄격한 답변 검증 전문가입니다.
                오직 주어진 릴스 강의 내용만을 기준으로 답변을 검증해주세요.
                릴스 강의 내용에 명시되지 않은 내용이 답변에 포함되어 있다면 이를 반드시 지적해주세요.
                
                다음 형식으로 답변해주세요:
                - 정확도 점수: (0-100)
                - 판단 근거: (릴스 강의의 어떤 부분을 참고했는지 구체적으로 명시)
                - 강의를 벗어난 내용: (릴스 강의에 없는 내용이 답변에 포함된 경우 지적)
                - 개선 제안: (필요한 경우)
                """},
                {"role": "user", "content": f"""
                스크립트: {script}
                질문: {question}
                답변: {answer}
                """}
            ],
            temperature=0,
            max_tokens=500
        )
        return verification.choices[0].message.content
    except Exception as e:
        return f"검증 중 오류 발생: {str(e)}"

# 메인 함수
def main():
    st.title("💬 릴스 강의 Q&A 챗봇")
    
    # 스크립트 로드
    script = load_script()
    
    # 사이드바에 시스템 프롬프트 표시 (선택사항)
    with st.sidebar:
        st.header("AI 챗봇 정보")
        st.info("이 AI 챗봇은 인스타그램 릴스 마케팅 강의 내용을 기반으로 답변합니다.")
        
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
                        당신은 주어진 릴스 강의 내용만을 기반으로 답변하는 Q&A 전문가입니다.
                        
                        중요한 규칙:
                        1. 오직 제공된 릴스 강의에 있는 내용만 사용하여 답변하세요.
                        2. 릴스 강의에 관련 내용이 없다면 "죄송하지만 주어진 강의 내용에서 해당 질문에 대한 정보를 찾을 수 없습니다"라고 답변하세요.
                        3. 릴스 강의의 내용을 벗어나는 일반적인 조언이나 추측은 하지 마세요.
                        4. 답변할 때는 릴스 강의의 어떤 부분을 참고했는지 명시하면서 설명해주세요.
                        
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
                        temperature=0.5,
                        max_tokens=1000
                    )
                    
                    assistant_response = response.choices[0].message.content
                    
                    # 답변 검증
                    with st.expander("답변 검증 결과 보기"):
                        verification_result = verify_response(script, prompt, assistant_response)
                        st.markdown(verification_result)
                    
                    st.markdown(assistant_response)
                    
                    # 어시스턴트 메시지 저장
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_response}
                    )
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 
