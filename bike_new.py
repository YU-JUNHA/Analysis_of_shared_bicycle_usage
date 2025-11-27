import pandas as pd
import datetime
import numpy as np


IN_PATH = "서울특별시 공공자전거 대여이력 정보_24.csv"
IN_PATH2 = "SURFACE_ASOS_108_DAY_2024_2024_2025.csv"

# =====================================================================
# csv읽기 및 전반적인 결측치 전처리하고 df만들기
# =====================================================================

# 자전거 csv
encodings_try = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]
last_err = None
df = None
for enc in encodings_try:
    try:
        df = pd.read_csv(IN_PATH, encoding=enc)
        break
    except Exception as e:
        last_err = e

# 기대 컬럼 결측치 방지
required_cols = ['대여일시','반납일시','이용시간(분)','이용거리(M)','생년','성별']
df = df.dropna(subset=required_cols).copy()
df['대여일시'] = pd.to_datetime(df['대여일시'])
df['반납일시'] = pd.to_datetime(df['반납일시'])

# 날씨 csv
df_rain = None  # 변경: 루프 전에 초기화(예외 시 NameError 방지)
for enc in encodings_try:
    try:
        df_rain = pd.read_csv(IN_PATH2, encoding=enc)
        break
    except Exception as e:
        last_err = e

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

hourly_total.to_csv("따릉이_시간별_이용건수.csv", index=False, encoding="utf-8-sig")
print("따릉이_시간별_이용건수 저장 완")

# =====================================================================
# 성별에 따른 이용량 확인
# =====================================================================

df3 = df.copy()
#대소문자 논값 섞여있어서 대문자로 통일 후 MF 말고 다 드롭
df3['성별'] = df3['성별'].astype(str).str.strip()
df3 = df3.dropna(subset=['성별'])
df3['성별'] = df3['성별'].str.upper()
df3 = df3[(df3['성별'] == 'M') | (df3['성별'] == 'F')] 

by_gender = (
    df3.groupby('성별')
      .size()
      .reset_index(name='rides')
      .sort_values('rides', ascending=False)
)

by_gender.to_csv("따릉이_성별_이용건수.csv", index=False, encoding="utf-8-sig")
print("따릉이_성별_이용건수 저장 완")

# =====================================================================
# 나이대에 따른 이용량 분류
# =====================================================================

CURRENT_YEAR = 2024

df4 = df.copy()
df4['생년'] = pd.to_numeric(df4['생년'], errors='coerce')
df4 = df4.dropna(subset=['생년'])
df4['생년'] = df4['생년'].astype(int)
df4 = df4[(df4['생년'] > 1925) & (df4['생년'] < 2020)]
df4['나이'] = CURRENT_YEAR - df4['생년']

def get_age_group(age):
    if age < 10:   return "10대 이하"
    elif age < 20: return "10대"
    elif age < 30: return "20대"
    elif age < 40: return "30대"
    elif age < 50: return "40대"
    elif age < 60: return "50대"
    elif age < 70: return "60대"
    elif age < 80: return "70대"
    elif age < 90: return "80대"
    else:          return "90대 이상"

df4['연령대'] = df4['나이'].apply(get_age_group)

by_agegroup = (
    df4.groupby('연령대')
      .size()
      .reset_index(name='rides')
      .sort_values('연령대')
)

by_agegroup.to_csv("따릉이_나이별_이용건수.csv", index=False, encoding='utf-8-sig')
print("따릉이_나이별_이용건수저장완")

# =====================================================================
# 시간대별 각 연령 사용량, 출퇴근 시간에 직장인들의 이용률이 올라가는지 보기 위한 지표
# =====================================================================

CURRENT_YEAR = 2024
df5 = df.copy()

df5['생년'] = pd.to_numeric(df5['생년'], errors='coerce')
df5 = df5.dropna(subset=['생년'])
df5['생년'] = df5['생년'].astype(int)
df5 = df5[(df5['생년'] > 1925) & (df5['생년'] < 2020)]
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
df5['midpoint'] = df5['대여일시'] + (df5['반납일시'] - df5['대여일시']) / 2
df5['hour'] = df5['midpoint'].dt.hour

cross = (
    df5
      .groupby(['연령대', 'hour'])
      .size()
      .reset_index(name='rides')
      .pivot(index='연령대', columns='hour', values='rides')
)

age_order = ["10대 이하","10대","20대","30대","40대","50대","60대","70대","80대","90대 이상"]
cross = cross.reindex(index=age_order)
cross = cross.reindex(columns=range(24), fill_value=0)
cross = cross.fillna(0).astype(int)

cross.to_csv("따릉이_시간대x연령대_이용건수.csv", encoding="utf-8-sig")
print("따릉이_시간대x연령대이용건수 저장 완")


# =====================================================================
# 위와 마찬가지로 출퇴근을 하는 월~금에 직장인 나이대의 사용량 증가를 보기 위한 지표
# =====================================================================

CURRENT_YEAR = 2024
df6 = df.copy()

df6['생년'] = pd.to_numeric(df6['생년'], errors='coerce')
df6 = df6.dropna(subset=['생년'])
df6['생년'] = df6['생년'].astype(int)
df6 = df6[(df6['생년'] > 1925) & (df6['생년'] < 2020)]
df6['나이'] = CURRENT_YEAR - df6['생년']
df6['연령대'] = df6['나이'].apply(age_to_group)

weekday_map = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
df6['weekday'] = df6['대여일시'].dt.weekday
df6['요일'] = df6['weekday'].map(weekday_map)

cross_wday = (
    df6
      .groupby(['연령대', '요일'])
      .size()
      .reset_index(name='rides')
      .pivot(index='연령대', columns='요일', values='rides')
)

age_order = ["10대 이하","10대","20대","30대","40대","50대","60대","70대","80대","90대 이상"]
weekday_order = ["월","화","수","목","금","토","일"]
cross_wday = cross_wday.reindex(index=age_order)
cross_wday = cross_wday.reindex(columns=weekday_order, fill_value=0)
cross_wday = cross_wday.fillna(0).astype(int)

cross_wday.to_csv("따릉이_요일x연령대_이용건수.csv", encoding="utf-8-sig")
print("따릉이_요일x연령대 저장 완")


# =====================================================================
# 비오는 날씨가 자전거 사용량에 어떤 영향을 미치는지 보기 위함
# 비오는 날 일 평균 사용량, 비 안 오는 날 일 평균 사용량을 확인하고 비가 올 경우 강수량에 따른 사용량까지도 확인
# =====================================================================


df7 = df.copy()
df7['date'] = df7['대여일시'].dt.date
daily_bike = (
    df7.groupby('date')
       .size()
       .reset_index(name='rides')
)
daily_bike['date'] = pd.to_datetime(daily_bike['date'])


rain = df_rain.copy()                                        
rain['date'] = pd.to_datetime(rain['일시']).dt.date   
rain['date'] = pd.to_datetime(rain['date']) 
rain['일강수량'] = rain['일강수량(mm)'].fillna(0)

rain['rain_yn'] = (rain['일강수량'] > 0).astype(int)

def rain_bin_func(v):     
    if v <= 0:
        return '0:무강수'
    elif v <= 5:
        return '1:0~5mm'
    elif v <= 20:
        return '2:5~20mm'
    else:
        return '3:20mm+'
rain['rain_bin'] = rain['일강수량'].apply(rain_bin_func)

merge_df = pd.merge(daily_bike, rain[['date','rain_yn','rain_bin','일강수량']], on='date', how='inner')

# 비 유무 평균
avg = merge_df.groupby('rain_yn')['rides'].mean()
no_rain_mean = avg.get(0, np.nan)
rain_mean = avg.get(1, np.nan)
pct = (rain_mean/no_rain_mean - 1) * 100 if pd.notnull(no_rain_mean) and pd.notnull(rain_mean) else np.nan
avg_df = avg.reset_index().rename(columns={'rain_yn':'rain_yn','rides':'mean_rides'})
avg_df.to_csv("비유무_평균이용건수.csv", index=False, encoding="utf-8-sig")

# 강수량 구간별 평균
by_bin = merge_df.groupby('rain_bin')['rides'].mean().round(3).reset_index()
by_bin.to_csv("강수구간별_평균이용건수.csv", index=False, encoding="utf-8-sig")
print("비유뮤_강수구간별_평균이용건수 저장 완")
print("끝~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")