import pathlib, os
import pandas as pd
from dash import html
from datetime import datetime

class ChartBase:
    def __init__(self):
        self.is_occurrence = True
        self.is_realtime = True


    def generate_section_banner(self, title):
        return html.Div(className="section-banner", children=title)

    def build_banner(self, id):
        return html.Div(
            id=id,
            className="banner",
            children=[
                html.Div(
                    id="banner-text",
                    children=[
                        html.H5("Kafka & Spark 기반의 실시간 DATALAKE"),
                        html.H6("따릉이 대여소 실시간 DASHBOARD"),
                    ],
                ),
                html.Div(
                    id="banner-logo",
                    children=[
                        html.A(
                            html.Button(children="LEARN MORE"),
                            href="https://plotly.com/get-demo/",
                        )
                    ],
                ),
            ],
        )

    def _filter_df(self, df, rent_return, cumul_occur):
        yaxis = ''
        if cumul_occur == 'cumul' and rent_return == '대여':
            df['RENT_CUM'] = df['RENT_CNT'].cumsum()
            yaxis = 'RENT_CUM'

        elif cumul_occur == 'cumul' and rent_return == '반납':
            df['RETURN_CUM'] = df['RETURN_CNT'].cumsum()
            yaxis = 'RETURN_CUM'

        elif cumul_occur == 'occur' and rent_return == '대여':
            yaxis = 'RENT_CNT'

        elif cumul_occur == 'occur' and rent_return == '반납':
            yaxis = 'RETURN_CNT'

        return df, yaxis