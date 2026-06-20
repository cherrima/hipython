# Generated from: power_db_management.ipynb

import requests
import datetime
import urllib3
import os
import pandas as pd
from urllib.parse import unquote
import dotenv
import sqlite3
import holidays

# HTTPS 경고 메시지 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''
    1. data.go.kr 사용자 등록 및 API 사용 등록하여 서비스-키를 발급받아야 함
    2. 서비스-키는 .env 파일에 숨겨서 보안성 확보
'''
def get_service_key():
    dotenv.load_dotenv()
    raw_key = os.getenv("SERVICE_KEY")
    return unquote(raw_key)

def get_sky_status(sky_code, pty_code):
    """하늘상태와 강수형태 코드를 조합해 한글 상태 반환"""
    pty_dict = {'1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}
    if pty_code in pty_dict and pty_code != '0':
        return pty_dict[pty_code]
    
    sky_dict = {'1': '맑음', '3': '구름많음', '4': '흐림'}
    return sky_dict.get(sky_code, '-')

def get_weather_forecast(pos=['99', '82']):
    serviceKey = get_service_key() 
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    # 발표 시각 설정
    now = datetime.now()
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    current_hour = now.hour
    past_times = [t for t in base_times if t <= current_hour]
    
    if not past_times:
        base_date = (now - datetime.timedelta(days=1)).strftime('%Y%m%d')
        base_time = "2300"
    else:
        base_date = now.strftime('%Y%m%d')
        base_time = f"{max(past_times):02d}00"

    # 울산 울주군 삼동면 암리 (중산기업) 기준 nx=99, ny=82
    params = {
        'serviceKey': serviceKey,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': pos[0], # '99',
        'ny': pos[1]  # '82'
    }

    try:
        response = requests.get(url, params=params, verify=False)
        res_json = response.json()

        if res_json['response']['header']['resultCode'] == '00':
            items = res_json['response']['body']['items']['item']
            weather_dict = {}

            for item in items:
                time_key = f"{item['fcstDate']} {item['fcstTime'][:2]}:00"
                category = item['category']
                value = item['fcstValue']

                if time_key not in weather_dict:
                    weather_dict[time_key] = {}
                if category in ['TMP', 'REH', 'PCP', 'WSD', 'SKY', 'PTY']:
                    weather_dict[time_key][category] = value

            data_list = []
            for time_str, d in sorted(weather_dict.items()):
                # 강수량(PCP) 숫자 변환 로직
                pcp_raw = d.get('PCP', '강수없음')
                if pcp_raw == '강수없음':
                    pcp_val = 0.0
                else:
                    try:
                        # "1.0mm" 등에서 숫자만 추출
                        pcp_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', pcp_raw)))
                    except:
                        pcp_val = 0.0

                data_list.append({
                    '예보시각': time_str,
                    '상태': get_sky_status(d.get('SKY'), d.get('PTY')),
                    'SKY': d.get('SKY'),
                    'PTY': d.get('PTY'),
                    '기온': float(d.get('TMP', 0)),
                    '습도': int(d.get('REH', 0)),
                    '풍속': float(d.get('WSD', 0)),
                    '강수량': pcp_val
                })
            
            df = pd.DataFrame(data_list)

            # print(f"[{base_date} {base_time} 발표] 울산 삼동면 날씨 예보 (DataFrame)")
            # print("-" * 110)
            # print(df.to_string(index=False)) 
            # print("-" * 110)

            return df
            
        else:
            print(f"API 오류: {res_json['response']['header']['resultMsg']}")
            return None
            
    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
        return None



def register_weather(weather_df):
    
    # DB File Path 지정 - DB 변경 시 수정
    db_path = './db/PowerMgt.db'
    df = weather_df.copy()
    
    # [수정] '20260319 15:00' 형태의 문자열에서 직접 추출
    # date: '20260319' 부분 추출 후 '2026-03-19'로 변환
    df['date'] = df['예보시각'].str[:4] + '-' + df['예보시각'].str[4:6] + '-' + df['예보시각'].str[6:8]
    
    # hour: '15:00'에서 앞의 두 글자('15')만 추출하여 정수 변환
    # '20260319 15:00' 구조이므로 index 9부터 2글자가 시간입니다.
    df['hour'] = df['예보시각'].str[9:11].astype(int)
    
    # DB 테이블 컬럼 순서 (date, hour, temperature, humidity, windspeed, rainfall, status)
    # 입력 DF의 컬럼명이 '기온', '습도' 등 한글인 경우를 가정합니다.
    data_to_db = df[['date', 'hour', '기온', '습도', '풍속', '강수량', '상태']].values.tolist()
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # PK(date, hour) 중복 시 REPLACE(Update) 실행
        sql = """
        INSERT OR REPLACE INTO WeatherForecast 
        (date, hour, temperature, humidity, windspeed, rainfall, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        cur.executemany(sql, data_to_db)
        conn.commit()
        print(f"성공: {len(data_to_db)}건의 데이터가 등록/업데이트되었습니다.")
        
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        conn.rollback()
        
    finally:
        conn.close()


def register_calendar(year):
    """
    입력받은 연도(year)의 365일(또는 366일) 데이터를 생성하여 
    Calendar 테이블에 저장합니다.
    """
    db_path = './db/PowerMgt.db'
    
    # 1. 해당 연도의 날짜 범위 생성
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # 2. 한국 공휴일 정보 가져오기
    kr_holidays = holidays.KR(years=year)
    
    calendar_data = []
    
    for dt in date_range:
        # 날짜 정보 추출
        date_str = dt.strftime('%Y-%m-%d')
        y = dt.year
        m = dt.month
        d = dt.day
        
        # 요일 (Pandas: 0:월 ~ 6:일 -> 요청: 1:월 ~ 7:일)
        weekday = dt.weekday() + 1
        
        # 주말 여부 (토:6, 일:7 이면 1, 아니면 0)
        weekend = 1 if weekday >= 6 else 0
        
        # 공휴일 여부 (한국 공휴일 리스트에 있으면 1)
        is_holiday = 1 if dt in kr_holidays else 0
        
        calendar_data.append((date_str, y, m, d, weekday, weekend, is_holiday))
    
    # 3. DB 저장
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 중복 방지를 위해 INSERT OR REPLACE 사용
        sql = """
        INSERT OR REPLACE INTO Calendar 
        (date, year, month, day, weekday, weekend, holiday) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.executemany(sql, calendar_data)
        conn.commit()
        print(f"성공: {year}년 달력 데이터 {len(calendar_data)}건이 등록되었습니다.")
        
    except sqlite3.Error as e:
        print(f"DB 오류: {e}")
        conn.rollback()
    finally:
        conn.close()



def register_electricity_tariff(file_path):
    
    # DB 파일 경로 지정
    db_path = './db/PowerMgt.db'
    
    # 1. CSV 로드 (첫 번째 컬럼 '시간'을 인덱스로 사용)
    # 이미지 구조상 첫 컬럼은 시간(0~23), 이후 1월~12월 컬럼이 있음
    df = pd.read_csv(file_path)
    
    # 첫 번째 컬럼명을 'hour'로 변경 (만약 '시간' 등으로 되어 있다면)
    df.columns.values[0] = 'hour'
    
    # 2. Matrix 구조를 세로로 풀기 (Unpivot / Melt)
    # 'hour'를 기준으로 각 '월' 컬럼들을 행으로 변환
    df_melted = df.melt(id_vars=['hour'], var_name='month_raw', value_name='bill_rate')
    
    # 3. 데이터 가공
    # '1월', '2월' 문자열에서 숫자만 추출하여 정수형으로 변환
    df_melted['month'] = df_melted['month_raw'].str.replace('월', '').astype(int)
    
    # DB 컬럼 순서에 맞게 정리 [month, hour, bill_rate]
    final_data = df_melted[['month', 'hour', 'bill_rate']].values.tolist()
    
    # 4. DB 저장
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 복합키(month, hour) 중복 시 덮어쓰기
        sql = "INSERT OR REPLACE INTO ElectricityTariff(month, hour, bill_rate) VALUES (?, ?, ?)"
        
        cur.executemany(sql, final_data)
        conn.commit()
        print(f"성공: 총 {len(final_data)}건의 요율 데이터가 등록되었습니다.")
        
    except sqlite3.Error as e:
        print(f"DB 오류: {e}")
        conn.rollback()
    finally:
        conn.close()

# --- 실행 ---
# register_electricity_tariff('electricity_tariff.csv')


def register_operation_result(csv_path):
    """
    power_estimate.csv 데이터를 읽어 OperationResult 테이블에 저장합니다.
    """
    db_path = './db/PowerMgt.db'
    
    # 1. CSV 로드
    df = pd.read_csv(csv_path)
    
    # 2. 데이터 전처리
    # '예보시각'('20260319 15:00' 형태 문자열 가정) -> date, hour 분리
    df['date'] = df['날짜_시간'].str[:4] + '-' + df['날짜_시간'].str[4:6] + '-' + df['날짜_시간'].str[6:8]
    
    # 3. 요청하신 컬럼 매칭 (CSV 컬럼명 -> DB 컬럼명)
    # [date, hour, op_code, manpower, output, peak_15, peak_30, peak_45, peak_60, power_usage, bill_rate]
    mapping = {
        '생산구분': 'op_code',
        '공장인원': 'manpower',
        '생산량': 'output',
        '15분': 'peak_15',
        '30분': 'peak_30',
        '45분': 'peak_45',
        '60분': 'peak_60',
        '추정사용전력량': 'power_usage',
        '전기요금(계절)': 'bill_rate'
    }
    
    # 필요한 컬럼만 추출하여 리스트로 변환
    data_to_db = []
    for _, row in df.iterrows():
        data_to_db.append((
            row['date'],
            row['시간'],
            row['생산구분'],
            row['공장인원'],
            row['생산량'],
            row['15분'],
            row['30분'],
            row['45분'],
            row['60분'],
            row['추정사용전력량'],
            row['전기요금(계절)']
        ))

    # 4. DB 접속 및 실행
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        sql = """
        INSERT OR REPLACE INTO OperationResult 
        (date, hour, op_code, manpower, output, peak_15, peak_30, peak_45, peak_60, power_usage, bill_rate) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cur.executemany(sql, data_to_db)
        conn.commit()
        print(f"성공: {len(data_to_db)}건의 운영 결과 데이터가 처리되었습니다.")
        
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        conn.rollback()
        
    finally:
        conn.close()

# --- 실행 예시 ---
# register_operation_result('power_estimate.csv')


def get_weather_info(target_dt=None):
    """
    지정된 일시(기본값: 현재 시각) 기준 가장 최근 과거의 날씨 정보를 반환
    """
    db_path = './db/PowerMgt.db'
    
    print(target_dt)
    
    # 인자가 없으면 현재 시각 사용
    if target_dt is None:
        target_dt = datetime.now()
    
    target_date = target_dt.strftime('%Y-%m-%d')
    target_hour = target_dt.hour

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # 입력 시점 포함, 가장 가까운 과거 데이터 1건 조회
            query = """
                SELECT * FROM WeatherForecast 
                WHERE date = ? AND hour == ?
            """
            
            cur.execute(query, (target_date, target_hour))
            row = cur.fetchone()
            
            return dict(row) if row else None

    except sqlite3.Error as e:
        print(f"DB Error: {e}")
        return None


def get_prediction_variables(target_date):
    """
    날씨 데이터가 없더라도 24시간 행 구조를 유지하며 데이터를 조회합니다.
    """
     
    db_path= './db/PowerMgt.db'
    conn = sqlite3.connect(db_path)
    
    # 입력된 날짜에서 '월' 추출 (예: '2024-05-20' -> '05')
    target_month = int(target_date.split('-')[1])
    
    # print("Target Month :", target_month)
    
    # 0~23시까지의 가상 시간축(Time Backbone)을 생성하여 조인의 기준으로 삼음
    query = f"""
    
    WITH RECURSIVE hours(h) AS (
        SELECT 0 UNION ALL SELECT h + 1 FROM hours WHERE h < 23
    )
    SELECT 
        '{target_date}' AS Date,
        h.h AS hour,
        -- WeatherForecast (데이터 없을 시 NULL)
        W.temperature,
        W.humidity,
        W.windspeed,
        W.rainfall,
        -- OperationForecast
        O.op_code,
        -- O.manpower,
        O.output,
        -- Calendar
        C.weekday,
        C.weekend,
        C.holiday
        -- OperationResult
        -- E.bill_rate  -- 월/시간 기준 요금표에서 조회
    FROM hours h
    LEFT JOIN WeatherForecast W 
        ON W.date = '{target_date}' AND W.hour = h.h
    LEFT JOIN OperationForecast O 
        ON O.date = '{target_date}' AND O.hour = h.h
    LEFT JOIN Calendar C 
        ON C.date = '{target_date}'
    -- LEFT JOIN ElectricityTariff E 
        -- ON E.month = {target_month} AND E.hour = h.h
    ORDER BY h.h ASC;
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        # 만약 공란을 NaN 대신 빈 문자열('')로 출력하고 싶다면 아래 주석 해제
        df = df.fillna('')
        return df
        
    except Exception as e:
        print(f"조회 중 오류 발생: {e}")
        return None
    finally:
        conn.close()

# 사용 예시
# df = get_prediction_variables('2024-05-20')
# print(df)


