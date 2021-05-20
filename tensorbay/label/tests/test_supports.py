import pytest

from .. import CategoryInfo, KeypointsInfo
from ..supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


class TestCategoryInfo:
    def test_loads(self):
        contents = {"name": "cat", "description": "This is an exmaple of test"}
        category_info = CategoryInfo.loads(contents)
        assert category_info.name == "cat"
        assert category_info.description == "This is an exmaple of test"

    def test_eq(self):
        category_info1 = CategoryInfo(name="cat", description="This is a cat")
        category_info2 = CategoryInfo(name="cat", description="This is a cat")
        category_info3 = CategoryInfo(name="dog", description="This is a dog")
        assert category_info1 == category_info2
        assert category_info1 != category_info3

    def test_dumps(self):
        category_info = CategoryInfo(name="cat", description="This is an exmaple of test")
        assert category_info.dumps() == {"name": "cat", "description": "This is an exmaple of test"}


class TestKeypointsInfo:
    @pytest.mark.parametrize("visible", ["TERNARY", "BINARY"])
    def test_init(self, visible):
        number = 4
        names = ["1", "2", "3", "4"]
        skeleton = [(1, 2), (1, 4)]
        parent_categories = "string"
        description = "Testing"

        with pytest.raises(ValueError):
            KeypointsInfo(
                number=number,
                names=names,
                skeleton=skeleton,
                visible="1",
                parent_categories=parent_categories,
                description=description,
            )

        keypoints_info = KeypointsInfo(
            number=number,
            names=names,
            skeleton=skeleton,
            visible=visible,
            parent_categories=parent_categories,
            description=description,
        )

        assert keypoints_info.number == number
        assert keypoints_info.names == names
        assert keypoints_info.skeleton == skeleton
        assert keypoints_info.visible == visible
        assert keypoints_info.parent_categories == [parent_categories]
        assert keypoints_info.description == description

    def test_eq(self):
        keypoints_info1 = KeypointsInfo(
            number=3,
            names=["a", "b", "c"],
            skeleton=[[1, 2], [2, 3]],
            visible="binary",
            parent_categories=["c1", "c2"],
        )
        keypoints_info2 = KeypointsInfo(
            number=3,
            names=["a", "b", "c"],
            skeleton=[[1, 2], [2, 3]],
            visible="binary",
            parent_categories=["c1", "c2"],
        )
        keypoints_info3 = KeypointsInfo(
            number=3,
            names=["a", "b", "c"],
            skeleton=[[2, 3], [1, 2]],
            visible="binary",
            parent_categories=["c2", "c1"],
        )

        assert keypoints_info1 == keypoints_info2
        assert keypoints_info1 != keypoints_info3

    def test_loads(self, keypoints_info_data):
        keypoints_info = KeypointsInfo.loads(keypoints_info_data)

        assert keypoints_info.number == keypoints_info_data["number"]
        assert keypoints_info.names == keypoints_info_data["names"]
        assert keypoints_info.skeleton == keypoints_info_data["skeleton"]
        assert keypoints_info.visible == keypoints_info_data["visible"]
        assert keypoints_info.parent_categories == keypoints_info_data["parentCategories"]
        assert keypoints_info.description == keypoints_info_data["description"]

    def test_number(self):
        keypoints_info = KeypointsInfo(number=5)
        assert keypoints_info.number == 5

    def test_dumps(self, keypoints_info_data):
        number = keypoints_info_data["number"]
        names = keypoints_info_data["names"]
        skeleton = keypoints_info_data["skeleton"]
        visible = keypoints_info_data["visible"]
        parent_categories = keypoints_info_data["parentCategories"]
        description = keypoints_info_data["description"]

        keypoints_info = KeypointsInfo(
            number=number,
            names=names,
            skeleton=skeleton,
            visible=visible,
            parent_categories=parent_categories,
            description=description,
        )

        assert keypoints_info.dumps() == keypoints_info_data


class TestIsTrackingMixin:
    def test_init(self):
        assert IsTrackingMixin().is_tracking == False
        assert IsTrackingMixin(True).is_tracking == True

    def test_eq(self):
        support_is_tracking1 = IsTrackingMixin()
        support_is_tracking2 = IsTrackingMixin()
        support_is_tracking3 = IsTrackingMixin(True)

        assert support_is_tracking1 == support_is_tracking2
        assert support_is_tracking1 != support_is_tracking3

    def test_loads(self, is_tracking_data):
        support_is_tracking = IsTrackingMixin()
        support_is_tracking._loads(contents={"isTracking": is_tracking_data})
        assert support_is_tracking.is_tracking == is_tracking_data

    def test_dumps(self, is_tracking_data):
        support_is_tracking = IsTrackingMixin(is_tracking_data)
        assert (
            support_is_tracking._dumps() == {"isTracking": is_tracking_data}
        ) == is_tracking_data


class TestCategoriesMixin:
    def test_loads(self, categories_catalog_data):
        support_categories = CategoriesMixin()
        support_categories._loads(
            contents={"categories": categories_catalog_data, "categoryDelimiter": "."}
        )
        assert support_categories.category_delimiter == "."

        for category in categories_catalog_data:
            support_categorie_0 = support_categories.categories[category["name"]]
            assert support_categorie_0.name == category["name"]
            assert support_categorie_0.description == category["description"]

    def test_get_category_to_index(self, categories_catalog_data):
        support_categories = CategoriesMixin()
        support_categories._loads(contents={"categories": categories_catalog_data})
        assert support_categories.get_category_to_index() == {"0": 0, "1": 1}

    def test_get_index_to_category(self, categories_catalog_data):
        support_categories = CategoriesMixin()
        support_categories._loads(contents={"categories": categories_catalog_data})
        assert support_categories.get_index_to_category() == {0: "0", 1: "1"}

    def test_eq(self):
        contents1 = {
            "categories": [
                {
                    "name": "Test",
                }
            ],
            "categoryDelimiter": ".",
        }
        contents2 = {
            "categories": [
                {
                    "name": "Test",
                }
            ],
            "categoryDelimiter": "-",
        }

        support_categories_1 = CategoriesMixin()
        support_categories_1._loads(contents1)

        support_categories_2 = CategoriesMixin()
        support_categories_2._loads(contents1)

        support_categories_3 = CategoriesMixin()
        support_categories_3._loads(contents2)

        assert support_categories_1 == support_categories_2
        assert support_categories_1 != support_categories_3

    def test_add_category(self):
        support_categories = CategoriesMixin()
        name = "Test"
        description = "This is a test"
        support_categories.add_category(name=name, description=description)

        assert support_categories.categories["Test"].name == name
        assert support_categories.categories["Test"].description == description

    def test_dumps(self, categories_catalog_data):
        support_categories = CategoriesMixin()
        name_1 = categories_catalog_data[0]["name"]
        name_2 = categories_catalog_data[1]["name"]
        description = categories_catalog_data[0]["description"]
        support_categories.add_category(name=name_1, description=description)
        support_categories.add_category(name=name_2, description=description)
        support_categories.category_delimiter = "."

        assert support_categories._dumps() == {
            "categories": categories_catalog_data,
            "categoryDelimiter": ".",
        }


class TestAttributesMixin:
    def test_loads(self, attributes_catalog_data):
        support_attributes = AttributesMixin()
        support_attributes._loads(contents={"attributes": attributes_catalog_data})
        gender = support_attributes.attributes["gender"]
        occluded = support_attributes.attributes["occluded"]

        assert gender.name == attributes_catalog_data[0]["name"]
        assert gender.enum == attributes_catalog_data[0]["enum"]

        assert occluded.type == attributes_catalog_data[1]["type"]
        assert occluded.minimum == attributes_catalog_data[1]["minimum"]
        assert occluded.maximum == attributes_catalog_data[1]["maximum"]

    def test_eq(self):
        contents1 = {
            "attributes": [
                {"name": "occluded", "enum": [1, 2, 3, 4, 5]},
            ]
        }
        contents2 = {
            "attributes": [
                {"name": "truncated", "enum": [1, 2, 3, 4, 5]},
            ]
        }

        support_attributes_1 = AttributesMixin()
        support_attributes_1._loads(contents=contents1)

        support_attributes_2 = AttributesMixin()
        support_attributes_2._loads(contents=contents1)

        support_attributes_3 = AttributesMixin()
        support_attributes_3._loads(contents=contents2)

        assert support_attributes_1 == support_attributes_2
        assert support_attributes_1 != support_attributes_3

    def test_add_attribute(self):
        name = "Test"
        type_ = "number"
        enum = [1.1, 2.2, 3.3]
        minimum = 1.1
        maximum = 3.3

        support_attributes = AttributesMixin()
        support_attributes.add_attribute(
            name=name, type_=type_, enum=enum, minimum=minimum, maximum=maximum
        )

        assert support_attributes.attributes["Test"].name == name
        assert support_attributes.attributes["Test"].type == type_
        assert support_attributes.attributes["Test"].enum == enum
        assert support_attributes.attributes["Test"].minimum == minimum
        assert support_attributes.attributes["Test"].maximum == maximum

    def test_dumps(self, attributes, attributes_catalog_data):
        support_attributes = AttributesMixin()
        support_attributes.attributes = attributes

        assert support_attributes._dumps() == {"attributes": attributes_catalog_data}
