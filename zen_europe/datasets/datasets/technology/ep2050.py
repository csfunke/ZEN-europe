from __future__ import annotations

from pathlib import Path
from typing import cast

import pandas as pd
from zen_creator import Attribute, SourceInformation, Technology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData


class EP2050(Dataset[pd.DataFrame]):
    """Swiss renewable-energy projections from Energieperspektiven 2050+."""

    name = "ep2050"

    WIND_ONSHORE_GENERATION_2050_GWH = 4_300.0

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Energieperspektiven 2050+ Technischer Bericht",
            author=[
                "Andreas Klemmer",
                "Almut Kirchner",
                "Sven Kreidelmeyer",
                "Alexander Piégsa",
                "Thomas Spillmann",
                "Hannes Dambeck",
                "Hanno Falkenberg",
                "Stefan Lübbers",
                "Andreas Brutsche",
                "Daniel Tschumi",
                "Jonas Thurau",
                "Florian Ess",
                "Christoph Thormeyer",
                "Hans-Jörg Althaus",
                "Brian Cox",
                "Benedikt Notter",
                "Martin Jakob",
                "Ulrich Reiter",
                "Giacomo Catenazzi",
                "Lukas Lienhard",
            ],
            publication="Swiss Federal Office of Energy",
            publication_year=2021,
            url="https://pubdb.bfe.admin.ch/de/publication/download/10783",
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_capacity_limit(self, element: Technology, attr: Attribute) -> Attribute:
        """Set the Swiss onshore-wind limit from projected annual generation."""
        if element.name != "wind_onshore":
            raise ValueError("EP2050 capacity data is only available for onshore wind.")
        max_load = cast(pd.DataFrame | None, element.max_load.df)
        if max_load is None:
            raise ValueError(
                "Cannot convert the EP2050 wind generation to capacity before "
                "onshore-wind max-load data is set."
            )
        if "CH" not in max_load.columns:
            raise ValueError(
                "Cannot convert the EP2050 wind generation to capacity because "
                "onshore-wind max-load data for CH is missing."
            )

        full_load_hours = max_load["CH"].sum()
        if pd.isna(full_load_hours) or full_load_hours <= 0:
            raise ValueError(
                "The sum of onshore-wind max-load values for CH must be positive."
            )

        data = cast(pd.Series, attr.df).copy()
        data.loc["CH"] = self.WIND_ONSHORE_GENERATION_2050_GWH / full_load_hours
        data.name = "capacity_limit"
        return attr.set_data(
            df=data,
            unit="GW",
            source=SourceInformation(
                description=(
                    "The Swiss onshore-wind capacity limit is the EP2050+ annual "
                    "generation projection of 4.3 TWh in 2050 divided by the sum "
                    "of the hourly Swiss onshore-wind maximum-load factors."
                ),
                metadata=self.metadata,
            ),
        )
