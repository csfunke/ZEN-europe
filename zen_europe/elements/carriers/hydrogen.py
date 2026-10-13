from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Scenario
from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute

from zen_europe.reg4fuels import CHEAP_H2_SCENARIOS, EXPENSIVE_H2_SCENARIOS


class Hydrogen(Carrier):
    """Hydrogen carrier class.

    This class implements the specific behavior for the hydrogen carrier.
    """

    name: str = "hydrogen"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ----Example of optional methods for overriding default attributes ------

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of hydrogen.

        """
        availability = (
            np.inf if self.settings.availability.allow_hydrogen_imports else 0
        )
        return Attribute(
            "availability_import",
            default_value=availability,
            element=self,
            unit=self.power_unit,
        )

    def _set_price_import(self) -> Attribute:
        """Set the Speed2Zero hydrogen-import price and sensitivities."""
        if not self.settings.availability.allow_hydrogen_imports:
            return self.price_import

        scenarios = None
        if self.settings.scenario.sensitivity_reg4fuels:
            scenarios = [
                *[
                    Scenario(name, default_op=73.8 / 94.3)
                    for name in CHEAP_H2_SCENARIOS
                ],
                *[
                    Scenario(name, default_op=164.4 / 94.3)
                    for name in EXPENSIVE_H2_SCENARIOS
                ],
            ]
        return self.price_import.set_data(
            default_value=94.3,
            unit="Euro/MWh",
            source=AssumptionInformation(
                description=(
                    "The hydrogen import price is 94.3 Euro/MWh, with the "
                    "Reg4Fuels low and high cases taken from Speed2Zero."
                )
            ),
            scenarios=scenarios,
        )
