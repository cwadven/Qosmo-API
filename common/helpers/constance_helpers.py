from common.dtos.helper_dtos import (
    ConstanceDetailType,
    ConstanceType,
    MapCategoryConstanceType
)
from map.models import Category


class ConstanceTypeHelper(object):
    def get_constance_types(self) -> list[ConstanceType]:
        return self._get_constance_types()

    def _get_constance_types(self) -> list[ConstanceType]:
        raise NotImplementedError


class HomeMapCategoryConstanceTypeHelper(ConstanceTypeHelper):
    @staticmethod
    def _get_active_categories() -> list[Category]:
        return Category.objects.filter(
            is_deleted=False
        )

    def _get_constance_types(self) -> list[ConstanceType]:
        return [
            MapCategoryConstanceType(
                id=category.id,
                name=category.name,
                display_name=category.name,
                icon_image=category.icon,
            )
            for category in self._get_active_categories()
        ]


CONSTANCE_TYPE_HELPER_MAPPER = {
    'home_map_category': HomeMapCategoryConstanceTypeHelper(),
}


class ConstanceDetailTypeHelper(object):
    def get_constance_detail_types(self) -> list[ConstanceDetailType]:
        raise NotImplementedError
