# Release audit (credentials, privacy, licensing)

## Credentials and personal data

| Finding | Location (original) | Action |
|---|---|---|
| Hard-coded MySQL URI with username and password | `drone_website/Server3.0/server_apps/main_app.py:23` (also Server2.0, `flask/base_app.py`) | Replaced by `DRONE_DB_URI` environment variable; Server2.0 and `flask/` excluded. **Rotate the password if it was ever reused.** |
| Absolute home path `/home/<user>/drone_ws/...` | `iq_sim/Maps/my_map.yaml` | Replaced by a relative path |
| Developer name in commit metadata | Local git history | Use a deliberately chosen author identity for the public repo |
| Google Fonts `@import` in CSS | `ground_station/static/css` | Public URLs; no key. Kept |
| API keys / tokens | Searched Python, HTML, JS, shell, yaml for key/token/secret/password patterns | None found outside the item above |
| Email addresses / phone numbers | Same search | None found |

## Excluded content

`build/ devel/ logs/ .catkin_tools/`, `another_send_test.py` (syntactically truncated), `a.out`, `get-pip.py`, `eeprom.bin`, `mav.tlog*`, `mav.parm`, `terrain/`, the `droneweb` virtualenv, `__pycache__`, `darknet_ros` and its 485 MB of weights, `web_video_server`, `async_web_server_cpp`, the AWS warehouse zip and package, `iq_gnc`, `drone_listener` (PPO skeleton), `extract_msg`, `offb`, Server2.0/`old_websites`/`gazebo_models`, other worlds and the 12 duplicate drone models, UI screenshots/icons, Leaflet, 16 MB PGM maps.

## Licensing

Own code: MIT. Derived iq_sim files keep the upstream MIT notice. No third-party source is bundled except these derivations. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). gmapping is BSD per current upstream metadata (older releases were CC-BY-NC-SA); see THIRD_PARTY_NOTICES.md note 1. The Gazebo Classic ArduPilot plugin is GPL-3.0 and is not redistributed.

## Required modifications (the only ones)

1. `main_app.py`: DB URI → environment variable (+ `import os`).
2. `my_map.yaml`: image path made relative.

All other source files are byte-for-byte copies of the archived originals.
