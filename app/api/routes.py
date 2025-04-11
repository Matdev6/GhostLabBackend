from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.database import get_db
from app.models.beats import Beats
from app.schemas.beats import BeatsRead, BeatsCreate

import cloudinary
import cloudinary.uploader
import re

cloudinary.config(
    cloud_name="dec0dwwvq",
    api_key="888773766288889",
    api_secret="hIIRzWYUkWjxmvj-wC1yM2Hlacg",
    secure=True
)

router = APIRouter()

# Função auxiliar para extrair public_id do Cloudinary
def extract_public_id(url: str):
    match = re.search(r"/([^/]+)\.[a-z]+$", url)
    return match.group(1) if match else None

@router.post("/beats/", response_model=BeatsRead)
async def create_beat(
    name: str = Form(...),
    exclusive: bool = Form(...),
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    image_upload = cloudinary.uploader.upload(
        await image.read(),
        folder="beats/images",
        resource_type="image",
        public_id=str(uuid4())
    )

    audio_upload = cloudinary.uploader.upload(
        await audio.read(),
        folder="beats/audio",
        resource_type="video",
        public_id=str(uuid4())
    )

    beat = Beats(
        name=name,
        image_path=image_upload["secure_url"],
        audio_path=audio_upload["secure_url"],
        exclusive=exclusive
    )
    db.add(beat)
    db.commit()
    db.refresh(beat)

    return beat


@router.get("/beats/", response_model=list[BeatsRead])
def get_beats(db: Session = Depends(get_db)):
    return db.query(Beats).all()


@router.put("/beats/{id}", response_model=BeatsRead)
async def update_beat(
    id: int,
    name: str = Form(...),
    exclusive: bool = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    beat = db.query(Beats).filter(Beats.id == id).first()
    if not beat:
        raise HTTPException(status_code=404, detail="Beat não encontrado")

    # Substituir imagem, se enviada
    if image:
        old_img_id = extract_public_id(beat.image_path)
        if old_img_id:
            cloudinary.uploader.destroy(f"beats/images/{old_img_id}", resource_type="image")

        new_image = cloudinary.uploader.upload(
            await image.read(),
            folder="beats/images",
            resource_type="image",
            public_id=str(uuid4())
        )
        beat.image_path = new_image["secure_url"]

    # Substituir áudio, se enviado
    if audio:
        old_audio_id = extract_public_id(beat.audio_path)
        if old_audio_id:
            cloudinary.uploader.destroy(f"beats/audio/{old_audio_id}", resource_type="video")

        new_audio = cloudinary.uploader.upload(
            await audio.read(),
            folder="beats/audio",
            resource_type="video",
            public_id=str(uuid4())
        )
        beat.audio_path = new_audio["secure_url"]

    beat.name = name
    beat.exclusive = exclusive

    db.commit()
    db.refresh(beat)
    return beat


@router.delete("/beats/{id}")
def delete_beat(id: int, db: Session = Depends(get_db)):
    beat = db.query(Beats).filter(Beats.id == id).first()
    if not beat:
        raise HTTPException(status_code=404, detail="Beat não encontrado")

    # Deletar arquivos no Cloudinary
    img_id = extract_public_id(beat.image_path)
    audio_id = extract_public_id(beat.audio_path)

    if img_id:
        cloudinary.uploader.destroy(f"beats/images/{img_id}", resource_type="image")
    if audio_id:
        cloudinary.uploader.destroy(f"beats/audio/{audio_id}", resource_type="video")

    db.delete(beat)
    db.commit()

    return {"detail": f"Beat com id {id} removido com sucesso."}
