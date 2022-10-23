import requests
from pandas import DataFrame
import pandas as pd
from io import StringIO

from .constants import MO_USER_AGENT, MO_HOMEPAGE, NAMES_CSV


def _load_from_mo2df(url: str) -> DataFrame:
    headers = {'User-Agent': MO_USER_AGENT}
    string = requests.get(url, headers=headers).text
    return pd.read_csv(StringIO(string), sep="\t")


def load_names() -> DataFrame:
    return _load_from_mo2df(f"{MO_HOMEPAGE}/{NAMES_CSV}")
