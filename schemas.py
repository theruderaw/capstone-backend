from pydantic import BaseModel,EmailStr
from datetime import date

class FinanceCreate(BaseModel):
    hours: int
    penalties: int

class LoginRequest(BaseModel):
    user: str
    password: str

class UserAction(BaseModel):
    user_id: int

class UserPersonal(BaseModel):
    aadhar_no: str
    dob: date
    name: str
    status_id: int

    gender: str | None = None
    father_name: str | None = None
    address: str | None = None
    active: bool | None = None
    email: EmailStr | None = None

class Auth(BaseModel):
    password: str

class UserCreate(BaseModel):
    user_personal: UserPersonal
    auth: Auth

class AuthReset(BaseModel):
    old_password: str
    new_password: str