######################
 Get Label Statistics
######################

This topic describes the get label statistics operation.

Label statistics of dataset could be obtained via :func:`~tensorbay.client.dataset.DatasetClientBase.get_label_statistics`
as follows:

    >>> from tensorbay import GAS
    >>> ACCESS_KEY = "Accesskey-*****"
    >>> gas = GAS(ACCESS_KEY)
    >>> dataset_client = gas.get_dataset("targetDataset")
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
   The method :func:`~tensorbay.client.statistics.Statistics.dumps` of :class:`~tensorbay.client.statistics.Statistics` can dump the statistics into a dict.
