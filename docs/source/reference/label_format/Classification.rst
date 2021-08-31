****************
 Classification
****************

Classification is to classify data into different categories.

It is the annotation for the entire file,
so each data can only be assigned with one classification label.

Classification labels applies to different types of data, such as images and texts.

The structure of one classification label is like::

        {
            "category": <str>
            "attributes": {
                <key>: <value>
                ...
                ...
            }
        }



To create a :class:`~tensorbay.label.label_classification.Classification` label:

    >>> from tensorbay.label import Classification
    >>> classification_label = Classification(
    ... category="data_category",
    ... attributes={"attribute_name": "attribute_value"}
    ... )
    >>> classification_label
    Classification(
      (category): 'data_category',
      (attributes): {...}
    )


Classification.category
=======================

The category of the entire data file.
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

Classification.attributes
=========================

The attributes of the entire data file.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

.. note::

   There must be either a category or attributes in one classification label.

ClassificationSubcatalog
========================

Before adding the classification label to data,
:class:`~tensorbay.label.label_classification.ClassificationSubcatalog` should be defined.

:class:`~tensorbay.label.label_classification.ClassificationSubcatalog`
has categories and attributes information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information` and
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` for details.

To add a :class:`~tensorbay.label.label_classification.Classification` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.classification = classification_label

.. note::

   One data can only have one classification label.

