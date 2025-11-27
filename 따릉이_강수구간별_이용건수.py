import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 경로
file_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/강수구간별_평균이용건수.csv"

# CSV 읽기
df = pd.read_csv(file_path)

# 한글 폰트 설정 (Mac 기준)
plt.rcParams['font.family'] = 'AppleGothic'

# 구간 라벨과 값
rain_bins = df['rain_bin']
rides = df['rides']

plt.figure(figsize=(8,6))
plt.bar(rain_bins, rides, color='skyblue')
plt.xlabel('강수 구간')
plt.ylabel('평균 이용 건수')
plt.title('강수 구간별 평균 따릉이 이용량')

# 각 막대 위에 실제 값 표시
for i, v in enumerate(rides):
    plt.text(i, v + 1000, f"{int(v):,}", ha='center', va='bottom')

plt.tight_layout()

# 그래프 저장
output_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/imgs/강수구간별_평균이용량_막대그래프.png"
plt.savefig(output_path, dpi=300)
plt.close()
