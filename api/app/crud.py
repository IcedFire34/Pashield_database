from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime
from .schemas import User  # Pydantic modelini import edin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        password=hashed_password,
        name=user.name,
        surname=user.surname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # SQLAlchemy modelini Pydantic modeline dönüştür
    return User(
        id=db_user.id,
        email=db_user.email,
        name=db_user.name,
        surname=db_user.surname,
        create_date=db_user.create_date,
        last_login_date=db_user.last_login_date
    )

def update_user_last_login(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.last_login_date = datetime.now()
        db.commit()
        db.refresh(db_user)
    return db_user

def get_passwords(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Password).filter(models.Password.user_id == user_id).offset(skip).limit(limit).all()

def get_password(db: Session, password_id: int, user_id: int):
    return db.query(models.Password).filter(
        models.Password.id == password_id,
        models.Password.user_id == user_id
    ).first()

def create_user_password(db: Session, password: schemas.PasswordCreate, user_id: int):
    db_password = models.Password(**password.dict(), user_id=user_id)
    db.add(db_password)
    db.commit()
    db.refresh(db_password)
    return db_password

def update_password(db: Session, password_id: int, password: schemas.PasswordCreate, user_id: int):
    db_password = get_password(db, password_id, user_id)
    if db_password:
        for key, value in password.dict().items():
            setattr(db_password, key, value)
        db.commit()
        db.refresh(db_password)
    return db_password

def delete_password(db: Session, password_id: int, user_id: int):
    db_password = get_password(db, password_id, user_id)
    if db_password:
        db.delete(db_password)
        db.commit()
    return db_password