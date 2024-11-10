from dash import html, dcc
import plotly.express as px
from charts.chart_base import ChartBase
from data.data_loader import DataLoader


class GeoChart(ChartBase):
    def __init__(self):
        super().__init__()

    def geo_graph(self):
        return html.Div(
            id='geo_graph_main',
            className="main-charts-class",
            children=[
                dcc.Graph(
                    id="geo_graph_chart",
                    figure=px.scatter_mapbox(DataLoader.get_default_df(),
                                             lat='stt_lttd',
                                             lon='stt_lgtd',
                                             size='rent_cnt',
                                             mapbox_style='open-street-map',
                                             hover_name='stt_nm',
                                             hover_data=['rent_cnt'],
                                             zoom=11,
                                             height=700,
                                             animation_frame='crt_dttm',
                                             animation_group='rent_cnt'
                                             ).update_layout(
                        margin={"r": 0, "t": 0, "l": 0, "b": 0},
                    ),
                    config={'scrollZoom': True},

                )
            ]
        )

    def generate_geo_graph_figure(self, filtered_df, tab, yaxis):
        if filtered_df.empty:
            filtered_df = DataLoader.get_default_df()
        if tab == 'tab-analytic':
            return [
                self.generate_section_banner("따릉이 대여/반납 현황 Map"),
                dcc.Graph(
                    id="geo_graph_chart",
                    figure=px.scatter_mapbox(filtered_df,
                                             lat='stt_lttd',
                                             lon='stt_lgtd',
                                             size=yaxis,
                                             mapbox_style='open-street-map',
                                             hover_name='stt_nm',
                                             hover_data=[yaxis, 'crt_dttm'],
                                             zoom=11,
                                             height=700,
                                             color_continuous_scale=[[0, 'green'], [1.0, 'red']],
                                             color=yaxis,
                                             animation_frame='crt_dttm',
                                             animation_group=yaxis
                                             ).update_layout(
                                                margin={"r":0,"t":0,"l":0,"b":0},
                                             ),
                    config={'scrollZoom':True},

                )
            ]
        elif tab == 'tab-realtime':
            filtered_df = filtered_df[filtered_df['crt_dttm'] == filtered_df['crt_dttm'].max()]

            return [
                self.generate_section_banner("따릉이 대여/반납 현황 Map"),
                dcc.Graph(
                    id="geo_graph_chart",
                    figure=px.scatter_mapbox(filtered_df,
                                             lat='stt_lttd',
                                             lon='stt_lgtd',
                                             size=yaxis,
                                             mapbox_style='open-street-map',
                                             hover_name='stt_nm',
                                             hover_data=[yaxis],
                                             zoom=11,
                                             height=700,
                                             ).update_layout(
                                                margin={"r":0,"t":0,"l":0,"b":0},
                                             ),
                    config={'scrollZoom':True},

                )
            ]

