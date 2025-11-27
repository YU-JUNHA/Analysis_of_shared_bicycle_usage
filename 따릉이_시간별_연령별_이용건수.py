import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 경로
file_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/datas/따릉이_시간대x연령대_이용건수.csv"

# CSV 읽기
df = pd.read_csv(file_path)

# 한글 폰트 설정 (Mac 기준)
plt.rcParams['font.family'] = 'AppleGothic'

# 시간대(0~23)
hours = list(range(24))

# 연령대별 색상 지정
colors = {
    "10대 이하": "lightcoral",
    "10대": "red",
    "20대": "orange",
    "30대": "gold",
    "40대": "green",
    "50대": "blue",
    "60대": "purple",
    "70대": "brown",
    "80대": "pink",
    "90대 이상": "gray"
}

plt.figure(figsize=(14,8))

# 각 연령대별 꺾은선 그리기
for age_group in df['연령대']:
    plt.plot(hours, df.loc[df['연령대']==age_group].iloc[0,1:], 
             label=age_group, color=colors.get(age_group, 'black'), marker='o')

plt.xlabel('시간대 (시)')
plt.ylabel('이용 건수')
plt.title('시간대별 연령대별 따릉이 이용량')
plt.xticks(hours)
plt.legend(title='연령대')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# 그래프 저장
output_path = "/Users/yujunha/projects/Analysis_of_shared_bicycle_usage/imgs/시간대x연령대_이용량_라인그래프.png"
plt.savefig(output_path, dpi=300)
plt.close()
