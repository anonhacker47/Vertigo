import sqlalchemy as sqla
from sqlalchemy import event
from datetime import datetime, timezone
from api.app import db

class Syncable:
    last_updated = sqla.Column(sqla.DateTime, index=True, 
                               default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc),
                               nullable=False)

def _log_deletion(mapper, connection, target):
    from api.models.deleted_record import DeletedRecord
    # We use a direct insert to avoid session issues during delete
    table = DeletedRecord.__table__
    connection.execute(
        table.insert().values(
            table_name=target.__tablename__,
            object_id=target.id,
            user_id=getattr(target, 'user_id', None),
            deleted_at=datetime.now(timezone.utc)
        )
    )

@event.listens_for(Syncable, 'after_delete', propagate=True)
def receive_after_delete(mapper, connection, target):
    _log_deletion(mapper, connection, target)
