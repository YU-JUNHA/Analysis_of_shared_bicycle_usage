import pandas as pd
import datetime
import numpy as np
IN_PATH = "서울특별시 공공자전거 대여이력 정보_24.csv"
IN_PATH2 = "SURFACE_ASOS_108_DAY_2024_2024_2025.csv"


# =====================================================================
# csv읽기 및 전반적인 결측치 전처리하고 df만들기
# =====================================================================

#자전거 csv
encodings_try = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]
last_err = None
df = None
for enc in encodings_try:
    try:
        df = pd.read_csv(IN_PATH, encoding=enc)
        break
    except Exception as e:
        last_err = e
if df is None:
    raise RuntimeError()

# 기대 컬럼 결측치 방지
required_cols = ['대여일시','반납일시','이용시간(분)','이용거리(M)','생년','성별']
df = df.dropna(subset=required_cols).copy()
df['대여일시'] = pd.to_datetime(df['대여일시'])
df['반납일시'] = pd.to_datetime(df['반납일시'])

#날씨 csv
for enc in encodings_try:
    try:
        df_rain = pd.read_csv(IN_PATH2, encoding=enc)
        print(f"✅ Loaded with encoding={enc}, rows={len(df):,}")
        break
    except Exception as e:
        last_err = e
if df_rain is None:
    raise RuntimeError(f"CSV 로딩 실패: {last_err}")

# 기대 컬럼 결측치 방지
required_cols = ['일시','일강수량(mm)']
df_rain['일시'] = pd.to_datetime(df_rain['일시'])
df_rain = df_rain.dropna(subset=required_cols).copy()


# =====================================================================
# 월별 공유자전거 이용 건 수 집계하기
# =====================================================================

df1 = df.copy()
df1['month'] = df1['대여일시'].dt.month
monthly = (
    df1.groupby('month')
      .size()
      .reset_index(name='total_rides')
      .rename(columns={'month': '월'})
      .sort_values('월')
)
monthly.to_csv("따릉이_월별_이용건수.csv", index=False, encoding="utf-8-sig")
print("따릉이_월별_이용건수 저장 완")

# =====================================================================
# 시간대별 따릉이 이용건수 확인
# =====================================================================

# 대여일시 기준으로 할 경우에 오래 이용하면 오차가 생길 수 있기에 중간시각 계산
df2 = df.copy()
midpoint = df2['대여일시'] + (df2['반납일시'] - df2['대여일시']) / 2
df2['midpoint'] = midpoint
df2['mid_hour'] = df2['midpoint'].dt.hour

hourly_total = (
    df2.groupby('mid_hour')
      .size()
      .reset_index(name='total_rides')
      .rename(columns={'mid_hour':'hour'})
      .sort_values('hour')
)

# 저장
hourly_total.to_csv("따릉이_시간별_이용건수.csv", index=False, encoding="utf-8-sig")
print("따릉이_시간별_이용건수 저장 완")

# ==============================================
# 3) 성별에 따른 이용량 → 따릉이_성별_이용건수.csv
# ==============================================
# ① 결측치 제거 + 문자열 변환
df3 = df.copy()
df3['성별'] = df3['성별'].astype(str).str.strip()   # 공백 제거
df3 = df3.dropna(subset=['성별'])

# ② 대문자로 통일
df3['성별'] = df3['성별'].str.upper()

# ③ 유효한 값만 남기기 (M, F만)
df3 = df3[df3['성별'].isin(['M', 'F'])]

# ④ 집계
by_gender = (
    df3.groupby('성별')
      .size()
      .reset_index(name='rides')
      .sort_values('rides', ascending=False)
)

# ⑤ 저장
by_gender.to_csv("따릉이_성별_이용건수.csv", index=False, encoding="utf-8-sig")
print("📦 Saved: 따릉이_성별_이용건수.csv")
# ==============================================
# 4) 생년에 따른 이용량 → 따릉이_나이별_이용건수.csv
#     (분석 용이하게 생년 오름차순)
# ==============================================
# 생년이 숫자로 들어있지 않다면 숫자 변환
# 기준연도 설정 (예: 데이터가 2024년이므로)
CURRENT_YEAR = 2024

# ① 생년 숫자화 + 결측치 제거
df4 = df.copy()
df4['생년'] = pd.to_numeric(df4['생년'], errors='coerce')
df4 = df4.dropna(subset=['생년'])
df4['생년'] = df4['생년'].astype(int)

# ② 비정상 생년 제거 (1925 이하 or 2020 이상)
df4 = df4[(df4['생년'] > 1925) & (df4['생년'] < 2020)]

# ③ 나이 계산
df4['나이'] = CURRENT_YEAR - df4['생년']

# ④ 연령대 구분 함수
def get_age_group(age):
    if age < 10:
        return "10대 이하"
    elif age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    elif age < 50:
        return "40대"
    elif age < 60:
        return "50대"
    elif age < 70:
        return "60대"
    elif age < 80:
        return "70대"
    elif age < 90:
        return "80대"
    else:
        return "90대 이상"

df4['연령대'] = df4['나이'].apply(get_age_group)

# ⑤ 연령대별 이용건수
by_agegroup = (
    df4.groupby('연령대')
      .size()
      .reset_index(name='rides')
      .sort_values('연령대')
)

# ⑥ 저장
by_agegroup.to_csv("따릉이_나이별_이용건수.csv", index=False, encoding='utf-8-sig')
print("📦 Saved: 따릉이_나이별_이용건수.csv (연령대 기준)")

# ===================================================================
# 5) 각 ‘시간’에 따른 ‘생년’별 이용량 → 따릉이_시간에따른생년별_이용건수.csv
#     - 중간시각 기준 hour 사용 (출퇴근 시간대 성인비율 확인 목적)
#     - Long format: hour, 생년, rides
#     - Wide가 필요하면 pivot 예시 주석 참고
# ===================================================================
# 기준연도 (데이터가 2024년이면 2024로, 2025년 분석이면 2025로 조정)
CURRENT_YEAR = 2024

# 복사본에서 작업 (앞 단계 영향 차단)
df5 = df.copy()

# 1) 생년 정제 → 비정상값 제거
df5['생년'] = pd.to_numeric(df5['생년'], errors='coerce')
df5 = df5.dropna(subset=['생년'])
df5['생년'] = df5['생년'].astype(int)
df5 = df5[(df5['생년'] > 1925) & (df5['생년'] < 2020)]

# 2) 연령대 계산
df5['나이'] = CURRENT_YEAR - df5['생년']

def age_to_group(age: int) -> str:
    if age < 10:   return "10대 이하"
    if age < 20:   return "10대"
    if age < 30:   return "20대"
    if age < 40:   return "30대"
    if age < 50:   return "40대"
    if age < 60:   return "50대"
    if age < 70:   return "60대"
    if age < 80:   return "70대"
    if age < 90:   return "80대"
    return "90대 이상"

df5['연령대'] = df5['나이'].apply(age_to_group)

# 3) 중간시각 기준 시간대(hour)
df5['midpoint'] = df5['대여일시'] + (df5['반납일시'] - df5['대여일시']) / 2
df5['hour'] = df5['midpoint'].dt.hour

# 4) 집계 → 피벗(행=연령대, 열=hour, 값=건수)
cross = (
    df5
      .groupby(['연령대', 'hour'])
      .size()
      .reset_index(name='rides')
      .pivot(index='연령대', columns='hour', values='rides')
)

# 5) 보기 좋게 정렬(연령대 순서, 0~23시 모두 포함), 결측은 0으로
age_order = ["10대 이하","10대","20대","30대","40대","50대","60대","70대","80대","90대 이상"]
cross = cross.reindex(index=age_order)                       # 연령대 행 순서
cross = cross.reindex(columns=range(24), fill_value=0)       # 0~23시 열 확정
cross = cross.fillna(0).astype(int)

# 6) 저장
cross.to_csv("따릉이_시간대x연령대_피벗.csv", encoding="utf-8-sig")
print("📦 Saved: 따릉이_시간대x연령대_피벗.csv (행=연령대, 열=시간대, 값=건수)")

# (참고) 와이드 피벗 예시:
# pivot = hour_birth.pivot(index='hour', columns='생년', values='rides').fillna(0).astype(int)
# pivot.to_csv("따릉이_시간에따른생년별_이용건수_wide.csv", encoding="utf-8-sig")

# 기준연도 (데이터가 2024년이면 2024로, 2025년 분석이면 2025로 조정)
CURRENT_YEAR = 2024

# 복사본에서 작업
df6 = df.copy()

# 1) 생년 정제 → 비정상값 제거
df6['생년'] = pd.to_numeric(df6['생년'], errors='coerce')
df6 = df6.dropna(subset=['생년'])
df6['생년'] = df6['생년'].astype(int)
df6 = df6[(df6['생년'] > 1925) & (df6['생년'] < 2020)]

# 2) 연령대 계산
df6['나이'] = CURRENT_YEAR - df6['생년']

def age_to_group(age: int) -> str:
    if age < 10:   return "10대 이하"
    if age < 20:   return "10대"
    if age < 30:   return "20대"
    if age < 40:   return "30대"
    if age < 50:   return "40대"
    if age < 60:   return "50대"
    if age < 70:   return "60대"
    if age < 80:   return "70대"
    if age < 90:   return "80대"
    return "90대 이상"

df6['연령대'] = df6['나이'].apply(age_to_group)

# 3) 요일(대여 시작 시각 기준): 0=월 ~ 6=일 → 한글 라벨
weekday_map = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
df6['weekday'] = df6['대여일시'].dt.weekday
df6['요일'] = df6['weekday'].map(weekday_map)

# 4) 집계 → 피벗(행=연령대, 열=요일, 값=건수)
cross_wday = (
    df6
      .groupby(['연령대', '요일'])
      .size()
      .reset_index(name='rides')
      .pivot(index='연령대', columns='요일', values='rides')
)

# 5) 보기 좋게 정렬(연령대 순서, 월~일 열 순서), 결측은 0으로
age_order = ["10대 이하","10대","20대","30대","40대","50대","60대","70대","80대","90대 이상"]
weekday_order = ["월","화","수","목","금","토","일"]
cross_wday = cross_wday.reindex(index=age_order)
cross_wday = cross_wday.reindex(columns=weekday_order, fill_value=0)
cross_wday = cross_wday.fillna(0).astype(int)

# 6) 저장
cross_wday.to_csv("따릉이_요일x연령대_피벗.csv", encoding="utf-8-sig")
print("📦 Saved: 따릉이_요일x연령대_피벗.csv (행=연령대, 열=요일, 값=건수)")


#########################################################################

df7 = df.copy()
daily_bike = (
    df7.assign(date=df7['대여일시'].dt.date)
        .groupby('date')
        .size()
        .reset_index(name='rides')
)
daily_bike['date'] = pd.to_datetime(daily_bike['date'])

# 2) 날씨: 날짜 + 비 여부
rain = df_rain.assign(
    date = df_rain['일시'].dt.normalize(),
    일강수량 = df_rain['일강수량(mm)'].fillna(0)
)
rain['rain_yn'] = (rain['일강수량'] > 0).astype(int)
rain['rain_bin'] = pd.cut(rain['일강수량'],
                        bins=[-0.001, 0, 5, 20, np.inf],
                        labels=['0:무강수','1:0~5mm','2:5~20mm','3:20mm+'])

# 3) 병합 & 간단 비교
merge_df = pd.merge(daily_bike, rain[['date','rain_yn','rain_bin','일강수량']], on='date', how='inner')

# 비 유무 평균
avg = merge_df.groupby('rain_yn')['rides'].mean()
no_rain, rain = avg.get(0, np.nan), avg.get(1, np.nan)
pct = (rain/no_rain - 1) * 100 if pd.notnull(no_rain) and pd.notnull(rain) else np.nan
print(f"무강수 평균: {no_rain:.1f}건, 강수일 평균: {rain:.1f}건, 차이: {pct:.1f}%")

# >>> 추가: 비 유무 평균을 CSV로 저장
avg_df = avg.reset_index().rename(columns={'rain_yn':'rain_yn','rides':'mean_rides'})
avg_df.to_csv("요약_비유무_평균이용건수.csv", index=False, encoding="utf-8-sig")
pd.DataFrame({
    "no_rain_mean":[round(no_rain,3)],
    "rain_mean":[round(rain,3)],
    "pct_diff_percent":[round(pct,3)]
}).to_csv("요약_비유무_변화율.csv", index=False, encoding="utf-8-sig")

# 강수량 구간별 평균
print("\n강수량 구간별 평균 이용건수:")
print(merge_df.groupby('rain_bin')['rides'].mean().round(1))

# >>> 추가: 강수량 구간별 평균을 CSV로 저장
by_bin = merge_df.groupby('rain_bin')['rides'].mean().round(3).reset_index()
by_bin.to_csv("요약_강수구간별_평균이용건수.csv", index=False, encoding="utf-8-sig")
