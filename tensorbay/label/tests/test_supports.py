import pytest

from tensorbay.label import CategoryInfo, KeypointsInfo, MaskCategoryInfo
from tensorbay.label.supports import (
    AttributesMixin,
    CategoriesMixin,
    IsTrackingMixin,
    MaskCategoriesMixin,
)


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


class TestMaskCategoryInfo:
    def test_loads(self):
        contents = {"name": "cat", "description": "This is an exmaple of test", "categoryId": 1}
        mask_category_info = MaskCategoryInfo.loads(contents)
        assert mask_category_info.name == "cat"
        assert mask_category_info.description == "This is an exmaple of test"
        assert mask_category_info.category_id == 1

    def test_eq(self):
        mask_category_info1 = MaskCategoryInfo(name="cat", description="test", category_id=1)
        mask_category_info2 = MaskCategoryInfo(name="cat", description="test", category_id=1)
        mask_category_info3 = MaskCategoryInfo(name="dog", description="test", category_id=3)
        assert mask_category_info1 == mask_category_info2
        assert mask_category_info1 != mask_category_info3

    def test_dumps(self):
        category_info = MaskCategoryInfo(name="cat", description="test", category_id=1)
        assert category_info.dumps() == {"name": "cat", "description": "test", "categoryId": 1}


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


class TestMaskCategoriesMixin:
    def test_loads(self, mask_categories_catalog_data):
        support_categories = MaskCategoriesMixin()
        support_categories._loads(
            contents={"categories": mask_categories_catalog_data, "categoryDelimiter": "."}
        )
        assert support_categories.category_delimiter == "."

        for category in mask_categories_catalog_data:
            support_categorie_0 = support_categories.categories[category["name"]]
            assert support_categorie_0.name == category["name"]
            assert support_categorie_0.description == category["description"]
            assert support_categorie_0.category_id == category["categoryId"]

    def test_get_category_to_index(self, mask_categories_catalog_data):
        support_categories = MaskCategoriesMixin()
        support_categories._loads(contents={"categories": mask_categories_catalog_data})
        assert support_categories.get_category_to_index() == {"cat": 0, "dog": 10}

    def test_get_index_to_category(self, mask_categories_catalog_data):
        support_categories = MaskCategoriesMixin()
        support_categories._loads(contents={"categories": mask_categories_catalog_data})
        assert support_categories.get_index_to_category() == {0: "cat", 10: "dog"}

    def test_eq(self):
        contents1 = {"categories": [{"name": "Test", "categoryId": 0}]}
        contents2 = {"categories": [{"name": "Test", "categoryId": 1}]}

        support_categories_1 = MaskCategoriesMixin()
        support_categories_1._loads(contents1)

        support_categories_2 = MaskCategoriesMixin()
        support_categories_2._loads(contents1)

        support_categories_3 = MaskCategoriesMixin()
        support_categories_3._loads(contents2)

        assert support_categories_1 == support_categories_2
        assert support_categories_1 != support_categories_3

    def test_add_category(self):
        support_categories = MaskCategoriesMixin()
        name = "Test"
        description = "This is a test"
        category_id = 1
        support_categories.add_category(name=name, description=description, category_id=category_id)

        assert support_categories.categories["Test"].name == name
        assert support_categories.categories["Test"].description == description
        assert support_categories.categories["Test"].category_id == category_id

    def test_dumps(self, mask_categories_catalog_data):
        support_categories = MaskCategoriesMixin()
        name_1 = mask_categories_catalog_data[0]["name"]
        name_2 = mask_categories_catalog_data[1]["name"]
        description = mask_categories_catalog_data[0]["description"]
        category_id_1 = mask_categories_catalog_data[0]["categoryId"]
        category_id_2 = mask_categories_catalog_data[1]["categoryId"]

        support_categories.add_category(name_1, category_id_1, description)
        support_categories.add_category(name_2, category_id_2, description)

        assert support_categories._dumps() == {"categories": mask_categories_catalog_data}


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
