from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.transport_technologies_costs import (
    TransportTechnologiesCosts,
)
from zen_europe.datasets.datasets.technology.dea_carbon_transport import (
    DEACarbonTransport,
)
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)
from zen_europe.utils.constants import Constants

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation
from zen_creator.elements import TransportTechnology
from zen_creator.utils.attribute import Attribute


class CarbonPipeline(TransportTechnology):
    """Class containing all data and assumptions for carbon (CO2) pipeline
    transport technology."""

    name: str = "carbon_pipeline"

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of carbon pipeline to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of carbon pipeline.
        """
        carbon_transport = DEACarbonTransport(source_path=self.source_path)
        return carbon_transport.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of carbon pipeline.
        """
        if not self.settings.investment.use_construction_times:
            return self.construction_time
        carbon_transport = DEACarbonTransport(source_path=self.source_path)
        return carbon_transport.get_construction_time(self)

    def _set_capex_per_distance_transport(self) -> Attribute:
        """
        Sets the distance-specific capex of carbon pipeline.
        """
        transport_costs = TransportTechnologiesCosts(
            source_path=self.source_path,
        )
        return transport_costs.get_capex_per_distance_transport(self)

    # TODO implement opex_specific_fixed_per_distance in ZEN-garden
    # def _set_opex_specific_fixed(self) -> Attribute:
    #     """
    #     Sets the distance-specific fixed opex of carbon pipeline.
    #     """
    #     transport_costs = TransportTechnologiesCosts(
    #         settings=self.settings,
    #         source_path=self.source_path,
    #         set_nodes=self.model.config.system.set_nodes,
    #     )
    #     return transport_costs.get_opex_specific_fixed_per_distance(self)

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of carbon pipeline.

        Capacity additions up to the size of a single reference project are
        exempt from the diffusion limit, so that a first pipeline can be built
        from a zero installed base.
        """
        attr = self.capacity_addition_unbounded
        if not self.settings.investment.use_unbounded_capacity_addition_carbon:
            return attr
        return attr.set_data(
            default_value=Constants.DUIVEN_CAPTURE_CAPACITY / Constants.HOURS_PER_YEAR,
            unit="tCO2/h",
            source=AssumptionInformation(
                description=(
                    "The unbounded capacity addition is the size of the Duiven "
                    "carbon capture plant (0.1 MtCO2 per year)."
                ),
            ),
        )

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of carbon pipeline.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

    # ---------- Attributes that still have to be ported ----------

    # TODO: opex_specific_variable ends at 0 in the legacy pipeline: a value of
    # 5.17 Euro per tCO2 from Smith et al. (2021) is computed and then
    # overwritten by the variable O&M of the DEA catalogue, which is 0. The
    # framework default of 0 therefore applies.

    # TODO: transport_loss_factor_linear is never written in the legacy
    # pipeline (only its unit is set), so the framework default of 0 applies.

    # TODO: capacity_existing and capacity_limit have no data source in the
    # legacy pipeline, so the framework defaults of 0 and infinity apply.
