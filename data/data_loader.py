import pathlib, os
from datetime import datetime
import pandas as pd


class DataLoader():
    def __init__(self):
        pass

    def load_data(self, ymd):
        if ymd is None:
            ymd = datetime.now().strftime('%Y-%m-%d')
        APP_PATH = str(pathlib.Path(__file__).parent.parent.resolve())
        df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "bicycle.csv"))).astype({'YMDH': 'string'})
        df = df[df['YMDH'].map(lambda x: x[:8]) == ymd.replace('-', '')]
        df['EVN_TS'] = df['YMDH'].map(lambda x: datetime.strptime(x, '%Y%m%d%H'))
        df['HH'] = pd.to_numeric(df['YMDH'].map(lambda x: x[-2:]))
        return df

    def filter_data(self,
                    loaded_df: pd,
                    time: str,
                    is_stt_sel_all: list,
                    stt: list,
                    rent_return: str,
                    is_occurrence: bool,
                    geo_selected_data: dict,
                    geo_click_data: dict,
                    tab: str,
                    triggered_nm: str):

        triggered_id = triggered_nm.split('.')[0]
        triggered_key = triggered_nm.split('.')[1]
        stt_sel_all_return = []

        if triggered_id == 'stations-select-all-checklist' and is_stt_sel_all:
            stt_nm_lst = loaded_df['STT_NM'].unique().tolist()
            stt_sel_all_return = is_stt_sel_all

        if triggered_id == 'stations-select-all-checklist' and len(is_stt_sel_all) == 0:
            stt_nm_lst = []

        elif triggered_id == 'station_dropdown':
            stt_nm_lst = stt

        elif triggered_id == 'geo_graph_chart' and triggered_key == 'selectedData':
            stt_nm_lst = [item.get('hovertext') for item in geo_selected_data.get('points')]

        elif triggered_id == 'geo_graph_chart' and triggered_key == 'clickData':
            stt_nm_lst = [item.get('hovertext') for item in geo_click_data.get('points')]

        else:
            if is_stt_sel_all:
                stt_nm_lst = loaded_df['STT_NM'].unique().tolist()
                stt_sel_all_return = is_stt_sel_all
            else:
                stt_nm_lst = stt

        loaded_df = loaded_df[loaded_df['STT_NM'].isin(stt_nm_lst)]
        if tab == 'tab-analytic':
            low_time = time[0]
            high_time = time[1]
            loaded_df = loaded_df[(loaded_df['HH'] >= low_time) & (loaded_df['HH'] <= high_time)]
        # 실시간 보기의 경우 일단 전체 시간 선택
        elif tab == 'tab-realtime':
            pass

        if not is_occurrence and rent_return == '대여':
            loaded_df = loaded_df[['STT_ID', 'STT_NM', 'EVN_TS', 'XCOR', 'YCOR', 'RENT_CNT']].sort_values(by=['STT_ID','STT_NM','EVN_TS'], ascending=True)
            loaded_df = loaded_df.reset_index(drop=True)
            loaded_df['RENT_CUM'] = loaded_df \
                    .groupby(['STT_ID', 'STT_NM', 'XCOR', 'YCOR', 'EVN_TS']) \
                    .sum() \
                    .groupby(level=3) \
                    .cumsum() \
                    .reset_index()['RENT_CNT']
            yaxis = 'RENT_CUM'

        elif not is_occurrence and rent_return == '반납':
             loaded_df = loaded_df[['STT_ID', 'STT_NM', 'EVN_TS', 'XCOR', 'YCOR', 'RETURN_CNT']].sort_values(by=['STT_ID','STT_NM','EVN_TS'], ascending=True)
             loaded_df = loaded_df.reset_index(drop=True)
             loaded_df['RETURN_CUM'] = loaded_df \
                     .groupby(['STT_ID', 'STT_NM', 'XCOR', 'YCOR', 'EVN_TS']) \
                     .sum() \
                     .groupby(level=3) \
                     .cumsum() \
                     .reset_index()['RETURN_CNT']
             yaxis = 'RETURN_CUM'

        elif is_occurrence and rent_return == '대여':
             yaxis = 'RENT_CNT'

        elif is_occurrence and rent_return == '반납':
             yaxis = 'RETURN_CNT'

        return loaded_df, yaxis, stt_nm_lst, stt_sel_all_return

    @staticmethod
    def get_default_df():
        # Empty Dataframe일 경우 geo_chart의 지도가 나오지 않으므로 Default DataFrame 생성후 리턴
        return pd.DataFrame({'STT_ID':[0],
                             'STT_NM':[''],
                             'EVN_TS':[datetime.now()],
                             'XCOR':[126.97072510625634],
                             'YCOR':[37.55441681177937],
                             'RENT_CNT':[0],
                             'RETURN_CNT':[0],
                             'RETURN_CUM':[0],
                             'RENT_CUM':[0]})