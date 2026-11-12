from pkg.booking import seats_left


def test_seats_left():
    assert seats_left(10, 4) == 6
