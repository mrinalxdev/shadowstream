import os 
import time 
import json
import requests

from shadowstream_pb2 import ChangeRecord, ReplayRequest


REDIS_STREAM = "shadowstream:events"
TARGET_URL = os.getenv("TARGET", "http://mock:8080/replay")


BASE_REAL_TIME = None
BASE_EVENT_TIME = None
SPEED_FACTOR = 2.0

def replay_event(event: ChangeRecord, job_id: str, virtual_time: int):


    req = ReplayRequest(
        job_id = job_id,
        event = event,
        virtual_time = virtual_time
    )

    try:
        requests.post(
            TARGET_URL,
            json={
                "job_id": job_id,
                "event" : {
                    "table": event.table,
                    "operation": event.operation,
                    "new": dict(event.new),
                    "time": virtual_time
                }
            }
        )

        print(f"replayed {event.operation} on {event.table} at virtual time {virtual_time}")
    except Exception as e:
        print("failed to replay", e)


def main():

    import redis
    r = redis.from_url(os.getenv("REDIS", "redis://localhost:6379/0"))

    last_id = "0-0"


    print("worker starting")

    while True:
        streams = r.xread({REDIS_STREAM: last_id}, count=1, block=1000)

        if not streams:
            time.sleep(0.1)
            continue
        


        stream_key, messages = streams[0]

        msg_id, fields = messages[0]
        last_id = msg_id

        payload = fields[b"payload"]
        event_time_ms = int(fields[b"time_ms"])

        event = ChangeRecord()
        event.ParseFromString(payload)

        global BASE_REAL_TIME, BASE_EVENT_TIME

        if BASE_REAL_TIME is None:
            BASE_REAL_TIME = time.time() * 1000
            BASE_EVENT_TIME = event_time_ms

        

        elapsed_event_ms = event_time_ms - BASE_EVENT_TIME
        virtual_time_ms = BASE_REAL_TIME + (elapsed_event_ms / SPEED_FACTOR)

        now_ms = time.time() * 1000
        if virtual_time_ms > now_ms:
            time.sleep((virtual_time_ms - now_ms) / 1000)


        replay_event(event, job_id="demo", virtual_time=int(virtual_time_ms))


if __name__ == "__main__":
    main()