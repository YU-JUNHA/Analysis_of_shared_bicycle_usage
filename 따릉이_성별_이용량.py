import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 경로
file_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/따릉이_성별_이용건수.csv"

# CSV 읽기
df = pd.read_csv(file_path)

# 한글 폰트 설정 (Mac 기준)
plt.rcParams['font.family'] = 'AppleGothic'

# 실제 값과 비율을 함께 표시하는 함수
def func(pct, allvals):
    absolute = int(pct/100.*sum(allvals))
    return "{:,}\n({:.1f}%)".format(absolute, pct)

# 원그래프 그리기
plt.figure(figsize=(6,6))
plt.pie(
    df['rides'], 
    labels=df['성별'], 
    autopct=lambda pct: func(pct, df['rides']), 
    startangle=90, 
    colors=['skyblue','pink']
)
plt.title('성별 따릉이 이용량')
plt.axis('equal')  # 원을 동그랗게 표시

# 그래프 저장
output_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/성별_따릉이_이용량_원그래프.png"
plt.savefig(output_path, dpi=300)
plt.close()
