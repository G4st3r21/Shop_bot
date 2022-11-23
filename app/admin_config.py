from os import getenv

JWT_SECRET = getenv("secret")
ADMIN_PASSWORD = getenv("admin_password")
ADMIN_LOGIN = getenv("admin_login")

DB_USER = getenv("user")
DB_PASSWORD = getenv("password")
DB_HOST = getenv("host")
DB_PORT = getenv("port")
DB_NAME = getenv("dbname")
