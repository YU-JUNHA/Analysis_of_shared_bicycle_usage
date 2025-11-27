import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 경로
file_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/따릉이_나이별_이용건수.csv"

# CSV 읽기
df = pd.read_csv(file_path)

# 한글 폰트 설정 (Mac 기준)
plt.rcParams['font.family'] = 'AppleGothic'

# 막대그래프 그리기
plt.figure(figsize=(10,6))
plt.bar(df['연령대'], df['rides'], color='skyblue')
plt.xlabel('연령대')
plt.ylabel('따릉이 이용 건수')
plt.title('연령대별 따릉이 이용량')
plt.xticks(rotation=45)  # x축 레이블 회전
plt.tight_layout()

# 그래프를 파일로 저장
output_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/imgs/연령대별_따릉이_이용량.png"
plt.savefig(output_path, dpi=300)  # 해상도 300dpi

# 화면에 표시하지 않고 바로 저장 후 종료
plt.close()
