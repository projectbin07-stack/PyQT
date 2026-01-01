import json
import time

def send_pickup_data(locker_no, pin, mode=""):
    """
    Called after successful PIN validation.
    locker_no : int
    pin       : str
    mode      : str ("PICKUP" or "DROP")
    """

    payload = {
        "locker_no": int(locker_no),
        "work": mode,  # "PICKUP" or "DROP"
        "timestamp": time.time()
    }

    print(f"[ASSIGN] {mode} request received")
    print(payload)

    try:
        with open("log.json", "a") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception as e:
        print("[ASSIGN] Log error:", e)
