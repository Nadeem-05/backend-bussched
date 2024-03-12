from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from geopy.distance import geodesic
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker,declarative_base
import requests
import json
APP_ID = '9147fe2e-8d34-4ce8-9d7e-6ebf30d3470f'
REST_API_KEY = 'NTczYjgxNDYtN2RjNi00M2I3LWEwOGMtNjc4ZDVlYjMyMDAw'

ONESIGNAL_API_URL = 'https://onesignal.com/api/v1/notifications'
message = {
    "app_id": APP_ID,
    "include_player_ids": ["ca57bb89-1bd7-4b28-8de2-2d205acfa860"],
    "contents": {"en": "Hooray your dynamic bus has been scheduled!"},
    "headings": {"en": "Dynamic Bus Scheduled"}
}

message_json = json.dumps(message)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {REST_API_KEY}'
}

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
    
Base.metadata.create_all(bind=engine)

coordinates = {
    "tambaram": (12.927921378842747, 80.11848114008859),
    "kundrathur": (12.996986941304302, 80.09611309025814),
    "nad_house": (12.925421, 80.141575),
    "cit_college": (12.971845651701978, 80.04306665944301)
}

def send_notification_to_voters(device_ids):
    message["include_player_ids"] = device_ids
    response = requests.post(ONESIGNAL_API_URL, headers=headers, data=message_json)
    if response.status_code == 200:
        print("Notification sent successfully to voters!")
    else:
        print("Failed to send notification to voters. Status code:", response.status_code)


@app.get("/vote/{BusNo_device_id}")
async def busfunc(BusNo_device_id: str):
    # Split the combined parameter into BusNo and device_id
    BusNo, device_id = BusNo_device_id.split(',')

    db = SessionLocal()
    result = db.query(BUS).filter(BUS.bus_no == BusNo).first()
    if result is None:
        bus_detail = BUS(bus_no=BusNo, vote_count=1, threshold=3)
        db.add(bus_detail)
        db.commit()
        db.close()
        record_vote(db, BusNo, device_id)
        return "Data added"
    else:
        result.vote_count += 1
        if result.vote_count > result.threshold:
            db = SessionLocal()
            try:

                device_ids = db.query(Vote.device_id).filter(Vote.bus_no == BusNo).all()
                device_ids = [device[0] for device in device_ids]
                send_notification_to_voters(device_ids)
                db.query(Vote).filter(Vote.bus_no == BusNo).delete()
                db.delete(result)
                db.commit()
                return "Vote count incremented and notifications sent"
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close() 
        else:
            record_vote(db, BusNo, device_id)
            return "Vote count incremented"

def record_vote(db, bus_no, device_id):
    vote = Vote(bus_no=bus_no, device_id=device_id)
    db.add(vote)
    db.commit()
if __name__ == "__main__":
    import uvicorn
    print("App is live")
    uvicorn.run(app="main:app", host="localhost", port=8000, reload=True)
