import pytest

from picomon.config import PicomonConfig


def test_max_points_derived_from_history_and_interval():
    cfg = PicomonConfig(update_interval=2.0, history_minutes=1)
    assert cfg.max_points == 30


@pytest.mark.parametrize(
    "kwargs",
    [
        {"update_interval": 0},
        {"history_minutes": 0},
        {"static_timeout": 0},
        {"metric_timeout": 0},
    ],
)
def test_invalid_values_raise_value_error(kwargs):
    with pytest.raises(ValueError):
        PicomonConfig(**kwargs)
