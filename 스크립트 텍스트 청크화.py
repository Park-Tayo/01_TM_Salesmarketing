import pandas as pd
import re

def split_into_chunks(text, max_chars=800):
    # 문장 단위로 분리 (마침표, 느낌표, 물음표 뒤에 공백이 오는 경우)
    # "요", "죠", "다" 등의 종결어미도 포함
    sentences = re.split(r'(?<=[요죠다!?.])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_length = len(sentence)
        
        # 현재 문장이 너무 길 경우 추가로 분리
        if sentence_length > max_chars:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            # 긴 문장을 쉼표나 접속사를 기준으로 분리
            sub_sentences = re.split(r'(?<=[,며고])\s+', sentence)
            for sub in sub_sentences:
                if len(sub.strip()) > 0:
                    if current_length + len(sub) > max_chars:
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                            current_chunk = []
                            current_length = 0
                    current_chunk.append(sub.strip())
                    current_length += len(sub)
            continue
            
        if current_length + sentence_length > max_chars:
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
df = pd.read_csv('릴스 강의_전체텍스트.csv')
text = df['text'].iloc[0]

# 청크로 분리
chunks = split_into_chunks(text)

# 결과를 DataFrame으로 변환
chunks_df = pd.DataFrame({
    'chunk_id': range(1, len(chunks) + 1),
    'text': chunks
})

# CSV 파일로 저장
chunks_df.to_csv('릴스 강의_AI청크.csv', index=False, encoding='utf-8-sig')

print(f"총 {len(chunks)}개의 청크로 분리되었습니다.")
for i, chunk in enumerate(chunks, 1):
    print(f"청크 {i} 길이: {len(chunk)}자")