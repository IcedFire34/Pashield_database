from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .auth import authenticate_user, create_access_token
from . import models, schemas, crud, auth
from .config import settings
from .database import engine, get_db
from datetime import timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "Pashield API çalışıyor!", "status": "OK"}

@app.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Email kontrolü
        if crud.get_user_by_email(db, email=user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Kullanıcı oluştur
        created_user = crud.create_user(db=db, user=user)
        return created_user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Kullanıcının son giriş tarihini güncelle
    crud.update_user_last_login(db, user.id)

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/passwords/", response_model=list[schemas.Password])
def read_passwords(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    passwords = crud.get_passwords(db, user_id=current_user.id, skip=skip, limit=limit)
    return passwords

@app.post("/passwords/", response_model=schemas.Password)
def create_password(
    password: schemas.PasswordCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    return crud.create_user_password(db=db, password=password, user_id=current_user.id)

@app.get("/passwords/{password_id}", response_model=schemas.Password)
def read_password(
    password_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    password = crud.get_password(db, password_id=password_id, user_id=current_user.id)
    if password is None:
        raise HTTPException(status_code=404, detail="Password not found")
    return password

@app.put("/passwords/{password_id}", response_model=schemas.Password)
def update_password(
    password_id: int,
    password: schemas.PasswordCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_password = crud.update_password(db, password_id=password_id, password=password, user_id=current_user.id)
    if db_password is None:
        raise HTTPException(status_code=404, detail="Password not found")
    return db_password

@app.delete("/passwords/{password_id}", response_model=schemas.Password)
def delete_password(
    password_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_password = crud.delete_password(db, password_id=password_id, user_id=current_user.id)
    if db_password is None:
        raise HTTPException(status_code=404, detail="Password not found")
    return db_password