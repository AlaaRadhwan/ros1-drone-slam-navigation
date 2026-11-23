# Known limitations and unresolved archival questions

## 1. Coordinate conversion in the path-to-MAVLink bridge (unresolved)

`overlay/iq_sim/scripts/navigation_test.py` (`convert_to_mavlink_waypoints`) reads the x/y of each pose in `/move_base/NavfnROS/plan` and writes them into `MISSION_ITEM_INT` as `x = int(x * 1e7)`, `y = int(y * 1e7)` in `MAV_FRAME_GLOBAL_RELATIVE_ALT_INT`. That frame expects **latitude/longitude in degrees × 1e7**, whereas the plan is in the `map` frame in **metres**. The metre→geographic conversion (a UTM-based variant) is present only as commented-out code. `rviz_nav_goal_publisher.py` has the same pattern (map x/y written to `GlobalPositionTarget.latitude/longitude`). The altitude is taken from the drone's current `GLOBAL_POSITION_INT`.

Read literally, a 5 m goal would become 5° of latitude. **The author nevertheless personally observed the drone flying to the RViz goals in Gazebo** (2024). The archive does not explain this.

What can and cannot be said:

| Statement | Basis |
|---|---|
| The code path RViz goal → NavFn plan → MAVLink mission → GUIDED/ARM/AUTO exists | Preserved source |
| The drone flew to RViz-selected goals in Gazebo | Author-confirmed; public video |
| The archived `navigation_test.py` alone explains that behaviour | **Not established** |

Possible explanations (hypotheses only, none verified):
- The demonstrated run used a later, un-archived revision of the bridge or a different bridge.
- A different component (for example `rviz_nav_goal_publisher.py` through MAVROS, or manual steps) produced the final behaviour.
- The behaviour in the video was achieved with parameters or frames not preserved in the backup.

**This repository does not alter the historical algorithm.** The archived scripts are included unmodified. `tools/local_to_global_reference.py` is a separate, clearly non-historical reference showing what a correct local-metres → latitude/longitude conversion would look like. It is not wired into any launch file and must not be described as the code that was demonstrated.

## 2. Odometry source during the demonstration

Three things must be kept distinct (details in [ARCHITECTURE.md](ARCHITECTURE.md#tf-and-odometry-what-the-evidence-shows)):

1. **Final demonstration (author recollection):** odometry came from MAVROS/ArduPilot, not directly from Gazebo.
2. **`docs/evidence/frames.gv`** (29 Jul 2024, later snapshot): `/mavros` publishes `odom -> base_link`; the Hokuyo frames come from static publishers named as in `gmapping.launch`. Consistent with the recollection.
3. **`docs/evidence/frames.png`** (26 Jul 2024, earlier snapshot): `/tf_broadcaster` publishes `odom -> base_link` and the Hokuyo frames, i.e. the Gazebo ground-truth broadcaster, apparently an earlier or alternative test configuration. The preserved `scripts/tf_broadcaster.py` implements that alternative (a later revision, dated 27 Jul).

Remaining uncertainty:
- Neither snapshot is a recording of the final navigation video, so which configuration that run used is established only by the author's recollection.
- **How MAVROS odometry became the TF `odom -> base_link` is not recoverable.** `apm.launch` loads the system-installed `apm_config.yaml`; upstream defaults do not broadcast TF from `local_position` (and would use `map -> base_link`), so the run must have used non-default MAVROS parameters or a different plugin that were not preserved. No custom MAVROS configuration exists in the backup.
- `scripts/start_gmapping_project.sh` starts both `gmapping.launch` and `tf_broadcaster.py` and does not start MAVROS; the final-demo process set is unknown.
- The LinkedIn post mentions "odometry challenges" without detail; the Medium articles could not be fetched during this audit.

## 3. Costmap sensor frame

`config/costmap_common_params.yaml` sets `sensor_frame: laser_frame`, but the TF tree uses `hokuyo_sensor_link`. Whether the observation source worked as written, or was overridden at launch time, is unknown.

## 4. Not preserved

- No rosbag, no ROS logs from the demonstration runs, no screenshots from the navigation runs beyond the TF tree and saved maps.
- `mav.tlog` / `mav.parm` in the original backup date from Dec 2023, before the walls world, and are therefore not included.
- Original maps are 16 MB PGM files (4000×4000); only cropped PNGs and the yaml metadata are included.
- No quantitative evaluation (map accuracy, localization error, goal-reach rate, timing).
- Simulation only; no hardware tests.

## 5. Ground station caveats

- The archived code used a hard-coded MySQL URI with a password. In this release it is read from the `DRONE_DB_URI` environment variable.
- UI images, Leaflet and Leaflet.draw were not included (third-party / unlicensed assets). Pages referencing them will show missing icons until Leaflet is added under `ground_station/static/leaflet/`.
- `Send_path_drone.py` only logs received paths; it does not command the drone.
- The PPO skeleton and YOLO search experiments in the original workspace were left out: no training or results exist.
