from dash import html
from charts.menu_selector import MenuSelector
from charts.time_chart import TimeChart
from charts.geo_chart import GeoChart


class Layout():
    def __init__(self, app):
        self.app = app
        self.time_chart = TimeChart()
        self.geo_chart = GeoChart()
        self.menu_selector = MenuSelector()

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
                            html.Button(id='github-button', className='link-button', children="github"),
                            href="https://github.com/kalwraith/yeardream_airflow/",
                            target="_blank"
                        ),
                        html.A(
                            html.Button(id='inflearn-button', className='link-button', children="Inflearn"),
                            href="https://plotly.com/get-demo/",
                            target="_blank"
                        )
                    ],
                ),
            ],
        )

    def main_layout(self):
        return html.Div(
            id="big-app-container",
            children=[
                self.build_banner('main-banner'),
                html.Div(
                    id="main-dashboard",
                    children=[
                        html.Div(
                            id="menu-container",
                            children=self.menu_selector.get_menu_container()
                            ),
                        html.Div(
                            id="loadingbar",
                            children=html.Img(src="assets/loadingbar.gif"),
                            style={
                                "display": "none",  # 기본적으로 숨김 상태
                                "position": "fixed",
                                "top": "50%",
                                "left": "50%",
                                "transform": "translate(-50%, -50%)",
                                "zIndex": "1000",
                            },
                        ),
                        html.Div(
                            id="chart-container",
                            children=[
                                self.geo_chart.geo_graph(),
                                self.time_chart.init_time_chart_figure(),
                            ]
                        )
                    ]
                )

            ]
    )