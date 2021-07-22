#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Mask related classes."""

from typing import Any, Callable, Dict, Optional, Tuple, Union

from ..utility import FileMixin, RemoteFileMixin, ReprMixin, common_loads
from .basic import AttributeType, SubcatalogBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


class SemanticMaskSubcatalog(SubcatalogBase, CategoriesMixin, AttributesMixin):
    """This class defines the subcatalog for semantic mask type of labels.

    Attributes:
        description: The description of the entire semantic mask subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    Examples:
        *Initialization Method 1:* Init from ``SemanticMaskSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "SEMANTIC_MASK": {
        ...         "categories": [{'name': 'cat'}, {'name': 'dog'}],
        ...         "attributes": [{'name': 'occluded', 'type': 'boolean'}],
        ...     }
        ... }
        >>> SemanticMaskSubcatalog.loads(catalog["SEMANTIC_MASK"])
        SemanticMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty SemanticMaskSubcatalog and then add the attributes.

        >>> semantic_mask_subcatalog = SemanticMaskSubcatalog()
        >>> semantic_mask_subcatalog.add_category("cat")
        >>> semantic_mask_subcatalog.add_category("dog")
        >>> semantic_mask_subcatalog.add_attribute("occluded", type_="boolean")
        >>> semantic_mask_subcatalog
        SemanticMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """


class InstanceMaskSubcatalog(SubcatalogBase, IsTrackingMixin, AttributesMixin):
    """This class defines the subcatalog for instance mask type of labels.

    Attributes:
        description: The description of the entire instance mask subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    Examples:
        *Initialization Method 1:* Init from ``InstanceMaskSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "INSTANCE_MASK": {
        ...         "attributes": [{'name': 'occluded', 'type': 'boolean'}],
        ...     }
        ... }
        >>> InstanceMaskSubcatalog.loads(catalog["INSTANCE_MASK"])
        InstanceMaskSubcatalog(
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty InstanceMaskSubcatalog and then add the attributes.

        >>> instance_mask_subcatalog = InstanceMaskSubcatalog()
        >>> instance_mask_subcatalog.add_attribute("occluded", type_="boolean")
        >>> instance_mask_subcatalog
        SemanticMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """


class PanopticMaskSubcatalog(SubcatalogBase, CategoriesMixin, AttributesMixin):
    """This class defines the subcatalog for panoptic mask type of labels.

    Attributes:
        description: The description of the entire panoptic mask subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    Examples:
        *Initialization Method 1:* Init from ``PanopticMaskSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "PANOPTIC_MASK": {
        ...         "categories": [{'name': 'cat'}, {'name': 'dog'}],
        ...         "attributes": [{'name': 'occluded', 'type': 'boolean'}],
        ...     }
        ... }
        >>> PanopticMaskSubcatalog.loads(catalog["PANOPTIC_MASK"])
        PanopticMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty PanopticMaskSubcatalog and then add the attributes.

        >>> panoptic_mask_subcatalog = PanopticMaskSubcatalog()
        >>> panoptic_mask_subcatalog.add_category("cat")
        >>> panoptic_mask_subcatalog.add_category("dog")
        >>> panoptic_mask_subcatalog.add_attribute("occluded", type_="boolean")
        >>> panoptic_mask_subcatalog
        PanopticMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """


class MaskBase(ReprMixin):  # pylint: disable=too-few-public-methods
    """MaskBase is a base class for the mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the pixel value,
            and the value is the corresponding attributes.

    """

    _repr_attrs: Tuple[str, ...] = ("all_attributes",)

    _PATH_KEY: str
    _ID_KEY: str

    path: str

    all_attributes: Dict[int, AttributeType]

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.path = contents[self._PATH_KEY]
        if "info" in contents:
            self.all_attributes = {
                item[self._ID_KEY]: item["attributes"] for item in contents["info"]
            }

    def _dumps(self) -> Dict[str, Any]:
        contents: Dict[str, Any] = {self._PATH_KEY: self.path}
        if hasattr(self, "all_attributes"):
            contents["info"] = [
                {self._ID_KEY: i, "attributes": attributes}
                for i, attributes in self.all_attributes.items()
            ]

        return contents


class SemanticMaskBase(MaskBase):  # pylint: disable=too-few-public-methods
    """SemanticMaskBase is a base class for the semantic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the category id,
            and the value is the corresponding attributes.

    """

    _Type = Union["SemanticMask", "RemoteSemanticMask"]

    _ID_KEY = "categoryId"

    @classmethod
    def loads(cls, contents: Dict[str, Any]) -> "_Type":
        """Loads a SemanticMaskBase subclass from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the semantic mask label.

        Returns:
            A :class:`SemanticMask` or :class:`RemoteSemanticMask` instance containing the
            information from the given dict.

        Examples:
            >>> contents = {
                "localPath": "mask_000000.png",
                "info": [
                    {
                        "categoryId": 0,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "categoryId": 1,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }
            >>> SemanticMaskBase.loads(contents)
            SemanticMask("mask_000000.png")(
              (all_attributes): {
                0: {
                  'occluded': True
                },
                1: {
                  'occluded': False
                }
              }
            )

        """
        class_ = RemoteSemanticMask if "remotePath" in contents else SemanticMask
        return common_loads(class_, contents)


class InstanceMaskBase(MaskBase):  # pylint: disable=too-few-public-methods
    """InstanceMaskBase is a base class for the instance mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    _Type = Union["InstanceMask", "RemoteInstanceMask"]

    _ID_KEY = "instanceId"

    @classmethod
    def loads(cls, contents: Dict[str, Any]) -> "_Type":
        """Loads a InstanceMaskBase subclass from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the instance mask label.

        Returns:
            A :class:`InstanceMask` or :class:`RemoteInstanceMask` instance containing the
            information from the given dict.

        Examples:
            >>> contents = {
                "localPath": "mask_000000.png",
                "info": [
                    {
                        "instanceId": 0,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "instanceId": 1,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }
            >>> InstanceMaskBase.loads(contents)
            InstanceMask("mask_000000.png")(
              (all_attributes): {
                0: {
                  'occluded': True
                },
                1: {
                  'occluded': False
                }
              }
            )

        """
        class_ = RemoteInstanceMask if "remotePath" in contents else InstanceMask
        return common_loads(class_, contents)


class PanopticMaskBase(MaskBase):  # pylint: disable=too-few-public-methods
    """PanopticMaskBase is a base class for the panoptic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.
        all_category_ids: The dict of the category id in this mask, which key is the instance id,
            and the value is the corresponding category id.

    """

    _Type = Union["PanopticMask", "RemotePanopticMask"]

    _repr_attrs = ("all_category_ids", "all_attributes")

    _ID_KEY = "instanceId"

    def __init__(self) -> None:
        self.all_category_ids: Dict[int, int] = {}

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.path = contents[self._PATH_KEY]
        info = contents["info"]
        self.all_category_ids = {item[self._ID_KEY]: item["categoryId"] for item in info}

        if "attributes" in info[0]:
            self.all_attributes = {item[self._ID_KEY]: item["attributes"] for item in info}

    def _dumps(self) -> Dict[str, Any]:
        contents: Dict[str, Any] = {self._PATH_KEY: self.path}
        all_attributes = getattr(self, "all_attributes", None)
        info = []
        for i, category_id in self.all_category_ids.items():
            item = {self._ID_KEY: i, "categoryId": category_id}
            if all_attributes:
                item["attributes"] = all_attributes[i]
            info.append(item)

        contents["info"] = info
        return contents

    @classmethod
    def loads(cls, contents: Dict[str, Any]) -> "_Type":
        """Loads a PanopticMaskBase subclass from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the panoptic mask label.

        Returns:
            A :class:`PanopticMask` or :class:`RemotePanopticMask` instance containing the
            information from the given dict.

        Examples:
            >>> contents = {
                "localPath": "mask_000000.png",
                "info": [
                    {
                        "instanceId": 0,
                        "categoryId": 100,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "instanceId": 1,
                        "categoryId": 101,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }
            >>> PanopticMaskBase.loads(contents)
            PanopticMask("mask_000000.png")(
              (all_category_ids): {
                0: 100,
                1: 101
              },
              (all_attributes): {
                0: {
                  'occluded': True
                },
                1: {
                  'occluded': False
                }
              }
            )

        """
        class_ = RemotePanopticMask if "remotePath" in contents else PanopticMask
        return common_loads(class_, contents)


class SemanticMask(SemanticMaskBase, FileMixin):
    """SemanticMask is a class for the local semantic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the category id,
            and the value is the corresponding attributes.

    """

    _PATH_KEY = "localPath"

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current semantic mask label into a dict.

        Returns:
            A dict containing all the information of the semantic mask label.

        Examples:
            >>> semantic_mask = SemanticMask("mask_000000.png")
            >>> semantic_mask.all_attributes = {}
            >>> semantic_mask.all_attributes[0] = {"occluded": True}
            >>> semantic_mask.all_attributes[1] = {"occluded": False}
            >>> semantic_mask.dumps()
            {
                "localPath": "mask_000000.png",
                "info": [
                    {
                        "categoryId": 0,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "categoryId": 1,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }

        """
        return self._dumps()


class InstanceMask(InstanceMaskBase, FileMixin):
    """InstanceMask is a class for the local instance mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    _PATH_KEY = "localPath"

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current instance mask label into a dict.

        Returns:
            A dict containing all the information of the semantic mask label.

        Examples:
            >>> instance_mask = InstanceMask("mask_000000.png")
            >>> instance_mask.all_attributes = {}
            >>> instance_mask.all_attributes[0] = {"occluded": True}
            >>> instance_mask.all_attributes[1] = {"occluded": False}
            >>> instance_mask.dumps()
            {
                "localPath": "mask_000000.png",
                "info": [
                    {
                        "instanceId": 0,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "instanceId": 1,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }

        """
        return self._dumps()


class PanopticMask(PanopticMaskBase, FileMixin):
    """PanopticMask is a class for the local panoptic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.
        all_category_ids: The dict of the category id in this mask, which key is the instance id,
            and the value is the corresponding category id.

    """

    _PATH_KEY = "localPath"

    def __init__(self, local_path: str) -> None:
        PanopticMaskBase.__init__(self)
        FileMixin.__init__(self, local_path)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current panoptic mask label into a dict.

        Returns:
            A dict containing all the information of the semantic mask label.

        Examples:
            >>> panoptic_mask = PanopticMask("mask_000000.png")
            >>> panoptic_mask.all_attributes = {}
            >>> panoptic_mask.all_attributes[0] = {"occluded": True}
            >>> panoptic_mask.all_category_ids[0] = 100
            >>> panoptic_mask.all_attributes[1] = {"occluded": False}
            >>> panoptic_mask.all_category_ids[1] = 101
            >>> panoptic_mask.dumps()
            {
                "localPath": "mask_000000.png",
                "info": [
                    {
                        "instanceId": 0,
                        "categoryId": 100,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "instanceId": 1,
                        "categoryId": 101,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }

        """
        return self._dumps()


class RemoteSemanticMask(SemanticMaskBase, RemoteFileMixin):
    """RemoteSemanticMask is a class for the remote semantic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the category id,
            and the value is the corresponding attributes.

    """

    _PATH_KEY = "remotePath"

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current semantic mask label into a dict.

        Returns:
            A dict containing all the information of the semantic mask label.

        Examples:
            >>> semantic_mask = RemoteSemanticMask("mask_000000.png")
            >>> semantic_mask.all_attributes[0] = {"occluded": True}
            >>> semantic_mask.all_attributes[1] = {"occluded": False}
            >>> semantic_mask.dumps()
            {
                "remotePath": "mask_000000.png",
                "info": [
                    {
                        "categoryId": 0,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "categoryId": 1,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }

        """
        return self._dumps()


class RemoteInstanceMask(InstanceMaskBase, RemoteFileMixin):
    """RemoteInstanceMask is a class for the remote instance mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    _PATH_KEY = "remotePath"

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current instance mask label into a dict.

        Returns:
            A dict containing all the information of the semantic mask label.

        Examples:
            >>> instance_mask = RemoteInstanceMask("mask_000000.png")
            >>> instance_mask.all_attributes = {}
            >>> instance_mask.all_attributes[0] = {"occluded": True}
            >>> instance_mask.all_attributes[1] = {"occluded": False}
            >>> instance_mask.dumps()
            {
                "remotePath": "mask_000000.png",
                "info": [
                    {
                        "instanceId": 0,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "instanceId": 1,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }

        """
        return self._dumps()


class RemotePanopticMask(PanopticMaskBase, RemoteFileMixin):
    """RemotePanoticMask is a class for the remote panotic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    _PATH_KEY = "remotePath"

    def __init__(
        self, remote_path: str, *, _url_getter: Optional[Callable[[str], str]] = None
    ) -> None:
        PanopticMaskBase.__init__(self)
        RemoteFileMixin.__init__(self, remote_path, _url_getter=_url_getter)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current panoptic mask label into a dict.

        Returns:
            A dict containing all the information of the semantic mask label.

        Examples:
            >>> panoptic_mask = RemotePanoticMask("mask_000000.png")
            >>> panoptic_mask.all_attributes = {}
            >>> panoptic_mask.all_attributes[0] = {"occluded": True}
            >>> panoptic_mask.all_category_ids[0] = 100
            >>> panoptic_mask.all_attributes[1] = {"occluded": False}
            >>> panoptic_mask.all_category_ids[1] = 101
            >>> panoptic_mask.dumps()
            {
                "remotePath": "mask_000000.png",
                "info": [
                    {
                        "instanceId": 0,
                        "categoryId": 100,
                        "attributes": {
                            "occluded": True
                        }
                    },
                    {
                        "instanceId": 1,
                        "categoryId": 101,
                        "attributes": {
                            "occluded": False
                        }
                    }
                ]
            }

        """
        return self._dumps()
