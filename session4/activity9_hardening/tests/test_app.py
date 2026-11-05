"""UI tests with Streamlit's AppTest: run the app headlessly and poke at widgets."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[3] / "session1" / "activity2_solution" / "app.py"


def fresh_app() -> AppTest:
    return AppTest.from_file(str(APP), default_timeout=60).run()


def units(at: AppTest) -> int:
    return int(at.metric[0].value.replace(",", ""))


def test_default_run_has_no_exception():
    at = fresh_app()
    assert not at.exception
    assert len(at.metric) == 3


def test_region_filter_reduces_units():
    at = fresh_app()
    all_units = units(at)
    at.multiselect(key="regions").set_value(["North"]).run()
    assert not at.exception
    assert 0 < units(at) < all_units


def test_empty_selection_shows_friendly_warning():
    at = fresh_app()
    at.multiselect(key="regions").set_value([]).run()
    assert not at.exception
    assert len(at.warning) == 1
