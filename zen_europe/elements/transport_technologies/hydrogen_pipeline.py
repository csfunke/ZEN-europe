from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.edges import Edges
from zen_europe.datasets.dataset_collections.transport_technologies_costs import (
    TransportTechnologiesCosts,
)
from zen_europe.datasets.datasets.technology.dea_energy_transport import (
    DEAEnergyTransport,
)
from zen_europe.datasets.datasets.technology.ec_pci_pmi_list import (
    ECProjectsOfCommonInterest,
)
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import TransportTechnology
from zen_creator.utils.attribute import Attribute


class HydrogenPipeline(TransportTechnology):
    """Class containing all data and assumptions for hydrogen pipeline
    transport technology."""

    name: str = "hydrogen_pipeline"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of hydrogen pipeline to hydrogen.
        """
        return Attribute(
            name="reference_carrier", default_value=["hydrogen"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of hydrogen pipeline.
        """
        energy_transport = DEAEnergyTransport(source_path=self.source_path)
        return energy_transport.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of hydrogen pipeline.
        """
        if not self.settings.investment.use_construction_times:
            return self.construction_time
        energy_transport = DEAEnergyTransport(source_path=self.source_path)
        return energy_transport.get_construction_time(self)

    def _set_transport_loss_factor_linear(self) -> Attribute:
        """
        Sets the linear transport loss factor of hydrogen pipeline.
        """
        energy_transport = DEAEnergyTransport(source_path=self.source_path)
        return energy_transport.get_transport_loss_factor_linear(self)

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of hydrogen pipeline.

        Capacity additions up to the size of a single reference project are
        exempt from the diffusion limit, so that a first pipeline can be built
        from a zero installed base.
        """
        pci_pmi_list = ECProjectsOfCommonInterest(source_path=self.source_path)
        return pci_pmi_list.get_capacity_addition_unbounded(self)

    def _set_capex_per_distance_transport(self) -> Attribute:
        """
        Sets the distance-specific capex of hydrogen pipeline.
        """
        transport_costs = TransportTechnologiesCosts(
            source_path=self.source_path,
        )
        return transport_costs.get_capex_per_distance_transport(self)

    # TODO implement opex_specific_fixed_per_distance in ZEN-garden
    # def _set_opex_specific_fixed(self) -> Attribute:
    #     """
    #     Sets the distance-specific fixed opex of hydrogen pipeline.
    #     """
    #     transport_costs = TransportTechnologiesCosts(
    #         settings=self.settings,
    #         source_path=self.source_path,
    #         set_nodes=self.model.config.system.set_nodes,
    #     )
    #     return transport_costs.get_opex_specific_fixed_per_distance(self)

    def _set_capacity_limit(self) -> Attribute:
        """
        Sets the capacity limit of hydrogen pipeline.

        Unless offshore chemical pipelines are allowed, the capacity limit is 0
        on the edges that cross the sea.
        """
        if self.settings.investment.allow_offshore_chemical_pipelines:
            return self.capacity_limit
        edges = Edges(source_path=self.source_path)
        return edges.get_capacity_limit_offshore(self)

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of hydrogen pipeline.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

    # ---------- Attributes that still have to be ported ----------

    # TODO: capacity_existing stays 0, as the legacy pipeline models no
    # existing hydrogen network.
