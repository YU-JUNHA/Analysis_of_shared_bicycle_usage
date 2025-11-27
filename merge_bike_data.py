import pandas as pd
import glob
import os

# 1️⃣ 파일 경로 패턴에 맞는 파일 불러오기
files = sorted(glob.glob("서울특별시 공공자전거 대여이력 정보_24*.csv"))
df_list = []

# 2️⃣ 병합
for file in files:
    print(f"📂 Loading {os.path.basename(file)} ...")
    try:
        temp = pd.read_csv(file, encoding='cp949')
    except UnicodeDecodeError:
        temp = pd.read_csv(file, encoding='euc-kr')

    # 3️⃣ 필요한 컬럼만 선택
    cols = ['대여일시', '반납일시', '이용시간(분)', '이용거리(M)', '생년', '성별']
    temp = temp[cols]

    # 4️⃣ 누락값 제거
    temp = temp.dropna(subset=cols)

    df_list.append(temp)

# 5️⃣ 전체 병합
bike_all = pd.concat(df_list, ignore_index=True)

# 6️⃣ 최종 CSV 저장
out_path = "서울특별시 공공자전거 대여이력 정보_24.csv"
bike_all.to_csv(out_path, index=False, encoding='utf-8-sig')

print(f"✅ 병합 완료: {len(bike_all):,} rows 저장됨 → {out_path}")
