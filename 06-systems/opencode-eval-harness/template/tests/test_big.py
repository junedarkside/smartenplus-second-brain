from pkg.uses_big import label


def test_label():
    assert label("ab", 2) == "station-1-AB:17.0"
