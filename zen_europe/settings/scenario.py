from typing import ClassVar

from zen_creator.utils.settings import SettingsCategory


class ScenarioSettings(SettingsCategory):
    """Scenario settings."""

    name: ClassVar[str] = "scenario"
    controls: ClassVar[dict[str, str]] = {
        "run_default_scenario": "system.run_default_scenario",
    }

    run_default_scenario: bool = True
    sensitivity_demand: bool = False
    sensitivity_discount_rate: bool = False
    sensitivity_biomass: bool = False
    sensitivity_no_diffusion_rate: bool = False
    sensitivity_reg4fuels: bool = False
    sensitivity_operations: bool = False
    sensitivity_transport_limits: bool = False
    sensitivity_net_survival: bool = False