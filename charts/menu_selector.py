from dash import html, dcc
from charts.chart_base import ChartBase
import dash_daq as daq
from datetime import datetime


class MenuSelector(ChartBase):
    def __init__(self):
        super().__init__()


    def get_menu_container(self):
        return [html.Div(
                    id='analytic-realtime-tabs',
                    className='menu-selector',
                    children=[
                        dcc.Store(id='date-selector-store',storage_type="session"),
                        dcc.Store(id='time-selector-store',storage_type="session"),
                        dcc.Store(id='need-reload-data-store', storage_type="session"),
                        dcc.Store(id='stations-select-all-checklist-store', storage_type="session"),
                        dcc.Store(id='station_dropdown-store', storage_type="session"),
                        dcc.Store(id='rent-return-selector-store', storage_type="session"),
                        dcc.Store(id='cumul-occur-toggle-store', storage_type="session"),
                        dcc.Store(id='geo_graph_chart-store', storage_type="session"),
                        dcc.Store(id='trigger-nm-store', storage_type="session"),
                        dcc.Store(id='loadingbar-store', storage_type="session"),
                        dcc.Interval(id='update-every-60sec', interval=60000),
                        dcc.Tabs(
                            id='tab-selector',
                            value='tab-analytic',
                            className="custom-tabs",
                            children=[
                                dcc.Tab(
                                    id="analytic-tab",
                                    label="기간 분석",
                                    value="tab-analytic",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                                dcc.Tab(
                                    id="realtime-tab",
                                    label="실시간 현황",
                                    value="tab-realtime",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    id='date-time-picker-container',
                    className='menu-selector',
                ),
                html.Div(
                    id='time-graph-station-dropdown',
                    className='menu-selector',
                    children=[
                        self.generate_section_banner("따릉이 정류소 선택"),
                        html.Br(),
                        dcc.Checklist(
                            id='stations-select-all-checklist',
                            options=['모두 선택'],
                            value=['모두 선택']
                        ),
                        dcc.Dropdown(
                            id='station_dropdown',
                            options=[],
                            multi=True
                        ),
                        html.Br(),
                        html.Br()
                    ]
                ),
                html.Div(
                    id='time-graph-type-dropdown',
                    className='menu-selector',
                    children=[
                        self.generate_section_banner("따릉이 대여/반납 선택"),
                        html.Br(),
                        dcc.RadioItems(id='rent-return-selector', options=['대여', '반납'], value='대여'),
                        html.Br(),
                        html.Br()
                    ]
                ),
                html.Div(
                    id='graph-type-container',
                    className='menu-selector',
                    children=[
                        html.Label(id="graph-type-label", children="Graph 출력 유형 선택"),
                        html.Br(),
                        html.Div(
                            id='cumulative-occurrence-selector',
                            children=[
                                html.P(id='cumulative-text',children=['누적량']),
                                daq.ToggleSwitch(
                                    id='cumul-occur-toggle',
                                    size=70,
                                    value=True      # False: Cululative / True: Occurrence
                                ),
                                html.P(id='occurrence-text',children=['발생량'])
                            ]
                        ),
                        html.Br(),
                        html.Br()
                    ]
                )
            ]

    def generate_tab_contents(self, tab, last_date, time_range):
        if tab == 'tab-analytic':
            return (
                html.Div(
                    id='date-selector-container',
                    className='menu-selector',
                    children=[
                        html.Br(),
                        html.Label(id="date-select-label", children="분석 날짜 선택"),
                        html.Br(),
                        dcc.DatePickerSingle(
                        #dmc.DatePicker(
                            id='date-selector',
                            date=last_date,
                            display_format='Y/M/D'
                        ),
                        html.Br(),
                        html.Br()
                    ]
                ),
                html.Div(
                    id='time-selector-container',
                    className='menu-selector',
                    children=[
                        html.Label(id="time-select-label", children="분석 시간 선택"),
                        html.Br(),
                        dcc.RangeSlider(0, 23, 1, value=time_range, id='time-selector'),
                        html.Br(),
                        html.Br()
                    ]
                ),
                html.A(
                    id='led-cur-date',
                    style={'display':'none'},
                ),
                html.A(
                    id='led-cur-time',
                    style={'display': 'none'},
                )
            )


        elif tab == 'tab-realtime':
            now_dt = datetime.now()
            now_day = now_dt.strftime('%Y.%m.%d')
            now_time = now_dt.strftime('%H:%M')
            return [(
                html.Div(
                    id='empty-date-time',
                    children=[
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.P('Current Time'),
                        html.Div(
                            id='current-time-led',
                            className='led-display',
                            children=[
                                daq.LEDDisplay(
                                    id="led-cur-date",
                                    value=now_day,
                                    color="#92e0d3",
                                    backgroundColor="#1e2130",
                                    size=30,
                                ),
                                daq.LEDDisplay(
                                    id="led-cur-time",
                                    value=now_time,
                                    color="#92e0d3",
                                    backgroundColor="#1e2130",
                                    size=30,
                                )
                            ]
                        ),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br()

                    ]
                )
            )]

    def cumul_occurr_select(self, value):
        if value:  # True: Occurrence / False: Cululative
            return {}, {'color':'#92e0d3'}
        else:
            return {'color': '#92e0d3'}, {}
