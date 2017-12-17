import pyfant


def test_greek_to_spdf():
    tt = [pyfant.greek_to_spdf(x) for x in pyfant.basic.conversion._SPDF_TO_GREEK.values()]
    assert(tt == list(pyfant.basic.conversion._GREEK_TO_SPDF.values()))


def test_spdf_to_greek():
    tt = [pyfant.spdf_to_greek(x) for x in range(len(pyfant.basic.conversion._SPDF_TO_GREEK))]
    assert(tt == list(pyfant.basic.conversion._SPDF_TO_GREEK.values()))


def test_parse_system_str():
    assert pyfant.parse_system_str("[d 3 phi - a 2 delta]") == ["d", 3, 3, "a", 2, 2]
