#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from tensorbay import GAS
from tensorbay.sensor import Sensor, Sensors

from .utility import get_dataset_name

LIDAR_DATA = {
    "name": "Lidar1",
    "type": "LIDAR",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}


class TestSensor:
    def test_sensor(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")

        segment_client.upload_sensor(Sensor.loads(LIDAR_DATA))

        sensors = segment_client.get_sensors()
        assert sensors == Sensors.loads([LIDAR_DATA])

        segment_client.delete_sensor(LIDAR_DATA["name"])
        sensors = segment_client.get_sensors()
        assert len(sensors) == 0

        gas_client.delete_dataset(dataset_name)
