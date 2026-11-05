class TransferError(Exception):
    """A problem with an upload that the user can fix; the message is shown as it is."""


class RestoreError(TransferError):
    """The uploaded file is not a backup we can restore."""
