"""Global scenario definitions for the ZEN-europe model.

Defines the system, analysis, and solver overrides and the set-wide entries
(e.g. across all technologies) of the scenario analysis. A scenario that
varies a single element's attribute is defined next to that attribute
instead, in the element's own file, via
`Attribute.set_data(scenarios=...)`.
"""

from zen_creator import Model


def define_global_scenarios(model: Model) -> None:
    """Register the system, analysis, solver, and set-wide scenarios.

    Called by `create_model` after `model.build()`, so every element's own
    scenario variations are already registered. Guided by `model.settings`.

    Args:
        model: The model to register scenarios on.

    Examples:
        >>> model.scenarios.add("coarse", system={"aggregated_time_steps_per_year": 96})
        >>> model.scenarios.add_set(
        ...     "slow_diffusion", "set_technologies", "max_diffusion_rate",
        ...     default_op=0.5,
        ... )
    """
    if model.settings.scenario.sensitivity_no_diffusion_rate:
        model.scenarios.add_set(
            name="no_diffusion_rate",
            set_label="set_technologies",
            param="max_diffusion_rate",
            default_op=0.0,
        )
    if model.settings.scenario.sensitivity_operations:
        model.scenarios.add(
            "full_year",
            system={
                "conduct_time_series_aggregation": False,
                "aggregated_time_steps_per_year": 8760,
            },
        )
