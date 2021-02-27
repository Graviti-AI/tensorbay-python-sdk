#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Label, LabelType and different types of labels.

:class:`LabelType` is an enumeration type
which includes all the supported label types within :class:`~graviti.dataset.data.Labels`.

:class:`Label` is the most basic label level in the TensorBay dataset structure,
and is the base class for the following various types of label classes.

Each :class:`Label` object contains one annotaion of a :class:`~graviti.dataset.data.Data` object.

.. table:: label classes
   :widths: auto

   ============================  ===================================
   label classes                 explaination
   ============================  ===================================
   :class:`Classification`       classification type of label
   :class:`LabeledBox2D`         2D bounding box type of label
   :class:`LabeledBox3D`         3D bounding box type of label
   :class:`LabeledPolygon2D`     2D polygon type of label
   :class:`LabeledPolyline2D`    2D polyline type of label
   :class:`LabeledKeypoints2D`   2D keypoints type of label
   :class:`LabeledSentence`      transcripted sentence type of label
   ============================  ===================================

"""

from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..geometry import Box2D, Box3D, Keypoints2D, Polygon2D, Polyline2D, Quaternion, Transform3D
from ..utility import ReprMixin, ReprType, TypeEnum, TypeMixin, TypeRegister, common_loads


class LabelType(TypeEnum):
    """This class defines all the supported types within :class:`~graviti.dataset.data.Labels`."""

    __subcatalog_registry__: Dict[TypeEnum, Type[Any]] = {}

    CLASSIFICATION = "classification"
    BOX2D = "box2d"
    BOX3D = "box3d"
    POLYGON2D = "polygon2d"
    POLYLINE2D = "polyline2d"
    KEYPOINTS2D = "keypoints2d"
    SENTENCE = "sentence"

    @property
    def subcatalog_type(self) -> Type[Any]:
        """Return the corresponding subcatalog class.

        Each label type has a corresponding Subcatalog class.

        Returns:
            The corresponding subcatalog type.
        """
        return self.__subcatalog_registry__[self]


class Label(TypeMixin[LabelType], ReprMixin):
    """This class defines the basic concept of label.

    :class:`Label` is the most basic label level in the TensorBay dataset structure,
    and is the base class for the following various types of label classes.

    Each :class:`Label` object
    contains one annotaion of a :class:`~graviti.dataset.data.Data` object.

    Arguments:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    """

    _T = TypeVar("_T", bound="Label")
    _label_attrs: Tuple[str, ...] = ("category", "attributes", "instance")
    _repr_attrs = _label_attrs

    category: str
    attributes: Dict[str, Any]
    instance: str

    def __init__(
        self,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        if category:
            self.category = category
        if attributes:
            self.attributes = attributes
        if instance:
            self.instance = instance

    def _loads(self, contents: Dict[str, Any]) -> None:
        for attribute_name in self._label_attrs:
            if attribute_name in contents:
                setattr(self, attribute_name, contents[attribute_name])

    def dumps(self) -> Dict[str, Any]:
        """Dumps the label into a dict.

        Returns:
            A dict containing all the information of the label.
            See dict format details in ``dumps()`` of different label classes .

        """
        contents: Dict[str, Any] = {}
        for attribute_name in self._label_attrs:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_value:
                contents[attribute_name] = attribute_value
        return contents


@TypeRegister(LabelType.CLASSIFICATION)
class Classification(Label):
    """This class defines the concept of classification label.

    :class:`Classification` is the classification type of label,
    which applies to different types of data, such as images and texts.

    Arguments:
        category: The category of the label.
        attributes: The attributes of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.

    """

    _T = TypeVar("_T", bound="Classification")
    _label_attrs = ("category", "attributes")
    _repr_attrs = _label_attrs

    def __init__(
        self,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        Label.__init__(self, category, attributes)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a Classification label from a dict containing the label information.

        Arguments:
            contents: A dict containing the information of the classification label,
                whose format should be like::

                    {
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        }
                    }

        Returns:
            The loaded :class:`Classification` object.

        """
        return common_loads(cls, contents)


@TypeRegister(LabelType.BOX2D)
class LabeledBox2D(Box2D, Label):  # pylint: disable=too-many-ancestors
    """This class defines the concept of 2D bounding box label.

    :class:`LabeledBox2D` is the 2D bounding box type of label,
    which is often used for CV tasks such as object detection.

    Arguments:
        *args: The coordinates of the top-left and bottom-right vertex of the 2D box,
            which can be initialized like:

            .. code:: python

                box = LabeledBox2D()
                box = LabeledBox2D(10, 20, 30, 40)
                box = LabeledBox2D([10, 20, 30, 40])

        category: The category of the label.
        attributes: The attributs of the label.
        instance: The instance id of the label.
        x: X coordinate of the top-left vertex of the box.
        y: Y coordinate of the top-left vertex of the box.
        width: Length of the 2D bounding box along the x axis.
        height: Length of the 2D bounding box along the y axis.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    """

    _T = TypeVar("_T", bound="LabeledBox2D")
    _repr_type = ReprType.INSTANCE
    _repr_attrs = Label._repr_attrs

    def __init__(
        self,
        *args: Union[None, float, Iterable[float]],
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ):
        Box2D.__init__(self, *args, x=x, y=y, width=width, height=height)
        Label.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledBox2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D bounding box label,
                whose format should be like::

                    {
                        "box2d": {
                            "xmin": <float>
                            "ymin": <float>
                            "xmax": <float>
                            "ymax": <float>
                        },
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledBox2D` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        Box2D._loads(self, contents["box2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current 2D bounding box label into a dict.

        Returns:
            A dict containing all the information of the 2D box label,
            whose format is like::

                {
                    "box2d": {
                        "xmin": <float>
                        "ymin": <float>
                        "xmax": <float>
                        "ymax": <float>
                    },
                    "category": <str>
                    "attributes": {
                        <key>: <value>
                        ...
                        ...
                    },
                    "instance": <str>
                }

        """
        contents = Label.dumps(self)
        contents["box2d"] = Box2D.dumps(self)
        return contents


@TypeRegister(LabelType.BOX3D)
class LabeledBox3D(Box3D, Label):
    """This class defines the concept of 3D bounding box label.

    :class:`LabeledBox3D` is the 3D bounding box type of label,
    which is often used for object detection in 3D point cloud.

    Arguments:
        transform: The transform of the 3D bounding box label in
            a :class:`~graviti.geometry.transform.Transform3D` object
            or a 4x4 or 3x4 transformation matrix.
        translation: Translation of the 3D bounding box label in a sequence of [x, y, z].
        rotation: Rotation of the 3D bounding box label in a sequence of [w, x, y, z]
            or a 3x3 rotation matrix
            or a :class:`~graviti.geometry.quaternion.Quaternion` object.
        size: Size of the 3D bounding box label in a sequence of [x, y, z].
        category: Category of the 3D bounding box label.
        attributes: Attributs of the 3D bounding box label.
        instance: The instance id of the 3D bounding box label.
        **kwargs: Other parameters to initialize the rotation of the 3D bounding box label.
            See :class:`~graviti.geometry.quaternion.Quaternion` documents for details.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.
        size: The size of the 3D bounding box.
        transform: The transform of the 3D bounding box.

    """

    _T = TypeVar("_T", bound="LabeledBox3D")
    _repr_attrs = Box3D._repr_attrs + Label._repr_attrs

    def __init__(
        self,
        transform: Transform3D.TransformType = None,
        *,
        translation: Optional[Iterable[float]] = None,
        rotation: Quaternion.ArgsType = None,
        size: Optional[Iterable[float]] = None,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
        **kwargs: Quaternion.KwargsType,
    ):
        Box3D.__init__(
            self,
            transform,
            translation=translation,
            rotation=rotation,
            size=size,
            **kwargs,
        )
        Label.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledBox3D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 3D bounding box label,
                whose format should be like::

                    {
                        "box3d": {
                            "translation": {
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            },
                            "rotation": {
                                "w": <float>
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            },
                            "size": {
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            }
                        },
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledBox3D` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        Box3D._loads(self, contents["box3d"])
        Label._loads(self, contents)

    def __rmul__(self: _T, other: Transform3D) -> _T:
        if isinstance(other, Transform3D):
            labeled_box_3d = Box3D.__rmul__(self, other)
            if hasattr(self, "category"):
                labeled_box_3d.category = self.category
            if hasattr(self, "attributes"):
                labeled_box_3d.attributes = self.attributes
            if hasattr(self, "instance"):
                labeled_box_3d.instance = self.instance
            return labeled_box_3d

        return NotImplemented  # type: ignore[unreachable]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current 3D bounding box label into a dict.

        Returns:
            A dict containing all the information of the 3D bounding box label,
            whose format is like::

                {
                    "box3d": {
                        "translation": {
                            "x": <float>
                            "y": <float>
                            "z": <float>
                        },
                        "rotation": {
                            "w": <float>
                            "x": <float>
                            "y": <float>
                            "z": <float>
                        },
                        "size": {
                            "x": <float>
                            "y": <float>
                            "z": <float>
                        }
                    },
                    "category": <str>
                    "attributes": {
                        <key>: <value>
                        ...
                        ...
                    },
                    "instance": <str>
                },

        """
        contents = Label.dumps(self)
        contents["box3d"] = Box3D.dumps(self)
        return contents


@TypeRegister(LabelType.POLYGON2D)
class LabeledPolygon2D(Polygon2D, Label):  # pylint: disable=too-many-ancestors
    """This class defines the concept of polygon2D label.

    :class:`LabeledPolygon2D` is the 2D polygon type of label,
    which is often used for CV tasks such as semantic segmentation.

    Arguments:
        points: A list of 2D points representing the vertexes of the 2D polygon.
        category: The category of the label.
        attributes: The attributs of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    """

    _T = TypeVar("_T", bound="LabeledPolygon2D")
    _repr_type = ReprType.SEQUENCE
    _repr_attrs = Label._repr_attrs

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        super().__init__(points)
        Label.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledPolygon2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D polygon label,
                whose format should be like::

                    {
                        "polygon": [
                            { "x": <int>
                              "y": <int>
                            },
                            ...
                            ...
                        ],
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledPolygon2D` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["polygon2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D polygon label into a dict.

        Returns:
            A dict containing all the information of the 2D polygon label,
            whose format is like::

                {
                    "polygon": [
                        { "x": <int>
                          "y": <int>
                        },
                        ...
                        ...
                    ],
                    "category": <str>
                    "attributes": {
                        <key>: <value>
                        ...
                        ...
                    },
                    "instance": <str>
                }

        """
        contents = Label.dumps(self)
        contents["polygon2d"] = super().dumps()

        return contents


@TypeRegister(LabelType.POLYLINE2D)
class LabeledPolyline2D(Polyline2D, Label):  # pylint: disable=too-many-ancestors
    """This class defines the concept of polyline2D label.

    :class:`LabeledPolyline2D` is the 2D polyline type of label,
    which is often used for CV tasks such as lane detection.

    Arguments:
        points: A list of 2D points representing the vertexes of the 2D polyline.
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    """

    _T = TypeVar("_T", bound="LabeledPolyline2D")
    _repr_type = ReprType.SEQUENCE
    _repr_attrs = Label._repr_attrs

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        super().__init__(points)
        Label.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledPolyline2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D polyline label,
                whose format should be like::

                    {
                        "polyline": [
                            { "x": <int>
                              "y": <int>
                            },
                            ...
                            ...
                        ],
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledPolyline2D` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["polyline2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D polyline label into a dict.

        Returns:
            A dict containing all the information of the 2D polyline label,
            whose format is like::

                {
                    "polyline": [
                        { "x": <int>
                          "y": <int>
                        },
                        ...
                        ...
                    ],
                    "category": <str>
                    "attributes": {
                        <key>: <value>
                        ...
                        ...
                    },
                    "instance": <str>
                }

        """
        contents = Label.dumps(self)
        contents["polyline2d"] = super().dumps()

        return contents


class Word(ReprMixin):
    """This class defines the concept of word.

    :class:`Word` is a word within a phonetic transcription sentence,
    containing the content of the word, the start and end time in the audio.

    Arguments:
        text: The content of the word.
        begin: The begin time of the word in the audio.
        end: The end time of the word in the audio.

    Attributes:
        text: The content of the word.
        begin: The begin time of the word in the audio.
        end: The end time of the word in the audio.

    """

    _T = TypeVar("_T", bound="Word")
    _repr_attrs = ("text", "begin", "end")

    def __init__(
        self,
        text: str,
        begin: Optional[float] = None,
        end: Optional[float] = None,
    ):
        self.text = text
        if begin is not None:
            self.begin = begin
        if end is not None:
            self.end = end

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Union[str, float]]) -> _T:
        """Loads a Word from a dict containing the information of the word.

        Arguments:
            contents: A dict containing the information of the word,
                whose format should be like::

                    {
                        "text": str ,
                        "begin": float,
                        "end": float,
                    }

        Returns:
            The loaded :class:`Word` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.text = contents["text"]

        if "begin" in contents:
            self.begin = contents["begin"]

        if "end" in contents:
            self.end = contents["end"]

    def dumps(self) -> Dict[str, Union[str, float]]:
        """Dumps the current word into a dict.

        Returns:
            A dict containing all the information of the word,
            whose format is like::

                {
                    "text": str ,
                    "begin": float,
                    "end": float,
                }

        """
        contents: Dict[str, Union[str, float]] = {"text": self.text}
        if hasattr(self, "begin"):
            contents["begin"] = self.begin
        if hasattr(self, "end"):
            contents["end"] = self.end
        return contents


@TypeRegister(LabelType.SENTENCE)  # pylint: disable=too-few-public-methods
class LabeledSentence(Label):
    """This class defines the concept of phonetic transcription lable.

    :class:`LabeledSentence` is the transcripted sentence type of label.
    which is often used for tasks such as automatic speech recognition.

    Arguments:
        sentence: A list of sentence.
        spell: A list of spell, only exists in Chinese language.
        phone: A list of phone.
        attributes: The attributes of the label.

    Attributes:
        sentence: The transcripted sentence.
        spell: The spell within the sentence, only exists in Chinese language.
        phone: The phone of the sentence label.
        attributes: The attributes of the label.

    """

    _T = TypeVar("_T", bound="LabeledSentence")
    _label_attrs = ("attributes",)
    _repr_maxlevel = 3
    _repr_attrs = ("sentence", "spell", "phone") + _label_attrs

    def __init__(
        self,
        sentence: Optional[Iterable[Word]] = None,
        spell: Optional[Iterable[Word]] = None,
        phone: Optional[Iterable[Word]] = None,
        *,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(attributes=attributes)
        if sentence:
            self.sentence = list(sentence)
        if spell:
            self.spell = list(spell)
        if phone:
            self.phone = list(phone)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledSentence from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the sentence label,
                whose format should be like::

                    {
                        "sentence": [
                            {
                                "text":  <str>
                                "begin": <float>
                                "end":   <float>
                            }
                            ...
                            ...
                        ],
                        "spell": [
                            {
                                "text":  <str>
                                "begin": <float>
                                "end":   <float>
                            }
                            ...
                            ...
                        ],
                        "phone": [
                            {
                                "text":  <str>
                                "begin": <float>
                                "end":   <float>
                            }
                            ...
                            ...
                        ],
                        "attributes": {
                            <key>: <value>,
                            ...
                            ...
                        }
                    }

        Returns:
            The loaded :class:`LabeledSentence` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)

        if "sentence" in contents:
            self.sentence = self._load_word(contents["sentence"])

        if "spell" in contents:
            self.spell = self._load_word(contents["spell"])

        if "phone" in contents:
            self.phone = self._load_word(contents["phone"])

    @staticmethod
    def _load_word(contents: Iterable[Dict[str, Any]]) -> List[Word]:
        return [Word.loads(word) for word in contents]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current label into a dict.

        Returns:
            A dict containing all the information of the sentence label,
            whose format is like::

                {
                    "sentence": [
                        {
                            "text":  <str>
                            "begin": <float>
                            "end":   <float>
                        }
                        ...
                        ...
                    ],
                    "spell": [
                        {
                            "text":  <str>
                            "begin": <float>
                            "end":   <float>
                        }
                        ...
                        ...
                    ],
                    "phone": [
                        {
                            "text":  <str>
                            "begin": <float>
                            "end":   <float>
                        }
                        ...
                        ...
                    ],
                    "attributes": {
                        <key>: <value>,
                        ...
                        ...
                    }
                }

        """
        contents = Label.dumps(self)
        if hasattr(self, "sentence"):
            contents["sentence"] = [word.dumps() for word in self.sentence]
        if hasattr(self, "spell"):
            contents["spell"] = [word.dumps() for word in self.spell]
        if hasattr(self, "phone"):
            contents["phone"] = [word.dumps() for word in self.phone]
        return contents


@TypeRegister(LabelType.KEYPOINTS2D)
class LabeledKeypoints2D(Keypoints2D, Label):  # pylint: disable=too-many-ancestors
    """This class defines the concept of 2D keypoints label.

    :class:`LabeledKeypoints2D` is the 2D keypoints type of label,
    which is often used for CV tasks such as human body pose estimation.

    Arguments:
        keypoints: A list of 2D keypoint.
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    """

    _T = TypeVar("_T", bound="LabeledKeypoints2D")
    _repr_type = ReprType.SEQUENCE
    _repr_attrs = Label._repr_attrs

    def __init__(
        self,
        keypoints: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ) -> None:
        super().__init__(keypoints)
        Label.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledKeypoints2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D keypoints label,
                whose format should be like::

                    {
                        "keypoints2d": [
                            { "x": <float>
                              "y": <float>
                              "v": <int>
                            },
                            ...
                            ...
                        ],
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledKeypoints2D` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["keypoints2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D keypoints label into a dict.

        Returns:
            A dict containing all the information of the 2D keypoints label,
            whose format is like::

                {
                    "keypoints2d": [
                        { "x": <float>
                          "y": <float>
                          "v": <int>
                        },
                        ...
                        ...
                    ],
                    "category": <str>
                    "attributes": {
                        <key>: <value>
                        ...
                        ...
                    },
                    "instance": <str>
                }

        """
        contents = Label.dumps(self)
        contents["keypoints2d"] = super().dumps()

        return contents
