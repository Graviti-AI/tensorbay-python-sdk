..
 Copyright 2021 Graviti. Licensed under MIT License.
 
******************************
 Common Subcatalog Properties
******************************

Before creating a label or adding a label to data,
it's necessary to define the annotation rules of the specific label type inside the dataset.
This task is done by subcatalog.

Different label types have different subcatalog classes.

Take :class:`~tensorbay.label.label_box.Box2DSubcatalog` as an example
to describe some common features of subcatalog.

   >>> from tensorbay.label import Box2DSubcatalog
   >>> box2d_subcatalog = Box2DSubcatalog(is_tracking=True)
   >>> box2d_subcatalog
   Box2DSubcatalog(
      (is_tracking): True
   )

tracking information
====================

If the label of this type in the dataset has the information of instance IDs,
then the subcatalog should set a flag to show its support for tracking information.

Pass ``True`` to the ``is_tracking`` parameter while creating the subcatalog,
or set the ``is_tracking`` attr after initialization.

   >>> box2d_subcatalog.is_tracking = True

category information
====================

common category information
---------------------------

If the label of this type in the dataset has category,
then the subcatalog should contain all the optional categories.

Each :ref:`reference/label_format/CommonLabelProperties:category` of a label
appeared in the dataset should be within the categories of the subcatalog.

Common category information can be added to the most subcatalogs except for mask subcatalogs.

    >>> box2d_subcatalog.add_category(name="cat", description="The Flerken")
    >>> box2d_subcatalog.categories
    NameList [
      CategoryInfo("cat")
    ]

:class:`~tensorbay.label.supports.CategoryInfo` is used to describe
a :ref:`reference/label_format/CommonLabelProperties:category`.
See details in :class:`~tensorbay.label.supports.CategoryInfo`.

mask category information
-------------------------

If the mask label in the dataset has category information,
then the subcatalog should contain all the optional mask categories.

MaskCategory information can be added to the mask subcatalog.

Different from common category, mask category information must have ``category_id`` which
is the pixel value of this category in all mask images.

    >>> semantic_mask_subcatalog.add_category(name="cat", category_id=1, description="Ragdoll")
    >>> semantic_mask_subcatalog.categories
    NameList [
      MaskCategoryInfo("cat")(...)
    ]

:class:`~tensorbay.label.supports.MaskCategoryInfo` is used to describe the category information of pixels in the mask image.
See details in :class:`~tensorbay.label.supports.MaskCategoryInfo`.

attributes information
======================

If the label of this type in the dataset has attributes,
then the subcatalog should contain all the rules for different attributes.

Each :ref:`reference/label_format/CommonLabelProperties:attributes` of a label
appeared in the dataset should follow the rules set in the attributes of the subcatalog.

Attribute information ca be added to the subcatalog.

    >>> box2d_subcatalog.add_attribute(
    ... name="<SUBCATALOG_ATTRIBUTE_NAME>",
    ... type_="number",
    ... maximum=100,
    ... minimum=0,
    ... description="<SUBCATALOG_ATTRIBUTE_DESCRIPTION>"
    ... )
    >>> box2d_subcatalog.attributes
    NameList [
      AttributeInfo("<SUBCATALOG_ATTRIBUTE_NAME>")(...)
    ]

:class:`~tensorbay.label.attributes.AttributeInfo` is used to describe the rules of an
:ref:`reference/label_format/CommonLabelProperties:attributes`, which refers to the `Json schema`_ method.

See details in :class:`~tensorbay.label.attributes.AttributeInfo`.

.. _Json schema: https://json-schema.org/

Other unique subcatalog features will be explained in the corresponding label type section.
