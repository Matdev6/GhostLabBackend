from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
import os

from app.db.database import get_db
from app.models.beats import Beats
from app.schemas.beats import BeatsRead, BeatsCreate

router = APIRouter()



@router.post("/beats/", response_model=BeatsRead)
async def create_beat(
    name: str = Form(...),
    exclusive: bool = Form(...),
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    image_filename = f"{uuid4()}_{image.filename}"
    audio_filename = f"{uuid4()}_{audio.filename}"

    image_path = os.path.join(UPLOAD_DIR, image_filename)
    audio_path = os.path.join(UPLOAD_DIR, audio_filename)

    with open(image_path, "wb") as f:
        f.write(await image.read())

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    beat = Beats(
        name=name,
        image_path=image_path,
        audio_path=audio_path,
        exclusive=exclusive
    )
    db.add(beat)
    db.commit()
    db.refresh(beat)

    return beat



@router.get("/beats/", response_model=list[BeatsRead])
def get_beats(db: Session = Depends(get_db)):
    beats = db.query(Beats).all()
    return beats

@router.put("/beats/{id}", response_model=BeatsRead)
def update_beat(id: int, updated_beat: BeatsCreate, db: Session = Depends(get_db)):
    beat = db.query(Beats).filter(Beats.id == id).first()
    if not beat:
        raise HTTPException(status_code=404, detail="Beat não encontrado")

    beat.name = updated_beat.name
    beat.exclusive = updated_beat.exclusive
    beat.image_path = updated_beat.image_path
    beat.audio_path = updated_beat.audio_path

    db.commit()
    db.refresh(beat)
    return beat

@router.delete("/beats/{id}")
def delete_beat(id: int, db: Session = Depends(get_db)):
    beat = db.query(Beats).filter(Beats.id == id).first()
    if not beat:
        raise HTTPException(status_code=404, detail="Beat não encontrado")

    # Remove arquivos do sistema
    if os.path.exists(beat.image_path):
        os.remove(beat.image_path)
    if os.path.exists(beat.audio_path):
        os.remove(beat.audio_path)

    db.delete(beat)
    db.commit()
    return {"detail": f"Beat com id {id} removido com sucesso."}
