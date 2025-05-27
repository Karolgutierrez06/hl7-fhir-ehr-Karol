from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.controlador.PatientCrud import (
    GetPatientById,
    GetPatientByIdentifier,
    WritePatient,
    read_service_request,
    WriteServiceRequest,
    WriteAppointment,
    WriteProcedure,
    WriteMedicationRequest
)

app = FastAPI()

# Middleware para permitir CORS desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------- RUTAS EXISTENTES ----------------------------

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

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    new_patient_dict = dict(await request.json())
    status, patient_id = WritePatient(new_patient_dict)
    if status == 'success':
        return {"_id": patient_id}
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")

@app.get("/service-request/{service_request_id}", response_model=dict)
async def get_service_request(service_request_id: str):
    service_request = read_service_request(service_request_id)
    if service_request:
        return service_request
    else:
        raise HTTPException(status_code=404, detail="Solicitud de servicio no encontrada")

@app.post("/service-request", response_model=dict)
async def add_service_request(request: Request):
    service_request_data = await request.json()
    status, service_request_id = WriteServiceRequest(service_request_data)
    if status == "success":
        return {"_id": service_request_id}
    else:
        raise HTTPException(status_code=500, detail=f"Error al registrar la solicitud: {status}")

# ----------------------- NUEVA RUTA: /appointment ----------------------------

@app.post("/appointment", response_model=dict)
async def add_appointment(request: Request):
    appointment_data = await request.json()
    status, appointment_id = WriteAppointment(appointment_data)
    if status == "success":
        return {"id": appointment_id}
    else:
        raise HTTPException(status_code=500, detail=f"Error al registrar la cita: {status}")

# ----------------------- NUEVA RUTA: /procedure ----------------------------

@app.post("/procedure", response_model=dict)
async def add_procedure_with_medication(request: Request):
    try:
        data = await request.json()
        procedure = data.get("procedure")
        medication_request = data.get("medicationRequest")

        if not procedure or not medication_request:
            raise HTTPException(status_code=400, detail="Faltan datos de procedure o medicationRequest")

        # Guardar procedimiento
        status_proc, proc_id = WriteProcedure(procedure)
        if status_proc != "success":
            raise HTTPException(status_code=500, detail="Error al registrar el procedimiento")

        # Guardar prescripción
        status_med, med_id = WriteMedicationRequest(medication_request)
        if status_med != "success":
            raise HTTPException(status_code=500, detail="Error al registrar la prescripción")

        return {"procedure_id": proc_id, "medication_id": med_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# ------------------------ INICIO MANUAL (opcional) ----------------------------

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
