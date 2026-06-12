from pathlib import Path

from zen_creator import Model

from .datasets import (
    dataset_collections,  # noqa: F401
    datasets,  # noqa: F401
)

# import custom element classes to register them in the registry (side effect)
from .elements import (
    carriers,  # noqa: F401
    conversion_technologies,  # noqa: F401
    energy_systems,  # noqa: F401
    storage_technologies,  # noqa: F401
    transport_technologies,  # noqa: F401
)


def create_model(
    config: Path | str | None = None,
    name: str = "zen-europe",
    output_folder: Path | str = ".",
    write: bool = True,
) -> Model:
    # Get path to crystal ball model
    zen_europe_package_dir = Path(__file__).resolve().parent.parent
    crystal_ball_path = zen_europe_package_dir / "data" / "crystal_ball"

    if config is None:
        config = zen_europe_package_dir / "data" / "config.yaml"

    # load crystal ball model as starting point
    # TODO: this should be remove in the long run and replaced
    # with model.from_config()
    model = Model.from_existing(crystal_ball_path, config=config)
    model.output_folder = Path(output_folder)
    model.name = name

    # apply changes
    model.build()

    # save model output
    if write:
        model.write()

    return model
