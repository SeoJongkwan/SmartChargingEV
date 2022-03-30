# -- DataBase information -----------------------------------------------------
host = "ev.i-on.net"
dbname = "evehicle"
user = "evehicle"
password = "iloveyou"
port = "5432"
table = ["charger_rawmessage", "charger_chargerusage"]

station_name = ["인덕원 IT밸리", "해오름 휴게소", "광주보건환경연구원", "국민차매매단지 공항점"]

member_type = ["회원", "로밍회원", "비회원"]

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

