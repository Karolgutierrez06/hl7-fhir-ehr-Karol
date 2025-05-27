from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
import json

# Conexiones a colecciones
collection = connect_to_mongodb("SamplePatientService", "Patient")
service_requests_collection = connect_to_mongodb("SamplePatientService", "service_requests")
appointments_collection = connect_to_mongodb("SamplePatientService", "appointments")  # NUEVO

# Obtener paciente por ID
def GetPatientById(patient_id: str):
    try:
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"notFound", None

# Escribir nuevo paciente
def WritePatient(patient_dict: dict):
    try:
        pat = Patient.model_validate(patient_dict)
    except Exception as e:
        return f"errorValidating: {str(e)}", None
    validated_patient_json = pat.model_dump()
    result = collection.insert_one(patient_dict)
    if result:
        inserted_id = str(result.inserted_id)
        return "success", inserted_id
    else:
        return "errorInserting", None

# Buscar paciente por sistema y valor de identificador
def GetPatientByIdentifier(patientSystem, patientValue):
    try:
        patient = collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": patientSystem,
                    "value": patientValue
                }
            }
        })
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        print("Error in GetPatientByIdentifier:", e)
        return "notFound", None

# Leer una solicitud de servicio
def read_service_request(service_request_id: str) -> dict:
    try:
        query = {"_id": ObjectId(service_request_id)}
    except Exception as e:
        print("Error al convertir el ID:", e)
        return None

    service_request = service_requests_collection.find_one(query)
    if service_request:
        service_request["_id"] = str(service_request["_id"])
        return service_request
    else:
        return None

# Escribir una solicitud de servicio
def WriteServiceRequest(service_request_data: dict):
    try:
        result = service_requests_collection.insert_one(service_request_data)
        return "success", str(result.inserted_id)
    except Exception as e:
        print("Error in WriteServiceRequest:", e)
        return "error", None

# ✅ NUEVO: Guardar cita quirúrgica (Appointment)
def WriteAppointment(appointment_data: dict):
    try:
        result = appointments_collection.insert_one(appointment_data)
        return "success", str(result.inserted_id)
    except Exception as e:
        print("Error in WriteAppointment:", e)
        return "error", None
