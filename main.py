from fastapi import FastAPI
from typing import Dict
from fastapi.encoders import jsonable_encoder
from geopy.distance import geodesic
import uvicorn

app = FastAPI()

coordinates = {
    "tambaram": (12.927921378842747,80.11848114008859),
    "kundrathur": (12.996986941304302,80.09611309025814),
    "nad_house":(12.925421,80.141575),
    "cit_college":(12.971845651701978,80.04306665944301)
}

@app.get("/check_coordinates/{new_coord}")
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
        return jsonable_encoder({"closest_location": closest_location, "distance_to_closest_location": min_distance,"message":True})
    else:
        return jsonable_encoder({"message": False})

if __name__ == "__main__":
    print("app is live")
    uvicorn.run(app="main:app", host="localhost", port=8000,reload=True)
    
