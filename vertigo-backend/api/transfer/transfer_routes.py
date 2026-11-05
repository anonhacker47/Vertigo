from apifairy import authenticate, other_responses
from flask import Blueprint, abort, jsonify, request, send_file

from api.transfer import backup, restore, runs, spreadsheet
from api.transfer.errors import TransferError
from api.utils.auth import token_auth

transfer = Blueprint('transfer', __name__)


def _upload():
    file = request.files.get('file')
    if file is None or not file.filename:
        abort(400, 'Choose a file to upload.')
    return file


@transfer.route('/export_data', methods=['GET'])
@authenticate(token_auth)
def export_data():
    """Download the collection as an .xlsx workbook with Series, Issues and Stats sheets."""
    user = token_auth.current_user()
    return send_file(
        spreadsheet.build_workbook(user), as_attachment=True,
        download_name=f'vertigo-collection-{user.username}.xlsx', mimetype=spreadsheet.XLSX_MIME)


@transfer.route('/backup', methods=['GET'])
@authenticate(token_auth)
def download_backup():
    """Download a restorable backup: a zip with backup.json and every image."""
    user = token_auth.current_user()
    fileobj, filename = backup.build(user)
    return send_file(fileobj, as_attachment=True, download_name=filename, mimetype='application/zip')


@transfer.route('/restore', methods=['POST'])
@authenticate(token_auth)
@other_responses({400: 'Not a backup we can restore',
                  409: 'The account already has data; send mode=merge or mode=replace'})
def restore_backup():
    """Restore a backup zip (multipart file). A full account needs mode=merge or mode=replace. Answers 202 with a run to poll."""
    user = token_auth.current_user()
    mode = (request.form.get('mode') or '').strip().lower() or None
    if mode is not None and mode not in restore.MODES:
        abort(400, 'mode must be "merge" or "replace".')
    try:
        path, info = restore.stage(_upload())
    except TransferError as exc:
        abort(400, str(exc))

    if mode is None and restore.has_collection(user):
        restore.discard(path)
        return jsonify({
            'error': 'account_not_empty',
            'message': 'Your collection already has data. Merge the backup into it or replace it.',
            'backup': info,
            'account': restore.account_counts(user),
        }), 409

    label = f'Restore backup ({info["series"]} series)'
    run = runs.create('restore', label, user.id,
                      work=lambda run: restore.apply(run, path, user.id, mode),
                      total=info['series'] + info['issues'] + info['entities'],
                      cleanup=lambda: restore.discard(path))
    runs.start(run)
    return jsonify(run.to_dict()), 202


@transfer.route('/transfer/runs/<run_id>', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: 'No such run'})
def get_run(run_id):
    """Progress of a restore started by the current user."""
    run = runs.get(run_id, token_auth.current_user().id) or abort(404)
    return jsonify(run.to_dict())
