import pandas as pd
import re

def split_into_chunks(text, max_chars=800):
    # 문장 단위로 분리 (마침표, 느낌표, 물음표 뒤에 공백이 오는 경우)
    sentences = re.split(r'(?<=[요죠다!?.])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_length = len(sentence)
        
        if current_length + sentence_length > max_chars and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks

# CSV 파일 읽기
df = pd.read_csv('영상편집 교육 영상.csv')

# text 컬럼만 추출하여 하나의 텍스트로 합치기
full_text = ' '.join(df['text'].astype(str))

# 청크 분리
chunks = split_into_chunks(full_text)

# 새로운 DataFrame 생성 (text 컬럼만 포함)
chunks_df = pd.DataFrame({'text': chunks})

# CSV 파일로 저장
chunks_df.to_csv('영상편집 교육 영상.csv', index=False, encoding='utf-8-sig')

print(f"총 {len(chunks)}개의 청크로 분리되었습니다.")
for i, chunk in enumerate(chunks, 1):
    print(f"청크 {i} 길이: {len(chunk)}자")