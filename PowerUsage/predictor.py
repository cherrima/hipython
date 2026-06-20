import joblib
import pandas as pd

features_kor = ['월', '일자', '시간', '요일', '주말여부', '휴일여부', '기온', '풍속', '습도', '강수량', '생산구분', '생산량']
features_eng = ['month', 'day', 'hour', 'weekday', 'weekend', 'holiday', 'temperature', 'windspeed', 'humidity', 'rainfall', 'op_code', 'output']


def predict_peak(input_df) :

    # 1 입력 데아터를 통한 
    # 1. 저장된 모델 파일 불러오기
    regressor_full_path = "./model/xgb_regressor_full.pkl"
    regressor_weather_path = "./model/xgb_regressor_weather.pkl"
    regressor_blind_path = "./model/xgb_regressor_blind.pkl"

    work_df = input_df.copy()
    # 컬럼명 일괄 변경
    work_df.columns = features_kor

    # 2. 입력데아터에 따라 Regressor 선택
    # 2.1. 생산 데아터 확인
   
    if ( work_df['생산구분'].dtype in ['int64', 'int32'] ) :
        xgb_regressor = joblib.load(regressor_full_path)
        print("Full Model")
    elif ( work_df['기온'].dtype in ['float64', 'float32'] ) :
        xgb_regressor = joblib.load(regressor_weather_path)
        print("Weather Model")
        work_df = work_df.drop(columns=['생산구분', '생산량'], errors='ignore')
    else :
        xgb_regressor = joblib.load(regressor_blind_path)
        print("Blind Model")
        work_df = work_df.drop(columns=['기온', '풍속', '습도', '강수량', '생산구분', '생산량'], errors='ignore')

    # 2. 예측 수행 (X_test 등 예측에 사용할 데이터가 필요합니다)
    # 예: pred = xgb_regressor_weather.predict(X_test_weather)

    print("모델 로드 완료 및 예측 준비가 되었습니다.")

    # print('xgb_regressor :', xgb_regressor )

    # print('work_df :', work_df.columns )

    pred_y = xgb_regressor.predict(work_df)

    # '시간' 컬럼 추가 (0부터 23까지)

    pred_df = pd.DataFrame(pred_y, columns=['peak_15', 'peak_30', 'peak_45', 'peak_60'])
    
    # 시간 컬럼 추가 : 0 ~ 23
    pred_df.insert(0, 'hour', range(24))

    # 정수형으로 반올림하여 회신
    return pred_df.round().astype(int)