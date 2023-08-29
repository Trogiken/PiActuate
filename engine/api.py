from fastapi import FastAPI, Depends, HTTPException
from source import Runtime
import options as opt

runtime = Runtime.getInstance()

app = FastAPI()

# Start this api
# uvicorn main:app --host 0.0.0.0 --port 8000

# TODO Configure setup_script.sh to start api server on boot

# TODO POST configure: If you transmit the database object as a dict, the way runtime accesses it
# will not work. You need to transmit the object itself. Try to use pickle to serialize
# the object and send it over the wire. Then deserialize it on the other end.

# TODO Use switch cases
# TODO Use request bodys instead of query params to send data


def ensure_runtime():
    if runtime is None:
        raise HTTPException(status_code=500, detail="Runtime not initialized")


@app.get("/")
def root():
    return {"message": "Runtime API"}


@app.post("/configure")
def configure(system_config, startup_config):
    global runtime
    try:
        runtime = Runtime(system_config, startup_config)
    except Exception as e:
        return {"message": "Failed", "error": f"{e}"}, 400
    return {"message": "Success"}


@app.post("/destroy")
def destroy(_: Runtime = Depends(ensure_runtime)):
    try:
        runtime.destroy()
    except Exception as e:
        return {"message": "Failed", "error": f"{e}"}, 400
    return {"message": "Success"}

@app.get("/auto/{option}")
def get_auto(option: opt.GetAuto, _: Runtime = Depends(ensure_runtime)):
    match option:
        case opt.GetAuto.sunrise_offset:
            return {"sunrise_offset": runtime.auto.sunrise_offset}
        case opt.GetAuto.sunset_offset:
            return {"sunset_offset": runtime.auto.sunset_offset}
        case opt.GetAuto.active_sunrise:
            return {"active_sunrise": runtime.auto.active_sunrise}
        case opt.GetAuto.active_sunset:
            return {"active_sunset": runtime.auto.active_sunset}
        case opt.GetAuto.active_current:
            return {"active_current": runtime.auto.active_current}
        case opt.GetAuto.is_alive:
            return {"is_alive": runtime.auto.is_alive()}
        case _:
            return {"message": "Invalid option"}, 400


@app.post("/auto/{option}")
def post_auto(option: opt.PostAuto, _: Runtime = Depends(ensure_runtime)):
    match option:
        case opt.PostAuto.sunrise_offset:
            runtime.auto.sunrise_offset = option
        case opt.PostAuto.sunset_offset:
            runtime.auto.sunset_offset = option
        case opt.PostAuto.start:
            runtime.auto.start()
        case opt.PostAuto.stop:
            runtime.auto.stop()
        case opt.PostAuto.refresh:
            runtime.auto.refresh()
        case _:
            return {"message": "Invalid option"}, 400
    return {"message": "Success"}


@app.get("/door/{option}")
def get_door(option: opt.GetDoor, _: Runtime = Depends(ensure_runtime)):
    match option:
        case opt.GetDoor.status:
            return {"status": runtime.door.status()}
        case _:
            return {"message": "Invalid option"}, 400


@app.post("/door/{option}")
def post_door(option: opt.PostDoor, _: Runtime = Depends(ensure_runtime)):
    match option:
        case opt.PostDoor.open:
            runtime.door.open()
        case opt.PostDoor.close:
            runtime.door.close()
        case _:
            return {"message": "Invalid option"}, 400
    return {"message": "Success"}


@app.get("/aux/{option}")
def get_aux(option: opt.GetAux, _: Runtime = Depends(ensure_runtime)):
    match option:
        case opt.GetAux.is_alive:
            return {"is_alive": runtime.aux.is_alive()}
        case _:
            return {"message": "Invalid option"}, 400


@app.post("/aux/{option}")
def post_aux(option: opt.PostAux, _: Runtime = Depends(ensure_runtime)):
    match option:
        case opt.PostAux.run_aux:
            runtime.aux.run_aux()
        case opt.PostAux.stop_aux:
            runtime.aux.stop_aux()
        case _:
            return {"message": "Invalid option"}, 400
    return {"message": "Success"}
