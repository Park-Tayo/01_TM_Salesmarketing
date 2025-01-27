import pandas as pd
import re

# 파일 읽기
with open(r"D:\cursor_ai\01_TM_Salesmarketing\터지는 릴스 (스크립트 및 슬라이드).md", 'r', encoding='utf-8') as file:
    content = file.read()

# 슬라이드 구분으로 텍스트 분리
sections = re.split(r'# 슬라이드 \d+(?:~\d+)?', content)
slide_numbers = re.findall(r'# 슬라이드 (\d+(?:~\d+)?)', content)

data = []
base_url = "https://docs.google.com/presentation/d/1E15oCcr1zNiuP3go01Yh1ao7PTvG9gqj/edit#slide=id.p"

for i, (section, slide_num) in enumerate(zip(sections[1:], slide_numbers)):  # sections[0]는 빈 문자열이므로 제외
    # 슬라이드 범위 처리
    if '~' in slide_num:
        start, end = map(int, slide_num.split('~'))
        slide_number = start  # 시작 슬라이드 번호 사용
    else:
        slide_number = int(slide_num)
    
    # 스크립트 텍스트 정리 (앞뒤 공백 제거)
    script = section.strip()
    
    # URL 생성
    url = f"{base_url}{slide_number}"
    
    data.append({
        '스크립트': script,
        '슬라이드': f'슬라이드 {slide_num}',
        'URL': url
    })

# DataFrame 생성
df = pd.DataFrame(data)

# CSV 파일로 저장
output_path = r"D:\cursor_ai\01_TM_Salesmarketing\스크립트_정리.csv"
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"CSV 파일이 생성되었습니다: {output_path}")
