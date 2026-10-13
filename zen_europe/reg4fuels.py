"""Cross-cutting model extensions ported from the legacy Reg4Fuels branch."""

from __future__ import annotations

import numpy as np
import pandas as pd
from zen_creator import AssumptionInformation, Attribute, Model, Scenario

CHEAP_H2_SCENARIOS = (
    "cheap_h2_scarce_substitutes",
    "cheap_h2_abundant_substitutes",
    "cheap_h2_scarce_substitutes_expensive_renewables",
    "cheap_h2_abundant_substitutes_expensive_renewables",
)
EXPENSIVE_H2_SCENARIOS = (
    "expensive_h2_scarce_substitutes",
    "expensive_h2_abundant_substitutes",
    "expensive_h2_scarce_substitutes_expensive_renewables",
    "expensive_h2_abundant_substitutes_expensive_renewables",
)
SCARCE_SUBSTITUTES_SCENARIOS = (
    "cheap_h2_scarce_substitutes",
    "expensive_h2_scarce_substitutes",
    "cheap_h2_scarce_substitutes_expensive_renewables",
    "expensive_h2_scarce_substitutes_expensive_renewables",
)
ABUNDANT_SUBSTITUTES_SCENARIOS = (
    "cheap_h2_abundant_substitutes",
    "expensive_h2_abundant_substitutes",
    "cheap_h2_abundant_substitutes_expensive_renewables",
    "expensive_h2_abundant_substitutes_expensive_renewables",
)
EXPENSIVE_RENEWABLES_SCENARIOS = (
    "cheap_h2_scarce_substitutes_expensive_renewables",
    "cheap_h2_abundant_substitutes_expensive_renewables",
    "expensive_h2_scarce_substitutes_expensive_renewables",
    "expensive_h2_abundant_substitutes_expensive_renewables",
)


def apply_reg4fuels_extensions(model: Model) -> None:
    """Add carrier-wide transport attributes and sensitivity scenarios."""
    if model.settings.scenario.sensitivity_transport_limits:
        for carrier in model.carriers.values():
            carrier.demand.add_scenarios(
                Scenario("increased_carrier_demand", file_op=1.1)
            )
        electricity = model.carriers.get("electricity")
        if electricity is not None:
            electricity.demand.add_scenarios(
                Scenario("increased_electricity_demand", file_op=1.1)
            )

    if not model.settings.availability.use_transport_limits:
        return

    nodes = pd.Index(model.config.system.set_nodes, name="node")
    for carrier in model.carriers.values():
        for name in (
            "transport_limit_in",
            "transport_limit_out",
            "transport_limit_net",
        ):
            attribute = Attribute(
                name=name,
                element=carrier,
                default_value=np.inf,
                unit=carrier.energy_unit,
                sources=[
                    AssumptionInformation(
                        description=(
                            "Carrier transport is unbounded unless a scenario "
                            "overrides this Reg4Fuels transport limit."
                        )
                    )
                ],
            )
            setattr(carrier, name, attribute)
            carrier._attribute_names.append(name)

        if model.settings.scenario.sensitivity_transport_limits:
            zero_limit = pd.Series(0.0, index=nodes, name="transport_limit_net")
            transport_limit_net = vars(carrier)["transport_limit_net"]
            transport_limit_net.add_scenarios(
                Scenario(
                    "net_carrier_import_limit",
                    df=zero_limit,
                    suffix="scenario",
                )
            )
            if carrier.name == "electricity":
                transport_limit_net.add_scenarios(
                    Scenario(
                        "net_electricity_import_limit",
                        df=zero_limit,
                        suffix="scenario",
                    )
                )
