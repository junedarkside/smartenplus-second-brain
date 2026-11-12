def total(prices: list[float], discount_percent: float = 0.0) -> float:
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    if any(p < 0 for p in prices):
        raise ValueError("price must not be negative")
    subtotal = sum(prices)
    return round(subtotal * (1 - discount_percent / 100), 2)
