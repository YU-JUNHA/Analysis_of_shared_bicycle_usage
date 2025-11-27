import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 경로
file_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/따릉이_시간별_이용건수.csv"

# CSV 읽기
df = pd.read_csv(file_path)

# 한글 폰트 설정 (Mac 기준)
plt.rcParams['font.family'] = 'AppleGothic'

# 막대그래프 그리기
plt.figure(figsize=(12,6))
plt.bar(df['hour'], df['total_rides'], color='orange')
plt.xlabel('시간대 (시)')
plt.ylabel('따릉이 이용 건수')
plt.title('시간대별 따릉이 이용량')
plt.xticks(df['hour'])  # 0~23시 모두 표시
plt.tight_layout()

# 그래프 저장
output_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/imgs/시간대별_따릉이_이용량.png"
plt.savefig(output_path, dpi=300)
plt.close()
