# -- DataBase information -----------------------------------------------------
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

charger_place = {0:"공동주택", 1:"휴게소", 2:"직장", 3:"공공건물"}
charger_type = {0:"완속", 1:"급속"}
charger_target = {0:"all", 1:"입주민"}
charger_opTime = {0:24, 1:[9,18]}
member_type = {0:"회원", 1:"로밍회원", 2:"비회원"}
dc_tz = {0:"새벽", 1:"오전", 2:"오후", 3:"밤"} #급속 충전기 이용현황 참조

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

