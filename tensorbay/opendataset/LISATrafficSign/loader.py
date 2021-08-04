#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring


import csv
import os

from ...dataset import Data, Dataset, Segment
from ...label import LabeledBox2D
from .._utility import glob

DATASET_NAME = "LISATrafficSign"


def LISATrafficSign(path: str) -> Dataset:
    """Dataloader of the `LISA Traffic Sign`_ dataset.

    .. _LISA Traffic Sign: http://cvrr.ucsd.edu/LISA/lisa-traffic-sign-dataset.html

    The file structure should be like::

        <path>
            readme.txt
            allAnnotations.csv
            categories.txt
            datasetDescription.pdf
            videoSources.txt
            aiua120214-0/
                frameAnnotations-DataLog02142012_external_camera.avi_annotations/
                    diff.txt
                    frameAnnotations.bak
                    frameAnnotations.bak2
                    frameAnnotations.csv
                    keepRight_1330547092.avi_image10.png
                    keepRight_1330547092.avi_image11.png
                    keepRight_1330547092.avi_image12.png
                    ...
            aiua120214-1/
                frameAnnotations-DataLog02142012_001_external_camera.avi_annotations/
            aiua120214-2/
                frameAnnotations-DataLog02142012_002_external_camera.avi_annotations/
            aiua120306-0/
                frameAnnotations-DataLog02142012_002_external_camera.avi_annotations/
            aiua120306-1/
                frameAnnotations-DataLog02142012_003_external_camera.avi_annotations/
            vid0/
                frameAnnotations-vid_cmp2.avi_annotations/
            vid1/
                frameAnnotations-vid_cmp1.avi_annotations/
            vid10/
                frameAnnotations-MVI_0122.MOV_annotations/
            vid11/
                frameAnnotations-MVI_0123.MOV_annotations/
            vid2/
                frameAnnotations-vid_cmp2.avi_annotations/
            vid3/
                frameAnnotations-vid_cmp2.avi_annotations/
            vid4/
                frameAnnotations-vid_cmp2.avi_annotations/
            vid5/
                frameAnnotations-vid_cmp2.avi_annotations/
            vid6/
                frameAnnotations-MVI_0071.MOV_annotations/
            vid7/
                frameAnnotations-MVI_0119.MOV_annotations/
            vid8/
                frameAnnotations-MVI_0120.MOV_annotations/
            vid9/
                frameAnnotations-MVI_0121.MOV_annotations/
            negatives/
                negativePics/
                negatives.dat
            tools/
                evaluateDetections.py
                extractAnnotations.py
                mergeAnnotationFiles.py
                splitAnnotationFiles.py

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for dir_entry in os.scandir(root_path):
        if not dir_entry.is_dir() or not dir_entry.name.startswith(("vid", "aiua")):
            continue
        dataset.add_segment(_load_positive_segment(dir_entry.name, dir_entry.path))
    dataset.add_segment(_load_negative_segment(root_path))

    return dataset


def _load_positive_segment(segment_name: str, segment_path: str) -> Segment:
    if segment_name.startswith("vid"):
        # Pad zero for segment name to change "vid0" to "vid00"
        segment_name = f"{segment_name[:3]}{int(segment_name[3:]):02}"
    segment = Segment(segment_name)
    annotation_file = glob(
        os.path.join(segment_path, "frameAnnotations-*", "frameAnnotations.csv")
    )[0]
    image_folder = os.path.dirname(annotation_file)
    pre_filename = ""
    with open(annotation_file, "r") as fp:
        for annotation in csv.DictReader(fp, delimiter=";"):
            filename = annotation["Filename"]

            if filename != pre_filename:
                data = Data(os.path.join(image_folder, filename))
                data.label.box2d = []
                segment.append(data)
                pre_filename = filename

            occluded, on_another_road = annotation["Occluded,On another road"].split(",", 1)
            data.label.box2d.append(
                LabeledBox2D(
                    int(annotation["Upper left corner X"]),
                    int(annotation["Upper left corner Y"]),
                    int(annotation["Lower right corner X"]),
                    int(annotation["Lower right corner Y"]),
                    category=annotation["Annotation tag"],
                    attributes={
                        "Occluded": bool(int(occluded)),
                        "On another road": bool(int(on_another_road)),
                        "Origin file": annotation["Origin file"],
                        "Origin frame number": int(annotation["Origin frame number"]),
                        "Origin track": annotation["Origin track"],
                        "Origin track frame number": int(annotation["Origin track frame number"]),
                    },
                )
            )
    return segment


def _load_negative_segment(root_path: str) -> Segment:
    segment = Segment("negative")
    for negative_image_path in glob(os.path.join(root_path, "negatives", "negativePics", "*.png")):
        data = Data(negative_image_path)
        data.label.box2d = []
        segment.append(data)
    return segment
