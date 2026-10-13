from typing import ClassVar

from zen_creator.utils.settings import SettingsCategory


class AvailabilitySettings(SettingsCategory):
    """Carrier availability/import settings."""

    name: ClassVar[str] = "availability"

    cap_waste_import: bool = True
    cap_coal_import: bool = False
    cap_oil_import: bool = True
    annual_cap_biomass_import: bool = False
    allow_heat_demand_shedding: bool = False
    allow_all_demand_shedding: bool = False
    allow_hydrogen_imports: bool = False
    use_transport_limits: bool = False
