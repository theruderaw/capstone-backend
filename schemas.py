from pydantic import BaseModel,EmailStr
from datetime import date
from typing import List

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

class ReportSubmission(BaseModel):
    reason: str
    description: str
    submission_date: date
    user_id: int

class ResolveReport(BaseModel):
    supervisor_id: int
    res_date: date
    remarks: str

class ProjectData(BaseModel):
    name: str
    description: str
    created_by: int

class ProjectAssign(BaseModel):
    project_id: int
    manager_id: int
    supervisor_id: int
    workers: List[int]

class CreateProject(BaseModel):
    projectData: ProjectData
    projectAssign: ProjectAssign

class EditUser(BaseModel):
    user_personal: UserPersonal
    user_action: UserAction