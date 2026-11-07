"""Regression tests for request-scoped loading in singleton datasets."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pandas as pd
import pytest
from zen_creator import Element
from zen_creator.utils.singleton_registry_meta import SingletonRegistryMeta

from zen_europe.datasets.datasets.carrier.entsoe import ENTSOE, _redact_api_token
from zen_europe.datasets.datasets.carrier.eurostat import Eurostat
from zen_europe.datasets.datasets.carrier.when2heat import When2Heat
from zen_europe.datasets.datasets.technology.pan_european_climate_database import (
    PanEuropeanClimateDatabase,
)
from zen_europe.datasets.datasets.technology.unece import UNECE


@pytest.fixture(autouse=True)
def isolated_singleton_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep singleton instances created here from leaking into other tests."""
    monkeypatch.setattr(SingletonRegistryMeta, "_registries", {})


def test_entsoe_reuses_only_matching_node_shards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Overlapping node requests query only missing or overwritten nodes."""
    dataset = ENTSOE(tmp_path)
    queried: list[str] = []

    def query_demand(year: int, nodes: list[str]) -> pd.DataFrame:
        assert year == 2020
        assert len(nodes) == 1
        queried.extend(nodes)
        return pd.DataFrame(
            {nodes[0]: [1000.0]},
            index=pd.DatetimeIndex(["2020-01-01"], name="time"),
        )

    monkeypatch.setattr(dataset, "_query_demand", query_demand)
    monkeypatch.setattr(
        "zen_europe.datasets.datasets.carrier.entsoe.canonicalize_hourly_year",
        lambda data, **_: data,
    )

    first = dataset.get_demand(year=2020, nodes=["DE", "FR"])
    second = dataset.get_demand(year=2020, nodes=["FR", "IT"])
    refreshed = dataset.get_demand(year=2020, nodes=["FR"], overwrite=True)

    assert Counter(queried) == Counter({"DE": 1, "FR": 2, "IT": 1})
    assert list(first.columns) == ["DE", "FR"]
    assert list(second.columns) == ["FR", "IT"]
    assert list(refreshed.columns) == ["FR"]


def test_entsoe_redacts_api_tokens_from_errors() -> None:
    """ENTSO-E request failures must not expose credentials in logs."""
    message = _redact_api_token(
        RuntimeError("https://example.test?securityToken=secret-value&period=2020")
    )
    assert "secret-value" not in message
    assert "securityToken=<redacted>" in message


def test_entsoe_reuses_matching_edge_shards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Overlapping transmission requests query only previously unseen edges."""
    dataset = ENTSOE(tmp_path)
    queried: list[tuple[str, str]] = []

    def query_capacity(
        year: int, monthly: bool, edges: list[tuple[str, str]]
    ) -> pd.Series:
        assert year == 2020
        assert monthly is False
        assert len(edges) == 1
        queried.extend(edges)
        edge = edges[0]
        return pd.Series({f"{edge[0]}-{edge[1]}": 1000.0})

    monkeypatch.setattr(dataset, "_query_transmission_capacity", query_capacity)
    monkeypatch.setattr(
        dataset,
        "_ntc_edges",
        lambda nodes: [("DE", "FR"), ("FR", "DE")] if "DE" in nodes else [("FR", "IT")],
    )

    dataset.get_transmission_capacity(year=2020, nodes=["DE", "FR"], monthly=False)
    dataset.get_transmission_capacity(year=2020, nodes=["FR", "IT"], monthly=False)

    assert Counter(queried) == Counter(
        {("DE", "FR"): 1, ("FR", "DE"): 1, ("FR", "IT"): 1}
    )


def test_unece_selects_codes_for_category_countries_and_years(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """UNECE converts requested labels to PXWeb codes and one later year."""
    dataset = UNECE(tmp_path)
    metadata = {
        "variables": [
            {
                "code": "Type of Vehicle",
                "values": ["V1", "V2"],
                "valueTexts": ["Passenger cars", "Lorries"],
            },
            {
                "code": "Country",
                "values": ["C1", "C2"],
                "valueTexts": ["Germany", "France"],
            },
            {
                "code": "Year",
                "values": ["Y1", "Y2", "Y3"],
                "valueTexts": ["2020", "2022", "2024"],
            },
        ]
    }
    monkeypatch.setattr(
        dataset, "_request", lambda _: SimpleNamespace(json=lambda: metadata)
    )
    requested: dict[str, object] = {}

    def query_vehicle_type(
        url: str,
        vehicle_type: str,
        *,
        country_values: list[str],
        years: list[str],
    ) -> pd.Series:
        requested.update(
            vehicle_type=vehicle_type,
            country_values=country_values,
            years=years,
        )
        index = pd.MultiIndex.from_tuples(
            [("Passenger cars", "Electricity", "Germany", 2020)],
            names=["Type of Vehicle", "Fuel Type", "Country", "Year"],
        )
        return pd.Series([1.0], index=index)

    monkeypatch.setattr(dataset, "_query_vehicle_type", query_vehicle_type)

    dataset._query_table(
        "table", vehicle_type="Passenger cars", nodes=["DE"], year=2022
    )

    assert requested == {
        "vehicle_type": "V1",
        "country_values": ["C1"],
        "years": ["Y1", "Y2", "Y3"],
    }


def test_pecd_loads_only_requested_technology_and_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PECD construction is inert and repeated element requests are memoized."""
    (tmp_path / "03-technology" / "climate_data").mkdir(parents=True)
    dataset = PanEuropeanClimateDatabase(tmp_path)
    assert dataset.data == {}
    requested: list[tuple[str, int, bool]] = []

    def load(
        technology: str,
        request: object,
        year: int,
        *,
        overwrite: bool = False,
    ) -> pd.DataFrame:
        requested.append((technology, year, overwrite))
        return pd.DataFrame({"DE": [1.0]})

    monkeypatch.setattr(dataset, "_get_technology_data", load)
    element = cast(
        Element,
        SimpleNamespace(
            settings=SimpleNamespace(
                time=SimpleNamespace(resolved_weather_year=2020),
                cache=SimpleNamespace(overwrite_pan_european_climate_database=False),
            )
        ),
    )

    first = dataset._get_for_element("photovoltaics", element)
    second = dataset._get_for_element("photovoltaics", element)

    assert first is second
    assert requested == [("photovoltaics", 2020, False)]


def test_eurostat_and_when2heat_construction_performs_no_remote_io(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Request-driven carrier datasets remain inert until a getter is called."""
    monkeypatch.setattr(
        "zen_europe.datasets.datasets.carrier.eurostat.es.get_toc_df",
        lambda **_: pytest.fail("Eurostat metadata queried during construction"),
    )
    monkeypatch.setattr(
        When2Heat,
        "_download_source",
        lambda *_: pytest.fail("When2Heat downloaded during construction"),
    )

    assert Eurostat(tmp_path).data.empty
    assert When2Heat(tmp_path).data == {}
