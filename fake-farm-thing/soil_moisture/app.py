from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)

import time
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay
import json
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, X509

connection_string = '[connection string here]' # MUST replace with your own thing

adc = ADC()
relay = GroveRelay(5)

host_name = "[host name here].azure-devices.net" # MUST replace with your own thing
device_id = "[device name here]-x509" # MUST replace with your own thing
x509 = X509("./[device name here]-x509-cert.pem", "./soil-moisture-sensor-x509-key.pem") # MUST replace with your own thing

device_client = IoTHubDeviceClient.create_from_x509_certificate(x509, host_name, device_id)

print('Connecting')
device_client.connect()
print('Connected')

def handle_method_request(request):
    print("Direct method received - ", request.name)
    
    if request.name == "relay_on":
        relay.on()
    elif request.name == "relay_off":
        relay.off()

    method_response = MethodResponse.create_from_method_request(request, 200)
    device_client.send_method_response(method_response)

device_client.on_method_request_received = handle_method_request

while True:
    soil_moisture = adc.read(0)
    print("Soil moisture:", soil_moisture)

    message = Message(json.dumps({ 'soil_moisture': soil_moisture }))
    device_client.send_message(message)

    time.sleep(10)