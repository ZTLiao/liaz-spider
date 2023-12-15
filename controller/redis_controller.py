from fastapi import APIRouter

from resp import response

router = APIRouter()


@router.get('/habu')
def habu():
    return response.ok()
