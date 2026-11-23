# Reproducibility guide

**Status: not re-run since archiving.** The steps below reconstruct the original environment from preserved files; they are untested. Do not treat a successful build as proof that the 2024 demonstration will be reproduced (see [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)).

## Environment (as evidenced)

| Item | Evidence |
|---|---|
| Ubuntu 20.04, ROS Noetic, Python 3.8 | `/opt/ros/noetic` in the workspace's toplevel link; Python 3.8 venv |
| Gazebo 11 (Noetic default) | Inferred from ROS distribution |
| ArduCopter SITL `V4.5.0-dev` (`d1ad9ccf`) | Recorded in the 2023 `mav.tlog` |
| `ardupilot_gazebo` Gazebo Classic plugin (likely `khancyr/ardupilot_gazebo`, per the Intelligent-Quads tutorial); exact commit unrecorded | `libArduPilotPlugin.so` in the models/worlds |
| catkin_tools | `.catkin_tools/` in the workspace |

## Prerequisites

Install per the Intelligent-Quads tutorials: ArduPilot + MAVProxy, `ardupilot_gazebo`, ROS Noetic desktop-full, `ros-noetic-mavros`, `ros-noetic-mavros-extras`, `ros-noetic-gmapping`, `ros-noetic-navigation`, `ros-noetic-map-server`, `pymavlink`, and `utm` (used only by commented-out code). Install the AWS small-warehouse world models (`aws_robomaker_warehouse_GroundB_01`) and the stock Gazebo `grey_wall` and `hokuyo` models.

## Build

See the Quick start in the [README](../README.md). The overlay is copied onto upstream `iq_sim` pinned to commit `13e72512cd9748b12a4aa1cac15a2e34b1cdcfd6`. Mesh files (`iris_base`) come from upstream.

## Ground station (optional)

```bash
python3 -m venv venv && . venv/bin/activate && pip install -r ground_station/requirements.txt
export DRONE_DB_URI='mysql://<user>:<password>@localhost:3306/drone_home_position'   # create the database and table first
cd ground_station/server_apps && python3 main_app.py   # needs a ROS master, SITL on UDP 14550
```
Add Leaflet and Leaflet.draw under `ground_station/static/leaflet/` and `static/Leaflet.draw-develop/` (omitted from this repo). UI icons are also omitted.

## Known gaps

- Launch order is encoded in `scripts/start_gmapping_project.sh` (Gazebo, SITL, gmapping, tf_broadcaster, rviz_nav_goal_publisher, RViz). That launcher does **not** start `move_base` or `navigation_test.py`; those appear to have been started separately.
- Original maps are not included as PGM; the PNGs in `docs/evidence/` are visualizations only. To get loadable maps, run SLAM and save with `map_saver`.
- The MAVROS odometry/TF configuration (the final-demo odometry source, per the author) was not preserved; see ARCHITECTURE.md. With stock MAVROS parameters no `odom -> base_link` TF is published. `tf_broadcaster.py` is the preserved ground-truth alternative.
- Exact package versions were not recorded.
- Gazebo/SITL timing and the coordinate-conversion issue may prevent the click-to-fly behaviour from reproducing as demonstrated.
