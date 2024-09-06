from fastapi import FastAPI, Depends, HTTPException,Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import jwt
import uvicorn
from urllib.parse import urljoin


app = FastAPI(
    title="CBWay API Mockup",
    description="This is the API mockup for the CBWay project.",
    version="1.0.0",
    contact={
        "name": "DN",
        "email": "dinhtruongnguyen11@gmail.com",
    }
)

# Mock secret key for JWT token generation (replace with a secure key)
SECRET_KEY = "secret_key"

# Mock user data
users_db = {
    "0901234567": {"name": "User A", "password": "password123"}
}

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Serve static files for icons and banners
app.mount("/static", StaticFiles(directory="static"), name="static")


# Token response model
class Token(BaseModel):
    access_token: str
    token_type: str


# User details response model
class User(BaseModel):
    full_name: str
    phone_number: str


# Feature list response model
class Feature(BaseModel):
    icon: str
    name: str
    link: str


# News response model
class News(BaseModel):
    banner_img: str
    title: str
    datetime: str

def get_base_url(request: Request):
    # Extract the scheme and host from the request URL
    scheme = request.url.scheme
    host = request.url.netloc
    return f"{scheme}://{host}/static/"



# Mock feature list
mock_features = [
    {"icon": "icons/icon_service_car.png", "name": "Tài khoản", "link": "/tai-khoan"},
    {"icon": "icons/icon_service_ddts.png", "name": "Thanh toán hóa đơn", "link": "/thanh-toan"},
    {"icon": "icons/icon_service_dtb.png", "name": "Chuyển tiền", "link": "/chuyen-tien"},
    {"icon": "icons/icon_service_hdd.png", "name": "Đặt phòng khách sạn", "link": "/dat-phong"},
    {"icon": "icons/icon_service_thc.png", "name": "Nạp tiền điện thoại", "link": "/nap-tien"},
    {"icon": "icons/icon_servive_internet.png", "name": "Quét mã QR", "link": "/quet-ma"}
]

# Mock news list
mock_news = [
    {"banner_img": "banners/banner1.jpg", "title": "Tin tức 1", "datetime": "2024-09-05T12:30:00"},
    {"banner_img": "banners/banner2.jfif", "title": "Tin tức 2", "datetime": "2024-09-04T15:00:00"},
    {"banner_img": "banners/banner3.webp", "title": "Tin tức 3", "datetime": "2024-09-03T10:45:00"}
]


# 1. Đăng nhập: /login
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect phone number or password")

    token_data = {
        "sub": form_data.username,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# Helper function to verify token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        phone_number = payload.get("sub")
        if phone_number is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"phone_number": phone_number, "full_name": users_db[phone_number]["name"]}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# 2. Get user detail: /user
@app.get("/user", response_model=User)
def get_user_details(current_user: dict = Depends(get_current_user)):
    return current_user


# 3. Get list feature: /features
@app.get("/features", response_model=List[Feature])
def get_feature_list(request: Request):
    base_url = get_base_url(request)
    features_with_full_urls = [
        {"icon": f"{base_url}{feature['icon']}", "name": feature["name"], "link": feature["link"]}
        for feature in mock_features
    ]
    return features_with_full_urls

@app.get("/news", response_model=List[News])
def get_news(request: Request):
    base_url = get_base_url(request)
    news_with_full_urls = [
        {"banner_img": f"{base_url}{news['banner_img']}", "title": news["title"], "datetime": news["datetime"]}
        for news in mock_news
    ]
    return news_with_full_urls


# Default root endpoint: /
@app.get("/")
def read_root():
    return {
        "Project": "CBWay API Mockup",
        "Author": "DN",
        "Version": "1.0.0"
    }



# Example endpoint using static files

# Main function to run the app with uvicorn
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
