from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str


class Roles(BaseModel):
    role_name: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    email: EmailStr | None = None


class UserRegister(User, UserLogin):
    pass


class UserFromDB(User):
    disabled: bool = False
    roles: list[str]


class UserCheck(BaseModel):
    id: int
    username: str
    password: str
    email: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class UserPatch(BaseModel):
    id: int | None = None
    username: str | None = None
    password: str | None = None
    email: str | None = None


class UserPut(UserCheck):
    pass


class UsersFromDBList(BaseModel):
    users: list[UserCheck]


class UserToDB(UserFromDB):
    password: str
