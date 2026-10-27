from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class RenewableEnergyCredit(Carrier):
    """Carrier for tracking renewable energy production and consumption.

    This class implements the specific behavior for the carbon carrier.
    """

    name: str = "renewable_energy_credit"

    def __init__(self, model: Model, power_unit: str = "GW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_export(self) -> Attribute:

        return Attribute(
            "availability_export",
            default_value=np.inf,
            unit=self.power_unit,
            element=self,
        )

    def _set_availability_export_yearly(self) -> Attribute:

        return Attribute(
            "availability_export_yearly",
            default_value=np.inf,
            unit=self.energy_unit,
            element=self,
        )