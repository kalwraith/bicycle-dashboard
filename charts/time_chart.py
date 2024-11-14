from dash import html, dcc
import plotly.graph_objs as go
from charts.chart_base import ChartBase
import pandas as pd

class TimeChart(ChartBase):
    def __init__(self):
        super().__init__()


    def init_time_chart_figure(self):
        return html.Div(
            id="rent_return_live",
            className="main-charts-class",
            children=[
                self.generate_section_banner("따릉이 대여/반납 현황 시간대별 Graph"),
                dcc.Graph(
                    id="rent-return-live-graph",
                    figure=go.Figure(
                        {
                            "data": [
                                {
                                    "x": [],
                                    "y": [],
                                    "mode": "lines+markers",
                                    "name": 'STT_ID별 대여 건수',
                                    "line": {"color": "#f4d44d"},
                                }
                            ],
                            "layout": {
                                "margin": dict(t=40),
                                "hovermode": "closest",
                                "uirevision": 'test_col',
                                "paper_bgcolor": "rgba(0,0,0,0)",
                                "plot_bgcolor": "rgba(0,0,0,0)",
                                "legend": {"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
                                "font": {"color": "darkgray"},
                                "showlegend": True,
                                "xaxis": {
                                    "zeroline": False,
                                    "showgrid": False,
                                    "title": "시간",
                                    "showline": False,
                                    "domain": [0, 0.8],
                                    "titlefont": {"color": "darkgray"},
                                },
                                "yaxis": {
                                    "title": '정거장',
                                    "showgrid": False,
                                    "showline": False,
                                    "zeroline": False,
                                    "autorange": True,
                                    "titlefont": {"color": "darkgray"},
                                },
                                "autosize": True,
                            },
                        }
                    ),
                ),
            ],
        )


    def generate_time_chart_figure(self, filtered_df, yaxis):
        figure_dict = {'data': []}
        pd.set_option('display.max_columns', None)
        for stt_nm in filtered_df['stt_nm'].unique().tolist():
            if yaxis.endswith('cum'):
                    figure_dict['data'].append(
                    {
                        "x": filtered_df[filtered_df['stt_nm'] == stt_nm]['crt_dttm'].tolist(),
                        "y": filtered_df[filtered_df['stt_nm'] == stt_nm][yaxis].tolist(),
                        "mode": "lines+markers",
                        'fill': "tozeroy",
                        "name": stt_nm
                    }
                )
            else:
                figure_dict['data'].append(
                    {
                        "x": filtered_df[filtered_df['stt_nm'] == stt_nm]['crt_dttm'].tolist(),
                        "y": filtered_df[filtered_df['stt_nm'] == stt_nm][yaxis].tolist(),
                        "mode": "lines+markers",
                        "name": stt_nm
                    }
                )

        figure_dict['layout'] = {
            "margin": dict(t=40),
            "hovermode": "closest",
            "uirevision": 'test_col',
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            #"legend": {"font": {"color": "darkgray"}, "orientation": "v", "x": 0, "y": 1.1},
            "legend": {"font": {"color": "darkgray"}, "orientation": "v", "yanchor":"top","xanchor":"left","x": 1, "y": 1},
            "font": {"color": "darkgray"},
            "showlegend": True,
            "xaxis": {
                "zeroline": False,
                "showgrid": False,
                "title": "시간",
                "showline": False,
                "domain": [0, 0.8],
                "titlefont": {"color": "darkgray"},
            },
            "yaxis": {
                "title": '자전거 대수',
                "showgrid": False,
                "showline": False,
                "zeroline": False,
                "autorange": True,
                "titlefont": {"color": "darkgray"},
            },
            "autosize": True,
        }

        return figure_dict