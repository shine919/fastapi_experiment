import pytz
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from todo.schema import AnalyticTodoResponse


async def check_timezone(timezone: str):
    print("w")
    try:
        tz = pytz.timezone(timezone)
        print(tz, "HELLOW")
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timezone {e}")


async def get_analysis_from_todos(timezone: str, session: AsyncSession):
    await check_timezone(timezone)
    total_stats_query = text("""SELECT COUNT(*)                                      as total,
                                       COUNT(CASE WHEN completed = true THEN 1 END)  AS completed_count,
                                       COUNT(CASE WHEN completed = false THEN 1 END) AS not_completed_count,
                                       AVG(CASE
                                               WHEN completed_at is not null
                                                   THEN EXTRACT(EPOCH FROM (created_at - completed_at)) / 3600
                                               else 0 END)::float                    AS avg_completed_time
                                FROM todo""")

    weekday_stats_query = text(
        """SELECT TO_CHAR(created_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone, 'Day') as weekday_distribution,
                  COUNT(*)                                                            as count_of_day
           FROM todo
           GROUP BY TO_CHAR(created_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone, 'Day'), EXTRACT(DOW FROM created_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone)"""
    )

    total_stats_result = await session.execute(total_stats_query)
    weekday_stats_result = await session.execute(weekday_stats_query, {"timezone": timezone})

    total_stats = total_stats_result.first()._asdict()
    weekday_stats = weekday_stats_result.all()

    response = AnalyticTodoResponse(**total_stats, weekday_distribution={row[0]: row[1] for row in weekday_stats})

    return response
