import requests
from pandas import DataFrame, Series
import pandas as pd
from io import StringIO
from warnings import warn
from typing import List, Tuple
from IPython.display import display

from .constants import MO_USER_AGENT, MO_HOMEPAGE, NAMES_CSV, OBSERVATIONS_CSV, IMAGES_CSV, NAME_DESCRIPTIONS_CSV, LOCATIONS_CSV, IMAGES_OBSERVATIONS_CSV


def _load_from_mo2df(url: str) -> DataFrame:
    headers = {'User-Agent': MO_USER_AGENT}
    string = requests.get(url, headers=headers).text
    return pd.read_csv(StringIO(string), sep="\t")



def load_names_csv() -> DataFrame:
    return _load_from_mo2df(f"{MO_HOMEPAGE}/{NAMES_CSV}")


def load_observations_csv() -> DataFrame:
    return _load_from_mo2df(f"{MO_HOMEPAGE}/{OBSERVATIONS_CSV}")


def load_images_csv() -> DataFrame:
    return _load_from_mo2df(f"{MO_HOMEPAGE}/{IMAGES_CSV}")


def load_name_descriptions_csv() -> DataFrame:
    headers = {'User-Agent': MO_USER_AGENT}
    url = f"{MO_HOMEPAGE}/{NAME_DESCRIPTIONS_CSV}"
    string = requests.get(url, headers=headers).text
    return pd.read_csv(StringIO(string.replace("\\n", "").replace("\r", "")), sep="\t")


def load_locations_csv() -> DataFrame:
    return _load_from_mo2df(f"{MO_HOMEPAGE}/{LOCATIONS_CSV}")


def load_image_observations_csv() -> DataFrame:
    return _load_from_mo2df(f"{MO_HOMEPAGE}/{IMAGES_OBSERVATIONS_CSV}")


def get_column_coverage(df: DataFrame):
    describe_df = df.describe(include="all")
    if "count" not in describe_df.index:
        warn(f"'count' must be contained in describe_df.index but it is not.")
        return

    for column in describe_df.columns:
        print(f'{describe_df.loc["count", column] / len(df) * 100:.2f}% of the entries have non-null {column}.')


def get_unique_values_and_counts(df: DataFrame, columns: List[str]):
    for column in columns:
        if column not in df.columns:
            warn(f"Input column {column} not in the data frame.")
            return
    for column in columns:
        counts_df = df.groupby(column).size().reset_index(name="Count").sort_values("Count", ascending=False)
        counts_df["Percentage"] = counts_df.Count / counts_df.Count.sum() * 100
        display(counts_df)


# -------------------------------------------------------------------------------------------------------------------------
# See https://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python
def _reproject(latitude: List[float], longitude: List[float]) -> Tuple[List[float], List[float]]:
    """Returns the x & y coordinates in meters using a sinusoidal projection"""
    from math import pi, cos, radians
    earth_radius = 6371009 # in meters
    lat_dist = pi * earth_radius / 180.0

    y = [lat * lat_dist for lat in latitude]
    x = [long * lat_dist * cos(radians(lat)) 
                for lat, long in zip(latitude, longitude)]
    return x, y


def area_of_polygon(x: List[float], y: List[float]) -> float:
    """Calculates the area of an arbitrary polygon given its vertices (lat/long)"""
    x, y = _reproject(latitude=y, longitude=x)
    area = 0.0
    for i in range(-1, len(x)-1):
        area += x[i] * (y[i+1] - y[i-1])
    return abs(area) / 2.0
# -------------------------------------------------------------------------------------------------------------------------


def row2bounding_box(row: Series) -> Tuple[List[float], List[float]]:
    x = [row["east"], row["east"], row["west"], row["west"]]
    y = [row["north"], row["south"], row["south"], row["north"]]
    return x, y
