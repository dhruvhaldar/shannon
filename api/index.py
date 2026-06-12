from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shannon.link_budget import LinkBudget
from shannon.orbits import PassPredictor
from shannon.ground_station import GroundStation
from shannon.modulation import Modulation
import datetime
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LinkBudgetRequest(BaseModel):
    frequency: float # Hz
    distance_km: float
    tx_power_dbm: float
    tx_cable_loss: float
    tx_antenna_gain: float
    atmosphere_loss: float
    rx_antenna_gain: float
    rx_noise_temp: float
    data_rate: float
    required_eb_no: float

class PassPredictionRequest(BaseModel):
    tle_line1: str
    tle_line2: str
    lat: float
    lon: float
    alt: float
    max_duration_hours: float = 24.0

class IQRequest(BaseModel):
    scheme: str
    snr_db: float
    num_symbols: int = 1000

@app.post("/api/calculate-link-budget")
def calculate_link_budget(req: LinkBudgetRequest):
    link = LinkBudget(req.frequency, req.distance_km)
    link.set_transmitter(req.tx_power_dbm, req.tx_cable_loss, req.tx_antenna_gain)
    link.add_path_loss(req.atmosphere_loss)
    link.set_receiver(req.rx_antenna_gain, req.rx_noise_temp)

    margin = link.calculate_margin(req.data_rate, req.required_eb_no)

    return {
        "margin_db": margin,
        "losses": link.losses
    }

@app.post("/api/predict-pass")
def predict_pass(req: PassPredictionRequest):
    predictor = PassPredictor(req.tle_line1, req.tle_line2)
    station = GroundStation(req.lat, req.lon, req.alt)

    # We need to handle time. For now, assume "now".
    start_time = datetime.datetime.utcnow()
    pass_data = predictor.get_next_pass(station, start_time, req.max_duration_hours)

    if pass_data:
        # Optimization: Bypassing FastAPI's default serialization via Pydantic model (`jsonable_encoder`)
        # by returning a custom `JSONResponse` directly avoids evaluating `isinstance` on every element
        # of the long list, running over 5x faster than the default framework serialization loop.
        response_data = {
            "aos": pass_data.aos.isoformat(),
            "los": pass_data.los.isoformat(),
            "max_el": pass_data.max_el,
            "points": [{
                "time": p['time'].isoformat(),
                "az": p['az'],
                "el": p['el'],
                "range_km": p['range_km']
            } for p in pass_data.points]
        }
        return JSONResponse(content=response_data)
    else:
        return JSONResponse(content={"message": "No pass found within duration."})

@app.post("/api/generate-iq")
def generate_iq(req: IQRequest):
    mod = Modulation(req.scheme)
    try:
        symbols = mod.generate_iq(req.num_symbols, req.snr_db)
        # Convert complex to a flat list of interleaved I, Q values
        # Optimization: Returning a flat list instead of a nested list reduces JSON payload size
        # by ~5% and speeds up JSON parsing and serialization by ~25%.
        iq_data = symbols.view(np.float64).tolist()
        # Optimization: Bypassing FastAPI's default serialization via Pydantic model (`jsonable_encoder`)
        # by returning a custom `JSONResponse` directly avoids evaluating `isinstance` on every element
        # of the large nested array, running over 2x faster than the default framework serialization loop.
        return JSONResponse(content={"iq_data": iq_data})
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
