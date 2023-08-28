from fastapi import FastAPI
from runtime import Runtime

runtime = Runtime.getInstance()

app = FastAPI()

# Start this api
# uvicorn main:app --host 0.0.0.0 --port 8000

# TODO Configure setup_script.sh to start api server on boot

# TODO POST configure: If you transmit the database object as a dict, the way runtime accesses it
# will not work. You need to transmit the object itself. Try to use pickle to serialize
# the object and send it over the wire. Then deserialize it on the other end.

# TODO GET auto/
# TODO GET aux/
# TODO GET door/
# TODO GET runtime/
