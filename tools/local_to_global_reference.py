#!/usr/bin/env python3
"""Reference only -- NOT part of the historically demonstrated pipeline.

Converts local ENU offsets in metres (e.g. a pose from a `map`-frame nav_msgs/Path whose
origin coincides with the vehicle home) into latitude/longitude using a flat-earth
approximation, valid for distances of a few hundred metres. It exists to document what a
correct metres->lat/lon conversion looks like next to the archived bridge
(overlay/iq_sim/scripts/navigation_test.py), which multiplies metres by 1e7 directly.
See docs/KNOWN_LIMITATIONS.md.

Assumes map +x = East and +y = North with the map origin at home; gmapping's map frame
orientation follows the drone's start orientation, so a yaw offset may also be required.
"""
import math

EARTH_RADIUS_M = 6378137.0  # WGS-84 equatorial radius


def local_to_global(home_lat_deg, home_lon_deg, east_m, north_m):
    dlat = north_m / EARTH_RADIUS_M
    dlon = east_m / (EARTH_RADIUS_M * math.cos(math.radians(home_lat_deg)))
    return home_lat_deg + math.degrees(dlat), home_lon_deg + math.degrees(dlon)


if __name__ == "__main__":
    # ArduPilot SITL default home (CMAC), as also used as the default in the ground station
    home = (-35.363263, 149.1652378)
    for e, n in [(0, 0), (5, 0), (0, 5), (10, 10)]:
        lat, lon = local_to_global(*home, e, n)
        print("E=%5.1f N=%5.1f m -> lat=%.7f lon=%.7f" % (e, n, lat, lon))
