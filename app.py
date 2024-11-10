from dash import Dash, Output, Input, State, callback_context
from datetime import datetime
from layout import Layout
from charts.time_chart import TimeChart
from charts.menu_selector import MenuSelector
from charts.geo_chart import GeoChart
from data.data_loader import DataLoader


# 객체 생성
time_chart = TimeChart()
menu_selector = MenuSelector()
geo_chart = GeoChart()
data_loader = DataLoader()
app = Dash(__name__,suppress_callback_exceptions=True)

layout = Layout(app)
app.layout = layout.main_layout()
loaded_df = DataLoader.get_default_df()


@app.callback(
    Output("date-time-picker-container", "children"),
    Input("tab-selector", "value"),
    [State('selected-date-store','data'),
     State('selected-time-store','data')]
)
def tab_selector(tab_value, date, time_range):
    if date is not None:
        selected_date = date
    else:
        selected_date = datetime.now().strftime('%Y-%m-%d')

    if time_range is not None:
        selected_time_range = time_range
    else:
        selected_time_range = [8,18]
    tab_contents = menu_selector.generate_tab_contents(tab_value, selected_date, selected_time_range)
    return tab_contents


# date-selector와 time-selector는 analytic 탭에서만 활성화되는 id 이므로
# Graph update 통합 callback의 Input에 직접 넣지 않고 dcc.Store에 값을 저장한다.
# 대신 Graph update 통합 callback이 발생하도록 is-changed-date-time-store 값을 update해준다.
@app.callback(
    [Output('selected-date-store','data'),
     Output('selected-time-store','data'),
     Output('is-changed-date-time-store','data')],
    [Input('date-selector','date'),
     Input('time-selector','value')]
)
def store_date(date, time):
    triggered_nm = [p["prop_id"] for p in callback_context.triggered][0]
    triggered_id = triggered_nm.split('.')[0]
    if triggered_id == 'date-selector':
        is_changed_date_time = 'date'
    else:
        is_changed_date_time = 'time'
    return date, time, is_changed_date_time


# 매 분 Dashboard update 하기 위한 콜백 함수
@app.callback(
    [Output('led-cur-date','value'),
     Output('led-cur-time','value')],
    Input('update-every-60sec','n_intervals')
)
def update_led(intervals):
    global loaded_df
    now_date = datetime.now().strftime('%Y.%m.%d')
    now_time = datetime.now().strftime('%H:%M')

    return now_date, now_time


# Graph update 통합 callback 함수
@app.callback(
    [Output('geo_graph_main','children'),
     Output('rent-return-live-graph','figure'),
     Output("station_dropdown", "options"),
     Output("station_dropdown", "value"),
     Output('stations-select-all-checklist','value')],
    [Input('stations-select-all-checklist','value'),
     Input('station_dropdown','value'),
     Input('rent-return-selector','value'),
     Input('cumul-occur-toggle','value'),
     Input("geo_graph_chart", "selectedData"),
     Input("geo_graph_chart", "clickData"),
     Input('tab-selector','value'),
     Input('update-every-60sec','n_intervals'),
     Input('is-changed-date-time-store','data')],
    [State('selected-date-store','data'),
     State('selected-time-store','data')]
)
def generate_all_charts(is_stt_sel_all, stt, rent_return, is_occurrence, geo_selected_data, geo_click_data, tab, intervals, is_date_time_changed, date, time):
    global loaded_df
    cur_date = datetime.now().strftime('%Y-%m-%d')
    triggered_nm = [p["prop_id"] for p in callback_context.triggered][0]
    triggered_id = triggered_nm.split('.')[0]

    # 실시간 현황에서 1분 update 발생 또는 분석탭에서 실시간 탭으로 변경했을 때 당일 기준으로 데이터 reload
    if (triggered_id == 'update-every-60sec' or triggered_id == 'tab-selector') and tab == 'tab-realtime':
        loaded_df = data_loader.load_data(cur_date)

    # 분석탭에서 날짜를 변경했을 경우 변경한 날짜로 데이터 reload
    elif triggered_id == 'is-changed-date-time-store' and is_date_time_changed == 'date':
        loaded_df = data_loader.load_data(date)

    all_stt_nm_lst = loaded_df['stt_nm'].unique().tolist()

    # 입력 파라미터에 따라 dataframe 가공
    filtered_df, yaxis, sel_stt_nm_lst, stt_sel_all_return = data_loader.filter_data(loaded_df,
                                                                                 time,
                                                                                 is_stt_sel_all,
                                                                                 stt,
                                                                                 rent_return,
                                                                                 is_occurrence,
                                                                                 geo_selected_data,
                                                                                 geo_click_data,
                                                                                 tab,
                                                                                 triggered_nm
                                                                                 )

    # chart & graph update
    new_geo_graph = geo_chart.generate_geo_graph_figure(filtered_df, tab, yaxis)
    new_time_chart = time_chart.generate_time_chart_figure(filtered_df, yaxis)

    return new_geo_graph, new_time_chart, all_stt_nm_lst, sel_stt_nm_lst, stt_sel_all_return


@app.callback(
    output=[Output("cumulative-text", "style"),
            Output("occurrence-text", "style")],
    inputs=Input("cumul-occur-toggle", "value")
)
def toggle_select(value):
    return menu_selector.cumul_occurr_select(value)


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
