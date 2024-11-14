import dash
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


# 탭 선택에 따라 분기
@app.callback(
    Output("date-time-picker-container", "children"),
    Input("tab-selector", "value"),
    [State('date-selector-store','data'),
     State('time-selector-store','data')]
)
def tab_selector(tab_value, date, time_range):
    if date is not None:
        selected_date = date
    else:
        selected_date = datetime.now().strftime('%Y-%m-%d')

    if time_range is not None:
        selected_time_range = time_range
    else:
        selected_time_range = [0,23]
    tab_contents = menu_selector.generate_tab_contents(tab_value, selected_date, selected_time_range)

    return tab_contents


# tab-realtime 선택시 date-selector, time-selector는 없는 ID 이므로 해당 input callback은 별도 분리
@app.callback(
    [Output('date-selector-store','data', allow_duplicate=True),
     Output('time-selector-store','data', allow_duplicate=True),
     Output('trigger-nm-store', 'data', allow_duplicate=True),
     Output('loadingbar-store','data', allow_duplicate=True)],
    Input('date-selector', 'date'),
    Input('time-selector', 'value'),
    prevent_initial_call=True
)
def save_date_time(date, time_range):
    triggered_nm = [p["prop_id"] for p in callback_context.triggered][0]
    triggered_id = triggered_nm.split('.')[0]

    return date, time_range, triggered_id, 'show'


# 매 분 Dashboard update 하기 위한 콜백 함수
@app.callback(
    [Output('led-cur-date','value'),
     Output('led-cur-time','value')],
    Input('update-every-60sec','n_intervals'),
    prevent_initial_call=True
)
def update_led(intervals):
    now_date = datetime.now().strftime('%Y.%m.%d')
    now_time = datetime.now().strftime('%H:%M')
    return now_date, now_time


# 사용자가 Action 수행시 loading bar를 우선 뜨게 하고 input 값은 store에 저장해둔다.
# Action에 대한 response는 generate_all_charts 메서드에서 수행
@app.callback(
    [Output('stations-select-all-checklist-store','data'),
     Output('station_dropdown-store','data'),
     Output('rent-return-selector-store','data'),
     Output('cumul-occur-toggle-store','data'),
     Output('geo_graph_chart-store','data'),
     Output('loadingbar-store','data', allow_duplicate=True),
     Output('trigger-nm-store', 'data', allow_duplicate=True)],
    [Input('update-every-60sec','n_intervals'),
     Input("tab-selector", "value"),
     Input('stations-select-all-checklist','value'),
     Input('station_dropdown','value'),
     Input('rent-return-selector','value'),
     Input('cumul-occur-toggle','value'),
     Input("geo_graph_chart", "selectedData"),
     Input("geo_graph_chart", "clickData")
     ],
    prevent_initial_call=True
)
def store_data_n_lodingbar(interval, tab, stt_chk_all, stt_drpdwn, rr_sel, co_tggl, gc_sel, gc_clck):
    triggered_nm = [p["prop_id"] for p in callback_context.triggered][0]
    geo_target = {}
    print(f'store_data_n_lodingbar: {triggered_nm}')
    if triggered_nm:
        triggered_id = triggered_nm.split('.')[0]
        triggered_key = triggered_nm.split('.')[1]

        if (triggered_id == 'geo_graph_chart' and gc_sel is None and gc_clck is None) or \
                (triggered_id == 'update-every-60sec' and tab == 'tab-analytic'):
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        if triggered_id == 'geo_graph_chart' and (gc_sel or gc_clck):
            geo_target = gc_sel if gc_sel is not None else gc_clck

        return stt_chk_all, stt_drpdwn, rr_sel, co_tggl, geo_target, 'show', triggered_id

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# 사용자 Action에 대한 실제적인 response 수행하는 콜백
# reponse를 마친 후 loading bar를 close 한다.
@app.callback(
    [Output('geo_graph_main','children'),
     Output('rent-return-live-graph','figure'),
     Output("station_dropdown", "options"),
     Output("station_dropdown", "value"),
     Output('stations-select-all-checklist','value'),
     Output('loadingbar-store','data', allow_duplicate=True)],
     Input('trigger-nm-store', 'data'),
    [State("tab-selector", "value"),
     State('date-selector-store','data'),
     State('time-selector-store','data'),
     State('stations-select-all-checklist-store','data'),
     State('station_dropdown-store','data'),
     State('rent-return-selector-store','data'),
     State('cumul-occur-toggle-store','data'),
     State('geo_graph_chart-store','data')],
    prevent_initial_call=True
)
def generate_all_charts(trigger_nm, tab, date, time, is_chk_all, stt, rent_return, is_occurrence, geo_target):
    global loaded_df
    cur_date = datetime.now().strftime('%Y-%m-%d')
    if trigger_nm is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update ,dash.no_update

    if (trigger_nm == 'update-every-60sec' or trigger_nm == 'tab-selector') and tab == 'tab-realtime':
        loaded_df = data_loader.load_data(cur_date)

    elif trigger_nm == 'tab-selector' and tab == 'tab-analytic' and date:
        loaded_df = data_loader.load_data(date)

    elif trigger_nm == 'date-selector':
        loaded_df = data_loader.load_data(date)

    # 로드된 DataFrame 내 모든 Station 리스트
    all_stt_nm_lst = loaded_df['stt_nm'].unique().tolist()
    filtered_df, yaxis, sel_stt_nm_lst, stt_sel_all_return = data_loader.filter_data(loaded_df,
                                                                                     time,
                                                                                     is_chk_all,
                                                                                     stt,
                                                                                     rent_return,
                                                                                     is_occurrence,
                                                                                     geo_target,
                                                                                     tab,
                                                                                     trigger_nm
                                                                                     )
    # chart & graph update
    new_geo_graph = geo_chart.generate_geo_graph_figure(filtered_df, tab, yaxis)
    new_time_chart = time_chart.generate_time_chart_figure(filtered_df, yaxis)

    return new_geo_graph, new_time_chart, all_stt_nm_lst, sel_stt_nm_lst, stt_sel_all_return, 'hide'


# loading bar 컨트롤
@app.callback(
    Output("loadingbar", "style"),
    Input('loadingbar-store','data')
)
def control_loading_bar(data):
    if data == 'show':
        return {
            "display": "flex",
            "position": "fixed",
            "top": "50%",
            "left": "50%",
            "transform": "translate(-50%, -50%)",
            "zIndex": "1000",
        }
    else:
        return {
            "display": "none",
            "position": "fixed",
            "top": "50%",
            "left": "50%",
            "transform": "translate(-50%, -50%)",
            "zIndex": "1000",
        }


@app.callback(
    output=[Output("cumulative-text", "style"),
            Output("occurrence-text", "style")],
    inputs=Input("cumul-occur-toggle", "value")
)
def toggle_select(value):
    return menu_selector.cumul_occurr_select(value)


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
