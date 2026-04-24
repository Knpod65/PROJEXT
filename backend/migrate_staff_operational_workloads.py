from sqlalchemy import create_engine, inspect, text

from database import DATABASE_URL, Base
import models


def main() -> None:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    with engine.begin() as conn:
        staff_columns = {col["name"] for col in inspector.get_columns("staff_unavailability")}
        if "start_time" not in staff_columns:
            conn.execute(text("ALTER TABLE staff_unavailability ADD COLUMN start_time VARCHAR(8)"))
            print("Added staff_unavailability.start_time")
        if "end_time" not in staff_columns:
            conn.execute(text("ALTER TABLE staff_unavailability ADD COLUMN end_time VARCHAR(8)"))
            print("Added staff_unavailability.end_time")

    Base.metadata.create_all(bind=engine, tables=[models.PaperDistributionAssignment.__table__])
    print("Ensured paper_distribution_assignments table exists")


if __name__ == "__main__":
    main()
