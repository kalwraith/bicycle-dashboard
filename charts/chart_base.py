from dash import html


class ChartBase:
    def __init__(self):
        pass

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