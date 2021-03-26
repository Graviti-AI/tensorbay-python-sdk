##########
 Examples
##########

| We write examples for labels in :ref:`reference/label_format:Label Format`.
| :numref:`Table. %s <examples_table>` lists the examples, including their data types and label types.

.. _examples_table:

.. table:: Examples
   :align: center
   :widths: auto

   =====================================================================================  ====================================================================================
   Examples                                                                               Description
   =====================================================================================  ====================================================================================
   :ref:`Dataset Management: Dogs vs Cats <examples/DogsVsCats:Dogs vs Cats>`             | This example describes how to manage `Dogs vs Cats`_ dataset,
                                                                                          | which is an image dataset with :ref:`reference/label_format:Classification` label.
   :ref:`Dataset Management: 20 Newsgroups <examples/NewsGroups20:20 Newsgroups>`         | This example describes how to manage `20 Newsgroups`_
                                                                                          | dataset, which is a text dataset with :ref:`reference/label_format:Classification` label.
   :ref:`Dataset Management: BSTLD <examples/BSTLD:BSTLD>`                                | This example describes how to manage `BSTLD`_ dataset,
                                                                                          | which is an image dataset with :ref:`reference/label_format:Box2D` label.
   :ref:`Dataset Management: Neolix OD <examples/NeolixOD:Neolix OD>`                     | This example describes how to manage `Neolix OD`_ dataset,
                                                                                          | which is a Point Cloud dataset with :ref:`reference/label_format:Box3D` label.
   :ref:`Dataset Management: LeedsSportsPose <examples/LeedsSportsPose:LeedsSportsPose>`  | This example describes how to manage `LeedsSportsPose`_
                                                                                          | dataset, which is an image dataset with :ref:`reference/label_format:Keypoints2D` label.
   :ref:`Dataset Management: THCHS-30 <examples/THCHS30:THCHS-30>`                        | This example describes how to manage `THCHS-30`_ dataset,
                                                                                          | which is an audio dataset with :ref:`reference/label_format:Sentence` label.
   :ref:`Read "Dataset" Class: BSTLD <examples/read_dataset_class:Read "Dataset" Class>`  | This example describes how to read `BSTLD`_ dataset
                                                                                          | when it has been organized by a :class:`~tensorbay.dataset.dataset.Dataset` class.
   =====================================================================================  ====================================================================================

.. _Dogs vs Cats: https://gas.graviti.cn/dataset/data-decorators/DogsVsCats
.. _20 Newsgroups: https://www.graviti.cn/open-datasets/data-decorators/Newsgroups20
.. _BSTLD: https://www.graviti.cn/open-datasets/data-decorators/BSTLD
.. _Neolix OD: https://www.graviti.cn/open-datasets/data-decorators/NeolixOD
.. _LeedsSportsPose: https://www.graviti.cn/open-datasets/data-decorators/LeedsSportsPose
.. _THCHS-30: https://www.graviti.cn/open-datasets/data-decorators/THCHS30


.. toctree::
   :hidden:
   :maxdepth: 1

   ../examples/DogsVsCats
   ../examples/BSTLD
   ../examples/LeedsSportsPose
   ../examples/NeolixOD
   ../examples/THCHS30
   ../examples/Newsgroups20
   ../examples/read_dataset_class
