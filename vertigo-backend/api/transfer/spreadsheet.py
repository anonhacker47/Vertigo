"""The spreadsheet export: a Series sheet, an Issues sheet and a Stats sheet."""
import io

import pandas as pd
from babel.numbers import get_currency_symbol
from sqlalchemy.orm import selectinload

from api import db, media
from api.models.series import Series
from api.transfer import excel_format

XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

def _yes_no(value) -> str:
    return 'Yes' if value else 'No'


def _custom_title(issue):
    title = (issue.title or '').strip()
    return title if title and title != str(issue.number) else None


def collection_rows(user):
    """``(series rows, issue rows, purchase column header)`` for the export sheets."""
    series_list = db.session.scalars(
        user.series_select().options(selectinload(Series.issue)).order_by(Series.title)).all()
    symbol = get_currency_symbol(user.preferred_currency or 'USD')
    purchase_field = f'Purchase Cost ({symbol})'
    series_rows, issue_rows = [], []
    for s in series_list:
        issues = sorted(s.issue, key=lambda i: (i.number, i.id))
        missing = [str(i.number) for i in issues if not i.is_owned]
        series_rows.append({
            'Thumbnail': s.thumbnail,
            'Series Title': s.title,
            'Publisher': ', '.join(p.title for p in s.publisher),
            'Genre': ', '.join(g.title for g in s.genre),
            'Creators': ', '.join(c.title for c in s.creator),
            'Characters': ', '.join(c.title for c in s.character),
            'Format': s.series_format,
            'Manga': _yes_no(s.manga),
            'Description': s.description,
            'Notes': s.notes,
            'Issue Count': s.issue_count,
            'Owned Count': f'{s.owned_count} / {s.issue_count}',
            'Missing Issues': ', '.join(missing) if missing else 'None',
            'Read Count': f'{s.read_count} / {s.issue_count}',
            'Rating': s.user_rating,
            purchase_field: s.purchase_cost,
            'Metron ID': s.metron_id,
        })
        for i in issues:
            issue_rows.append({
                'Series Title': s.title,
                'Issue Number': i.number,
                'Issue Title': _custom_title(i),
                'Owned Already?': _yes_no(i.is_owned),
                'Read Already?': _yes_no(i.is_read),
                'Bought Price': i.bought_price,
                'Bought Date': i.bought_date,
                'Read Date': i.read_date,
                'Cover Date': i.cover_date,
                'Rating': i.user_rating,
                'Notes': i.notes,
                'Metron ID': i.metron_id,
            })
    return series_rows, issue_rows, purchase_field


def build_workbook(user) -> io.BytesIO:
    """The .xlsx export: Series, Issues and Stats sheets, formatted."""
    series_rows, issue_rows, _ = collection_rows(user)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_series = pd.DataFrame(series_rows)
        df_issues = pd.DataFrame(issue_rows)
        df_series.to_excel(writer, index=False, sheet_name='Series')
        df_issues.to_excel(writer, index=False, sheet_name='Issues')
        if not df_series.empty:
            excel_format.format_series_sheet(
                writer.book['Series'], df_series, lambda value: media.resolve(user.id, value))
        if not df_issues.empty:
            excel_format.format_issues_sheet(writer.book['Issues'], df_issues)
        excel_format.create_stats_sheet(writer.book, df_series, df_issues)
    output.seek(0)
    return output
