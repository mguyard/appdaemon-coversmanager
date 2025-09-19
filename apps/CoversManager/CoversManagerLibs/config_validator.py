from datetime import time, timedelta
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    RootModel,
    field_validator,
    model_validator,
)
from pydantic.functional_validators import AfterValidator
from typing_extensions import Self

import CoversManagerLibs.utils as Utils

sensor_entity_format = Annotated[str, AfterValidator(Utils.isEntityFormat)]
locker_format = Annotated[str, AfterValidator(Utils.isLockerEntityFormat)]
time_ = time  # To resolve issue : https://github.com/pydantic/pydantic/discussions/9284


class PositionConfig(BaseModel):
    opened: int = Field(ge=0, le=100, default=100)
    closed: int = Field(ge=0, le=100, default=0)
    min_ratio_change: int = Field(ge=0, le=100, default=5)
    min_time_change: PositiveInt = Field(ge=1, default=10)


class TemperatureOutdoorConfig(BaseModel):
    sensor: sensor_entity_format | None = None
    low_temperature: PositiveInt | None = None
    high_temperature: PositiveInt | None = None

    @model_validator(mode="after")
    def checks(self) -> Self:
        if self.sensor is not None and self.high_temperature is None:
            raise ValueError("High temperature must be defined when outdoor sensor is defined")
        return self

class SeasonConfig(BaseModel):
    setpoint: PositiveInt | None = None

class SeasonsConfig(BaseModel):
    spring: SeasonConfig = SeasonConfig()
    summer: SeasonConfig = SeasonConfig()
    autumn: SeasonConfig = SeasonConfig()
    winter: SeasonConfig = SeasonConfig()

    @field_validator("spring", mode="before")
    def spring_none_default_values(cls, value):
        if value is None:
            return SeasonConfig()
        return value

    @field_validator("summer", mode="before")
    def summer_none_default_values(cls, value):
        if value is None:
            return SeasonConfig()
        return value

    @field_validator("autumn", mode="before")
    def autumn_none_default_values(cls, value):
        if value is None:
            return SeasonConfig()
        return value

    @field_validator("winter", mode="before")
    def winter_none_default_values(cls, value):
        if value is None:
            return SeasonConfig()
        return value

class TemperatureIndoorConfig(BaseModel):
    sensor: sensor_entity_format | None = None
    setpoint: PositiveInt | None = None
    seasons: SeasonsConfig = SeasonsConfig()

    @field_validator("seasons", mode="before")
    def seasons_none_default_values(cls, value):
        if value is None:
            return SeasonsConfig()
        return value


class TemperatureConfig(BaseModel):
    indoor: TemperatureIndoorConfig = TemperatureIndoorConfig()
    outdoor: TemperatureOutdoorConfig = TemperatureOutdoorConfig()

    @field_validator("indoor", mode="before")
    def indoor_none_default_values(cls, value):
        if value is None:
            return TemperatureIndoorConfig()
        return value

    @field_validator("outdoor", mode="before")
    def outdoor_none_default_values(cls, value):
        if value is None:
            return TemperatureOutdoorConfig()
        return value


class LuxConfig(BaseModel):
    sensor: sensor_entity_format | None = None
    open_lux: PositiveInt | None = None
    close_lux: int = Field(ge=0, default=None)


class ManualConfig(BaseModel):
    allow: bool = False
    timer: timedelta | None = None

    @model_validator(mode="after")
    def checks(self) -> Self:
        if self.allow and self.timer is None:
            raise ValueError(
                "Timer argument (config.common.manual.timer) must be defined "
                "when manual mode (config.common.manual.timer) is enabled (True)"
            )
        return self

class OpenCloseSeasonsPositionConfig(BaseModel):
    spring: int = Field(ge=0, le=100, default=None)
    summer: int = Field(ge=0, le=100, default=None)
    autumn: int = Field(ge=0, le=100, default=None)
    winter: int = Field(ge=0, le=100, default=None)


class OpenClosePositionConfig(BaseModel):
    default: int = Field(ge=0, le=100, default=None)
    seasons: OpenCloseSeasonsPositionConfig | None = None


class OpeningConfig(BaseModel):
    type: Literal["off", "time", "sunrise", "lux", "prefer-lux"] = "off"
    time: time_ | None = None
    locker: locker_format | None = None
    position: OpenClosePositionConfig = OpenClosePositionConfig()

    @field_validator("position", mode="before")
    def position_none_default_values(cls, value):
        if value is None:
            return OpenClosePositionConfig()
        return value

    @model_validator(mode="after")
    def checks(self) -> Self:
        if self.type in ["time", "prefer-lux"] and self.time is None:
            raise ValueError(
                "Time argument (config.common.opening.time) must be defined when type is time or prefer-lux"
            )
        return self


class ClosingConfig(BaseModel):
    type: Literal["off", "time", "sunset", "lux", "prefer-lux"] = "off"
    time: time_ | None = None
    secure_dusk: bool = False
    locker: locker_format | None = None
    bypass_global_locker: bool = False
    position: OpenClosePositionConfig = OpenClosePositionConfig()

    @field_validator("position", mode="before")
    def position_none_default_values(cls, value):
        if value is None:
            return OpenClosePositionConfig()
        return value

    @model_validator(mode="after")
    def checks(self) -> Self:
        if self.type == "time" and self.time is None:
            raise ValueError("Time configuration (config.common.closing.time) must be defined when type is time")
        if self.type == "prefer-lux" and (self.time is None and self.secure_dusk is False):
            raise ValueError(
                "Time (config.common.closing.time) or secure_dusk (config.common.closing.secure_dusk) "
                "configuration must be defined when type is prefer-lux"
            )
        if self.type in ["time", "prefer-lux"] and (self.time is not None and self.secure_dusk is True):
            raise ValueError(
                "Only one of time (config.common.closing.time) or "
                "secure_dusk (config.common.closing.secure_dusk) configuration must be defined"
            )
        return self

class AdaptiveConfig(BaseModel):
    enable: bool = False
    locker: locker_format | None = None


class CommonConfig(BaseModel):
    position: PositionConfig = PositionConfig()
    opening: OpeningConfig = OpeningConfig()
    closing: ClosingConfig = ClosingConfig()
    adaptive: AdaptiveConfig = AdaptiveConfig()
    manual: ManualConfig = ManualConfig()
    temperature: TemperatureConfig = TemperatureConfig()
    lux: LuxConfig | None = None
    locker: locker_format | None = None
    seasons: sensor_entity_format | None = None

    @field_validator("position", mode="before")
    def position_none_default_values(cls, value):
        if value is None:
            return PositionConfig()
        return value

    @field_validator("opening", mode="before")
    def opening_none_default_values(cls, value):
        if value is None:
            return OpeningConfig()
        return value

    @field_validator("closing", mode="before")
    def closing_none_default_values(cls, value):
        if value is None:
            return ClosingConfig()
        return value

    @field_validator("adaptive", mode="before")
    def adaptive_none_default_values(cls, value):
        if value is None:
            return AdaptiveConfig()
        return value

    @field_validator("manual", mode="before")
    def manual_none_default_values(cls, value):
        if value is None:
            return ManualConfig()
        return value

    @field_validator("temperature", mode="before")
    def temperature_none_default_values(cls, value):
        if value is None:
            return TemperatureConfig()
        return value

    @model_validator(mode="after")
    def checks(self) -> Self:
        # Seasons configuration check
        if (
            self.seasons is None
            and (
                self.temperature.indoor.seasons.spring.setpoint is not None
                or self.temperature.indoor.seasons.summer.setpoint is not None
                or self.temperature.indoor.seasons.autumn.setpoint is not None
                or self.temperature.indoor.seasons.winter.setpoint is not None
            )
        ):
            raise ValueError(
                "Seasons configuration (config.common.seasons) is missing to use "
                "seasons setpoints (config.common.temperature.indoor.seasons)"
            )

        if (
            self.seasons is None
            and (
                self.opening.position.seasons is not None
                or self.closing.position.seasons is not None
            )
        ):
            raise ValueError(
                "Seasons configuration (config.common.seasons) is missing to use "
                "seasons position for open or close (config.common.opening.position.seasons "
                "or config.common.closing.position.seasons)"
            )
        return self


class PositionalConfig(BaseModel):
    action: bool = True
    status: bool = True


class FovConfig(BaseModel):
    left: int = Field(ge=0, lt=180, default=90)
    right: int = Field(ge=0, lt=180, default=90)


class CoversConfig(BaseModel):
    window_heigh: PositiveInt
    window_azimuth: int = Field(ge=0, lt=360)
    positional: PositionalConfig = PositionalConfig()
    fov: FovConfig = FovConfig()

    @field_validator("positional", mode="before")
    def positional_none_default_values(cls, value):
        if value is None:
            return PositionalConfig()
        return value

    @field_validator("fov", mode="before")
    def fov_none_default_values(cls, value):
        if value is None:
            return FovConfig()
        return value


class CoversName(RootModel):
    root: dict[Annotated[str, AfterValidator(Utils.isCoverEntityFormat)], CoversConfig]


class Config(BaseModel):
    dryrun: bool = False
    common: CommonConfig
    covers: CoversName | None = None

    @model_validator(mode="after")
    def checks(self) -> Self:
        # Lux configuration check
        luxMode = ["lux", "prefer-lux"]
        if self.common.lux is None and (self.common.opening.type in luxMode or self.common.closing.type in luxMode):
            raise ValueError(
                "Lux configuration (config.common.lux) is missing as at least one of "
                f"opening or closing is configured with one of {', '.join(luxMode)} mode"
            )
        if self.common.lux.sensor is None and (
            self.common.opening.type in luxMode or self.common.closing.type in luxMode
        ):
            raise ValueError(
                "Lux sensor configuration (config.common.lux.sensor) is missing as at least one of "
                f"opening or closing is configured with one of {', '.join(luxMode)} mode"
            )
        if self.common.opening.type in luxMode and self.common.lux.open_lux is None:
            raise ValueError(
                "Lux configuration (config.common.lux.open_lux) is missing as opening "
                f"is configured with {self.common.opening.type} mode"
            )
        if self.common.closing.type in luxMode and self.common.lux.close_lux is None:
            raise ValueError(
                "Lux configuration (config.common.lux.close_lux) is missing "
                f"as closing is configured with {self.common.closing.type} mode"
            )
        # Temperature configuration check
        temperatureIndoorParameters = [
            "sensor",
            "setpoint",
        ]
        if self.common.adaptive.enable and (self.common.temperature is None or self.common.temperature.indoor is None):
            raise ValueError(
                "Temperature configuration (config.common.temperature.indoor) is missing as "
                "adaptive mode (config.common.adaptive.enable) is enabled (True)"
            )
        for param in temperatureIndoorParameters:
            if self.common.adaptive.enable and getattr(self.common.temperature.indoor, param) is None:
                raise ValueError(
                    f"Configuration {param} (config.common.temperature.indoor.{param}) must be defined as "
                    "adaptive mode (config.common.adaptive.enable) is enabled (True)"
                )
        # Covers configuration check
        if self.covers is None:
            raise ValueError("At least one cover must be defined")
        return self
