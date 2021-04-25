import os

from pymongo import MongoClient

from bot import get_bot_info

def make_connection():
    """Utility function to connect to database.

    Returns:
        instance of MongoClient.
    """
    client = MongoClient('mongodb+srv://eora_tester:' + os.environ.get('MONGO_PASS', 'password') + '@eora-test.idkwk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

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

    if db.users.find_one({'username': user['username']}):
        return None

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


def add_bot(username, token):
    """Add token to database. 

    Args:
        user: user object (TODO).
        token (str): token from request.

    Returns:
        telegram bot_id if added successfully.
    """
    db = make_connection()

    bot_info = get_bot_info(token)

    db.bots.insert_one({**bot_info, 'token': token})

    db.users.update_one({'username': username}, {'$push': {'bots': bot_info['bot_id']}})

    return bot_info['bot_id']


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


def get_bots_tokens():
    """Supplementary function for startup to get all bots.

    Returns:
        list of bots tokens.
    """
    db = make_connection()

    bots_tokens = []

    bots_in_db = db.bots.find({}, {'token': True})

    for el in bots_in_db:
        bots_tokens.append(el['token'])

    return bots_tokens