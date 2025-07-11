import os
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
from dotenv import load_dotenv


CONNECTION_STRING = os.getenv("IOTHUB_CONNECTION_STRING")

def invoke_direct_method(device_id: str, module_id: str, method_name: str, payload: dict):
    try:
        manager = IoTHubRegistryManager(CONNECTION_STRING)

        direct_method = CloudToDeviceMethod(
            method_name=method_name,
            payload=payload,
            response_timeout_in_seconds=10,
            connect_timeout_in_seconds=5
        )

        response = manager.invoke_device_module_method(
            device_id=device_id,
            module_id=module_id,
            direct_method_request=direct_method
        )

        print(f"Response from module '{module_id}' on device '{device_id}': {response}")
        return {
            "status": "success",
            "status_code": response.status,
            "payload": response.payload
        }
    except Exception as e:
        print("Error invoking method:", e)
        return {
            "status": "error",
            "detail": str(e)
        }