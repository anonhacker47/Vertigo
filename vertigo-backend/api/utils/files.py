import os
from flask import current_app

def init_user_folders(user_id):
    base = os.path.join(current_app.config['user_path'], str(user_id))

    folders = [
        f"{base}/Avatar",
        f"{base}/Covers",
        f"{base}/Entities/Publisher",
        f"{base}/Entities/Creator",
        f"{base}/Entities/Character",
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    return base

def get_user_path(user_id, folder):
    """
    folder = "Avatar" or "Covers" OR "Entities/Publisher" OR "Entities/Creator" etc.
    """
    base = os.path.join(current_app.config["user_path"], str(user_id))
    final_path = os.path.join(base, folder)

    os.makedirs(final_path, exist_ok=True)
    return final_path