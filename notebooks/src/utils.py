import requests
from pandas import DataFrame, Series
import pandas as pd
from io import StringIO
from warnings import warn
from typing import List, Tuple, Dict, Union, Literal
from IPython.display import display
import numpy as np
from pathlib import Path
import asyncio
import aiohttp
import aiofiles

from .constants import MO_USER_AGENT, MO_HOMEPAGE, NAMES_CSV, OBSERVATIONS_CSV, IMAGES_CSV, NAME_DESCRIPTIONS_CSV,\
    LOCATIONS_CSV, IMAGES_OBSERVATIONS_CSV


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


# ----------------------------------------------------------------------------------------------------------------------
# https://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python
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
# ----------------------------------------------------------------------------------------------------------------------


def row2bounding_box(row: Series) -> Tuple[List[float], List[float]]:
    x = [row["east"], row["east"], row["west"], row["west"]]
    y = [row["north"], row["south"], row["south"], row["north"]]
    return x, y


def get_id2preferred_id(names_df: DataFrame, include_deprecated: bool = False) -> Dict[int, int]:
    id2preferred_id = {}
    for _, df in names_df.groupby("synonym_id"):
        mask = df.deprecated == 0
        preferred_id = df[mask]["id"].min()
        for id_ in df["id"].values:
            if include_deprecated:
                if preferred_id is np.nan:
                    id2preferred_id[id_] = df["id"].min()
                else:
                    id2preferred_id[id_] = preferred_id
            else:
                id2preferred_id[id_] = preferred_id
    return id2preferred_id


def get_names_pref_df(names_df: DataFrame) -> DataFrame:
    names_pref_df = names_df.copy()
    id2preferred_id = get_id2preferred_id(names_df=names_df, include_deprecated=True)
    names_pref_df["preferred_id"] = names_pref_df["id"].map(lambda id_: id2preferred_id.get(id_, id_))
    return names_pref_df

# We need to open a new connection for each image. Maybe we can bring the downloading time down with async IO

async def _fetch_and_save_image(
    session: aiohttp.ClientSession, image_id: Literal[320, 640, 960, 1280], size: int, image_folder: Path
):
    # No header -> 403 permission denied.
    headers = {'User-Agent': MO_USER_AGENT}
    # I've seen some people streaming images to avoid interruptions. Should I do that, too?
    async with session.get(f"https://mushroomobserver.org/images/{size}/{image_id}.jpg", headers=headers) as resp:
        if resp.status == 200:
            async with aiofiles.open(image_folder / f"{image_id}.jpg", mode="wb") as handle:
                await handle.write(await resp.read())


async def fetch_and_save_images(
    image_ids: List[int], size: Literal[320, 640, 960, 1280], image_folder: Union[Path, str]
):
    if isinstance(image_folder, str):
        image_folder = Path(image_folder)
    # Creates folder if not already existent
    image_folder.mkdir(parents=True, exist_ok=True)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for image_id in image_ids:
            tasks.append(
                _fetch_and_save_image(session=session, image_id=image_id, size=size, image_folder=image_folder)
            )
        return await asyncio.gather(*tasks, return_exceptions=True)
