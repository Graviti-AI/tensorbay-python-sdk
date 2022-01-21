#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The implementation of the Graviti type based on Pandas extensions."""


from typing import Any, Optional, Sequence, Type, Union

import numpy as np
from pandas._typing import Dtype
from pandas.api.extensions import (
    ExtensionArray,
    ExtensionDtype,
    ExtensionScalarOpsMixin,
    register_extension_dtype,
)


@register_extension_dtype
class GravitiDtype(ExtensionDtype):  # type: ignore[misc]
    """Pandas extension type for graviti."""

    @property
    def type(self) -> Type["GravitiObject"]:
        """Type for a single row of a GravitiSeries column.

        Returns:
            The GravitiObject type.

        """
        return GravitiObject

    @property
    def name(self) -> str:
        """Name of the GravitiDtype.

        Returns:
            The GravitiDtype name.

        """
        return "GravitiDtype"

    @classmethod
    def construct_array_type(cls) -> Type["GravitiSeries"]:
        """Return the array type associated with this dtype.

        Returns:
            The GravitiSeries type.

        """
        return GravitiSeries

    @classmethod
    def construct_from_string(cls, string: str) -> "GravitiDtype":
        """Construct this type from a string.

        Arguments:
            string : The name of the type, for example ``Graviti.int``.

        Return:
            Instance of the GravitiDtype.

        Raises:# flake8: noqa: F402
            TypeError: If a class cannot be constructed from this 'string'.

        """


class GravitiObject:
    """A single element in a GravitiSeries.

    GravitiObject representing a single element in a GravitiSeries, or row in a Pandas column of
    GravitiDtype.

    Arguments:
        values: Numpy ndarrays values for this instance.

    """

    def __init__(self, values: np.ndarray) -> None:
        pass

    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass


class GravitiSeries(ExtensionArray, ExtensionScalarOpsMixin):  # type: ignore[misc]
    """An ExtensionArray column of the DataFrame.

    Arguments:
        values: Numpy ndarrays values for this instance.

    """

    def __init__(self, values: np.ndarray) -> None:
        pass

    def __getitem__(self, item: Union[int, slice, np.ndarray]) -> Union["GravitiSeries", Any]:
        """Select a subset of self.

        Arguments:
            item : The select logical, There are three types:
                1. int: The position in 'self' to get.
                2. slice: A slice object, where 'start', 'stop', and 'step' are integers or None.
                3. ndarray: A 1-d boolean NumPy ndarray the same length as 'self'.

        Return:
            The selected subset.

        """

    def __setitem__(self, key: Union[int, slice, np.ndarray], value: Any) -> None:
        """Set one or more values inplace.

        Arguments:
            key : Name of the key, There are four types:
                1. scalar int
                2. ndarray of integers.
                3. boolean ndarray
                4. slice object
            value : ExtensionDtype.type, Sequence[ExtensionDtype.type], or object
                value or values to be set of ``key``.

        """

    def __len__(self) -> int:
        """Length of this array.

        Return:
            length : int

        """

    def __eq__(self, other: Any) -> Sequence[bool]:  # type: ignore[override]
        """Return for `self == other` (element-wise equality).

        Arguments:
            other: The object needed to be compare.

        """

    @classmethod
    def _from_sequence(  # pylint: disable=arguments-differ
        cls, scalars: Sequence[Any], *, dtype: Optional[Dtype] = None, copy: bool = False
    ) -> "GravitiSeries":
        """Construct a new GravitiSeries from a sequence of scalars.

        Arguments:
            scalars : Each element will be an instance of the scalar type for this
                array, ``cls.dtype.type`` or be converted into this type in this method.
            dtype : Construct for this particular dtype. This should be a Dtype
                compatible with the ExtensionArray.
            copy : If True, copy the underlying data.

        Return:
            The instance of the GravitiSeries.
        """

    @classmethod
    def _from_factorized(cls, values: np.ndarray, original: "GravitiSeries") -> Any:
        """Reconstruct an ExtensionArray after factorization.

        Arguments:
            values :An integer ndarray with the factorized values.
            original : The original ExtensionArray that factorize was called on.

        """

    @property
    def dtype(self) -> "GravitiDtype":
        """Return an instance of 'GravitiDtype'.

        Returns:
            dtype: Instance of GravitiDtype.

        """
        return GravitiDtype()

    @property
    def nbytes(self) -> int:
        """The number of bytes needed to store this object in memory.

        Return:
            number: The number of bytes needed to store.

        """

    @classmethod
    def _concat_same_type(
        cls: Type["GravitiSeries"], to_concat: Sequence["GravitiSeries"]
    ) -> "GravitiSeries":
        """Concatenate multiple array of this dtype.

        Arguments:
            to_concat : Sequence of this type.

        Return:
            The concentrated GravitiSeries

        """

    def isna(self) -> np.ndarray:
        """A 1-D array indicating if each value is missing.

        Return:
            na_values : In most cases, this should return a NumPy ndarray. For
                exceptional cases like ``SparseArray``, where returning
                an ndarray would be expensive, an ExtensionArray may be
                returned.

        """

    def take(  # pylint: disable=arguments-differ
        self, indices: Sequence[int], *, allow_fill: bool = False, fill_value: Any = None
    ) -> "GravitiSeries":
        """Take elements from an array.

        The take is called by ``Series.__getitem__``, ``.loc``,
        ``iloc``, when `indices` is a sequence of values. Additionally,
        it's called by :meth:`Series.reindex`, or any other method
        that causes realignment, with a `fill_value`.

        Arguments:
            indices : Indices to be taken.
            allow_fill : How to handle negative values in `indices`, There are three options:
                * False: negative values in `indices` indicate positional indices
                  from the right (the default). This is similar to :func:`numpy.take`.
                * True: negative values in `indices` indicate missing values.
                  These values are set to `fill_value`. Any other
                  other negative values raise a ``ValueError``.
            fill_value : Fill value to use for NA-indices when `allow_fill` is True.
                This may be ``None``, in which case the default NA value for
                the type, ``self.dtype.na_value``, is used.
                For many ExtensionArrays, there will be two representations of
                `fill_value`: a user-facing "boxed" scalar, and a low-level
                physical NA value. `fill_value` should be the user-facing version,
                and the implementation should handle translating that to the
                physical version for processing the take if necessary.

        Return:
            The GravitiSeries.

        Raises:# flake8: noqa: F402
            IndexError: When the indices are out of bounds for the array.
            ValueError: When `indices` contains negative values other than ``-1``
                and `allow_fill` is True.

        """

    def copy(self) -> "GravitiSeries":
        """Return a copy of the array.

        Return:
            The copied GravitiSerie.
        """
