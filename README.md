<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/5968/5968914.png" width="100" />
</p>
<p align="center">
    <h1 align="center">AppDaemon - Covers Manager</h1>
</p>
<p align="center">
    <em><code>All you need to manage your covers !</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/mguyard/appdaemon-coversmanager?style=default&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/mguyard/appdaemon-coversmanager?style=default&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/mguyard/appdaemon-coversmanager?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/mguyard/appdaemon-coversmanager?style=default&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
    <img src="https://img.shields.io/github/v/release/mguyard/appdaemon-coversmanager" alt="Last Release">
    <img src="https://img.shields.io/github/release-date/mguyard/appdaemon-coversmanager" alt="Last Release Date">
    <a href="https://github.com/mguyard/appdaemon-coversmanager/actions/workflows/lint.yaml" target="_blank">
        <img src="https://github.com/mguyard/appdaemon-coversmanager/actions/workflows/lint.yaml/badge.svg" alt="Python Lint Action">
    </a>
    <a href="https://github.com/mguyard/appdaemon-coversmanager/actions/workflows/hacs_validate.yaml" target="_blank">
        <img src="https://github.com/mguyard/appdaemon-coversmanager/actions/workflows/hacs_validate.yaml/badge.svg" alt="Container Build Action">
    </a>
<p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<hr>

## 🔗 Quick Links

> - [📍 Overview](#-overview)
> - [📦 Features](#-features)
> - [🚀 Getting Started](#-getting-started)
>   - [🔝 Requirements](#️-requirements)
>   - [⚙️ Installation](#️-installation)
> - [🏷️ Configuration](#-configuration)
>   - [🤖 AppDaemon](#-appdaemon)
>   - [🪟 Covers Manager](#-covers-manager)
>   - [🧩 Parameters](#-parameters)
>   - [📄 Full Configuration Example](#-full-configuration-example)
> - [🪲 Debug](#-debug)
> - [🤝 Contributing](#-contributing)

---

## 📍 Overview

### Objective

The objective of the Covers Manager project is to provide a comprehensive solution for managing covers. The project aims to simplify and streamline the process of managing covers by automating various tasks and providing an efficient tool for users.
The Covers Manager project is designed to address the specific needs of managing covers, such as those used in home automation systems or other applications. It offers a range of features and functionalities to facilitate the management of covers, including opening, closing or manage covers position depending of sun position and temperature (indoor and outdoor).
Overall, the objective of the Covers Manager project is to simplify and optimize the management of covers, providing users with a powerful and efficient tool for controlling their covers.

> [!NOTE]
>
> It's important to note that the Covers Manager project is under development.
> Project is open-source, and users are encouraged to adapt it to their own needs if necessary and purpose all evolutions by submitting a PR.


### Motivation

This AppDaemon application was born out of the need to manage roller shutters as I did on Jeedom before migrating to Home Assistant.
The aim was simple: recover the automatic opening and closing functions, as well as the ability to close the shutters proportionally according to the position of the sun.

### Inspiration

I was greatly inspired by the Volets plugin on Jeedom by mika-nt28 as well as the work of BasBrus and Langestefan (https://community.home-assistant.io/t/custom-component-adaptive-cover/712626).

## 📦 Features

CoversManager is developped to help you with these features :
- Opening covers (based on time, lux, sunrise hour)
- Closing covers (based on time, lux, sunset hour)
- Adaptive covers management based on sun position, indoor and outdoor temperature (optional)
- Block adaptive changes when manual position change is detected

## 🚀 Getting Started

### 🔝 Requirements

- A valid and functional deployment of [`AppDaemon Addon` connected to Home Assistant](https://community.home-assistant.io/t/home-assistant-community-add-on-appdaemon-4/163259)
- A valid and functional [`HACS` (Home Assistant Community Store) integration](https://hacs.xyz/docs/setup/download)

### ⚙️ Installation

- [Enable AppDaemon Apps in HACS](https://hacs.xyz/docs/categories/appdaemon_apps/)
- [Add Automation repository](https://my.home-assistant.io/redirect/hacs_repository/?owner=mguyard&repository=appdaemon-coversmanager&category=appdaemon) in HACS as AppDaemon repo : https://github.com/mguyard/appdaemon-coversmanager
- Install Covers Manager in HACS
- [Install `Studio Code Server` addon](https://my.home-assistant.io/redirect/supervisor_store/) to edit your AppDaemon & CoversManager configuration (optional if your prefer another method to modify your configuration)

## 🏷️ Configuration

### 🤖 AppDaemon

Firstly you need to configure your newly AppDaemon installation.

> [!NOTE]
> 
> Please continue to next chapter if AppDaemon was already configured before this App

[AppDaemon Main configuration](https://appdaemon.readthedocs.io/en/latest/CONFIGURE.html#appdaemon) is available in file `appdaemon.yaml` most of the time stored in `/add_config/<guid>_appdaemon/`

Please find below an example of basic configuration :

```yaml
---
secrets: /homeassistant/secrets.yaml
appdaemon:
  latitude: 48.80506979319244
  longitude: 2.12031248278925
  elevation: 130
  time_zone: Europe/Paris
  plugins:
    HASS:
      type: hass
http:
  url: http://127.0.0.1:5050
admin:
api:
hadashboard:

logs:
  main_log:
    filename: /config/logs/appdaemon.log
  error_log:
    filename: /config/logs/error.log
```

Add in logs part the log for Covers Manager :

```yaml
logs:
    [...]
    CoversManager:
        name: CoversManager
        filename: /conf/logs/CoversManager.log
```

### 🪟 Covers Manager

To configure Covers Manager app you need to edit `apps.yaml` configuration most of the time stored in `/add_config/<guid>_appdaemon/apps/`

Please find below an simple example of configuration to add in file :

```yaml
CoversManager:
    module: covers_manager
    class: CoversManager
    use_dictionary_unpacking: true
    log: CoversManager
    config:
        common:
            opening:
                type: "lux"
            closing:
                type: "lux"
                adaptive: True
            temperature:
                indoor:
                    sensor: "sensor.indoor_temperature"
                    setpoint: 23
                outdoor:
                    sensor: "sensor.outdoor_temperature"
                    high_temperature: 40
            lux:
                sensor: "sensor.outdoor_sensor_illuminance_lux"
                open_lux: 23
                close_lux: 5
        covers:
            cover.roller_shutter_1:
                window_heigh : 210 
                window_azimuth: 180
            cover.roller_shutter_2:
                window_heigh : 210
                window_azimuth: 320
```

You have more configuration available. All is detailled in next chapter [🧩 Parameters](#-parameters)

### 🧩 Parameters

Please find below all configuration parameters who don't apply to covers directly

| Parent              | Parameters       | Description                                                                                                                         | Configuration Path                                 | Default | Type                 | Status   |
|---------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|---------|----------------------|----------|
| -                   | dryrun           | Enable a dryrun mode that don't execute open or close functions                                                                     | config.dryrun                                      | False   | Boolean              | Optional |
| -                   | locker           | A binary sensor who block opening for open and close when state is On                                                               | config.locker                                      | None    | Binary Sensor Entity | Optional |
| position            | opened           | Define the max position allowed (%) when cover is open                                                                              | config.common.position.opened                      | 100     | Integer              | Optional |
| position            | closed           | Define the min position allowed (%) when cover is closed                                                                            | config.common.position.opened                      | 0       | Integer              | Optional |
| position            | min_ratio_change | Define minimum percent of move to allow action                                                                                      | config.common.position.min_ratio_change            | 5       | Integer              | Optional |
| position            | min_time_change  | Define minimum time in minutes allowed between move                                                                                 | config.common.position.min_time_change             | 10      | Integer              | Optional |
| opening             | type             | Define method to open covers the morning (Allowed value : off|time|sunrise|lux|prefer-lux)                                          | config.common.opening.type                         | off     | String               | Optional |
| opening             | time             | Time to open covers - Only work with time or prefer-lux type                                                                        | config.common.opening.time                         | None    | Time                 | Optional |
| opening             | locker           | A binary sensor who block opening when state is On                                                                                  | config.common.opening.locker                       | None    | Binary Sensor Entity | Optional |
| closing             | type             | Define method to open covers the morning (Allowed value : off|time|sunrise|lux|prefer-lux)                                          | config.common.closing.type                         | off     | String               | Optional |
| closing             | time             | Time to open covers - Only work with time or prefer-lux type                                                                        | config.common.closing.time                         | None    | Time                 | Optional |
| closing             | locker           | A binary sensor who block opening when state is On                                                                                  | config.common.closing.locker                       | None    | Binary Sensor Entity | Optional |
| closing             | secure_sunset    | Close at sunset in 2 layer if first closing method failed - Only work with time or prefer-lux type                                  | config.common.closing.secure_sunset                | False   | Boolean              | Optional |
| closing             | adaptive         | Enable adaptive mode who close/open covers based on Sun position and indoor/outdoor temperature                                     | config.common.closing.adaptive                     | False   | Boolean              | Optional |
| manual              | allow            | Enable or Disable detection of manual position change of covers                                                                     | config.common.manual.allow                         | False   | Boolean              | Optional |
| manual              | timer            | Time to block movements when manual position change is detected. Required if config.common.manual.allow is True                     | config.common.manual.timer                         | None    | TimeDelta            | Optional |
| temperature.indoor  | sensor           | Sensor who provide indoor temperature (Positive Integer - No Float)                                                                 | config.common.temperature.indoor.sensor            | None    | Sensor Entity        | Optional |
| temperature.indoor  | setpoint         | Indoor temperature setpoint. Below => We need to heat with sun / Above => We need to block sun                                      | config.common.temperature.indoor.setpoint          | None    | PositiveInt          | Optional |
| temperature.outdoor | sensor           | Sensor who provide outdoor temperature (Positive Integer - No Float)                                                                | config.common.temperature.outdoor.sensor           | None    | Sensor Entity        | Optional |
| temperature.outdoor | high_temperature | Outdoor temperature to trigger when we need to totally close cover to protect from heat. Required when Outdoor sensor is configured | config.common.temperature.outdoor.high_temperature | None    | PositiveInt          | Optional |
| lux                 | sensor           | Sensor who provide outside Lux                                                                                                      | config.common.lux.sensor                           | None    | Sensor Entity        | Optional |
| lux                 | open_lux         | Trigger in lux to open covers. Required if type of opening is lux or prefer-lux                                                     | config.common.lux.open_lux                         | None    | PositiveInt          | Optional |
| lux                 | close_lux        | Trigger in lux to close covers. Required if type of closing is lux or prefer-lux                                                    | config.common.lux.close_lux                        | None    | PositiveInt          | Optional |

Parameters for covers are :

| Parent                                  | Parameters     | Description                                                                              | Configuration Path                             | Default | Type              | Status   |
|-----------------------------------------|----------------|------------------------------------------------------------------------------------------|------------------------------------------------|---------|-------------------|----------|
| config.covers.<cover-entity>            | window_heigh   | Window Heigh in centimeters                                                              | config.covers.<cover-entity>.window_heigh      |         | PositiveInt       | Required |
| config.covers.<cover-entity>            | window_azimuth | Window Azimuth in the middle of window                                                   | config.covers.<cover-entity>.window_azimuth    |         | Int between 0-360 | Required |
| config.covers.<cover-entity>.positional | action         | True if cover is positional                                                              | config.covers.<cover-entity>.positional.action | True    | Boolean           | Optional |
| config.covers.<cover-entity>.positional | status         | True if cover provide is position                                                        | config.covers.<cover-entity>.positional.status | True    | Boolean           | Optional |
| config.covers.<cover-entity>.fov        | left           | What is the left FOV angle between window_azimuth and the sun azimuth entering in window | config.covers.<cover-entity>.fov.left          | 90      | Int between 0-180 | Optional |
| config.covers.<cover-entity>.fov        | right          | What is the right FOV angle between window_azimuth and the sun azimuth leaving in window | config.covers.<cover-entity>.fov.right         | 90      | Int between 0-180 | Optional |


> [!TIP]
>
> You can declare multiple covers in the same configuration.
> If you need a specific global configuration for one or more covers, you can also create a new application configuration for these covers.

### 📄 Full Configuration Example

```yaml
CoversManager:
    module: covers_manager
    class: CoversManager
    use_dictionary_unpacking: true
    log: CoversManager
    config:
        common:
            locker: "binary_sensor.alarm_status"
            position:
                opened: 100
                closed: 0
                min_ratio_change: 5
                min_time_change: 10
            opening:
                type: "prefer-lux"
                time: "10:00:00"
                locker: "binary_sensor.locker_opening" # If at least one of opening and global locker are True, lock is True
            closing:
                type: "off"
                time: "23:00:00"
                secure_sunset: False
                adaptive: True
                locker: "binary_sensor.locker_closing" # If at least one of closing and global locker are True, lock is True
            manual:
                allow: true
                timer: 01:00:00
            temperature:
                indoor:
                    sensor: "sensor.indoor_temperature"
                    setpoint: 23
                outdoor:
                    sensor: "sensor.outdoor_sensor_temperature"
                    high_temperature: 40
            lux:
                sensor: "sensor.outdoor_sensor_illuminance_lux"
                open_lux: 23
                close_lux: 5
        covers:
            cover.roller_1:
                window_heigh : 210
                window_azimuth: 180
                positional:
                    action : True
                    status: True
                fov:
                    left: 60
                    right: 70
            cover.roller_shutter_2:
                window_heigh : 210
                window_azimuth: 320
                positional:
                    action : True
                    status: True
                fov:
                    left: 90
                    right: 90
```

## 🪲 Debug

To help to debug and understand an issue, you can enable the debug mode in app.
For this, edit the app configuration and set `log_level` to DEBUG

```yaml
CoversManager:
    [...]
    log: CoversManager
    log_level: DEBUG    <---- HERE
    config:
        [...]
```

If you need some assistance, you can open a topic in [Discussions](https://github.com/mguyard/appdaemon-coversmanager/discussions) or by [opening an Issue](https://github.com/mguyard/appdaemon-coversmanager/issues/new?assignees=&labels=Bug&projects=&template=bug_report.yml)

## 🤝 Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/mguyard/appdaemon-coversmanager/pulls)**: Review open PRs, and submit your own PRs.
- **[Report Issues](https://github.com/mguyard/appdaemon-coversmanager/issues/new?assignees=&labels=Bug&projects=&template=bug_report.yml)**: Submit bugs found or log feature requests.

<details closed>
    <summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone https://github.com/mguyard/appdaemon-coversmanager
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the dev branch.

> [!IMPORTANT]
>
> Only PR to `dev` branch will be accepted.

</details>