import requests
import datetime
import typing
from pprint import pprint

date = typing.TypeVar("date", str, datetime.date, datetime.datetime)


def getResource(token: str, endpoint: str, params: dict[str, str] = None):
    headers = {"accept": "application/json"}
    if params is None:
        params = {"apiToken": token}
    else:
        params["apiToken"] = token
    return requests.get(
        "https://onemocneni-aktualne.mzcr.cz/api/v3/"+endpoint,
        params=params,
        headers=headers
    ).json()


def getZakladniPrehled(token: str, date: date = None):
    """Gets the základní přehled endpoint, for specific date.
    Only today works tho (MZCR's bad, not mine)

    Args:
        token (:class:`str`): your API token
        date (:class:`date`, optional): Date you want základní přehled for. \
            Defaults to todays date.

    Returns:
        JSON: Základní přehled endpoint
    """
    if date is None:
        date = datetime.date.today().isoformat()
    elif isinstance(date, datetime.date):
        date = date.isoformat()
    elif isinstance(date, datetime.datetime):
        date = date.date().isoformat()

    return getResource(token, f"zakladni-prehled/{date}")


def getTestyPcrAntigenni(
    token: str,
    date_before: date = None,
    date_striclty_before: date = None,
    date_after: date = None,
    date_striclty_after: date = None
):
    """Gets the testy prc antigenni for specified time range.

    Args:
        token (:class:`str`): Your api token
        date_before (:class:`date`, optional): [description].
        Defaults to None.
        date_striclty_before (:class:`date`, optional): [description].
        Defaults to None.
        date_after (:class:`date`, optional): [description].
        Defaults to None.
        date_striclty_after (:class:`date`, optional): [description].
        Defaults to None.

    Returns:
        :class:`list[dict[str, Union[int, str]]]`: JSON response.
    """
    params = {}
    if date_before is not None:
        params["datum[before]"] = date_before
    if date_striclty_before is not None:
        params["datum[strictly_before"] = date_striclty_before
    if date_after is not None:
        params["datum[after]"] = date_after
    if date_striclty_after is not None:
        params["datum[strictly_after]"] = date_striclty_after
    return getResource(
        token,
        "testy-pcr-antigenni",
        params=params
    )
