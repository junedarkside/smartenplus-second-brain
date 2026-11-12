from pkg.big import station_name_1, fare_8


def label(code: str, km: float) -> str:
    return f"{station_name_1(code)}:{fare_8(km)}"
