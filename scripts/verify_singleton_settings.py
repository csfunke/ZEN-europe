"""Build contrasting models sequentially to detect stale singleton settings."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Model
from zen_creator.utils.settings import Settings

import zen_europe.settings  # noqa: F401  (register settings categories)
from zen_europe.datasets.datasets.carrier.entsoe import ENTSOE
from zen_europe.datasets.datasets.technology.pan_european_climate_database import (
    PanEuropeanClimateDatabase,
)
from zen_europe.model_creator import DEFAULT_CONFIG_PATH
from zen_europe.settings.cache import set_active_cache_settings


def _build_model(
    *, patch: dict[str, object], excluded_nodes: set[str], name: str
) -> tuple[Model, pd.DataFrame]:
    """Build one in-process model and retain its electricity demand."""
    default_settings = Settings.load_from_yaml(DEFAULT_CONFIG_PATH)
    effective_patch = dict(patch)
    effective_patch["region"] = {
        "set_nodes": [
            node
            for node in default_settings.region.set_nodes
            if node not in excluded_nodes
        ]
    }
    settings = Settings.load_from_yaml(DEFAULT_CONFIG_PATH, patch=effective_patch)
    model = Model.from_config(DEFAULT_CONFIG_PATH, settings=settings)
    model.name = name
    set_active_cache_settings(settings.cache)
    model.build()
    demand = model.elements["electricity"].demand.df
    if not isinstance(demand, pd.DataFrame):
        raise TypeError("Electricity demand must be a DataFrame after model build.")
    return model, demand.copy()


def main() -> None:
    """Verify contrasting sequential builds reuse settings-independent instances."""
    first, first_demand = _build_model(
        patch={
            "time": {"time_series_year": 2019, "weather_year": 2019},
            "cost": {"use_learning_curves": True},
            "investment": {
                "allow_investment": True,
                "use_existing_capacities": True,
            },
        },
        excluded_nodes=set(),
        name="singleton-settings-first",
    )
    source_path = Path(first.source_path)
    entsoe_id = id(ENTSOE(source_path))
    pecd_id = id(PanEuropeanClimateDatabase(source_path))

    second, second_demand = _build_model(
        patch={
            "time": {"time_series_year": 2020, "weather_year": 2019},
            "cost": {"use_learning_curves": False},
            "investment": {
                "allow_investment": False,
                "use_existing_capacities": True,
            },
        },
        excluded_nodes={"LU"},
        name="singleton-settings-second",
    )

    assert id(ENTSOE(source_path)) == entsoe_id
    assert id(PanEuropeanClimateDatabase(source_path)) == pecd_id
    assert first.settings.time.time_series_year == 2019
    assert second.settings.time.time_series_year == 2020
    assert first.settings.cost.use_learning_curves is True
    assert second.settings.cost.use_learning_curves is False
    assert first.settings.investment.allow_investment is True
    assert second.settings.investment.allow_investment is False
    assert "LU" in first.config.system.set_nodes
    assert "LU" not in second.config.system.set_nodes
    assert not first_demand.equals(second_demand)


if __name__ == "__main__":
    main()
