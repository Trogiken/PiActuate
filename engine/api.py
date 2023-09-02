"""
API for the internal runtime object.

This API is used by the webui to communicate with the runtime object
through the uvicorn application server.

Status Codes:
    200: Success
    400: Invalid option
    500: General internal server error
    522: Runtime not initialized
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from source import Runtime
import options as opt

runtime = Runtime.getInstance()
app = FastAPI()

# Start this api
# uvicorn main:app --host 0.0.0.0 --port 8000

# TODO Secure this api with HTTPS or CORS
# TODO Configure setup_script.sh to start api server on boot

# TODO POST configure: If you transmit the database object as a dict, the way runtime accesses it
# will not work. You need to transmit the object itself. Try to use pickle to serialize
# the object and send it over the wire. Then deserialize it on the other end.

# TODO Make these models inherit from the BaseModel class
class BasicModel(BaseModel):
    route: str
    message: str

    class Config:
        frozen = True

class ErrorModel(BaseModel):
    route: str
    message: str
    error: str

    class Config:
        frozen = True

class DataModel(BaseModel):
    route: str
    message: str
    data: dict

    class Config:
        frozen = True


class ConfigureRequest(BaseModel):
    system_config: dict
    startup_config: dict


def ensure_runtime():
    if runtime is None:
        raise HTTPException(status_code=522, detail="Runtime not initialized")


@app.get("/")
def root():
    return {"message": "Runtime API",
            "routes": ["/configure", "/destroy", "/auto", "/door", "/aux"]}

# BUG This is not working properly
@app.post("/configure")
def configure(config_data: ConfigureRequest):
    global runtime
    try:
        system_config = config_data['system_config']
        startup_config = config_data['startup_config']
        print(system_config)
        print(startup_config)

        # TODO Make runtime get from the dictionary instead of the db method
        # runtime = Runtime(system_config, startup_config)

        response = JSONResponse(content={
            BasicModel(route="/configure",
                          message="Configure Endpoint",
                          )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/configure",
                          message="An error occurred",
                          error=f"{str(e)}"
                          )}, status_code=500)
    return response


@app.post("/destroy")
def destroy(_: Runtime = Depends(ensure_runtime)):
    try:
        runtime.destroy()

        response = JSONResponse(content={
            BasicModel(route="/destroy",
                          message="Destroy Endpoint",
                          )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/destroy",
                          message="An error occurred",
                          error=f"{e}"
                          )}, status_code=500)
    return response


@app.get("/auto")
def get_auto(_: Runtime = Depends(ensure_runtime)):
    try:
        response = JSONResponse(content={
            DataModel(route="/auto",
                          message="Automation Endpoint",
                          data={"sunrise_offset": runtime.auto.sunrise_offset,
                                "sunset_offset": runtime.auto.sunset_offset,
                                "active_sunrise": runtime.auto.active_sunrise,
                                "active_sunset": runtime.auto.active_sunset,
                                "active_current": runtime.auto.active_current,
                                "is_alive": runtime.auto.scheduler.is_alive()}
                            )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/auto",
                          message="An error occurred",
                          error=f"{e}"
                          )}, status_code=500)
    return response

    

@app.post("/auto")
def post_auto(option: opt.PostAuto, value: int=None, _: Runtime = Depends(ensure_runtime)):
    try:
        if opt.PostAuto.sunrise_offset:
            runtime.auto.sunrise_offset = value
        elif opt.PostAuto.sunset_offset:
            runtime.auto.sunset_offset = value
        elif opt.PostAuto.start:
            runtime.auto.start()
        elif opt.PostAuto.stop:
            runtime.auto.stop()
        elif opt.PostAuto.refresh:
            runtime.auto.refresh()
        else:
            return JSONResponse(content={
                ErrorModel(route="/auto",
                           message=f"'{option}' is not a valid option",
                           error="Invalid option"
                           )}, status_code=400)
        response = JSONResponse(content={
            BasicModel(route="/auto",
                          message="Automation Endpoint",
                          )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/auto",
                          message="An error occurred",
                          error=f"{e}"
                          )}, status_code=500)
    return response


@app.get("/door")
def get_door(_: Runtime = Depends(ensure_runtime)):
    try:
        response = JSONResponse(content={
            DataModel(route="/door",
                          message="Door Endpoint",
                          data={"status": runtime.door.status()}
                          )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/door",
                          message="An error occurred",
                          error=f"{e}"
                          )}, status_code=500)
    return response


@app.post("/door")
def post_door(option: opt.PostDoor, _: Runtime = Depends(ensure_runtime)):
    try:
        if opt.PostDoor.open:
            runtime.door.move(option)
        elif opt.PostDoor.close:
            runtime.door.move(option)
        else:
            return JSONResponse(content={
                ErrorModel(route="/door",
                              message=f"'{option}' is not a valid option",
                              error="Invalid option"
                              )}, status_code=400)
        response = JSONResponse(content={
            BasicModel(route="/door",
                        message="Door Endpoint",
                        )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/door",
                        message="An error occurred",
                        error=f"{e}"
                        )}, status_code=500)
    return response


@app.get("/aux")
def get_aux(_: Runtime = Depends(ensure_runtime)):
    try:
        response = JSONResponse(content={
            DataModel(route="/aux",
                          message="Auxiliary Endpoint",
                          data={"is_alive": runtime.aux.is_alive()}
                          )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/aux",
                          message="An error occurred",
                          error=f"{e}"
                          )}, status_code=500)
    return response


@app.post("/aux")
def post_aux(option: opt.PostAux, _: Runtime = Depends(ensure_runtime)):
    try:
        if opt.PostAux.start:
            runtime.aux.run_aux()
        elif opt.PostAux.stop:
            runtime.aux.stop_aux()
        else:
            return JSONResponse(content={
                ErrorModel(route="/aux",
                              message=f"'{option}' is not a valid option",
                              error="Invalid option"
                              )}, status_code=400)
        response = JSONResponse(content={
            BasicModel(route="/aux",
                          message="Auxiliary Endpoint",
                          )}, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            ErrorModel(route="/aux",
                          message="An error occurred",
                          error=f"{e}"
                          )}, status_code=500)
    return response
