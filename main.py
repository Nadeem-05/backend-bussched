from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from geopy.distance import geodesic 
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker,declarative_base, Session
import requests
import json
from jinja2 import Environment, FileSystemLoader
import os
APP_ID = '9147fe2e-8d34-4ce8-9d7e-6ebf30d3470f'
REST_API_KEY = 'NTczYjgxNDYtN2RjNi00M2I3LWEwOGMtNjc4ZDVlYjMyMDAw'

ONESIGNAL_API_URL = 'https://onesignal.com/api/v1/notifications'


app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqldb.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BUS(Base):
    __tablename__ = 'bus'
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    bus_no = Column(String(5), unique=True)
    vote_count = Column(Integer)
    threshold = Column(Integer)

class Vote(Base):
    __tablename__ = 'vote'
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    bus_no = Column(String(5))
    device_id = Column(String(255))
class  Active(Base):
    __tablename__='active_buses'
    s_no = Column(Integer,primary_key=True, autoincrement=True)
    bus_no = Column(String(5))
    origin = Column(String(10))
    dest = Column(String(10))
    
Base.metadata.create_all(bind=engine)

coordinates = {
    "tambaram": (12.927921378842747, 80.11848114008859),
    "kundrathur": (12.996986941304302, 80.09611309025814),
    "nad_house": (12.925421, 80.141575),
    "cit_college": (12.971845651701978, 80.04306665944301)
}

@app.get("/check/{new_coord}")
async def check_coordinates(new_coord: str):
    closest_location = None
    min_distance = float('inf')
    new_coord = tuple(map(float, new_coord.split(',')))

    for location, coord in coordinates.items():
        distance = geodesic(new_coord, coord).meters
        if distance < min_distance:
            min_distance = distance
            closest_location = location
    if min_distance <= 1000:
        return jsonable_encoder({"closest_location": closest_location, "distance_to_closest_location": int(min_distance),"message":True})
    else:
        return jsonable_encoder({"message": False})
def send_notification_to_voters(device_ids):
    message = {
    "app_id": APP_ID,
    "contents": {"en": "Hooray your dynamic bus has been scheduled!"},
    "headings": {"en": "Dynamic Bus Scheduled"},
    "include_player_ids" : device_ids,
    "large_icon": "https://i.imgur.com/AXydRIM.png",
    "big_picture":"https://i.imgur.com/Wsf4w9f.png",
    "android_accent_color":"FFFF0000"

}

    message_json = json.dumps(message)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {REST_API_KEY}'
    }
    message["include_player_ids"] = device_ids
    print(device_ids)
    response = requests.post(ONESIGNAL_API_URL, headers=headers, data=message_json)
    if response.status_code == 200:
        print("Notification sent successfully to voters!")
    else:
        print("Failed to send notification to voters. Status code:", response.status_code)


@app.get("/vote/{BusNo_device_id}")
async def busfunc(BusNo_device_id: str):
    BusNo, device_id = BusNo_device_id.split(',')

    db = SessionLocal()
    try:
        result = db.query(BUS).filter(BUS.bus_no == BusNo).first()
        if result is None:
            bus_detail = BUS(bus_no=BusNo, vote_count=1, threshold=3)
            db.add(bus_detail)
            db.commit()
            record_vote(db, BusNo, device_id)
            return "Data added"
        else:
            result.vote_count += 1
            if result.vote_count > result.threshold:
                record_vote(db, BusNo, device_id)
                device_ids = db.query(Vote.device_id).filter(Vote.bus_no == BusNo).all()
                device_ids = [device[0] for device in device_ids]
                send_notification_to_voters(device_ids)
                db.query(Vote).filter(Vote.bus_no == BusNo).delete()
                db.delete(result)
                db.commit()
                return "Vote count incremented and notifications sent"
            else:
                record_vote(db, BusNo, device_id)
                return "Vote count incremented"
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while processing the request")
    finally:
        db.close()
        
templates_dir = os.path.join(os.getcwd(), "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/view")
async def view_databases(db: Session = Depends(get_db)):
    votes = db.query(Vote).all()
    buses = db.query(BUS).all()
    template = env.get_template("view_db.html")
    rendered_html = template.render(votes=votes, buses=buses)
    return HTMLResponse(content=rendered_html)

def record_vote(db, bus_no, device_id):
    vote = Vote(bus_no=bus_no, device_id=device_id)
    db.add(vote)
    db.commit()
if __name__ == "__main__":
    import uvicorn
    print("App is live")
    uvicorn.run(app="main:app", host="localhost", port=8000, reload=True)
