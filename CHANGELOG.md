# [2.0.0-beta.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.5.0-beta.2...v2.0.0-beta.1) (2024-11-10)


### Features

* Refactor adaptive configuration to allow a dedicated locker for adaptive ([440fba2](https://github.com/mguyard/appdaemon-coversmanager/commit/440fba2ad1982d7d922e1e791eb2bd4fa469837b))


### BREAKING CHANGES

* adaptive configuration is no more in common.closing.adaptive but directly in common.adaptive with 2 parameters (enable and locker). You need to adjust your configuration to follow this change. Follow documentation please

# [1.5.0-beta.2](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.5.0-beta.1...v1.5.0-beta.2) (2024-10-12)


### Bug Fixes

* Update _get_indoor_setpoint method to allow None for seasons parameter ([3dbc033](https://github.com/mguyard/appdaemon-coversmanager/commit/3dbc03337aa91bfe8616e63e6a2b43d555ca1d11))

# [1.5.0-beta.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.4.0...v1.5.0-beta.1) (2024-10-12)


### Features

* Add seasonal configuration support for indoor temperature setpoints ([8c2c853](https://github.com/mguyard/appdaemon-coversmanager/commit/8c2c853f0d9f62ce934dc39f98c1f52a8a872bf4))

# [1.4.0](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.1...v1.4.0) (2024-08-11)


### Bug Fixes

* Resolve critical issue in a log who block application loading ([820adf3](https://github.com/mguyard/appdaemon-coversmanager/commit/820adf377d602e7b33d4a6ee19ad37bb0c088b8c))
* Resolve issue with adaptive mode conditional for outdoor sensor ([9a462ff](https://github.com/mguyard/appdaemon-coversmanager/commit/9a462ff973eca04733198a6d5a2ccad02e07a126))
* Update lambda functions to handle non-integer values when HA return None (following start for example) ([181b4b4](https://github.com/mguyard/appdaemon-coversmanager/commit/181b4b40553f6de2cf2e0efb4c5faf5b839ed2f7))
* Update lambda functions to handle non-integer values when HA return unknown (following start for example) ([c59eefc](https://github.com/mguyard/appdaemon-coversmanager/commit/c59eefc14c90506001ddc40d523b191aa190d563))
* Update lambda functions to handle non-integer values when HA returns None or unknown ([39043a2](https://github.com/mguyard/appdaemon-coversmanager/commit/39043a2510b822f83a7c91f6d134cb1505741e9c))
* Update log message for state change callback to better understand which callback is trigger ([2e3246f](https://github.com/mguyard/appdaemon-coversmanager/commit/2e3246fcca29771f71b9e0ab183ee2d08f9b4369))


### Features

* Manage locker (global and close) for adaptive mode. ([5a45554](https://github.com/mguyard/appdaemon-coversmanager/commit/5a45554b2114b26a5223ed449c8c9565091c54e1))

# [1.4.0-beta.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.2-beta.5...v1.4.0-beta.1) (2024-08-11)


### Features

* Manage locker (global and close) for adaptive mode. ([5a45554](https://github.com/mguyard/appdaemon-coversmanager/commit/5a45554b2114b26a5223ed449c8c9565091c54e1))

## [1.3.2-beta.5](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.2-beta.4...v1.3.2-beta.5) (2024-06-12)


### Bug Fixes

* Update lambda functions to handle non-integer values when HA returns None or unknown ([39043a2](https://github.com/mguyard/appdaemon-coversmanager/commit/39043a2510b822f83a7c91f6d134cb1505741e9c))

## [1.3.2-beta.4](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.2-beta.3...v1.3.2-beta.4) (2024-06-12)


### Bug Fixes

* Update lambda functions to handle non-integer values when HA return None (following start for example) ([181b4b4](https://github.com/mguyard/appdaemon-coversmanager/commit/181b4b40553f6de2cf2e0efb4c5faf5b839ed2f7))

## [1.3.2-beta.3](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.2-beta.2...v1.3.2-beta.3) (2024-06-12)


### Bug Fixes

* Update lambda functions to handle non-integer values when HA return unknown (following start for example) ([c59eefc](https://github.com/mguyard/appdaemon-coversmanager/commit/c59eefc14c90506001ddc40d523b191aa190d563))

## [1.3.2-beta.2](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.2-beta.1...v1.3.2-beta.2) (2024-06-09)


### Bug Fixes

* Resolve critical issue in a log who block application loading ([820adf3](https://github.com/mguyard/appdaemon-coversmanager/commit/820adf377d602e7b33d4a6ee19ad37bb0c088b8c))

## [1.3.2-beta.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.1...v1.3.2-beta.1) (2024-06-09)


### Bug Fixes

* Resolve issue with adaptive mode conditional for outdoor sensor ([9a462ff](https://github.com/mguyard/appdaemon-coversmanager/commit/9a462ff973eca04733198a6d5a2ccad02e07a126))
* Update log message for state change callback to better understand which callback is trigger ([2e3246f](https://github.com/mguyard/appdaemon-coversmanager/commit/2e3246fcca29771f71b9e0ab183ee2d08f9b4369))

## [1.3.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.0...v1.3.1) (2024-06-05)


### Bug Fixes

* Change module name to avoid collision with my others apps ([f29bc83](https://github.com/mguyard/appdaemon-coversmanager/commit/f29bc8399b3be08870542926a9ab3c19a28154cb))
* Rename ConfigValidator to avoid collision with my others apps ([eaf0889](https://github.com/mguyard/appdaemon-coversmanager/commit/eaf08893f22a28a7485b6dd5a8440075ddbea4d6))
* Rename ConfigValidator to avoid collision with my others apps ([460cd0f](https://github.com/mguyard/appdaemon-coversmanager/commit/460cd0f099e9a7e0c42c4b255b8cbdc544304319))

## [1.3.1-beta.3](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.1-beta.2...v1.3.1-beta.3) (2024-06-05)


### Bug Fixes

* Change module name to avoid collision with my others apps ([f29bc83](https://github.com/mguyard/appdaemon-coversmanager/commit/f29bc8399b3be08870542926a9ab3c19a28154cb))

## [1.3.1-beta.2](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.1-beta.1...v1.3.1-beta.2) (2024-06-05)


### Bug Fixes

* Rename ConfigValidator to avoid collision with my others apps ([eaf0889](https://github.com/mguyard/appdaemon-coversmanager/commit/eaf08893f22a28a7485b6dd5a8440075ddbea4d6))

## [1.3.1-beta.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.3.0...v1.3.1-beta.1) (2024-06-05)


### Bug Fixes

* Rename ConfigValidator to avoid collision with my others apps ([460cd0f](https://github.com/mguyard/appdaemon-coversmanager/commit/460cd0f099e9a7e0c42c4b255b8cbdc544304319))

# [1.3.0](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.2.0...v1.3.0) (2024-05-26)


### Bug Fixes

* Issue with unpacking during manual lock info_timer (when lock exist in entity but not the task, like following a app reload ([9a6a0fb](https://github.com/mguyard/appdaemon-coversmanager/commit/9a6a0fbb3c02895522b1847a13f6cab86d5f9cbe))


### Features

* Add config.temperature.outdoor.low_temperature as parameter ([47e784c](https://github.com/mguyard/appdaemon-coversmanager/commit/47e784ce618c160220063a1203fb18e672109d46))

# [1.3.0-beta.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.2.0...v1.3.0-beta.1) (2024-05-26)


### Bug Fixes

* Issue with unpacking during manual lock info_timer (when lock exist in entity but not the task, like following a app reload ([9a6a0fb](https://github.com/mguyard/appdaemon-coversmanager/commit/9a6a0fbb3c02895522b1847a13f6cab86d5f9cbe))


### Features

* Add config.temperature.outdoor.low_temperature as parameter ([47e784c](https://github.com/mguyard/appdaemon-coversmanager/commit/47e784ce618c160220063a1203fb18e672109d46))

# [1.2.0-beta.3](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.2.0-beta.2...v1.2.0-beta.3) (2024-05-26)


### Bug Fixes

* Issue with unpacking during manual lock info_timer (when lock exist in entity but not the task, like following a app reload ([9a6a0fb](https://github.com/mguyard/appdaemon-coversmanager/commit/9a6a0fbb3c02895522b1847a13f6cab86d5f9cbe))


### Features

* Add config.temperature.outdoor.low_temperature as parameter ([47e784c](https://github.com/mguyard/appdaemon-coversmanager/commit/47e784ce618c160220063a1203fb18e672109d46))

# [1.2.0](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.1.0...v1.2.0) (2024-05-24)


### Bug Fixes

* Issue [#27](https://github.com/mguyard/appdaemon-coversmanager/issues/27) with azimuth < 0 who still move adaptive ([9196d2d](https://github.com/mguyard/appdaemon-coversmanager/commit/9196d2d7edfaf3ceaf126ba9e9a04e31fb6454d3))


### Features

* Switch from secure_sunset to secure_dusk [#25](https://github.com/mguyard/appdaemon-coversmanager/issues/25) ([3a28bbb](https://github.com/mguyard/appdaemon-coversmanager/commit/3a28bbb6a409a7aca31247d6b22f75228684b579))

# [1.2.0-beta.2](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.2.0-beta.1...v1.2.0-beta.2) (2024-05-24)


### Bug Fixes

* Issue [#27](https://github.com/mguyard/appdaemon-coversmanager/issues/27) with azimuth < 0 who still move adaptive ([9196d2d](https://github.com/mguyard/appdaemon-coversmanager/commit/9196d2d7edfaf3ceaf126ba9e9a04e31fb6454d3))

# [1.2.0-beta.1](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.1.0...v1.2.0-beta.1) (2024-05-19)


### Features

* Switch from secure_sunset to secure_dusk [#25](https://github.com/mguyard/appdaemon-coversmanager/issues/25) ([3a28bbb](https://github.com/mguyard/appdaemon-coversmanager/commit/3a28bbb6a409a7aca31247d6b22f75228684b579))

# [1.1.0](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.0.0...v1.1.0) (2024-05-19)


### Features

* Open covers if outdoor temperature is less than indoor temperature ([7c6f9ba](https://github.com/mguyard/appdaemon-coversmanager/commit/7c6f9ba1667509f60bf8a256869d718dd3b12b68))

# [1.0.0-beta.6](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.0.0-beta.5...v1.0.0-beta.6) (2024-05-19)


### Features

* Open covers if outdoor temperature is less than indoor temperature ([7c6f9ba](https://github.com/mguyard/appdaemon-coversmanager/commit/7c6f9ba1667509f60bf8a256869d718dd3b12b68))

# 1.0.0 (2024-05-19)


### Bug Fixes

* Add adaptive position check for cover move detection + change in timer of move verification ([c17e03e](https://github.com/mguyard/appdaemon-coversmanager/commit/c17e03e22460cea8c8ac322b0b365abe35fd8fd5))
* Add debug log for manual cover move detection ([a723cad](https://github.com/mguyard/appdaemon-coversmanager/commit/a723cad7860ba93cf9d48cd0e68cb70481b68ee0))
* better implementation of locker verification ([f831094](https://github.com/mguyard/appdaemon-coversmanager/commit/f83109477b095905e03716cfe6a866f28c07845d))
* Fix log issue with bad content ([4155d1a](https://github.com/mguyard/appdaemon-coversmanager/commit/4155d1a492593b4320e4afed71a2bb71223d103f))
* Improved cover lock management and entity verification ([c6954e0](https://github.com/mguyard/appdaemon-coversmanager/commit/c6954e04bd0fe9e6d13367555f770ba9748e6032))
* Minor change in logs ([c188da6](https://github.com/mguyard/appdaemon-coversmanager/commit/c188da627af07f01e64b868a5d9b0b61bd7b0ea5))
* Raise exception in case of invalid configuration ([589ab7d](https://github.com/mguyard/appdaemon-coversmanager/commit/589ab7de49f0fb295da63a742905d61a517954c2))


### Features

* Add locker binary sensor in global, opening and closing configuration ([b8fd489](https://github.com/mguyard/appdaemon-coversmanager/commit/b8fd48973f04877eac68c7342630cce8c399c572))
* Initial beta version ([113b335](https://github.com/mguyard/appdaemon-coversmanager/commit/113b335a504ce02ebbdcb6182cc0d5b89482b938))

# [1.0.0-beta.5](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.0.0-beta.4...v1.0.0-beta.5) (2024-05-19)


### Bug Fixes

* Improved cover lock management and entity verification ([c6954e0](https://github.com/mguyard/appdaemon-coversmanager/commit/c6954e04bd0fe9e6d13367555f770ba9748e6032))

# [1.0.0-beta.4](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.0.0-beta.3...v1.0.0-beta.4) (2024-05-12)


### Bug Fixes

* Add adaptive position check for cover move detection + change in timer of move verification ([c17e03e](https://github.com/mguyard/appdaemon-coversmanager/commit/c17e03e22460cea8c8ac322b0b365abe35fd8fd5))
* better implementation of locker verification ([f831094](https://github.com/mguyard/appdaemon-coversmanager/commit/f83109477b095905e03716cfe6a866f28c07845d))
* Raise exception in case of invalid configuration ([589ab7d](https://github.com/mguyard/appdaemon-coversmanager/commit/589ab7de49f0fb295da63a742905d61a517954c2))

# [1.0.0-beta.3](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.0.0-beta.2...v1.0.0-beta.3) (2024-05-12)


### Bug Fixes

* Add debug log for manual cover move detection ([a723cad](https://github.com/mguyard/appdaemon-coversmanager/commit/a723cad7860ba93cf9d48cd0e68cb70481b68ee0))


### Features

* Add locker binary sensor in global, opening and closing configuration ([b8fd489](https://github.com/mguyard/appdaemon-coversmanager/commit/b8fd48973f04877eac68c7342630cce8c399c572))

# [1.0.0-beta.2](https://github.com/mguyard/appdaemon-coversmanager/compare/v1.0.0-beta.1...v1.0.0-beta.2) (2024-05-11)


### Bug Fixes

* Fix log issue with bad content ([4155d1a](https://github.com/mguyard/appdaemon-coversmanager/commit/4155d1a492593b4320e4afed71a2bb71223d103f))
* Minor change in logs ([c188da6](https://github.com/mguyard/appdaemon-coversmanager/commit/c188da627af07f01e64b868a5d9b0b61bd7b0ea5))

# 1.0.0-beta.1 (2024-05-09)


### Features

* Initial beta version ([113b335](https://github.com/mguyard/appdaemon-covermanager/commit/113b335a504ce02ebbdcb6182cc0d5b89482b938))
