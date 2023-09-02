from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from source import Runtime
import options as opt

runtime = Runtime.getInstance()
app = FastAPI()

# Start this api
# uvicorn main:app --host 0.0.0.0 --port 8000

# TODO Secure this api with HTTPS or CORS
# TODO Configure setup_script.sh to start api server on boot

def ensure_runtime():
    if runtime is None:
        raise HTTPException(status_code=522, detail="Runtime not initialized")

@app.get("/")
def root():
    return {"message": "Runtime API",
            "routes": ["/configure", "/destroy", "/auto", "/door", "/aux"]}

@app.post("/configure")
def configure(config_data: dict):
    global runtime
    try:
        system_config = config_data.get('system_config')
        startup_config = config_data.get('startup_config')

        runtime = Runtime(system_config, startup_config)

        response = JSONResponse(content={
            "route": "/configure",
            "message": "Configure Endpoint",
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/configure",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
    return response

@app.post("/destroy")
def destroy(_: Runtime = Depends(ensure_runtime)):
    try:
        runtime.destroy()

        response = JSONResponse(content={
            "route": "/destroy",
            "message": "Destroy Endpoint",
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/destroy",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
    return response

@app.get("/auto")
def get_auto(_: Runtime = Depends(ensure_runtime)):
    try:
        response = JSONResponse(content={
            "route": "/auto",
            "message": "Automation Endpoint",
            "data": {"sunrise_offset": runtime.auto.sunrise_offset,
                    "sunset_offset": runtime.auto.sunset_offset,
                    "active_sunrise": runtime.auto.active_sunrise(),
                    "active_sunset": runtime.auto.active_sunset(),
                    "active_current": runtime.auto.active_current(),
                    "is_alive": runtime.auto.scheduler.is_alive()}
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/auto",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
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
                "route": "/auto",
                "message": f"'{option}' is not a valid option",
                "error": "Invalid option"
            }, status_code=400)
        response = JSONResponse(content={
            "route": "/auto",
            "message": "Automation Endpoint",
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/auto",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
    return response

@app.get("/door")
def get_door(_: Runtime = Depends(ensure_runtime)):
    try:
        response = JSONResponse(content={
            "route": "/door",
            "message": "Door Endpoint",
            "data": {"status": runtime.door.status()}
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/door",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
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
                "route": "/door",
                "message": f"'{option}' is not a valid option",
                "error": "Invalid option"
            }, status_code=400)
        response = JSONResponse(content={
            "route": "/door",
            "message": "Door Endpoint",
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/door",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
    return response

@app.get("/aux")
def get_aux(_: Runtime = Depends(ensure_runtime)):
    try:
        response = JSONResponse(content={
            "route": "/aux",
            "message": "Auxiliary Endpoint",
            "data": {"is_alive": runtime.aux.is_alive()}
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/aux",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
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
                "route": "/aux",
                "message": f"'{option}' is not a valid option",
                "error": "Invalid option"
            }, status_code=400)
        response = JSONResponse(content={
            "route": "/aux",
            "message": "Auxiliary Endpoint",
        }, status_code=200)
    except Exception as e:
        response = JSONResponse(content={
            "route": "/aux",
            "message": "An error occurred",
            "error": str(e)
        }, status_code=500)
    return response
