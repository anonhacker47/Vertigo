from functools import wraps
from flask import abort,request
from apifairy import arguments, response
from api.models.user import User
from api.models.series import Series
from api.models.issue import Issue
import sqlalchemy as sqla
from api.app import db
from api.schemas.pagination_schema import StringPaginationSchema, PaginatedCollection


def paginated_response(schema, max_limit=25, order_by=None,
                       order_direction='desc',
                       pagination_schema=StringPaginationSchema):
    def inner(f):
        @wraps(f)
        def paginate(*args, **kwargs):
            args = list(args)
            pagination = args.pop(-1)
            order_by_object = request.args.get('orderby')
            order_by_dir = request.args.get('orderdir')
            nonlocal order_by
            nonlocal order_direction
            
            if order_by_dir == 'desc':
                order_direction = 'desc'
            elif order_by_dir == 'asc': 
                order_direction = 'asc'
            print(order_direction)

            if order_by == Series.timestamp or order_by == Series.title:
                if order_by_object is not None:
                    order_by = getattr(Series, order_by_object)
            elif order_by == Issue.timestamp:
                if order_by_object is not None:
                    order_by = getattr(Issue, order_by_object)

            select_query = f(*args, **kwargs)

            print(order_by)
            if order_by is not None:
                if "Issue" in str(order_by):
                    o = sqla.func.cast(sqla.func.substr(order_by, 8), sqla.Integer()).desc() if order_direction == 'desc' else sqla.func.cast(sqla.func.substr(order_by, 8), sqla.Integer()).asc()                        # Convert the volume number to an integer for proper sorting
                else:
                    o = order_by.desc() if order_direction == 'desc' else order_by
                select_query = select_query.order_by(o)
                            # print(select_query)

                count = db.session.scalar(sqla.select(
                    sqla.func.count()).select_from(select_query))

            limit = pagination.get('limit', max_limit)
            offset = pagination.get('offset')
            after = pagination.get('after')
            if limit > max_limit:
                limit = max_limit
            if after is not None:
                if offset is not None or order_by is None:  # pragma: no cover
                    abort(400)
                if order_direction != 'desc':
                    order_condition = order_by > after
                    offset_condition = order_by <= after
                else:
                    order_condition = order_by < after
                    offset_condition = order_by >= after
                query = select_query.limit(limit).filter(order_condition)
                offset = db.session.scalar(sqla.select(
                    sqla.func.count()).select_from(select_query.filter(
                        offset_condition)))
            else:
                if offset is None:
                    offset = 0
                if offset < 0 or (count > 0 and offset >= count) or limit <= 0:
                    abort(400)

                query = select_query.limit(limit).offset(offset)

            data = db.session.scalars(query).all()
            return {'data': data, 'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(data),
                'total': count,
            }}

        # wrap with APIFairy's arguments and response decorators
        return arguments(pagination_schema)(response(PaginatedCollection(
            schema, pagination_schema=pagination_schema))(paginate))

    return inner
