from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, ConversionTechnology, SourceInformation
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData


class WorldNuclearPolicies(Dataset[pd.DataFrame]):
    """European nuclear capacity and policy snapshot used by Reg4Fuels."""

    name = "world_nuclear_policies"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="World Nuclear Association Country Profiles",
            author=["World Nuclear Association"],
            publication="World Nuclear Association Website",
            publication_year=2025,
            url="https://world-nuclear.org/information-library/country-profiles",
            note=(
                "Dataset created manually by searching information available"
                " on the website"
            ),
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load nuclear policy data.")
        return Path(self.source_path) / "03-technology" / "nuclear"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path / "world_nuclear_policies.csv")
        return data.set_index("node")

    def get_capacity_limit(self, element: ConversionTechnology) -> Attribute:
        """Return the maximum nuclear expansion allowed by current policies."""
        data = (
            self.data["current_capacity_mw"]
            + self.data["planned_or_proposed_capacity_mw"]
            + self.data["capacity_under_construction_mw"]
        ) / 1000
        data = data.reindex(element.model.config.system.set_nodes).fillna(0)
        data.index.name = "node"
        data.name = "capacity_limit"
        return element.capacity_limit.set_data(
            default_value=0,
            df=data,
            unit="GW",
            source=SourceInformation(
                description=(
                    "The nuclear expansion limit is the existing capacity plus "
                    "capacity under construction "
                    "plus planned or proposed capacity in the 2025 World Nuclear "
                    "Association policy snapshot."
                ),
                metadata=self.metadata,
            ),
        )
