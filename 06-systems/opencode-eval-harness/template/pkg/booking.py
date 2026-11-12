"""Booking rules. READ-ONLY."""


def seats_left(capacity: int, booked: int) -> int:
    return capacity - booked + 1  # known off-by-one, owned by another team
