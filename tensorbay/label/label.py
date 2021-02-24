#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines class Label, LabelType, Classification, LabeledBox2D, LabeledBox3D,
LabeledPolygon2D and LabeledPolyline2D
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..geometry import Box2D, Box3D, Keypoints2D, Polygon2D, Polyline2D, Quaternion, Transform3D
from ..utility import ReprMixin, ReprType, TypeEnum, TypeMixin, TypeRegister, common_loads


class LabelType(TypeEnum):
    """this class defines the type of the labels.

    :param label_key: The key string of the json format label annotation
    """

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
        """Get the corresponding subcatalog class.

        Returns:
            The correspoinding subcatalog type.
        """
        return self.__subcatalog_registry__[self]


class Label(TypeMixin[LabelType], ReprMixin):
    """This class defines the concept of label and some operations on it."""

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
        """dump a label into a dict."""

        contents: Dict[str, Any] = {}
        for attribute_name in self._label_attrs:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_value:
                contents[attribute_name] = attribute_value
        return contents


@TypeRegister(LabelType.CLASSIFICATION)
class Classification(Label):
    """This class defines the concept of classification label.

    :param category: Category of the label
    :param attributes: Attributs of the label
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
        """Load a Classification label from a dict containing the information of the label.

        :param contents: A dict containing the information of a Classification label
        {
            "category": <str>
            "attributes": <Dict>
            "instance": <str>
        }
        :return: The loaded Classification label
        """
        return common_loads(cls, contents)


@TypeRegister(LabelType.BOX2D)
class LabeledBox2D(Box2D, Label):  # pylint: disable=too-many-ancestors
    """Contain the definition of LabeledBox2D bounding box and some related operations.

    :param args: Union[None, float, Sequence[float]],
        box = LabeledBox2D()
        box = LabeledBox2D(10, 20, 30, 40)
        box = LabeledBox2D([10, 20, 30, 40])
    :param category: Category of the label
    :param attributes: Attributs of the label
    :param instance: Labeled instance
    :param x: X coordinate of the top left vertex of the box
    :param y: Y coordinate of the top left vertex of the box
    :param width: Length along the x axis
    :param height: Length along the y axis
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
        """Load a LabeledBox2D from a dict containing the information of the label.

        :param contents: A dict containing the information of a LabeledBox2D
        {
            "box2d": <Dict>
            "category": <str>
            "attributes": <Dict>
            "instance": <str>
        }
        :return: The loaded LabeledBox2D
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        Box2D._loads(self, contents["box2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:
        contents = Label.dumps(self)
        contents["box2d"] = Box2D.dumps(self)
        return contents


@TypeRegister(LabelType.BOX3D)
class LabeledBox3D(Box3D, Label):
    """Contain the definition of LabeledBox3D bounding box and some related operations.

    :param transform: A Transform3D object or a 4x4 or 3x4 transfrom matrix
    :param translation: Translation in a sequence of [x, y, z]
    :param rotation: Rotation in a sequence of [w, x, y, z] or 3x3 rotation matrix or `Quaternion`
    :param size: Size in a sequence of [x, y, z]
    :param category: Category of the label
    :param attributes: Attributs of the label
    :param instance: Labeled instance
    :param kwargs: Other parameters to initialize rotation of the transform
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
        """Load a LabeledBox3D from a dict containing the information of the label.

        :param contents: A dict containing the information of a LabeledBox3D
        {
            "translation": translation in a sequence of [x, y, z]
            "rotation": rotation in a sequence of [w, x, y, z]
            "size": size in a sequence of [x, y, z]
            "category": <str>
            "attributes": <Dict>
            "instance": <str>
        }
        :return: The loaded LabeledBox3D
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
        contents = Label.dumps(self)
        contents["box3d"] = Box3D.dumps(self)
        return contents


@TypeRegister(LabelType.POLYGON2D)
class LabeledPolygon2D(Polygon2D, Label):  # pylint: disable=too-many-ancestors
    """this class defines the polygon2D with labels

    :param points: a list of 2D point list
    :param category: Category of the label
    :param attributes: Attributs of the label
    :param instance: Labeled instance
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
        """Load a LabeledPolygon2D from a dict containing the information of the label.

        :param contents: A dict containing the information of a LabeledPolygon2D
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
                "<key>": "<value>" <str>
                ...
                ...
            }
            "instance": <str>
        }
        :return: The loaded LabeledPolygon2D
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["polygon2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """dump a LabeledPolygon2D into a dict"""

        contents = Label.dumps(self)
        contents["polygon2d"] = super().dumps()

        return contents


@TypeRegister(LabelType.POLYLINE2D)
class LabeledPolyline2D(Polyline2D, Label):  # pylint: disable=too-many-ancestors
    """this class defines the polyline2D with labels

    :param points: a list of 2D point list
    :param category: Category of the label
    :param attributes: Attributs of the label
    :param instance: Labeled instance
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
        """Load a LabeledPolyline2D from a dict containing the information of the label.

        :param contents: A dict containing the information of a LabeledPolyline2D
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
                "<key>": "<value>" <str>
                ...
                ...
            }
            "instance": <str>
        }
        :return: The loaded LabeledPolyline2D
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["polyline2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """dump a LabeledPolyline2D into a dict"""

        contents = Label.dumps(self)
        contents["polyline2d"] = super().dumps()

        return contents


class Word(ReprMixin):
    """Contain the content and time of the word

    :param text: content of the word
    :param begin: the begin time of the word in audio
    :param end: the end time of the word in audio
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
        """Load a Word from a dict containing the information of the word.

        :param contents: A dict containing the information of a Word
        {
            "text": str ,
            "begin": float,
            "end": float,
        }
        :return: The loaded Word
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.text = contents["text"]

        if "begin" in contents:
            self.begin = contents["begin"]

        if "end" in contents:
            self.end = contents["end"]

    def dumps(self) -> Dict[str, Union[str, float]]:
        """Dumps a word into a dict"""
        contents: Dict[str, Union[str, float]] = {"text": self.text}
        if hasattr(self, "begin"):
            contents["begin"] = self.begin
        if hasattr(self, "end"):
            contents["end"] = self.end
        return contents


@TypeRegister(LabelType.SENTENCE)  # pylint: disable=too-few-public-methods
class LabeledSentence(Label):
    """this class defines the speech to sentence with lables

    :param sentence: a list of sentence
    :param speech: a list of spell, only exists in chinese language
    :param phone: a list of phone
    :param attributes: attributes of the label
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
        """Load a LabeledSentence from a dict containing the information of the label.

        :param contents: A dict containing the information of a LabeledSentence
        {
            "sentence": [
                {
                    "text":          <string>
                    "begin":         <number>
                    "end":           <number>
                }
                ...
                ...
            ],
            "spell": [
                {
                    "text":          <string>
                    "begin":         <number>
                    "end":           <number>
                }
                ...
                ...
            ],
            "phone": [
                {
                    "text":          <string>
                    "begin":         <number>
                    "end":           <number>
                }
                ...
                ...
            ],
            "attributes": {
                <key>: <value>,    <str>
                ...
                ...
            }
        }
        :return: The loaded LabeledSentence
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
        """dump a LabeledSentence into a dict"""

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
    """This class defines Keypoints2D with labels.

    :param keypoints: a list of 2D keypoint list
    :param category: Category of the label
    :param attributes: Attributs of the label
    :param instance: Labeled instance
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
        """Load a LabeledKeypoints2D from a dict containing the information of the label.

        :param contents: A dict containing the information of a LabeledKeypoints2D
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
                "<key>": "<value>" <str>
                ...
                ...
            }
            "instance": <str>
        }
        :return: The loaded LabeledKeypoints2D
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["keypoints2d"])
        Label._loads(self, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps a LabeledKeypoints2D into a dict

        :return: a dictionary containing the labeled 2D keypoints
        """
        contents = Label.dumps(self)
        contents["keypoints2d"] = super().dumps()

        return contents
