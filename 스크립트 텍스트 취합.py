import pandas as pd

# CSV 파일 읽기
df = pd.read_csv('릴스 강의_정리.csv')

# 모든 스크립트를 하나의 텍스트로 합치기
full_text = ' '.join(df['스크립트'].astype(str))

# 불필요한 따옴표와 줄바꿈 제거
full_text = full_text.replace('"', '').replace('\n', ' ').strip()

# 연속된 공백을 하나의 공백으로 변경
full_text = ' '.join(full_text.split())

# 전체 텍스트를 새로운 CSV 파일로 저장
pd.DataFrame({'text': [full_text]}).to_csv('릴스 강의_전체텍스트.csv', index=False, encoding='utf-8-sig')

print("전체 텍스트 저장이 완료되었습니다.")
print(f"전체 텍스트 길이: {len(full_text)} 글자")