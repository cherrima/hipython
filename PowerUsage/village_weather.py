import requests
import datetime
import urllib3
import os
import pandas as pd
from urllib.parse import unquote
from dotenv import load_dotenv

# HTTPS 경고 메시지 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_service_key():
    load_dotenv()
    raw_key = os.getenv("SERVICE_KEY")
    return unquote(raw_key)

def get_sky_status(sky_code, pty_code):
    """하늘상태와 강수형태 코드를 조합해 한글 상태 반환"""
    pty_dict = {'1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}
    if pty_code in pty_dict and pty_code != '0':
        return pty_dict[pty_code]
    
    sky_dict = {'1': '맑음', '3': '구름많음', '4': '흐림'}
    return sky_dict.get(sky_code, '-')

def get_weather_forecast(pos_nx, pos_ny):
    serviceKey = get_service_key() 
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    # 발표 시각 설정
    now = datetime.datetime.now()
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
        'nx': pos_nx, # '99',
        'ny': pos_ny  # '82'
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
                    'SKY코드': d.get('SKY'),
                    'PTY코드': d.get('PTY'),
                    '기온(℃)': float(d.get('TMP', 0)),
                    '습도(%)': int(d.get('REH', 0)),
                    '풍속(m/s)': float(d.get('WSD', 0)),
                    '강수량(mm)': pcp_val
                })
            
            df = pd.DataFrame(data_list)

            print(f"[{base_date} {base_time} 발표] 울산 삼동면 날씨 예보 (DataFrame)")
            print("-" * 110)
            print(df.to_string(index=False)) 
            print("-" * 110)

            return df
            
        else:
            print(f"API 오류: {res_json['response']['header']['resultMsg']}")
            return None
            
    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
        return None
