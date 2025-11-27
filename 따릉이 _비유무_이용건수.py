import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 경로
file_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/비유무_평균이용건수.csv"

# CSV 읽기
df = pd.read_csv(file_path)

# 한글 폰트 설정 (Mac 기준)
plt.rcParams['font.family'] = 'AppleGothic'

# 레이블
labels = ['비 없음', '비 있음']

# 실제 값과 비율을 함께 표시하는 함수
def func(pct, allvals):
    absolute = int(round(pct/100.*sum(allvals)))
    return "{:,}\n({:.1f}%)".format(absolute, pct)

# 원그래프 그리기
plt.figure(figsize=(6,6))
plt.pie(
    df['mean_rides'], 
    labels=labels, 
    autopct=lambda pct: func(pct, df['mean_rides']), 
    startangle=90, 
    colors=['skyblue','lightgreen']
)
plt.title('비/비 없음 평균 따릉이 이용량')
plt.axis('equal')  # 원을 동그랗게 표시

# 그래프 저장
output_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/비유무_평균이용량_원그래프.png"
plt.savefig(output_path, dpi=300)
plt.close()
