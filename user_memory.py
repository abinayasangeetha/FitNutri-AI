user_profiles = {}
chat_history = {}


def save_profile(user_id, profile):
    user_profiles[user_id] = profile


def get_profile(user_id):
    return user_profiles.get(user_id)


def add_message(user_id, role, content):

    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append(
        {
            "role": role,
            "content": content
        }
    )


def get_history(user_id):
    return chat_history.get(user_id, [])