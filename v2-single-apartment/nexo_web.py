import logging
import os

import dash
import dash_leaflet as dl
from dash import html, dcc, Output, Input

from apartment_finder import Apartment
from mydb import MyDb, create_table_sql, insert_sql
from nexo_finder import NexoFinder

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

CUR_DIR = os.path.dirname(__file__)
NEXO_CACHE_DIR = os.path.join(CUR_DIR, "nexo_web")
DB_FILE = os.path.join(NEXO_CACHE_DIR, "nexo_web.sqlite3")

os.makedirs(NEXO_CACHE_DIR, exist_ok=True)


def _get_location(url_location: str):
    # url_location = https://www.google.com/maps/search/?api=1&query=-12.1661626,-77.0245367
    keyword = "query="
    idx = url_location.find(keyword)
    (lat, lon) = url_location[idx + len(keyword):].split(",")
    return (float(lat), float(lon))


class ApartmentDb:

    def __init__(self):
        self.db: MyDb = ApartmentDb.__setup_db()

    @staticmethod
    def __setup_db() -> MyDb:
        log.info("Setting up DB")
        db = MyDb(DB_FILE)

        scripts: list[str] = [
            create_table_sql(Apartment),
            "CREATE INDEX IF NOT EXISTS idx_apartment_id ON Apartment(id);",
        ]

        db.setup_db(scripts)
        return db

    def add(self, fn_get_apartments):
        if self.db.count(Apartment) > 0:
            log.info("Apartments already loaded. Skipping...")
            return

        apartments = fn_get_apartments()
        total = len(apartments)

        current = 1
        for sql, values in insert_sql(Apartment, apartments):
            self.db.execute(sql, values)
            log.info("Loading apartments %d/%d", current, total)
            current += 1


class AppWeb():
    def __init__(self):
        aptDb = ApartmentDb()
        nexo = NexoFinder()
        aptDb.add(lambda: nexo.get_all())

        self.all_apartments: list[Apartment] = aptDb.db.all(Apartment)

        self.app = dash.Dash(__name__)

    def run(self):
        unique_districts = sorted(set(apt.district for apt in self.all_apartments))
        phases = sorted(set(apt.construction_status for apt in self.all_apartments))

        @self.app.callback(
            Output('map', 'children'),
            [
                Input('district-dropdown', 'value'),
                Input('construction-status-dropdown', 'value'),
                Input('min-price-input', 'value'),
                Input('max-price-input', 'value'),
                Input('min-bedroom-input', 'value'),
                Input('max-bedroom-input', 'value'),
                Input('min-area-input', 'value'),
                Input('max-area-input', 'value'),
                Input('common-area-input', 'value'),
                Input('investment-input', 'value')
            ]
        )
        def update_map(selected_districts, selected_phases, min_price, max_price, min_bedroom, max_bedroom,
                       min_area, max_area, common_area, investment_ratio):
            min_price = min_price | 0
            max_price = max_price | 0
            min_bedroom = min_bedroom | 0
            max_bedroom = max_bedroom | 0
            min_area = min_area | 0
            max_area = max_area | 0
            selected_districts = selected_districts or unique_districts
            selected_phases = selected_phases or phases
            common_area = common_area | 0

            aux = filter(lambda apt: min_price * 1000 <= apt.price_soles <= max_price * 1000, self.all_apartments)
            aux = filter(lambda apt: apt.district in selected_districts, aux)
            aux = filter(lambda apt: min_bedroom <= apt.bedrooms <= max_bedroom, aux)
            aux = filter(lambda apt: apt.construction_status in selected_phases, aux)
            aux = filter(lambda apt: apt.common_area_count >= common_area, aux)
            aux = filter(lambda apt: min_area <= apt.area_m2 <= max_area, aux)
            aux = filter(lambda apt: apt.investment_ratio >= investment_ratio, aux)

            return [
                dl.TileLayer(),
                dl.LayerGroup(self.__create_markers(aux))
            ]

        self.app.layout = html.Main([
            html.Div([
                html.Label('District'),
                dcc.Dropdown(
                    id='district-dropdown',
                    options=[{'label': i, 'value': i} for i in unique_districts],
                    multi=True
                ),
            ]),
            html.Div([
                html.Label('Building'),
                dcc.Dropdown(
                    id='construction-status-dropdown',
                    options=[{'label': i, 'value': i} for i in phases],
                    multi=True
                ),
            ]),
            html.Div([
                html.Label('Price (miles soles) Min '),
                dcc.Input(
                    id='min-price-input',
                    type='number',
                    value=150
                ),
                html.Label('Max '),
                dcc.Input(
                    id='max-price-input',
                    type='number',
                    value=600
                ),
            ]),
            html.Div([
                html.Label('Bedrooms Min '),
                dcc.Input(
                    id='min-bedroom-input',
                    type='number',
                    value=1
                ),
                html.Label(' Max '),
                dcc.Input(
                    id='max-bedroom-input',
                    type='number',
                    value=4
                ),
            ]),
            html.Div([
                html.Label('Area m2 Min '),
                dcc.Input(
                    id='min-area-input',
                    type='number',
                    value=20
                ),
                html.Label(' Max '),
                dcc.Input(
                    id='max-area-input',
                    type='number',
                    value=100
                ),
            ]),
            html.Div([
                html.Label('Investment Ratio Min'),
                dcc.Input(
                    id='investment-input',
                    type='number',
                    step=0.01,
                    value=0.7
                ),
            ]),
            html.Div([
                html.Label('Common Area Min'),
                dcc.Input(
                    id='common-area-input',
                    type='number',
                    value=1
                ),
            ]),
            dl.Map(
                id="map",
                center=(-12.0893, -77.0513), zoom=10,
                children=[
                    dl.TileLayer(),
                    dl.LayerGroup(self.__create_markers(self.all_apartments))
                ], style={'width': '1000px', 'height': '500px'}),
        ])

        self.app.run_server(debug=True)

    @staticmethod
    def __create_markers(data):
        markers = []
        for apt in data:
            lat, lon = _get_location(apt.url_location)

            custom_tooltip = html.Div([
                html.H2(apt.name),
                html.P(f"District: {apt.district}"),
                html.P(f"Address: {apt.address}"),
                html.P(f"Prices: S/ {apt.price_soles} - {apt.area_m2} m2"),
                html.P(f"Bedrooms: {apt.bedrooms}"),
                html.P(f"Common area count: {apt.common_area_count}"),
                html.P(f"Construction status: {apt.construction_status} - {apt.delivery_date}"),
                html.A("More info", href=apt.url, target="_blank")
            ])
            markers.append(dl.Marker(position=(lat, lon),
                                     children=[dl.Tooltip(children=custom_tooltip)]))
        return markers


def main():
    webApp = AppWeb()
    webApp.run()


if __name__ == "__main__":
    main()
