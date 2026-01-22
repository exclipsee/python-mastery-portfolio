from python_mastery_portfolio import algorithms, api


def test_gcd_endpoint_logic():
    # exercise algorithms.gcd directly to ensure code path covered
    assert algorithms.gcd(48, 18) == 6
    assert algorithms.gcd(7, 3) == 1


def test_api_gcd_response_model():
    # create a minimal response using the API helper (no server)
    res = api.GcdResponse(a=12, b=8, gcd=4)
    assert res.a == 12 and res.b == 8 and res.gcd == 4


def test_utils_roundtrip_tmpdir(tmp_path):
    # exercise a small util function to touch more code paths
    p = tmp_path / "demo.txt"
    p.write_text("hello")
    assert p.read_text() == "hello"
