import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from telegram.error import InvalidToken

from bot import start_bot
from database import *
from models import *

app = FastAPI(title='EORA Test Assignment')

ACTIVE_BOTS = {}

tags_metadata = [
    {
        'name': 'Authentication',
        'description': 'Routes for registering and authorizing users.'
    },
    {
        'name': 'Bots Interaction',
        'description': 'Routes to interact with bots routes'
    }
]

SECRET_KEY = os.environ.get('SECRET_KEY', '45a2c62837898dc6d13cafa11521b67befef713456b8868cdb3410e0475e35ef')
TOKEN_EXPIRATION = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(form_password, hashed_password):
    return pwd_context.verify(form_password, hashed_password)


def hash_password(form_password):
    return pwd_context.hash(form_password)


def generate_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION)
    to_encode.update({'exp': expiration})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail='invalid_token')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('user')

        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_dict = get_user(username)

    if not user_dict:
        raise credentials_exception

    return UserInDB(**user_dict)


@app.post('/login/', tags=['Authentication'])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = get_user(form_data.username)

    if not user_dict:
        raise HTTPException(status_code=400, detail='wrong_user_password')

    user = UserInDB(**user_dict)

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail='wrong_user_password')

    access_token = generate_token(data={'user': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/register/', tags=['Authentication'])
def register(user: User):
    user.password = hash_password(user.password)

    if add_user(user.dict()) is None:
        raise HTTPException(status_code=400, detail='user_exists')

    access_token = generate_token(data={'user': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/bot/', tags=['Bots Interaction'])
def new_bot(token: str, current_user: str = Depends(get_current_user)):

    if current_user.bots_limit():
        raise HTTPException(status_code=403, detail='bots_limit_reached')

    try:
        updater = start_bot(token)
    except InvalidToken:
        raise HTTPException(status_code=400, detail='invalid_token')

    bot_id = add_bot(current_user.username, token)

    return {'status': 'ok'}



@app.delete('/bot/{bot_id}/', tags=['Bots Interaction'])
def delete_bot(bot_id: int, current_user: str = Depends(get_current_user)):
    if not current_user.has_bot(bot_id):
        raise HTTPException(status_code=400, detail='invalid_id')

    result = remove_bot(current_user.username, bot_id)

    return {'status': 'ok'}


@app.get('/bots/', tags=['Bots Interaction'])
def get_bots(current_user: str = Depends(get_current_user)):
    return {'bots': load_bots(current_user.username)}