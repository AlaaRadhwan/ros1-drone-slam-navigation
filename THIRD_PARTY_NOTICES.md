# Third-party notices

This project builds on the following upstream work. None of it was created by this project's author, and licenses should be re-verified at publication time against each upstream repository.

| Component | Role | Included here? | License (per upstream; verify) |
|---|---|---|---|
| Intelligent-Quads `iq_sim` (commit `13e72512cd9748b12a4aa1cac15a2e34b1cdcfd6`) | Base package: worlds, drone models, ArduPilot plugin wiring, launch files. The world and drone model in `overlay/` are derived from it | Derived files only; notice in `overlay/iq_sim/LICENSE.iq_sim-upstream-MIT` | MIT (© 2020 Intelligent-Quads) |
| Intelligent-Quads tutorials / `iq_gnc` | Setup tutorials the environment followed | No | MIT |
| ROS Noetic, `move_base`, `navfn`, `base_local_planner`, `costmap_2d`, `tf`, `map_server` | Navigation stack | No (apt) | BSD-3 |
| ROS `gmapping`, `slam_gmapping`, `openslam_gmapping` | 2D SLAM | No (apt) | BSD per current upstream metadata (see note 1) |
| ArduPilot (ArduCopter SITL), MAVProxy | Flight controller | No | GPLv3 |
| `ardupilot_gazebo` (Gazebo Classic plugin, `libArduPilotPlugin.so`) | Gazebo ↔ ArduPilot link | No | GPL-3.0 (see note 2) |
| MAVROS | MAVLink ↔ ROS | No (apt) | GPLv3 / LGPLv3 / BSD |
| pymavlink | MAVLink in Python | No (pip) | LGPLv3 |
| Gazebo 11 / `grey_wall`, `hokuyo` models | Simulator and stock models | No | Apache-2.0 (Gazebo); model licenses per OSRF model database |
| AWS RoboMaker small warehouse world (`aws_robomaker_warehouse_GroundB_01`) | Floor model referenced by `walls.world` | No (install separately) | MIT-0-style license (© Amazon.com) |
| Flask, Flask-SocketIO, Flask-SQLAlchemy | Ground station | No (pip) | BSD / MIT |
| Leaflet, Leaflet.draw | Ground station map | No (omitted) | BSD-2 / MIT |

**Notes**

1. *gmapping licensing.* ros-perception upstream (`melodic-devel`, checked Nov 2026): `openslam_gmapping` 0.2.1 declares `BSD` (changelog 0.2.0, 2019-07-07: "update license to BSD-3"; earlier 0.1.x releases were CC-BY-NC-SA); `slam_gmapping`/`gmapping` 1.4.2 declare `BSD` and, as a second tag, `Apache 2.0` (changelog 1.4.0, 2019-07-12: "update license to BSD"). The upstream repository has no LICENSE file and no `noetic` branch, so the license metadata of the historically installed Noetic apt package was not verified here; check its `package.xml` when installing. Older package-index pages still show CC-BY-NC-SA for legacy distros.
2. *ArduPilot Gazebo plugin.* The Intelligent-Quads tutorial (`docs/installing_gazebo_arduplugin.md`) tells users to clone **`khancyr/ardupilot_gazebo`** and install Gazebo 11 (Ubuntu 20.04) or Gazebo 9 (18.04), i.e. the Gazebo **Classic** plugin. That repository is GPL-3.0, was archived on 5 Aug 2024 and is marked deprecated. Its successor, `ArduPilot/ardupilot_gazebo` (LGPL-3.0), targets **Gazebo Sim** (Garden/Harmonic/...) and is *not* the plugin used here. The exact branch/commit built in 2024 was not recorded in the backup and is **unverified**; the plugin is not redistributed here.

Excluded because they are third-party or unrelated to the demonstrated pipeline: `darknet_ros` + YOLO weights, `web_video_server`, `async_web_server_cpp`, the AWS warehouse zip, `iq_gnc`, `get-pip.py`.

The author's contributions are described in the README and licensed under [LICENSE](LICENSE). That MIT license covers only the author's original contributions. Files under `overlay/iq_sim/` that derive from Intelligent-Quads `iq_sim` (the world and drone model) remain subject to the upstream MIT notice in `overlay/iq_sim/LICENSE.iq_sim-upstream-MIT`. Third-party components keep their own licenses. AI assistance (ChatGPT) was used during development.
