from pymongo import MongoClient

from bot import get_bot_info

def make_connection():
    """Utility function to connect to database.

    Returns:
        instance of MongoClient.
    """
    client = MongoClient('127.0.0.1', 27017)

    db = client.eora
    return db


def add_user(user):
    """Add user to database from register endpoint.

    Args:
        user: data of user.

    Returns:
        user_id.
    """
    db = make_connection()

    user_id = db.users.insert_one({**user, 'bots': []}).inserted_id

    return user_id


def get_user(username):
    """Get user by username.

    Args:
        username (str)

    Returns:
        user instance from mongo.
    """
    db = make_connection()

    user = db.users.find_one({'username': username}, {'_id': False})

    return user


def check_max_bots(username):
    """Check if bots amount is maximum for given user.

    Args:
        user: user object (TODO)

    Returns:
        True or False depending on result.
    """
    db = make_connection()

    bots = db.users.find_one({'username': username})['bots']
    return len(bots) >= 5


def add_bot(username, token):
    """Add token to database. 

    Args:
        user: user object (TODO).
        token (str): token from request.

    Returns:
        "ok" if added successfully. 
        "bots_limit" if 5 bots already added.
    """
    db = make_connection()

    bot_info = get_bot_info(token)

    bot_id = db.bots.insert_one({**bot_info, 'token': token}).inserted_id

    db.users.update_one({'username': username}, {'$push': {'bots': bot_info['bot_id']}})

    return bot_id


def load_bots(user):
    """Get list of bots of specific user.

    Args:
        user: user object (TODO).
    
    Returns:
        list of bots info.
    """
    db = make_connection()

    bot_ids = db.users.find_one({'username': user})['bots']

    print(bot_ids)

    bots = []

    for bot_id in bot_ids:
        print(db.bots.find_one({'bot_id': bot_id}, {'_id': False}))
        bots.append(db.bots.find_one({'bot_id': bot_id}, {'_id': False}))

    return bots


def remove_bot(username, bot_id):
    """Remove bot from user list.

    Args:
        username (str): username of targeted user.
        bot_id (int): id of bot to be removed.

    Returns:
        bot_id if removed successfully, None otherwise.
    """
    db = make_connection()

    user = db.users.find_one({'username': username})

    if bot_id in user['bots']:
        db.users.update_one({'username': username}, {'$pull': {'bots': bot_id}})
        db.bots.remove({'bot_id': bot_id})
        return bot_id

    return None


def user_has_bot(username, bot_id):
    """Check if requested bot is added by user.

    Args:
        username(str): username of requested user.
        bot_id (int): id of requested bot.

    Returns:
        True or False depending on whether such bot is added by user or not.
    """
    db = make_connection()

    user_bots = db.users.find_one({'username': username})['bots']
    return bot_id in user_bots