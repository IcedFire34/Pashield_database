# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime
from .security import encrypt_data, decrypt_data
from .schemas import User

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
    db_passwords = db.query(models.Password).filter(
        models.Password.user_id == user_id
    ).offset(skip).limit(limit).all()

    passwords = []
    for db_password in db_passwords:
        password_dict = {
            "id": db_password.id,
            "user_id": db_password.user_id,
            "hesap_yeri": db_password.hesap_yeri,
            "username": db_password.username,
            "password": decrypt_data(db_password.password)  # Her zaman çöz
        }
        passwords.append(schemas.Password(**password_dict))

    return passwords

def get_password(db: Session, password_id: int, user_id: int, decrypt: bool = False):
    db_password = db.query(models.Password).filter(
        models.Password.id == password_id,
        models.Password.user_id == user_id
    ).first()
    if not db_password:
        return None

    # Veritabanı nesnesini Pydantic modeline dönüştür
    password_dict = {
        "id": db_password.id,
        "user_id": db_password.user_id,
        "hesap_yeri": db_password.hesap_yeri,
        "username": db_password.username,
        "password": decrypt_data(db_password.password) if decrypt else db_password.password
    }
    return schemas.Password(**password_dict)


def create_user_password(db: Session, password: schemas.PasswordCreate, user_id: int):
    encrypted_password = encrypt_data(password.password)
    db_password = models.Password(
        user_id=user_id,
        hesap_yeri=password.hesap_yeri,
        username=password.username,
        password=encrypted_password
    )
    db.add(db_password)
    db.commit()
    db.refresh(db_password)

    # SQLAlchemy modelini Pydantic modeline dönüştürüyoruz
    return schemas.Password(
        id=db_password.id,
        user_id=db_password.user_id,
        hesap_yeri=db_password.hesap_yeri,
        username=db_password.username,
        password=db_password.password  # Şifreli halini döndürüyoruz
    )


def update_password(db: Session, password_id: int, password: schemas.PasswordCreate, user_id: int):
    # Önce veritabanından orijinal password'ü al
    db_password = db.query(models.Password).filter(
        models.Password.id == password_id,
        models.Password.user_id == user_id
    ).first()

    if not db_password:
        return None

    # Güncelleme yap
    encrypted_password = encrypt_data(password.password)
    db_password.hesap_yeri = password.hesap_yeri
    db_password.username = password.username
    db_password.password = encrypted_password

    db.commit()
    db.refresh(db_password)  # Bu artık models.Password üzerinde çalışıyor

    # Sonucu Pydantic modeline çevirerek dön
    return schemas.Password(
        id=db_password.id,
        user_id=db_password.user_id,
        hesap_yeri=db_password.hesap_yeri,
        username=db_password.username,
        password=db_password.password  # veya decrypt_data(db_password.password)
    )


def delete_password(db: Session, password_id: int, user_id: int):
    # Önce veritabanından orijinal password'ü al (SQLAlchemy modeli olarak)
    db_password = db.query(models.Password).filter(
        models.Password.id == password_id,
        models.Password.user_id == user_id
    ).first()

    if not db_password:
        return None

    # Silmeden önce bilgileri sakla (response için)
    password_data = {
        "id": db_password.id,
        "user_id": db_password.user_id,
        "hesap_yeri": db_password.hesap_yeri,
        "username": db_password.username,
        "password": db_password.password
    }

    # Silme işlemini yap
    db.delete(db_password)
    db.commit()

    # Silinen kaydı Pydantic modeline çevirerek dön
    return schemas.Password(**password_data)