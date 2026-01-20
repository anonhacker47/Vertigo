import sqlalchemy as sqla
from datetime import datetime, timezone
from api.app import db

class DeletedRecord(db.Model):
    __tablename__ = 'deleted_records'

    id = sqla.Column(sqla.Integer, primary_key=True)
    table_name = sqla.Column(sqla.String(64), index=True, nullable=False)
    object_id = sqla.Column(sqla.Integer, index=True, nullable=False)
    deleted_at = sqla.Column(sqla.DateTime, index=True, 
                             default=lambda: datetime.now(timezone.utc),
                             nullable=False)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey("users.id"), index=True)

    def __repr__(self):
        return f'<DeletedRecord {self.table_name}:{self.object_id}>'
