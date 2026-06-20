/* 1. 날씨예보 : WeatherForecast (PK: date, hour) */
DROP TABLE IF EXISTS WeatherForecast;
CREATE TABLE WeatherForecast (
    date         TEXT NOT NULL,    -- 예보 일자 (YYYY-MM-DD 형식 권장)
    hour         INTEGER NOT NULL, -- 0-23
    temperature  REAL NOT NULL,
    humidity     REAL NOT NULL,
    windspeed    REAL NOT NULL,
    rainfall     REAL NOT NULL,
    status       TEXT,
	update_date  TEXT,
    PRIMARY KEY (date, hour)       -- 날짜와 시간의 조합을 기본키로 설정
);

/* 2. 운영예측 : OperationForecast (PK: date, hour) */
DROP TABLE IF EXISTS OperationForecast;
CREATE TABLE OperationForecast (
    date         TEXT NOT NULL,
    hour         INTEGER NOT NULL,
    op_code      INTEGER,
    manpower     REAL,
    output       INTEGER,
    peak_15      INTEGER,
    peak_30      INTEGER,
    peak_45      INTEGER,
    peak_60      INTEGER,
    PowerUsage   REAL,
    PRIMARY KEY (date, hour)
);

/* 3. 운영결과 : OperationResult (PK: date, hour) */
DROP TABLE IF EXISTS OperationResult;
CREATE TABLE OperationResult (
    date         TEXT NOT NULL,
    hour         INTEGER NOT NULL,
    op_code      INTEGER,
    manpower     REAL,
    output       INTEGER,
    peak_15      INTEGER,
    peak_30      INTEGER,
    peak_45      INTEGER,
    peak_60      INTEGER,
    power_usage  REAL,
    bill_rate    REAL,
    PRIMARY KEY (date, hour)
);

/* 4. 달력 : Calendar (PK: date) */
DROP TABLE IF EXISTS Calendar;
CREATE TABLE Calendar (
    date         TEXT PRIMARY KEY, -- 달력은 일자별로 유일하므로 단일 PK
    year         INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    day          INTEGER NOT NULL,
    weekday      INTEGER NOT NULL,
    weekend      INTEGER NOT NULL,
    holiday      INTEGER NOT NULL DEFAULT 0
);

/* 5. 전기요율표 : ElectricityRate (PK: month, hour) */
DROP TABLE IF EXISTS ElectricityTariff;
CREATE TABLE ElectricityTariff (
    month        INTEGER NOT NULL,
    hour         INTEGER NOT NULL,
    bill_rate    REAL NOT NULL,
    PRIMARY KEY (month, hour)
);
