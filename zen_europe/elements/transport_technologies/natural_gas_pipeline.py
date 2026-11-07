from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.transport_technologies_costs import (
    TransportTechnologiesCosts,
)
from zen_europe.datasets.datasets.technology.entsog_capacity_map import (
    ENTSOGCapacityMap,
)
from zen_europe.datasets.datasets.technology.scigrid import SciGridIGGIELGNC1
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation
from zen_creator.elements import TransportTechnology
from zen_creator.utils.attribute import Attribute


class NaturalGasPipeline(TransportTechnology):
    """Class containing all data and assumptions for natural gas pipeline
    transport technology."""

    name: str = "natural_gas_pipeline"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of natural gas pipeline to natural gas.
        """
        return Attribute(
            name="reference_carrier", default_value=["natural_gas"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of natural gas pipeline.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=60,
            source=AssumptionInformation(
                description=(
                    "The lifetime of natural gas pipelines is manually set to "
                    "60 years, in line with the lifetime of the other linear "
                    "transport infrastructure."
                ),
            ),
        )

    def _set_transport_loss_factor_linear(self) -> Attribute:
        """
        Sets the linear transport loss factor of natural gas pipeline.
        """
        attr = self.transport_loss_factor_linear
        return attr.set_data(
            default_value=5e-5,
            unit="1/km",
            source=AssumptionInformation(
                description=(
                    "The transport losses of natural gas pipelines are "
                    "manually set to 5e-5 per km, in line with the losses of "
                    "the other linear transport infrastructure."
                ),
            ),
        )

    def _set_capex_per_distance_transport(self) -> Attribute:
        """
        Sets the distance-specific capex of natural gas pipeline.
        """
        transport_costs = TransportTechnologiesCosts(
            source_path=self.source_path,
        )
        return transport_costs.get_capex_per_distance_transport(self)

    # TODO implement opex_specific_fixed_per_distance in ZEN-garden
    # def _set_opex_specific_fixed(self) -> Attribute:
    #     """
    #     Sets the distance-specific fixed opex of natural gas pipeline.
    #     """
    #     transport_costs = TransportTechnologiesCosts(
    #         settings=self.settings,
    #         source_path=self.source_path,
    #         set_nodes=self.model.config.system.set_nodes,
    #     )
    #     return transport_costs.get_opex_specific_fixed_per_distance(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of natural gas pipeline.
        """
        if not self.settings.investment.use_existing_capacities:
            attr = self.capacity_existing
            return attr.set_data(
                default_value=0,
                source=AssumptionInformation(
                    description="We do not consider existing capacities.",
                ),
            )
        if self.settings.data_source.use_full_scigrid_dataset:
            scigrid = SciGridIGGIELGNC1(source_path=self.source_path)
            return scigrid.get_capacity_existing_pipeline(self)
        capacity_map = ENTSOGCapacityMap(source_path=self.source_path)
        return capacity_map.get_capacity_existing_pipeline(self)

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of natural gas pipeline.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

    # ---------- Attributes that still have to be ported ----------

    # NOTE: DEAEnergyTransport also reports a lifetime of 50 years, a
    # construction time of 1 year and losses of 0.1% per km for the main gas
    # distribution line, which are not used: the assumptions above are kept.

    # TODO: the offshore cost of the natural gas pipeline is the onshore cost
    # scaled with the offshore cost increase of the ammonia pipelines of
    # Galimova et al. (2023), as the DEA catalogue reports no offshore cost for
    # gas pipelines. See OFFSHORE_COST_INCREASE_PROXY in
    # TransportTechnologiesCosts.

    # TODO: the ENTSOG capacity map lists no interconnection point for the
    # DK-SE and the EE-LV border, and none for the Norwegian entry into the
    # Netherlands, so those edges have no existing capacity. The legacy
    # pipeline adds them by hand, together with the Greek capacity towards
    # Italy, which the map reports as an Albanian point.
