from fastapi import FastAPI, HTTPException, Request, Body
import uvicorn
from app.controlador.PatientCrud import (
    GetPatientById,
    GetPatientByIdentifier,
    WritePatient,
    read_service_request,
    WriteServiceRequest
)
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solo este dominio (ajustar en producción)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status, patient = GetPatientById(patient_id)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    print("received", system, value)
    status, patient = GetPatientByIdentifier(system, value)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.get("/service-request/{service_request_id}", response_model=dict)
async def get_service_request(service_request_id: str):
    service_request = read_service_request(service_request_id)
    if service_request:
        return service_request
    else:
        raise HTTPException(status_code=404, detail="Solicitud de servicio no encontrada")

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    new_patient_dict = dict(await request.json())
    status, patient_id = WritePatient(new_patient_dict)
    if status == 'success':
        return {"_id": patient_id}
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")

@app.post("/service-request", response_model=dict)
async def add_service_request(request: Request):
    service_request_data = await request.json()
    status, service_request_id = WriteServiceRequest(service_request_data)
    if status == "success":
        return {"_id": service_request_id}
    else:
        raise HTTPException(status_code=500, detail=f"Error al registrar la solicitud: {status}")

# --- NUEVO ENDPOINT PARA APPOINTMENT ---
@app.post("/appointment", response_model=dict)
async def add_appointment(appointment: dict = Body(...)):
    """
    Endpoint para crear citas quirúrgicas (Appointment).
    Actualmente simula almacenamiento generando un ID único.
    """
    print("Recibí appointment:", appointment)
    
    # Aquí implementa la lógica para guardar la cita en tu BD
    appointment_id = str(uuid.uuid4())  # Generar un ID único
    
    return {"id": appointment_id, "appointment": appointment}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
