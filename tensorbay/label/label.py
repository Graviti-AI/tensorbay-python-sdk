#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Label.

A :class:`~.tensorbay.dataset.data.Data` instance contains one or several types of labels,
all of which are stored in :attr:`~tensorbay.dataset.data.Data.label`.

Different label types correspond to different label classes classes.

.. table:: label classes
   :widths: auto

   ============================================================= ===================================
   label classes                                                 explaination
   ============================================================= ===================================
   :class:`~tensorbay.label.label_classification.Classification` classification type of label
   :class:`~tensorbay.label.label_box.LabeledBox2D`              2D bounding box type of label
   :class:`~tensorbay.label.label_box.LabeledBox3D`              3D bounding box type of label
   :class:`~tensorbay.label.label_polygon.LabeledPolygon`        polygon type of label
   :class:`~tensorbay.label.label_polyline.LabeledPolyline2D`    2D polyline type of label
   :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D`  2D keypoints type of label
   :class:`~tensorbay.label.label_sentence.LabeledSentence`      transcripted sentence type of label
   ============================================================= ===================================

"""

from functools import partial
from typing import Any, Dict, List, Type, TypeVar

from ..utility import AttrsMixin, ReprMixin, ReprType, attr, common_loads, upper
from .basic import LabelType
from .label_box import LabeledBox2D, LabeledBox3D
from .label_classification import Classification
from .label_keypoints import LabeledKeypoints2D
from .label_polygon import LabeledPolygon
from .label_polyline import LabeledPolyline2D
from .label_sentence import LabeledSentence

_ERROR_MESSAGE = "The '{attr_name}' label is not provided in this data"
_attr = partial(attr, is_dynamic=True, key=upper, error_message=_ERROR_MESSAGE)


class Label(ReprMixin, AttrsMixin):
    """This class defines :attr:`~tensorbay.dataset.data.Data.label`.

    It contains growing types of labels referring to different tasks.

    Examples:
        >>> from tensorbay.label import Classification
        >>> label = Label()
        >>> label.classification = Classification("example_category", {"example_attribute1": "a"})
        >>> label
        Label(
          (classification): Classification(
            (category): 'example_category',
            (attributes): {...}
          )
        )

    """

    _T = TypeVar("_T", bound="Label")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = tuple(label_type.value for label_type in LabelType)
    _repr_maxlevel = 2

    classification: Classification = _attr()
    box2d: List[LabeledBox2D] = _attr()
    box3d: List[LabeledBox3D] = _attr()
    polygon: List[LabeledPolygon] = _attr()
    polyline2d: List[LabeledPolyline2D] = _attr()
    keypoints2d: List[LabeledKeypoints2D] = _attr()
    sentence: List[LabeledSentence] = _attr()

    def __bool__(self) -> bool:
        for label_type in LabelType:
            if hasattr(self, label_type.value):
                return True
        return False

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads data from a dict containing the labels information.

        Arguments:
            contents: A dict containing the labels information.

        Returns:
            A :class:`Label` instance containing labels information from the given dict.

        Examples:
            >>> contents = {
            ...     "CLASSIFICATION": {
            ...         "category": "example_category",
            ...         "attributes": {"example_attribute1": "a"}
            ...     }
            ... }
            >>> Label.loads(contents)
            Label(
              (classification): Classification(
                (category): 'example_category',
                (attributes): {...}
              )
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all labels into a dict.

        Returns:
            Dumped labels dict.

        Examples:
            >>> from tensorbay.label import Classification
            >>> label = Label()
            >>> label.classification = Classification("category1", {"attribute1": "a"})
            >>> label.dumps()
            {'CLASSIFICATION': {'category': 'category1', 'attributes': {'attribute1': 'a'}}}

        """
        return self._dumps()
