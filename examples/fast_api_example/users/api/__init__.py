from fastapi import APIRouter

from .create import router as create_router
from .delete import router as delete_router
from .get import router as get_router
from .list import router as list_router
from .rename_city import router as rename_city_router
from .update import router as update_router

router = APIRouter()
router.include_router(create_router)
router.include_router(list_router)
router.include_router(get_router)
router.include_router(update_router)
router.include_router(delete_router)
router.include_router(rename_city_router)

