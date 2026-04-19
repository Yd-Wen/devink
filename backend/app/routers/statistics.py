"""统计分析路由"""

from databases import Database
from fastapi import APIRouter, Depends

from app.database import get_db
from app.depends import require_admin
from app.schemas.common import BaseResponse
from app.schemas.statistics import StatisticsVO
from app.schemas.user import LoginUserVO
from app.services.statistics import StatisticsService

router = APIRouter(
    prefix="/statistics", 
    tags=["statisticsController"]
)


@router.get("/overview", response_model=BaseResponse[StatisticsVO])
async def get_statistics(
    db: Database = Depends(get_db),
    _: LoginUserVO = Depends(require_admin),
):
    """获取系统统计数据（仅管理员）"""
    service = StatisticsService(db)
    stats = await service.get_statistics()
    return BaseResponse.success(data=stats)