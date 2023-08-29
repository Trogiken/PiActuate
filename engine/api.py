from fastapi import FastAPI
from source.runtime import Runtime
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


@app.get("/auto/{option}")
def get_auto(option: opt.GetAuto):
    global runtime
    if option == opt.GetAuto.sunrise_offset:
        return {"sunrise_offset": runtime.auto.sunrise_offset}
    elif option == opt.GetAuto.sunset_offset:
        return {"sunset_offset": runtime.auto.sunset_offset}
    elif option == opt.GetAuto.active_sunrise:
        return {"active_sunrise": runtime.auto.active_sunrise}
    elif option == opt.GetAuto.active_sunset:
        return {"active_sunset": runtime.auto.active_sunset}
    elif option == opt.GetAuto.active_current:
        return {"active_current": runtime.auto.active_current}
    elif option == opt.GetAuto.is_alive:
        return {"is_alive": runtime.auto.is_alive()}
    else:
        return {"message": "Invalid option"}, 400


@app.post("/auto/{option}")
def post_auto(option: opt.PostAuto):
    global runtime
    if option == opt.PostAuto.sunrise_offset:
        runtime.auto.sunrise_offset = option
        return {"message": "Success"}
    elif option == opt.PostAuto.sunset_offset:
        runtime.auto.sunset_offset = option
        return {"message": "Success"}
    elif option == opt.PostAuto.start:
        runtime.auto.start()
        return {"message": "Success"}
    elif option == opt.PostAuto.stop:
        runtime.auto.stop()
        return {"message": "Success"}
    elif option == opt.PostAuto.refresh:
        runtime.auto.refresh()
        return {"message": "Success"}
    else:
        return {"message": "Invalid option"}, 400


@app.get("/door/{option}")
def get_door(option: opt.GetDoor):
    global runtime
    if option == opt.GetDoor.status:
        return {"status": runtime.door.status()}
    else:
        return {"message": "Invalid option"}, 400


@app.post("/door/{option}")
def post_door(option: opt.PostDoor):
    global runtime
    if option == opt.PostDoor.open:
        runtime.door.open()
        return {"message": "Success"}
    elif option == opt.PostDoor.close:
        runtime.door.close()
        return {"message": "Success"}
    else:
        return {"message": "Invalid option"}, 400


@app.get("/aux/{option}")
def get_aux(option: opt.GetAux):
    global runtime
    if option == opt.GetAux.is_alive:
        return {"is_alive": runtime.aux.is_alive()}
    else:
        return {"message": "Invalid option"}, 400


@app.post("/aux/{option}")
def post_aux(option: opt.PostAux):
    global runtime
    if option == opt.PostAux.run_aux:
        runtime.aux.run_aux()
        return {"message": "Success"}
    elif option == opt.PostAux.stop_aux:
        runtime.aux.stop_aux()
        return {"message": "Success"}
    else:
        return {"message": "Invalid option"}, 400