from datetime import datetime
import pandas as pd
import boto3
import awswrangler as wr
import os, pathlib


AWS_USER_NM = 'py-dash'
STG_BUCKET_NM = 's3://athena-query-result-hjkim'


class DataLoader():
    def __init__(self):
        self.set_aws_key()

    def set_aws_key(self):
        home_path = os.path.expanduser('~')
        key_csv = f'{AWS_USER_NM}_accessKeys.csv'
        try:
            key_file = os.path.join(home_path,'Downloads',key_csv)
        except:
            raise Exception('키 파일 찾을 수 없음')

        key_df = pd.read_csv(key_file)
        self.access_key = key_df.iloc[0]['Access key ID']
        self.secret_key = key_df.iloc[0]['Secret access key']

    # def load_data(self, ymd):
    #     if ymd is None:
    #         ymd = datetime.now().strftime('%Y-%m-%d')
    #     APP_PATH = str(pathlib.Path(__file__).parent.parent.resolve())
    #     df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "bicycle.csv"))).astype({'ymdh': 'string'})
    #     df = df[df['ymdh'].map(lambda x: x[:8]) == ymd.replace('-', '')]
    #     df['crt_dttm'] = df['ymdh'].map(lambda x: datetime.strptime(x, '%Y%m%d%H'))
    #     df['hh'] = pd.to_numeric(df['ymdh'].map(lambda x: x[-2:]))
    #
    #     return df

    def load_data(self, ymd):
        ymd = ymd.replace('-', '')
        session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="ap-northeast-2"  # 원하는 리전으로 설정
        )

        # 10분 구간으로 rent_cnt, return_cnt 집계하는 쿼리
        sql = f'''
                    select
                        stt_id
                        ,stt_nm
                        ,crt_dttm
                        ,sum(rent_cnt)                   as rent_cnt
                        ,sum(return_cnt)                 as return_cnt
                        ,cast(min(stt_lttd) as double)   as stt_lttd
                        ,cast(min(stt_lgtd) as double)   as stt_lgtd
                    from (
                        select
                            stt_id
                            ,stt_nm
                            ,date_add('minute',FLOOR(minute(crt_dttm)/10)*10, date_trunc('hour',crt_dttm)) as crt_dttm
                            ,rent_cnt
                            ,return_cnt
                            ,stt_lttd
                            ,stt_lgtd
                        from lesson.bicycle_rent_info
                        where ymd = '{ymd}'
                    )
                    group by stt_id, stt_nm, crt_dttm
                    order by stt_id, stt_nm, crt_dttm
                '''

        df = wr.athena.read_sql_query(
            sql=sql,
            database="lesson",
            s3_output=STG_BUCKET_NM,
            boto3_session=session
        )
        df['hh'] = df['crt_dttm'].dt.hour
        print('data load complete')
        return df


    def filter_data(self,
                    loaded_df: pd,
                    time: str,
                    is_stt_sel_all: list,
                    stt: list,
                    rent_return: str,
                    is_occurrence: bool,
                    geo_target: dict,
                    tab: str,
                    triggered_nm: str):

        triggered_id = triggered_nm.split('.')[0]
        stt_sel_all_return = []

        if triggered_id == 'stations-select-all-checklist' and is_stt_sel_all:
            stt_nm_lst = loaded_df['stt_nm'].unique().tolist()
            stt_sel_all_return = is_stt_sel_all

        if triggered_id == 'stations-select-all-checklist' and len(is_stt_sel_all) == 0:
            stt_nm_lst = []

        elif triggered_id == 'station_dropdown':
            stt_nm_lst = stt

        elif triggered_id == 'geo_graph_chart':
            if geo_target:
                stt_nm_lst = [item.get('hovertext') for item in geo_target.get('points')]
            else:
                stt_nm_lst = []
        else:
            if is_stt_sel_all:
                stt_nm_lst = loaded_df['stt_nm'].unique().tolist()
                stt_sel_all_return = is_stt_sel_all
            else:
                stt_nm_lst = stt

        stt_nm_lst = stt_nm_lst if stt_nm_lst is not None else []
        loaded_df = loaded_df[loaded_df['stt_nm'].isin(stt_nm_lst)]
        if tab == 'tab-analytic':
            low_time = time[0] if time is not None else 0
            high_time = time[1] if time is not None else 23
            loaded_df = loaded_df[(loaded_df['hh'] >= low_time) & (loaded_df['hh'] <= high_time)]
        # 실시간 보기의 경우 일단 전체 시간 선택
        elif tab == 'tab-realtime':
            pass

        yaxis = 'return_cnt'
        if not is_occurrence and rent_return == '대여':
            loaded_df = loaded_df[['stt_id', 'stt_nm', 'crt_dttm', 'stt_lttd', 'stt_lgtd', 'rent_cnt']].sort_values(by=['stt_id','stt_nm','crt_dttm'], ascending=True)
            loaded_df = loaded_df.reset_index(drop=True)
            loaded_df['rent_cum'] = loaded_df \
                    .groupby(['stt_id', 'stt_nm', 'stt_lttd', 'stt_lgtd', 'crt_dttm']) \
                    .sum() \
                    .groupby(level=3) \
                    .cumsum() \
                    .reset_index()['rent_cnt']
            yaxis = 'rent_cum'

        elif not is_occurrence and rent_return == '반납':
             loaded_df = loaded_df[['stt_id', 'stt_nm', 'crt_dttm', 'stt_lttd', 'stt_lgtd', 'return_cnt']].sort_values(by=['stt_id','stt_nm','crt_dttm'], ascending=True)
             loaded_df = loaded_df.reset_index(drop=True)
             loaded_df['return_cum'] = loaded_df \
                     .groupby(['stt_id', 'stt_nm', 'stt_lttd', 'stt_lgtd', 'crt_dttm']) \
                     .sum() \
                     .groupby(level=3) \
                     .cumsum() \
                     .reset_index()['return_cnt']
             yaxis = 'return_cum'

        elif is_occurrence and rent_return == '대여':
             yaxis = 'rent_cnt'

        elif is_occurrence and rent_return == '반납':
             yaxis = 'return_cnt'

        return loaded_df, yaxis, stt_nm_lst, stt_sel_all_return

    @staticmethod
    def get_default_df():
        # Empty Dataframe일 경우 geo_chart의 지도가 나오지 않으므로 Default DataFrame 생성후 리턴
        return pd.DataFrame({'stt_id':[0],
                             'stt_nm':[''],
                             'crt_dttm':[datetime.now()],
                             'stt_lttd':[37.5544168117],
                             'stt_lgtd':[126.9707251062],
                             'rent_cnt':[0],
                             'return_cnt':[0],
                             'return_cum':[0],
                             'rent_cum':[0],
                             'hh': [0]})

t = DataLoader()
#t.load_data('2024-11-08')
