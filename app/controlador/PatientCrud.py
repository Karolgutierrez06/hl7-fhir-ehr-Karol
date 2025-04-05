from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
import json

collection = connect_to_mongodb("SamplePatientService", "Patient")

def GetPatientById(patient_id: str):
    try:
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"notFound", None

def WritePatient(patient_dict: dict):
    try:
        pat = Patient.model_validate(patient_dict)
    except Exception as e:
        return f"errorValidating: {str(e)}",None
    validated_patient_json = pat.model_dump()
    result = collection.insert_one(patient_dict)
    if result:
        inserted_id = str(result.inserted_id)
        return "success",inserted_id
    else:
        return "errorInserting", None


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

def read_service_request(service_request_id: str) -> dict:
    """
    Recupera una solicitud de servicio a partir de su ID.
    """
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