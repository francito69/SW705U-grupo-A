from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/convenios", tags=["Convenios"])


@router.get(
    "",
    response_model=list[schemas.ConvenioOut],
    summary="Listar convenios activos",
    responses={200: {"description": "Convenios disponibles para registrar pacientes"}},
)
def listar_convenios(db: Session = Depends(get_db)):
    return crud.listar_convenios(db)
