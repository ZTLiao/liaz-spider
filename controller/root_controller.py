from fastapi import APIRouter
from resp import response

router = APIRouter()


@router.get('/')
def get_index():
    return response.ok()


@router.head('/')
def head_index():
    return response.ok()


@router.get('/favicon.ico')
def favicon():
    return
