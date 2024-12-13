from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, field_validator
from simulator import run_simulation
import uuid
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    duration: int # this one is a temporary value for testing
    name: str
    num_scenarios: int
    scenario_type: str
    start_date: datetime
    end_date: datetime

class SimulationResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime
    estimated_completion_time: datetime
    num_scenarios: int
    scenario_type: str
    start_date: datetime
    end_date: datetime

# Global variable to store simulation results
# temporarily in memory (in the future, we will use a database) :)
simulation_store = {}

@app.get("/")
def read_root():
    return {"Hello": "THIS IS CODDDYY!!!!!"}

async def run_mock_simulation(simulation_id: str, duration: int = 10):
    """
    Simulate a long-running task with a specified duration
    """
    # Simulate some processing
    await asyncio.sleep(duration)

    # run the actual simulation
    simulation_results = run_simulation(
        num_scenarios=simulation_store[simulation_id]['num_scenarios'],
        scenario_type=simulation_store[simulation_id]['scenario_type'],
        start=simulation_store[simulation_id]['start_date'],
        end=simulation_store[simulation_id]['end_date']
    )
    
    # Update simulation status
    if simulation_id in simulation_store:
        simulation_store[simulation_id].update({
            'status': 'completed',
            'results': {
                'message': f'Simulation {simulation_id} completed successfully',
                'processed_duration': duration,
                'data': simulation_results
            },
            'completed_at': datetime.now()
        })

@app.post("/start-simulation", response_model=SimulationResponse)
async def start_simulation(
    simulation_request: SimulationRequest, 
    background_tasks: BackgroundTasks
):
    # Validate request data
    if not simulation_request.name:
        raise HTTPException(status_code=400, detail="Name is required")
    if not simulation_request.num_scenarios:
        raise HTTPException(status_code=400, detail="Number of scenarios is required")
    if not simulation_request.scenario_type:
        raise HTTPException(status_code=400, detail="Scenario type is required")
    if not simulation_request.start_date:
        raise HTTPException(status_code=400, detail="Start date is required")
    if not simulation_request.end_date:
        raise HTTPException(status_code=400, detail="End date is required")
    if simulation_request.duration <= 0:
        raise HTTPException(status_code=400, detail="Duration must be a positive integer")
    if simulation_request.end_date <= simulation_request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    simulation_id = str(uuid.uuid4())
    created_at = datetime.now()
    estimated_completion = created_at + timedelta(seconds=simulation_request.duration)

    simulation_store[simulation_id] = {
        'id': simulation_id,
        'status': 'pending',
        'name': simulation_request.name,
        'created_at': created_at,
        'num_scenarios': simulation_request.num_scenarios,
        'scenario_type': simulation_request.scenario_type,
        'start_date': simulation_request.start_date,
        'end_date': simulation_request.end_date
    }

    print(simulation_store)
    
    # Start simulation in background
    background_tasks.add_task(
        run_mock_simulation, 
        simulation_id, 
        simulation_request.duration
    )
    
    return SimulationResponse(
        id=uuid.UUID(simulation_id),
        status='pending',
        name=simulation_request.name,
        created_at=created_at,
        estimated_completion_time=estimated_completion,
        num_scenarios=simulation_request.num_scenarios,
        scenario_type=simulation_request.scenario_type,
        start_date=simulation_request.start_date,
        end_date=simulation_request.end_date
    )

@app.get("/simulations")
def get_simulations():
    return {"simulations": list(simulation_store.values())}

@app.get("/simulations/{simulation_id}")
def get_simulation(simulation_id: uuid.UUID):
    simulation_id_str = str(simulation_id)
    if simulation_id_str in simulation_store:
        return {"simulation": simulation_store[simulation_id_str]}
    return {"error": "Simulation not found"}

@app.delete("/simulations/{simulation_id}")
def delete_simulation(simulation_id: uuid.UUID):
    simulation_id_str = str(simulation_id)
    if simulation_id_str in simulation_store:
        del simulation_store[simulation_id_str]
        return {"message": "Simulation deleted successfully"}
    return {"error": "Simulation not found"}
