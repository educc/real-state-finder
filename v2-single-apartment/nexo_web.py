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
        @self.app.callback(
            Output('map', 'children'),
            [
                Input('district-dropdown', 'value'),
                Input('min-price-input', 'value'),
                Input('max-price-input', 'value'),
                Input('min-bedroom-input', 'value'),
                Input('max-bedroom-input', 'value')
            ]
        )
        def update_map(selected_districts, min_price, max_price, min_bedroom, max_bedroom):
            if not min_price:
                min_price = 0
            if not max_price:
                max_price = 5_000_000
            if not min_bedroom:
                min_bedroom = 0
            if not max_bedroom:
                max_bedroom = 10

            aux = filter(lambda apt: min_price <= apt.price_soles <= max_price, self.all_apartments)
            if selected_districts:
                aux = filter(lambda apt: apt.district in selected_districts, aux)

            aux = filter(lambda apt: min_bedroom <= apt.bedrooms <= max_bedroom, aux)

            return [
                dl.TileLayer(),
                dl.LayerGroup(self.__create_markers(aux))
            ]

        # Get unique districts and min, max values for price_soles and bedrooms
        unique_districts = sorted(set(apt.district for apt in self.all_apartments))

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
                html.Label('Min Price'),
                dcc.Input(
                    id='min-price-input',
                    type='number',
                    value=50_000
                ),
            ]),
            html.Div([
                html.Label('Max Price'),
                dcc.Input(
                    id='max-price-input',
                    type='number',
                    value=1_200_000
                ),
            ]),
            html.Div([
                html.Label('Min Bedrooms'),
                dcc.Input(
                    id='min-bedroom-input',
                    type='number',
                    value=1
                ),
            ]),
            html.Div([
                html.Label('Max Bedrooms'),
                dcc.Input(
                    id='max-bedroom-input',
                    type='number',
                    value=5
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
                html.P(f"Prices: S/ {apt.price_soles}"),
                html.P(f"Area m2: {apt.area_m2}"),
                html.P(f"Bedrooms: {apt.bedrooms}"),
                html.P(f"Common area count: {apt.common_area_count}"),
                html.P(f"Construction status: {apt.construction_status}"),
                html.P(f"Delivery date: {apt.delivery_date}"),
                html.P(f"Builder: {apt.builder}"),
            ])
            markers.append(dl.Marker(position=(lat, lon),
                                     children=[dl.Tooltip(children=custom_tooltip)]))
        return markers


def main():
    webApp = AppWeb()
    webApp.run()


if __name__ == "__main__":
    main()
