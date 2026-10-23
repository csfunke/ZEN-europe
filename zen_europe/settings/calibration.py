from typing import ClassVar

from zen_creator.utils.settings import SettingsCategory


class CalibrationSettings(SettingsCategory):
    """Project-specific calibration switches."""

    name: ClassVar[str] = "calibration"

    use_swiss_calibration: bool = False
    use_renewable_credits: bool = False
