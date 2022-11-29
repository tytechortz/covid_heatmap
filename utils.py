from retrying import retry
import datashader as ds
from pyproj import Transformer

scheduler_url = "127.0.0.1:8786"

# Coordinate transformations
transformer_4326_to_3857 = Transformer.from_crs("epsg:4326", "epsg:3857")
transformer_3857_to_4326 = Transformer.from_crs("epsg:3857", "epsg:4326")

def epsg_4326_to_3857(coords):
    return [transformer_4326_to_3857.transform(*reversed(row)) for row in coords]


def epsg_3857_to_4326(coords):
    return [list(reversed(transformer_3857_to_4326.transform(*row))) for row in coords]


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, stop_max_delay=6000)
def get_dataset(client, name):
    return client.get_dataset(name)