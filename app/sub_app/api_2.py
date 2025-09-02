from fastapi import FastAPI

sub_app = FastAPI()


@sub_app.get("/sub/")
async def read_sub():
    return {"message": "This is a sub app"}
