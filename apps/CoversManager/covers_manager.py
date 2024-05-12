import math as Math

import hassapi as hass
import src.config_validator as ConfigValidator
import src.constants as Constants
from pydantic import ValidationError

"""
Author : Marc Guyard
Doc : https://github.com/mguyard/appdaemon-coversmanager/blob/main/README.md
Bug Report : https://github.com/mguyard/appdaemon-coversmanager/issues/new?assignees=&labels=bug&projects=&template=bug_report.yml
Feature Request : https://github.com/mguyard/appdaemon-coversmanager/issues/new?assignees=&labels=%F0%9F%9A%80%20feature-request&projects=&template=feature_request.yml
"""  # noqa: E501


class CoversManager(hass.Hass):
    def initialize(self):
        config = None
        try:
            config = ConfigValidator.Config(**self.args["config"])
        except ValidationError as e:
            self.stop_app(self.name)
            self.log(e, level="ERROR")
            # TODO : To enable for production
            # raise RuntimeError(
            #     "Invalid configuration. Please check the app logs for more information."
            # )  # => To enable after dev

        if config is not None:
            self.dryrun = config.dryrun
            try:
                self._verify_entities(config=config)
            except RuntimeError as e:
                self.stop_app(self.name)
                self.log(e, level="ERROR")
                # TODO : To enable for production
                # raise RuntimeError(
                #     "Invalid configuration. Please check the app logs for more information."
                # )  # => To enable after dev

            self.log(f"Configuration : {config.dict()}", level="DEBUG")

            # Manage Opening
            if not self._get_islocked(config=config, type="open"):
                match config.common.opening.type:
                    case "time":
                        self.run_daily(
                            callback=self._callback_move_covers,
                            start=config.common.opening.time,
                            config=config,
                            action="open",
                        )
                    case "sunrise":
                        self.log(f"Next sunrise : {self.sunrise()}", level="INFO")
                        self.run_at_sunrise(callback=self._callback_move_covers, config=config, action="open")
                    case "lux":
                        self.listen_state(
                            callback=self._callback_listenstate_covers,
                            entity_id=config.common.lux.sensor,
                            new=lambda x: int(x) >= config.common.lux.open_lux,
                            old=lambda x: int(x) < config.common.lux.open_lux,
                            config=config,
                            action="open",
                        )
                    case "prefer-lux":
                        self.preferlux_open_handler = self.run_daily(
                            callback=self._callback_move_covers,
                            start=config.common.opening.time,
                            config=config,
                            action="open",
                        )
                        self.listen_state(
                            callback=self._callback_listenstate_covers,
                            entity_id=config.common.lux.sensor,
                            new=lambda x: int(x) >= config.common.lux.open_lux,
                            old=lambda x: int(x) < config.common.lux.open_lux,
                            config=config,
                            action="open",
                        )
                    case "off":
                        self.log(
                            "Opening is disabled by configuration (config.common.opening.type: off)",
                            level="INFO",
                        )
            else:
                self.log("Opening is locked by locker entity (global or open locker)", level="INFO")

            # Manage Adaptive
            if config.common.closing.adaptive:
                self.log("Adaptive mode is enabled", level="DEBUG")
                for cover in config.covers.dict().keys():
                    self.log(
                        f"Configuration Cover : '{self.friendly_name(entity_id=cover).strip()}' ({cover})",
                        level="DEBUG",
                    )

                    if config.covers.root[cover].positional.action:
                        self.log(
                            f"Cover '{self.friendly_name(entity_id=cover).strip()}' "
                            f"({cover}) supports positional move. Adaptive mode is enable for this cover",
                            level="DEBUG",
                        )

                        # Create adaptive entity to store the adaptive position
                        adaptive_position_entity = self._get_adaptive_entity(cover=cover)
                        self.log(
                            "Content of Adaptive Entity for cover "
                            f"'{self.friendly_name(entity_id=cover).strip()}' ({cover}) "
                            f"to create/update : {adaptive_position_entity}",
                            level="DEBUG",
                        )
                        self._create_update_covermanager_entity(
                            entity=adaptive_position_entity,
                            state=self.get_state(entity_id=cover, attribute="current_position"),
                        )

                        # Create manual lock entity to store the manual lock status
                        manual_lock_entity = self._get_manuallock_entity(cover=cover)
                        self.log(
                            "Content of ManualLock Entity for cover "
                            f"'{self.friendly_name(entity_id=cover).strip()}' ({cover}) "
                            f"to create/update : {manual_lock_entity}",
                            level="DEBUG",
                        )
                        manual_lock_state = (
                            self.get_state(entity_id=manual_lock_entity["name"])
                            if self.entity_exists(entity_id=manual_lock_entity["name"])
                            else "off"
                        )
                        self._create_update_covermanager_entity(entity=manual_lock_entity, state=manual_lock_state)

                        # Calculate azimuth left and right
                        azimuth_left = (
                            config.covers.root[cover].window_azimuth - config.covers.root[cover].fov.left
                        ) % 360
                        azimuth_right = (
                            config.covers.root[cover].window_azimuth + config.covers.root[cover].fov.right
                        ) % 360
                        self.log(
                            f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) - "
                            f"Azimuth left : {azimuth_left} - Azimuth right : {azimuth_right}",
                            level="DEBUG",
                        )
                        sun_elevation = self.get_state(entity_id="sun.sun", attribute="elevation")
                        # Listen for azimuth change if sun is in the window and sun elevation is positive
                        # TODO : Verifier si il prend vraiment en compte l'elevation du soleil dans les conditions
                        #          Ou bien si il prend l'information au moment du chargement de l'application
                        self.listen_state(
                            callback=self._callback_listenstate_suninwindow,
                            entity_id="sun.sun",
                            attribute="azimuth",
                            new=lambda sunazimuth,
                            azimuth_left=azimuth_left,
                            azimuth_right=azimuth_right,
                            sun_elevation=sun_elevation: (int(sunazimuth) >= azimuth_left)
                            and (int(sunazimuth) <= azimuth_right)
                            and (sun_elevation > 0),
                            config=config,
                            cover=cover,
                            azimuth_left=azimuth_left,
                            azimuth_right=azimuth_right,
                        )
                        # Listen for azimuth change if sun is leaving the window
                        # TODO : Verifier si il prend vraiment en compte l'elevation du soleil dans les conditions
                        #          Ou bien si il prend l'information au moment du chargement de l'application
                        self.listen_state(
                            callback=self._callback_listenstate_sunleavewindow,
                            entity_id="sun.sun",
                            attribute="azimuth",
                            old=lambda sunazimuth,
                            azimuth_left=azimuth_left,
                            azimuth_right=azimuth_right,
                            sun_elevation=sun_elevation: (int(sunazimuth) >= azimuth_left)
                            and (int(sunazimuth) <= azimuth_right)
                            and (sun_elevation > 0),
                            new=lambda sunazimuth, azimuth_right=azimuth_right: int(sunazimuth) > azimuth_right,
                            cover=cover,
                        )
                        # Listen state for cover manual move detection
                        self.listen_state(
                            callback=self._callback_listenstate_manualmove_detection,
                            entity_id=cover,
                            attribute="current_position",
                            config=config,
                            adaptive_position_entity=adaptive_position_entity,
                        )

                    else:
                        self.log(
                            f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) "
                            "does not support positional move. Adaptive mode is disabled for this cover",
                            level="INFO",
                        )

            # Manage Closing
            if not self._get_islocked(config=config, type="close"):
                match config.common.closing.type:
                    case "time":
                        self.run_daily(
                            callback=self._callback_move_covers,
                            start=config.common.closing.time,
                            config=config,
                            action="close",
                        )
                    case "sunset":
                        self.log(f"Next sunset : {self.sunset()}", level="INFO")
                        self.run_at_sunset(callback=self._callback_move_covers, config=config, action="close")
                    case "lux":
                        self.listen_state(
                            callback=self._callback_listenstate_covers,
                            entity_id=config.common.lux.sensor,
                            new=lambda x: int(x) <= config.common.lux.close_lux,
                            old=lambda x: int(x) > config.common.lux.close_lux,
                            config=config,
                            action="close",
                        )
                    case "prefer-lux":
                        # If prefer-lux is configured, we need to check if time or secure_sunset is configured
                        if config.common.closing.secure_sunset:
                            self.preferlux_close_handler = self.run_at_sunset(
                                callback=self._callback_move_covers, config=config, action="close"
                            )
                        elif config.common.closing.time is not None:
                            self.preferlux_close_handler = self.run_daily(
                                callback=self._callback_move_covers,
                                entity_id=config.common.closing.time,
                                config=config,
                                action="close",
                            )
                        self.listen_state(
                            callback=self._callback_listenstate_covers,
                            entity_id=config.common.lux.sensor,
                            new=lambda x: int(x) <= config.common.lux.close_lux,
                            old=lambda x: int(x) > config.common.lux.close_lux,
                            config=config,
                            action="close",
                        )
                    case "off":
                        self.log(
                            "Closing is disabled by configuration (config.common.closing.type: off)",
                            level="INFO",
                        )
            else:
                self.log("Closing is locked by locker entity (global or close locker)", level="INFO")

            # TODO : Create a method will look all sensors and check if create by AD-CoverManager
            #       if yes, look if it's an cover existing in configuration and if not, delete it.
            #       Objective : Clean entities for deleted covers in configuration

            self.log(f"{self.name} fully Initialized !", level="INFO")

    def _verify_entities(self, config: ConfigValidator.Config) -> None:
        """
        Verify the entities defined in the configuration.

        Args:
            config (ConfigValidator.Config): The configuration object.

        Raises:
            ValueError: If a configured cover is not a valid cover entity.
            RuntimeError: If an entity defined in the configuration does not exist.
        """
        # Define all entities to check
        entities_dict = {
            "config.common.temperature.indoor.sensor": (
                config.common.temperature.indoor.sensor if config.common.temperature is not None else None
            ),
            "config.common.temperature.outdoor.sensor": (
                config.common.temperature.outdoor.sensor if config.common.temperature is not None else None
            ),
            "config.common.lux.sensor": (config.common.lux.sensor if config.common.lux is not None else None),
            "config.common.locker": (config.common.locker if config.common.locker is not None else None),
            "config.common.opening.locker": (
                config.common.opening.locker if config.common.opening.locker is not None else None
            ),
            "config.common.closing.locker": (
                config.common.closing.locker if config.common.closing.locker is not None else None
            ),
        }
        # Add covers entities in list of entities to check
        for index, cover in enumerate(config.covers.dict().keys()):
            # Verify if still needed as already checked in Pydantic
            # if not cover.startswith("cover."):
            #     raise ValueError(
            #         f"Configured cover {cover} is not a valid cover entity. Please check your configuration"
            #     )
            entities_dict[f"cover{index+1}"] = cover

        self.log(f"List all entities : {entities_dict}", level="DEBUG")
        # Remove None entities
        entities = {k: v for k, v in entities_dict.items() if v is not None}
        self.log(f"Filter all entities (excluding None) : {entities}", level="DEBUG")

        # Check if entities exists
        for configKey, entity in entities.items():
            if not self.entity_exists(entity_id=entity):
                raise RuntimeError(
                    f"Entity {entity} defined in configuration {configKey} does not exist. "
                    "Please check your configuration."
                )
        self.log("All entities exists and are valid", level="DEBUG")

    def _callback_move_covers(self, **kwargs: dict) -> None:
        """
        Callback function for opening or closing covers.

        This method is called when a callback event for opening/closing covers is triggered.
        It takes keyword arguments containing the necessary configuration data.

        Args:
            **kwargs (dict): Keyword arguments containing the following data:
                - config (CoverConfig): The configuration data for the covers.
                - action (str): The action to perform (open/close).

        Returns:
            None
        """
        self.log(f"{kwargs['action'].capitalize()} callback triggered...", level="DEBUG")
        covers_list = list(kwargs["config"].covers.dict().keys())  # List all configured covers
        self.log(f"Covers list : {covers_list}", level="DEBUG")
        try:
            covers_to_move = self._get_action_coverlist(
                covers_list=covers_list, action=kwargs["action"], config=kwargs["config"]
            )
        except ValueError as e:
            self.log(e, level="ERROR")
            return

        if (kwargs["action"] == "open" and kwargs["config"].common.position.opened == 100) or (
            kwargs["action"] == "close" and kwargs["config"].common.position.closed == 0
        ):
            if len(covers_to_move) > 0:
                self.log(f"Covers list to {kwargs['action']} : {covers_to_move}", level="DEBUG")
                try:
                    self._set_openclose_cover_full(covers=covers_to_move, action=kwargs["action"])
                except ValueError as e:
                    self.log(e, level="ERROR")
                    return
        else:
            covers_positional = self._get_positional_coverlist(covers_list=covers_to_move, config=kwargs["config"])
            covers_unpositional = [value for value in covers_to_move if value not in covers_positional]
            self.log(f"Positional Covers list to {kwargs['action']} : {covers_positional}", level="DEBUG")
            self.log(f"Unpositional Covers list to {kwargs['action']} : {covers_unpositional}", level="DEBUG")
            if len(covers_positional) > 0:
                position_requested = (
                    kwargs["config"].common.position.opened
                    if kwargs["action"] == "open"
                    else kwargs["config"].common.position.closed
                )
                self._set_cover_position(covers=covers_positional, position=position_requested)
            if len(covers_unpositional) > 0:
                if kwargs["action"] == "open":
                    self._set_openclose_cover_full(covers=covers_unpositional, action=kwargs["action"])

    def _callback_listenstate_covers(self, entity: str, attribute: str, old: str, new: str, **kwargs: dict) -> None:
        """
        Callback function triggered by a state change of the specified entity.

        Args:
            entity (str): The entity that triggered the state change.
            attribute (str): The attribute of the entity that changed.
            old (str): The previous state of the entity.
            new (str): The new state of the entity.
            **kwargs (dict): Additional keyword arguments.

        Returns:
            None
        """
        self.log(f"Callback triggered by state change of {entity} from {old} to {new}", level="DEBUG")
        self._callback_move_covers(**kwargs)

    def _callback_listenstate_suninwindow(
        self, entity: str, attribute: str, old: str, new: str, **kwargs: dict
    ) -> None:
        """
        Callback function triggered by a state change of the azimuth entity when sun is in windows.

        Args:
            entity (str): The entity that triggered the callback.
            attribute (str): The attribute of the entity that triggered the callback.
            old (str): The old value of the attribute.
            new (str): The new value of the attribute.
            **kwargs (dict): Additional keyword arguments.
                - azimuth_left (float): The azimuth value representing the left direction.
                - azimuth_right (float): The azimuth value representing the right direction.
                - cover (str): The cover entity.
                - config (ConfigValidator.Config): The configuration data.

        Returns:
            None
        """
        self.log(f"Callback triggered by state change of {entity}/{attribute} from {old} to {new}", level="DEBUG")

        # Check if the sun is entering in the window
        if old is not None and old < kwargs["azimuth_left"]:
            self.log(
                "Sun has entered the window of "
                f"'{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']})",
                level="INFO",
            )
        position = None

        # Get the current temperature (indoor and outdoor)
        indoor_temperature = float(self.get_state(entity_id=kwargs["config"].common.temperature.indoor.sensor))
        outdoor_temperature = float(self.get_state(entity_id=kwargs["config"].common.temperature.outdoor.sensor))

        # Check if the indoor temperature is lower or equal than the indoor setpoint
        if indoor_temperature <= int(kwargs["config"].common.temperature.indoor.setpoint):
            self.log(
                f"Indoor temperature ({indoor_temperature}) < "
                f"{kwargs['config'].common.temperature.indoor.setpoint} "
                f"- Cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) "
                "need to be open to heat the room",
                level="DEBUG",
            )
            position = 100

        # Check if the indoor temperature is greater than the indoor setpoint
        if indoor_temperature > int(kwargs["config"].common.temperature.indoor.setpoint):
            self.log(
                f"Indoor temperature ({indoor_temperature}) is greater than "
                f"{kwargs['config'].common.temperature.indoor.setpoint} - Adaptive mode will be used for cover "
                f"'{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']})",
                level="DEBUG",
            )
            # Check if the last changed time is greater than the minimum time change
            last_changed_seconds = round(self.get_entity(entity_id=kwargs["cover"]).last_changed_seconds)
            self.log(
                f"Cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) "
                f"last changed was {round(last_changed_seconds /60)} minutes ago",
                level="DEBUG",
            )
            if last_changed_seconds < (kwargs["config"].common.position.min_time_change * 60):
                self.log(
                    f"Last changed is lower than {kwargs['config'].common.position.min_time_change} minutes "
                    f"(Actually : {round(last_changed_seconds / 60)}). Adaptive mode is not used this time "
                    f"for cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']})",
                    level="INFO",
                )
                position = None  # Block change
            else:
                self.log(
                    f"Last changed is greater than {kwargs['config'].common.position.min_time_change} minutes "
                    "(common.position.min_time_change). Allowed to move cover "
                    f"'{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']})",
                    level="DEBUG",
                )
                # Calculate the adaptive position with min_ratio_change
                calculated_adaptive_position = (
                    Math.floor(
                        self._get_calculated_adaptive(cover=kwargs["cover"], sun_azimuth=new, config=kwargs["config"])
                        / kwargs["config"].common.position.min_ratio_change
                    )
                    * kwargs["config"].common.position.min_ratio_change
                )
                self.log(
                    f"Update adaptive position for cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' "
                    f"({kwargs['cover']}) based on min_ratio_change : {calculated_adaptive_position}%",
                    level="DEBUG",
                )
                position = calculated_adaptive_position

        # Check if the outdoor temperature is defined and if the high temperature is defined
        if (
            kwargs["config"].common.temperature.outdoor.sensor is not None
            and kwargs["config"].common.temperature.outdoor.high_temperature is not None
        ):
            # Check if the outdoor temperature is greater than the outdoor high temperature
            if outdoor_temperature >= int(kwargs["config"].common.temperature.outdoor.high_temperature):
                self.log(
                    f"Outdoor temperature ({outdoor_temperature}) > "
                    f"{kwargs['config'].common.temperature.outdoor.high_temperature} "
                    f"- Cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) "
                    "need to be close to avoid the heat",
                    level="DEBUG",
                )
                position = 0

        # Check if the position is defined
        if position is not None:
            position = min(
                max(kwargs["config"].common.position.closed, position), kwargs["config"].common.position.opened
            )
            self.log(
                "Update adaptive position for Cover "
                f"'{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) "
                "based on opened (config.common.position.opened) and "
                f"closed configuration (config.common.position.closed) : {position}%",
                level="DEBUG",
            )
            # TODO : Gerer aussi le mode manuel, uniquement quand on est en mode adaptatif
            if self._get_cover_currentposition(cover=kwargs["cover"]) != position:
                self.log(
                    f"Cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) is not "
                    f"at the required position ({position}) "
                    f"- Actual position : {self._get_cover_currentposition(cover=kwargs['cover'])}%",
                    level="DEBUG",
                )
                self._set_cover_position(covers=[kwargs["cover"]], position=position, adaptive=True)
            else:
                # If the cover is already at the needed position, only log event
                self.log(
                    f"Cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) "
                    f"is already at the needed position ({position}%)",
                    level="DEBUG",
                )

    def _callback_listenstate_sunleavewindow(
        self, entity: str, attribute: str, old: str, new: str, **kwargs: dict
    ) -> None:
        """
        Callback function triggered by a state change of the sun leaving the window.

        Args:
            entity (str): The entity that triggered the state change.
            attribute (str): The attribute that changed.
            old (str): The previous state value.
            new (str): The new state value.
            **kwargs (dict): Additional keyword arguments.
                - cover (str): The cover entity.

        Returns:
            None
        """
        self.log(f"Callback triggered by state change of {entity}/{attribute} from {old} to {new}", level="DEBUG")
        self.log(
            "Sun have leaved the window of "
            f"'{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']})",
            level="INFO",
        )
        self._set_cover_position(covers=[kwargs["cover"]], position=100, adaptive=True)

    def _get_calculated_adaptive(self, cover: str, sun_azimuth: str, config: ConfigValidator.Config) -> int:
        """
        Calculates the position of the cover based on the sun azimuth and configuration.

        Args:
            cover (str): The name of the cover.
            sun_azimuth (int): The azimuth of the sun.
            config (ConfigValidator.Config): The configuration object.

        Returns:
            int: The position of the cover as a percentage.

        """
        # Distance between floor and window to limit the sun
        floor_distance_window = 0.5
        # Retrieve sun elevation
        sun_elevation = self.get_state(entity_id="sun.sun", attribute="elevation")
        # Calculate the angular difference between the azimuth of the sun and the window azimuth
        angle_diff_azimut_sun_window = (config.covers.root[cover].window_azimuth - int(sun_azimuth) + 180) % 360 - 180
        # Calculate the height of the cover based on the angle difference and the sun elevation
        cover_heigh = min(
            max(
                0,
                (floor_distance_window / Math.cos(Math.radians(angle_diff_azimut_sun_window)))
                * Math.tan(Math.radians(sun_elevation)),
            ),
            config.covers.root[cover].window_heigh / 100,
        )
        # Convert the height of the cover to a percentage
        cover_percent = min(max(0, round(cover_heigh / (config.covers.root[cover].window_heigh / 100) * 100)), 100)
        self.log(
            f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) shoud be "
            f"position to {cover_percent}% (adaptive calculation)",
            level="DEBUG",
        )
        return cover_percent

    def _get_action_coverlist(self, covers_list: list, action: str, config: ConfigValidator.Config) -> list:
        """
        Get the list of covers to open/close.

        Args:
            covers_list (list): List of covers.
            action (str): Action to perform (open/close).
            config (ConfigValidator.Config): Configuration object.

        Returns:
            list: List of covers to move.
        """
        covers_to_move = []
        # Verify if action received by function is valid, otherwise raise an error
        if action not in ["open", "close"]:
            raise ValueError(
                "Action received by method _get_action_coverlist is not valid. "
                f"You have received : {action} but only 'open' or 'close' are allowed. "
                f"Please open issue to developer on GitHub {Constants.GITHUB_ISSUE_URL}"
            )
        for cover in covers_list:
            # If cover supports positional status
            if config.covers.root[cover].positional.status:
                current_position = self._get_cover_currentposition(cover=cover)
                if current_position is None:
                    self.log(
                        f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) current position is unknown",
                        level="WARNING",
                    )
                self.log(
                    f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) "
                    f"current position : {current_position}",
                    level="DEBUG",
                )
                # Define position requested based on action and configuration
                position_requested = (
                    config.common.position.opened if action == "open" else config.common.position.closed
                )
                # If cover does not support positional action, force position request to 100% or 0%
                if not config.covers.root[cover].positional.action:
                    self.log(
                        f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) "
                        "does not support positional action",
                        level="DEBUG",
                    )
                    if action == "open":
                        position_requested = 100
                        self.log(
                            f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) is not positional, "
                            "force position request to 100%",
                            level="DEBUG",
                        )
                    else:
                        position_requested = 0
                        self.log(
                            f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) is not positional, "
                            "force position request to 0%",
                            level="DEBUG",
                        )
                # If cover is not at requested position we add to move list
                if current_position != position_requested:
                    covers_to_move.append(cover)
                else:
                    self.log(
                        f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) is already opened "
                        f"at configured position ({position_requested}%)",
                        level="DEBUG",
                    )
            # If cover does not support positional status we add to move list by security
            else:
                covers_to_move.append(cover)
        return covers_to_move

    def _get_positional_coverlist(self, covers_list: list, config: ConfigValidator.Config) -> list:
        """
        Returns a list of positional covers from the given covers_list based on the provided config.

        Args:
            covers_list (list): A list of covers.
            config (ConfigValidator.Config): The configuration object.

        Returns:
            list: A list of positional covers.
        """
        positional_covers = []
        for cover in covers_list:
            if config.covers.root[cover].positional.action:
                positional_covers.append(cover)
        return positional_covers

    def _set_openclose_cover_full(self, covers: list, action: str, adaptive: bool = False) -> None:
        """
        Open or close the covers to a specified position. Used by the _callback_move_covers method.
        So only used for open or close covers (not for adaptive mode)

        Args:
            covers (list): List of cover entity IDs.
            action (str): Action to perform, either "open" or "close".

        Returns:
            None
        """
        if action not in ["open", "close"]:
            raise ValueError(
                "Action received by method _set_openclose_cover_full is not valid. "
                f"You have received : {action} but only 'open' or 'close' are allowed. "
                f"Please open issue to developer on GitHub {Constants.GITHUB_ISSUE_URL}"
            )
        position_required = 100 if action == "open" else 0
        if self.dryrun:
            self.log(
                f"DRY-RUN : {action.capitalize()} cover {covers} to {position_required}% ...",
                level="INFO",
            )
        else:
            self.log(f"{action.capitalize()} cover {covers} to {position_required}% ...", level="INFO")
            if action == "open":
                self.call_service("cover/open_cover", entity_id=covers)
            elif action == "close":
                self.call_service("cover/close_cover", entity_id=covers)
            for cover in covers:
                if adaptive:
                    self._create_update_covermanager_entity(
                        entity=self._get_adaptive_entity(cover), state=position_required
                    )
                self.run_in(
                    callback=self._callback_verify_cover_status,
                    delay=30,
                    cover=cover,
                    position_required=position_required,
                )

    def _set_cover_position(self, covers: list, position: int, adaptive: bool = False) -> None:
        """
        Sets the position of the specified covers to the given position.

        Args:
            covers (list): A list of cover entity IDs.
            position (int): The desired position of the covers.
            adaptive (bool): Whether the covers are being moved in adaptive mode.

        Returns:
            None
        """
        if self.dryrun:
            self.log(
                f"DRY-RUN : Setting position of cover {covers} to {position}% ...",
                level="INFO",
            )
        else:
            for cover in covers.copy():
                manual_lock_entity = self._get_manuallock_entity(cover=cover)
                if self.get_state(entity_id=manual_lock_entity["name"]) == "on":
                    manual_lock_handle = self.get_state(
                        entity_id=manual_lock_entity["name"], attribute="running_handler"
                    )
                    handler_end, _, _ = self.info_timer(handle=manual_lock_handle)
                    self.log(
                        f"Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) "
                        "is locked following a manual change. All move are blocked until manual lock "
                        f"is released (end: {handler_end.strftime('%Y-%m-%d %H:%M:%S')})",
                        level="INFO",
                    )
                    # If cover is locked, remove it from the list of covers to move
                    covers.remove(cover)
                    continue

                if adaptive:
                    self.log(f"Updating state of adaptive entity for cover {cover} to {position}%", level="DEBUG")
                    self._create_update_covermanager_entity(
                        entity=self._get_adaptive_entity(cover=cover), state=position
                    )

            if len(covers) > 0:
                self.log(f"Moving cover {covers} to {position}% ...", level="INFO")
                self.call_service("cover/set_cover_position", entity_id=covers, position=position)
                for cover in covers:
                    self.run_in(
                        callback=self._callback_verify_cover_status, delay=30, cover=cover, position_required=position
                    )

    def _callback_verify_cover_status(self, **kwargs: dict) -> None:
        """
        Verify the status of a cover and log the result.

        This method checks the current position of a cover and compares it with the required position.
        If the current position is different from the required position, an error message is logged.
        Otherwise, an info message is logged indicating that the cover is opened as requested.

        Args:
            kwargs (dict): Keyword arguments containing the cover and the required position.
                - 'cover' (str): The name or identifier of the cover.
                - 'position_required' (int): The required position of the cover in percentage.

        Returns:
            None
        """
        current_position = self._get_cover_currentposition(cover=kwargs["cover"])
        if current_position != kwargs["position_required"]:
            self.log(
                f"Cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) don't have "
                f"the required position ({kwargs['position_required']}%). "
                f"Current Position : {current_position}%",
                level="ERROR",
            )
        else:
            self.log(
                f"Cover '{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) is opened "
                f"as requested at {kwargs['position_required']}%",
                level="INFO",
            )

    def _get_cover_currentposition(self, cover: str) -> int | None:
        """
        Get the current position of a cover.

        Args:
            cover (str): The name of the cover.

        Returns:
            int | None: The current position of the cover, or None if the position is not available.
        """
        self.log(
            f"Getting Cover '{self.friendly_name(entity_id=cover).strip()}' ({cover}) current position...",
            level="DEBUG",
        )
        return self.get_state(entity_id=cover, attribute="current_position")

    def _generate_covermanager_entity_infos(self, cover: str, domain: str, type: str, icon: str) -> dict:
        """
        Generate the entity information for the CoversManager.

        Args:
            cover (str): The cover name.
            domain (str): The domain of the entity (sensor, binary_sensor, etc...).
            addon (str): The addon name.
            icon (str): The icon for the entity.

        Returns:
            dict: A dictionary containing the entity information, including the base name, entity name,
                  friendly name, and icon.
        """
        entity = {}
        entity_basename = cover.split(".", 1)[1]
        entity_name = f"{domain}.{entity_basename}_{type.replace(' ', '_').lower()}"
        entity_friendlyname = f"{self.friendly_name(entity_id=cover).strip()} - {type.title()}"
        entity.update(
            {
                "base": entity_basename,
                "name": entity_name,
                "friendlyname": entity_friendlyname,
                "icon": icon,
            }
        )
        return entity

    def _get_adaptive_entity(self, cover: str) -> dict:
        """
        Get the adaptive entity information for a given cover.

        Args:
            cover (str): The name of the cover.

        Returns:
            dict: A dictionary containing the adaptive entity information.

        """
        return self._generate_covermanager_entity_infos(
            cover=cover, domain="sensor", type="Adaptive Position", icon="mdi:window-shutter-auto"
        )

    def _get_manuallock_entity(self, cover: str) -> dict:
        """
        Get the manual lock entity information for a given cover.

        Args:
            cover (str): The name of the cover.

        Returns:
            dict: A dictionary containing the manual lock entity information.

        """
        return self._generate_covermanager_entity_infos(
            cover=cover, domain="binary_sensor", type="Manual Lock", icon="mdi:lock-clock"
        )

    def _check_covermanager_entity_existence(self, entity: str) -> bool:
        self.log(f"Checking if CoverManager entity {entity} exist...", level="DEBUG")
        if not self.entity_exists(entity_id=entity):
            return False
        elif (
            self.entity_exists(entity_id=entity)
            and self.get_state(entity_id=entity, attribute="source") == "AD-CoverManager"
        ):
            return True
        else:
            raise RuntimeError(
                f"Entity {entity} exist but not created by AD-CoverManager. "
                "Please update your HA configuration to remove exixting entity."
            )

    def _create_update_covermanager_entity(
        self, entity: dict, state: str | int, running_handler: str | None = None
    ) -> None:
        """
        Creates or updates a cover manager entity.

        Args:
            entity (dict): The entity information, including name, friendlyname, and icon.
            state (str | int): The state of the entity.
            running_handler (str | None, optional): The running handler of the entity. Defaults to None.
        """
        try:
            if self._check_covermanager_entity_existence(entity=entity["name"]):
                self.log(
                    f"Entity {entity['name']} already exists and was created by AD-CoverManager - Updating...",
                    level="DEBUG",
                )
            else:
                self.log(f"Entity {entity['name']} does not exist - Creating...", level="DEBUG")
            self.set_state(
                entity_id=entity["name"],
                state=state,
                attributes={
                    "friendly_name": entity["friendlyname"],
                    "icon": entity["icon"],
                    "running_handler": running_handler,
                    "source": "AD-CoverManager",
                },
            )
            self.log(f"Entity {entity['name']} created/updated successfully with state {state}", level="INFO")
        except RuntimeError as e:
            self.log(e, level="ERROR")

    def _callback_listenstate_manualmove_detection(
        self, entity: str, attribute: str, old: str, new: str, **kwargs: dict
    ) -> None:
        """
        Callback function triggered when a manual move is detected for a cover.

        Args:
            entity (str): The entity ID of the cover.
            attribute (str): The attribute that triggered the callback.
            old (str): The previous value of the attribute.
            new (str): The new value of the attribute.
            **kwargs (dict): Additional keyword arguments.
                - config (object): An object containing configuration settings.
                - adaptive_position_entity (dict): A dictionary containing information about the adaptive entity

        Returns:
            None
        """
        # Check if the new position is different from the adaptive position
        if int(new) != int(self.get_state(entity_id=kwargs["adaptive_position_entity"]["name"])):
            lock_duration_minutes = int(kwargs["config"].common.manual.timer.total_seconds() / 60)
            self.log(
                f"MANUAL MOVE DETECTED - New position is {new}% but "
                f"adaptive position is {self.get_state(entity_id=kwargs['adaptive_position_entity']['name'])}%",
                level="DEBUG",
            )
            self.log(
                "MANUAL MOVE DETECTED - Blocking move of cover "
                f"'{self.friendly_name(entity_id=entity).strip()}' ({entity}) "
                f"for {lock_duration_minutes} minutes",
                level="INFO",
            )
            manual_lock_entity = self._get_manuallock_entity(cover=entity)
            # Check if the manual lock entity already exists and is on
            if (
                self.entity_exists(entity_id=manual_lock_entity["name"])
                and self.get_state(entity_id=manual_lock_entity["name"]) == "on"
                and self.get_state(entity_id=manual_lock_entity["name"], attribute="running_handler") is not None
            ):
                self.log(
                    f"Manual lock already exists for cover {self.friendly_name(entity_id=entity).strip()}' ({entity}) "
                    "- Resetting timer...",
                    level="DEBUG",
                )
                self.reset_timer(
                    handle=self.get_state(entity_id=manual_lock_entity["name"], attribute="running_handler")
                )
            else:
                # Create a new timer for the manual lock
                handler = self.run_in(
                    callback=self._callback_manuallock_timer_end,
                    delay=kwargs["config"].common.manual.timer.total_seconds(),
                    cover=entity,
                )
                # Update the manual lock entity
                self._create_update_covermanager_entity(entity=manual_lock_entity, state="on", running_handler=handler)

    def _callback_manuallock_timer_end(self, **kwargs: dict) -> None:
        """
        Callback method called when the manual lock timer ends.

        Args:
            kwargs (dict): Keyword arguments containing information about the cover.
                - cover (str): The name of the cover.

        Returns:
            None
        """
        self.log(
            "Manual lock timer ended for cover "
            f"'{self.friendly_name(entity_id=kwargs['cover']).strip()}' ({kwargs['cover']}) - Unlocking cover",
            level="INFO",
        )
        # Update the manual lock entity
        manual_lock_entity = self._get_manuallock_entity(cover=kwargs["cover"])
        self._create_update_covermanager_entity(entity=manual_lock_entity, state="off", running_handler=None)

    def _get_islocked(self, config: ConfigValidator.Config, type: str) -> bool:
        """
        Check if the locker is locked for the specified type.

        Args:
            config (ConfigValidator.Config): The configuration object.
            type (str): The type of locker to check. Must be either 'open' or 'close'.

        Returns:
            bool: True if the locker is locked for the specified type, False otherwise.
        """
        if type not in ["open", "close"]:
            self.log(
                f"Type {type} is not valid for locker verification. Only 'open' or 'close' are allowed. "
                "Locker is disabled for this test",
                level="ERROR",
            )
            return False

        if config.common.locker is not None:
            global_locker = True if self.get_state(entit_id=config.common.locker) == "on" else False
        else:
            global_locker = False

        if config.common.opening.locker is not None:
            opening_locker = True if self.get_state(entit_id=config.common.opening.locker) == "on" else False
        else:
            opening_locker = False

        if config.common.closing.locker is not None:
            closing_locker = True if self.get_state(entit_id=config.common.closing.locker) == "on" else False
        else:
            closing_locker = False

        self.log(
            f"Global Locker: {global_locker} - Opening Locker: {opening_locker} - Closing Locker: {closing_locker}",
            level="DEBUG",
        )

        match type:
            case "open":
                return global_locker or opening_locker
            case "close":
                return global_locker or closing_locker
            case _:
                return False
