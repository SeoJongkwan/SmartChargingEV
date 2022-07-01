#DB information
host = "ev.i-on.net"
dbname = "evehicle"
user = "evehicle"
password = "iloveyou"
port = "5432"
table = ["charger_rawmessage", "charger_chargerusage"]

#station name, station code, charger code, charger num
station_info = [
    ('광주보건환경연구원','1802','1','305'),
    ('인덕원 IT밸리','1371','5','378'),
    ('해오름 휴게소','1848','1','405'),
    ('국민차매매단지 공항점','1846',['1','2'],['408','409'])
]

charger_place = {0:"직장", 1:"상업시설", 2:"편의시설", 3:"지식산업센터", 4:"주차시설", 5:"기타시설"}
charger_type = {0:"완속", 1:"급속"}
charger_target = {0:"all", 1:"입주민"}
charger_optime = {0:24, 1:[9,18]}
charger_region = {0:"서울", 1:"경기", 2:"인천"}
member_type = {0:"회원", 1:"로밍회원", 2:"비회원"}
dc_tz = {0:"새벽", 1:"오전", 2:"오후", 3:"밤"}
weekday = [(0, "mon"), (1, "tue"), (2, "wed"), (3, "thu"), (4, "fri"), (5, "sat"), (6, "sun")]
week_type = [(0, "주중"), (1,"주말")]

distance = [
    (50, '3km 이내'),
    (40, '5km 이내')
]

charger_density = [
    (20, '30 이상'),
    (18, '20 ~ 30'),
    (16, '10 ~ 20'),
    (14, '10 미만')
]

accessibility = [
    (10, '주차시설'),
    (8, '상업시설'),
    (6, '편의시설'),
    (4, '직장'),
    (2, '기타시설')
]

avg_num_users = [
    (5, '평균 이하'),
    (0, '평균 이상')
]

charging_fee = [
    (5, '무료'),
    (0, '유료')
]

unable_charge = [
    (5, '5회 이하'), # 횟수 변경 가능
    (0, '5회 이상')
]

#value는 min 의미(ex.20분), 90분 이상은 특정값 정의 -> component.py의 utilization_group 함수에서 사용
minutes_by_utilization = {1: 20, 2: 40, 3: 60, 4: 90, 5: 200}


# -- Message Type information ---------------------------------------------------
mt_dict = {
    '05': ['Access Request', '충전기<-서버'],
    '09': ['Cancel Request', '충전기<-서버'],
    '0D': ['FW Upgrade Request', '충전기<-서버', 'v1.0'],
    '0E': ['FW Upgrade Response', '충전기->서버', 'v1.0'],
    '0F': ['Charger Reboot Request', '충전기<-서버', 'v1.0'],
    '10': ['Charger Reboot Response', '충전기->서버', 'v1.0'],
    '15': ['Device Status Report', '충전기->서버'],
    '16': ['Charging Status Report', '충전기->서버'],
    '1A': ['Device Status Report ACK', '충전기<-서버'],
    '1B': ['Charging Status Report ACK', '충전기<-서버'],
    '22': ['Device Init Request', '충전기->서버'],
    '23': ['Device Init Response', '충전기<-서버'],
    '24': ['RF Card Device Status Report', '충전기->서버', 'v0.2'],
    '25': ['RF Card Status Report ACK / IC Card Payment Response', '충전기<-서버', 'v0.2'],
    '26': ['IC Card Payment Response', '충전기->서버', 'v0.5'],
    '27': ['RF Card Auth Cancel Report', '충전기->서버', 'v0.5'],
    '28': ['RF/IC Card Auth Cancel Response', '충전기<-서버', 'v0.5'],
    '29': ['IC Card Auth Cancel Report', '충전기->서버', 'v0.6'],
    'all': ['All Message Type']
}

