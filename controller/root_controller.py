from fastapi import APIRouter
from resp import response

router = APIRouter()


@router.get('/')
def index():
    return response.ok()


@router.get('/favicon.ico')
def favicon():
    return
