from functools import wraps
from flask import abort,request
from apifairy import arguments, response
from api.models.series import Series
from api.models.issue import Issue
import sqlalchemy as sqla
from api.app import db
from api.schemas.pagination_schema import StringPaginationSchema, paginated_collection


def _sort_key(default, default_direction, sorts):
    """The (expression, direction) this request asks for, within what the route allows.

    With ``sorts``, ``orderBy`` must be one of its keys. Without, it may name any column
    of the default key's model. Anything else is a 400, not a guess.
    """
    direction = request.args.get('orderDir')
    if direction not in ('asc', 'desc'):
        direction = default_direction
    name = request.args.get('orderBy')
    if name is None or default is None:
        return default, direction
    if sorts is not None:
        if name not in sorts:
            abort(400, f'Cannot sort by {name!r}.')
        return sorts[name], direction
    model = default.class_
    if name not in model.__table__.columns:
        abort(400, f'Cannot sort by {name!r}.')
    return getattr(model, name), direction


def paginated_response(schema, max_limit=100, order_by=None,
                       order_direction='desc',
                       pagination_schema=StringPaginationSchema,
                       sorts=None, tiebreak=None):
    """Paginate the select a view returns, ordered by the client's ``orderBy``/``orderDir``.

    ``sorts`` whitelists the ``orderBy`` names a client may send, each mapped to the column
    or expression to sort by; those sorts put empty values last whatever the direction, and
    ``tiebreak`` settles equal keys. Without ``sorts``, ``orderBy`` may name any column of
    the default key's model.
    """
    defaults = {'order_by': order_by}

    def inner(f):
        @wraps(f)
        def paginate(*args, **kwargs):
            args = list(args)
            pagination = args.pop(-1)
            order_by, direction = _sort_key(defaults['order_by'], order_direction, sorts)

            result  = f(*args, **kwargs)

            extra_meta = {}
            if isinstance(result, tuple):
                select_query, extra_meta = result
            else:
                select_query = result

            count = db.session.scalar(sqla.select(
                sqla.func.count()).select_from(select_query))

            if order_by is not None:
                if order_by is Issue.title:
                    key = sqla.func.cast(sqla.func.substr(order_by, 8), sqla.Integer())
                else:
                    key = order_by
                o = key.desc() if direction == 'desc' else key.asc()
                if sorts is not None:
                    o = sqla.nullslast(o)
                order = [o]
                if tiebreak is not None and order_by is not tiebreak:
                    order.append(tiebreak.asc())
                select_query = select_query.order_by(*order)

            limit = pagination.get('limit', max_limit)
            offset = pagination.get('offset')
            after = pagination.get('after')
            if limit > max_limit:
                limit = max_limit
            if after is not None:
                if offset is not None or order_by is None:  # pragma: no cover
                    abort(400)
                if direction != 'desc':
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

            pagination_payload = {
                'offset': offset,
                'limit': limit,
                'count': len(data),
                'total': count,  # filtered total
            }
            
            if "base_total" in extra_meta:
                pagination_payload["base_total"] = extra_meta["base_total"]
            
            return {
                'data': data,
                'pagination': pagination_payload
            }
            
        # wrap with APIFairy's arguments and response decorators
        return arguments(pagination_schema)(response(paginated_collection(
            schema, pagination_schema=pagination_schema))(paginate))

    return inner
