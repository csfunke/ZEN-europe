from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation
from zen_creator.elements import StorageTechnology
from zen_creator.utils.attribute import Attribute


class RenewableEnergyCreditStorage(StorageTechnology):
    """Class containing all data and assumptions for natural gas storage
    technology."""

    name: str = "renewable_energy_credit_storage"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of natural gas storage to natural gas.
        """
        return Attribute(
            name="reference_carrier",
            default_value=["renewable_energy_credit"],
            element=self,
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of natural gas storage.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=200,
            source=AssumptionInformation(
                description=(
                    "Renewable Energy Credits Storage is not physical infrastructure"
                    " and therefore it can last forever."
                ),
            ),
        )
