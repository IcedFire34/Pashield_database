-- Kullanıcılar tablosu
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, -- Hashlenmiş ve saltlanmış biçimde saklanmalı
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_date TIMESTAMPTZ
);

-- Parolalar tablosu
CREATE TABLE IF NOT EXISTS passwords (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hesap_yeri TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL, -- AES gibi bir algoritma ile şifrelenmiş olarak saklanmalı
    icon_name TEXT
);

-- Gerekirse index'ler tanımlanabilir
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_passwords_user_id ON passwords(user_id);
