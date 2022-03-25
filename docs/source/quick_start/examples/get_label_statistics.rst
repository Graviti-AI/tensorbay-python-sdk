..
 Copyright 2021 Graviti. Licensed under MIT License.
 
######################
 Get Label Statistics
######################

This topic describes the operation to get label statistics.

Label statistics of dataset could be obtained via :func:`~tensorbay.client.dataset.DatasetClientBase.get_label_statistics`
as follows:

    >>> from tensorbay import GAS
    >>> gas = GAS("YOUR_ACCESSKEY")
    >>> dataset_client = gas.get_dataset("<DATASET_NAME>")
    >>> statistics = dataset_client.get_label_statistics()
    >>> statistics
    Statistics {
        'BOX2D': {...},
        'BOX3D': {...},
        'KEYPOINTS2D': {...}
    }
 
The details of the statistics structure for the targetDataset are as follows:

.. code-block:: json

    {
        "BOX2D": {
            "quantity": 1508722,
            "categories": [
                {
                    "name": "vehicle.bike",
                    "quantity": 8425,
                    "attributes": [
                        {
                            "name": "trafficLightColor",
                            "enum": ["none", "red", "yellow"],
                            "quantities": [8420, 3, 2]
                        }
                    ]
                }
            ],
            "attributes": [
                {
                    "name": "trafficLightColor",
                    "enum": ["none", "red", "yellow", "green"],
                    "quantities": [1356224, 54481, 4107, 93910]
                }
            ]
        },
        "BOX3D": {
            "quantity": 1234
        },
        "KEYPOINTS2D":{
            "quantity": 43234,
            "categories":[
                {
                    "name": "person.person",
                    "quantity": 43234
                }
            ]
        }
    }

.. note::
   The :func:`~tensorbay.client.statistics.Statistics.dumps` of :class:`~tensorbay.client.statistics.Statistics` can dump the statistics into a dict.
