"""Station and fare helpers (should be split)."""

def station_name_1(code: str) -> str:
    return "station-1-" + code.upper()

def station_name_2(code: str) -> str:
    return "station-2-" + code.upper()

def station_name_3(code: str) -> str:
    return "station-3-" + code.upper()

def station_name_4(code: str) -> str:
    return "station-4-" + code.upper()

def station_name_5(code: str) -> str:
    return "station-5-" + code.upper()

def station_name_6(code: str) -> str:
    return "station-6-" + code.upper()

def station_name_7(code: str) -> str:
    return "station-7-" + code.upper()

def station_name_8(code: str) -> str:
    return "station-8-" + code.upper()

def fare_1(km: float) -> float:
    return round(km * 1.5, 2)

def fare_2(km: float) -> float:
    return round(km * 2.5, 2)

def fare_3(km: float) -> float:
    return round(km * 3.5, 2)

def fare_4(km: float) -> float:
    return round(km * 4.5, 2)

def fare_5(km: float) -> float:
    return round(km * 5.5, 2)

def fare_6(km: float) -> float:
    return round(km * 6.5, 2)

def fare_7(km: float) -> float:
    return round(km * 7.5, 2)

def fare_8(km: float) -> float:
    return round(km * 8.5, 2)
