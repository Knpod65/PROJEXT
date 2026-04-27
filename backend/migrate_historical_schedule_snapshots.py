from sqlalchemy import text

from database import Base, engine
import models


def main() -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS historical_distribution_slots"))
        conn.execute(text("DROP TABLE IF EXISTS historical_schedule_invigilators"))
        conn.execute(text("DROP TABLE IF EXISTS historical_schedule_entries"))
        conn.execute(text("DROP TABLE IF EXISTS historical_schedule_batches"))

    Base.metadata.create_all(
        bind=engine,
        tables=[
            models.HistoricalScheduleBatch.__table__,
            models.HistoricalScheduleEntry.__table__,
            models.HistoricalScheduleInvigilator.__table__,
            models.HistoricalDistributionSlot.__table__,
        ],
    )
    print("Rebuilt historical schedule snapshot tables")


if __name__ == "__main__":
    main()
