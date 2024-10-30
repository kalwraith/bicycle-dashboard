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
                                             lat='YCOR',
                                             lon='XCOR',
                                             size='RENT_CNT',
                                             mapbox_style='open-street-map',
                                             hover_name='STT_NM',
                                             hover_data=['RENT_CNT'],
                                             zoom=11,
                                             height=700,
                                             animation_frame='EVN_TS',
                                             animation_group='RENT_CNT'
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
                                             lat='YCOR',
                                             lon='XCOR',
                                             size=yaxis,
                                             mapbox_style='open-street-map',
                                             hover_name='STT_NM',
                                             hover_data=[yaxis, 'EVN_TS'],
                                             zoom=11,
                                             height=700,
                                             color_continuous_scale=[[0, 'green'], [1.0, 'red']],
                                             color=yaxis,
                                             animation_frame='EVN_TS',
                                             animation_group=yaxis
                                             ).update_layout(
                                                margin={"r":0,"t":0,"l":0,"b":0},
                                             ),
                    config={'scrollZoom':True},

                )
            ]
        elif tab == 'tab-realtime':
            filtered_df = filtered_df[filtered_df['EVN_TS'] == filtered_df['EVN_TS'].max()]

            return [
                self.generate_section_banner("따릉이 대여/반납 현황 Map"),
                dcc.Graph(
                    id="geo_graph_chart",
                    figure=px.scatter_mapbox(filtered_df,
                                             lat='YCOR',
                                             lon='XCOR',
                                             size=yaxis,
                                             mapbox_style='open-street-map',
                                             hover_name='STT_NM',
                                             hover_data=[yaxis],
                                             zoom=11,
                                             height=700,
                                             ).update_layout(
                                                margin={"r":0,"t":0,"l":0,"b":0},
                                             ),
                    config={'scrollZoom':True},

                )
            ]

