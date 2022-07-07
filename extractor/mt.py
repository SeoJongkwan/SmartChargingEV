import pandas as pd
import json
import psycopg2
from tqdm import tqdm
from dateutil.relativedelta import relativedelta
from common import info

con = psycopg2.connect(host=info.host, dbname=info.dbname, user=info.user, password=info.password, port=info.port)
cursor = con.cursor()

print("<DB Info>")
print("dbname:", info.dbname + "\nhost:", info.host + "\nport:", info.port)

db_table = info.table[0]
print(f'table: {db_table} \n')

def parse_data(df):
    """
    :param df: original data pulled from DB
    :return: parsed json_data format
    """
    elem = []
    df1 = dict(df['json_data'])
    for i in tqdm(range(0,len(df1)), desc="json parsing"):
        elem.append(json.loads(df1[i]))
    df2 = pd.DataFrame(elem)
    return df2


def convert_status_code(df):
    """
    :param df: message type is Device Status
    status code value is converted int to hex
    :return: dataframe with hex column
    """
    hex_ds = []
    for i in df["Device Status"]:
        hex_ds.append('{0:02X}'.format(i))
    df["Device Status"] = hex_ds
    return df


def select(mt):
    """
    :param mt: message type predefined protocol specification ref. info.py -> mt_type
    :return: dataframe corresponding mt
    """
    if info.mt_dict.get(mt) is None:
        raise MessageTypeException
    print(f"message_type: {info.mt_dict[mt]}")

    if mt == 'all':
        raw_msg = f"SELECT * FROM {db_table}"

    else:
        cond = f"message_type = '{mt.lower()}'"  # value format is lower character in DB
        raw_msg = f"SELECT * FROM {db_table} WHERE {cond}"

    cursor.execute(raw_msg)
    raw = pd.DataFrame(cursor.fetchall())
    raw.columns = [desc[0] for desc in cursor.description]
    df = parse_data(raw)
    df1 = pd.concat([raw, df], axis=1)

    if mt == '15':
        df1 = convert_status_code(df1)
    return df1

def select_usage(table):
    """
    :param table: DB table name
    :return: result for select table
    """
    raw_msg = f'SELECT * FROM {table} ORDER BY "chStartTm" ASC'
    cursor.execute(raw_msg)
    df1 = pd.DataFrame(cursor.fetchall())
    df1.columns = [desc[0] for desc in cursor.description]
    return df1

def select_time(df, col, start, month):
    """
    :param df: target
    :param col: start date column
    :param start: specific start date
    :param month: relativedelta end date
    :return: apply date
    """
    end = start + relativedelta(months=month)
    df1 = df[(df[col] > str(start)) & (df[col] < str(end))].reset_index(drop=True)
    print("duration: {} ~ {}".format(start, end))
    return df1

def select_station(station_name, charger_code):
    """
   :param station_name: station name
   :return: result for select station
   """
    charger_id = '0' + str(charger_code)
    raw_msg = f"SELECT * FROM charger_station WHERE station_name='{station_name}' AND charger_id='{charger_id}'"
    cursor.execute(raw_msg)
    df1 = pd.DataFrame(cursor.fetchall())
    if df1.empty:
        print('\nEmpty information from charger_station table')
    else:
        df1.columns = [desc[0] for desc in cursor.description]
        return df1

def all_stations():
    """
   :return: result for all stations
   """
    raw_msg = "SELECT station_id, station_name, charger_id, address FROM charger_station"
    cursor.execute(raw_msg)
    df1 = pd.DataFrame(cursor.fetchall())
    if df1.empty:
        print('\nEmpty information from charger_station table')
    else:
        df1.columns = [desc[0] for desc in cursor.description]
        df1 = df1.sort_values(by=['station_name']).reset_index(drop=True)
        return df1