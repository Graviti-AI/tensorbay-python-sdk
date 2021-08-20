#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Mask related classes."""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

from ..utility import FileMixin, RemoteFileMixin, ReprMixin
from .basic import AttributeType, SubcatalogBase
from .supports import AttributesMixin, IsTrackingMixin, MaskCategoriesMixin


class SemanticMaskSubcatalog(SubcatalogBase, MaskCategoriesMixin, AttributesMixin):
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
        ...         "categories": [
        ...             {'name': 'cat', "categoryId": 1},
        ...             {'name': 'dog', "categoryId": 2}
        ...         ],
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
        >>> semantic_mask_subcatalog.add_category("cat", 1)
        >>> semantic_mask_subcatalog.add_category("dog", 2)
        >>> semantic_mask_subcatalog.add_attribute("occluded", type_="boolean")
        >>> semantic_mask_subcatalog
        SemanticMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """


class InstanceMaskSubcatalog(SubcatalogBase, MaskCategoriesMixin, IsTrackingMixin, AttributesMixin):
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
        ...         "categories": [
        ...             {'name': 'background', "categoryId": 0}
        ...         ],
        ...         "attributes": [{'name': 'occluded', 'type': 'boolean'}],
        ...     }
        ... }
        >>> InstanceMaskSubcatalog.loads(catalog["INSTANCE_MASK"])
        InstanceMaskSubcatalog(
          (is_tracking): False,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty InstanceMaskSubcatalog and then add the attributes.

        >>> instance_mask_subcatalog = InstanceMaskSubcatalog()
        >>> instance_mask_subcatalog.add_category("background", 0)
        >>> instance_mask_subcatalog.add_attribute("occluded", type_="boolean")
        >>> instance_mask_subcatalog
        InstanceMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """


class PanopticMaskSubcatalog(SubcatalogBase, MaskCategoriesMixin, AttributesMixin):
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
        ...         "categories": [
        ...             {'name': 'cat', "categoryId": 1},
        ...             {'name': 'dog', "categoryId": 2}
        ...         ],
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
        >>> panoptic_mask_subcatalog.add_category("cat", 1)
        >>> panoptic_mask_subcatalog.add_category("dog", 2)
        >>> panoptic_mask_subcatalog.add_attribute("occluded", type_="boolean")
        >>> panoptic_mask_subcatalog
        PanopticMaskSubcatalog(
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """


class SemanticMaskBase(ReprMixin):
    """SemanticMaskBase is a base class for the semantic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the category id,
            and the value is the corresponding attributes.

    """

    _repr_attrs = ("all_attributes",)

    all_attributes: Dict[int, AttributeType]


class InstanceMaskBase(ReprMixin):
    """InstanceMaskBase is a base class for the instance mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    _repr_attrs = ("all_attributes",)

    all_attributes: Dict[int, AttributeType]


class PanopticMaskBase(ReprMixin):
    """PanopticMaskBase is a base class for the panoptic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.
        all_category_ids: The dict of the category id in this mask, which key is the instance id,
            and the value is the corresponding category id.

    """

    _repr_attrs = ("all_category_ids", "all_attributes")

    all_attributes: Dict[int, AttributeType]

    def __init__(self) -> None:
        self.all_category_ids: Dict[int, int] = {}


class SemanticMask(SemanticMaskBase, FileMixin):
    """SemanticMask is a class for the local semantic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the category id,
            and the value is the corresponding attributes.

    """

    def __init__(self, local_path: str) -> None:
        FileMixin.__init__(self, local_path)

    def get_callback_body(self) -> Dict[str, Any]:
        """Get the callback request body for uploading.

        Returns:
            The callback request body, which looks like::

                    {
                        "checksum": <str>,
                        "fileSize": <int>,
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
        body = super()._get_callback_body()
        if hasattr(self, "all_attributes"):
            body["info"] = [
                {"categoryId": i, "attributes": attributes}
                for i, attributes in self.all_attributes.items()
            ]
        return body


class InstanceMask(InstanceMaskBase, FileMixin):
    """InstanceMask is a class for the local instance mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    def __init__(self, local_path: str) -> None:
        FileMixin.__init__(self, local_path)

    def get_callback_body(self) -> Dict[str, Any]:
        """Get the callback request body for uploading.

        Returns:
            The callback request body, which looks like::

                    {
                        "checksum": <str>,
                        "fileSize": <int>,
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
        body = super()._get_callback_body()
        if hasattr(self, "all_attributes"):
            body["info"] = [
                {"instanceId": i, "attributes": attributes}
                for i, attributes in self.all_attributes.items()
            ]
        return body


class PanopticMask(PanopticMaskBase, FileMixin):
    """PanopticMask is a class for the local panoptic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.
        all_category_ids: The dict of the category id in this mask, which key is the instance id,
            and the value is the corresponding category id.

    """

    def __init__(self, local_path: str) -> None:
        PanopticMaskBase.__init__(self)
        FileMixin.__init__(self, local_path)

    def get_callback_body(self) -> Dict[str, Any]:
        """Get the callback request body for uploading.

        Returns:
            The callback request body, which looks like::

                    {
                        "checksum": <str>,
                        "fileSize": <int>,
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
        body = super()._get_callback_body()
        all_attributes = getattr(self, "all_attributes", None)
        info = []
        for i, category_id in self.all_category_ids.items():
            item = {"instanceId": i, "categoryId": category_id}
            if all_attributes:
                item["attributes"] = all_attributes[i]  # pylint: disable=unsubscriptable-object
            info.append(item)

        body["info"] = info
        return body


class RemoteSemanticMask(SemanticMaskBase, RemoteFileMixin):
    """RemoteSemanticMask is a class for the remote semantic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the category id,
            and the value is the corresponding attributes.

    """

    _T = TypeVar("_T", bound="RemoteSemanticMask")

    @classmethod
    def from_response_body(cls: Type[_T], body: Dict[str, Any]) -> _T:
        """Loads a :class:`RemoteSemanticMask` object from a response body.

        Arguments:
            body: The response body which contains the information of a remote semantic mask,
                whose format should be like::

                    {
                        "remotePath": <str>,
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

        Returns:
            The loaded :class:`RemoteSemanticMask` object.

        """
        mask = cls(body["remotePath"])
        if "info" in body:
            mask.all_attributes = {item["categoryId"]: item["attributes"] for item in body["info"]}

        return mask


class RemoteInstanceMask(InstanceMaskBase, RemoteFileMixin):
    """RemoteInstanceMask is a class for the remote instance mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    _T = TypeVar("_T", bound="RemoteInstanceMask")

    @classmethod
    def from_response_body(cls: Type[_T], body: Dict[str, Any]) -> _T:
        """Loads a :class:`RemoteInstanceMask` object from a response body.

        Arguments:
            body: The response body which contains the information of a remote instance mask,
                whose format should be like::

                    {
                        "remotePath": <str>,
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

        Returns:
            The loaded :class:`RemoteInstanceMask` object.

        """
        mask = cls(body["remotePath"])
        if "info" in body:
            mask.all_attributes = {item["instanceId"]: item["attributes"] for item in body["info"]}

        return mask


class RemotePanopticMask(PanopticMaskBase, RemoteFileMixin):
    """RemotePanoticMask is a class for the remote panotic mask label.

    Attributes:
        all_attributes: The dict of the attributes in this mask, which key is the instance id,
            and the value is the corresponding attributes.

    """

    _T = TypeVar("_T", bound="RemotePanopticMask")

    def __init__(
        self, remote_path: str, *, _url_getter: Optional[Callable[[str], str]] = None
    ) -> None:
        PanopticMaskBase.__init__(self)
        RemoteFileMixin.__init__(self, remote_path, _url_getter=_url_getter)

    @classmethod
    def from_response_body(cls: Type[_T], body: Dict[str, Any]) -> _T:
        """Loads a :class:`RemotePanopticMask` object from a response body.

        Arguments:
            body: The response body which contains the information of a remote panoptic mask,
                whose format should be like::

                    {
                        "remotePath": <str>,
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

        Returns:
            The loaded :class:`RemotePanopticMask` object.

        """
        mask = cls(body["remotePath"])
        info = body["info"]
        mask.all_category_ids = {item["instanceId"]: item["categoryId"] for item in info}
        if "attributes" in info[0]:
            mask.all_attributes = {item["instanceId"]: item["attributes"] for item in body["info"]}

        return mask
