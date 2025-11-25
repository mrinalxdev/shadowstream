import time 
import json
import redis
import psycopg2
from psycopg2.extras import LogicalReplicationConnection
from shadowstream_pb2 import ChangeRecord 


REDIS_STREAM = "shadowstream:events"
REPLICATION_SLOT = "shadowstream_slot"


def main():
    r = redis.from_url("redis://redis:6379/0")
    
    conn = psycopg2.connect(
        host="postgres",
        user="repluser",
        password="replpass",
        dbname="shadowdb",
        connection_factory=LogicalReplicationConnection
    )
    
    
    cur = conn.cursor()
    
    
    try:
        cur.create_replication_slot(REPLICATION_SLOT, output_plugin="wal2json")
    except psycopg2.ProgrammingError:
        pass #this will just prompt that the slot exists
    
    
    options = {
        "format-version" : "2",
        "include-xids" : "0",
        "include-timestamp" : "1",
        "add-tables" : "public.events"
    }
    
    
    cur.start_replication(
        slot_name = REPLICATION_SLOT,
        options=options,
        decode=True
    )
    
    
    def consume(msg):
        msg.cursor.send_feedback(flush_lsn=msg.data_start)
        payload = json.loads(msg.payload)
        
        
        for change in payload.get("change", []):
            commit_time = int(payload["timestamp"][:10])
            
            record = ChangeRecord (
                lsn = str(msg.data_start),
                commit_time=commit_time  * 1000,
                table=change["table"]
            )
            
            #now we will be pushing this to redis streams 
            r.xadd(
                REDIS_STREAM,
                {
                    "payload" : record.SerializeToString(),
                    "time_ms" : str(record.commit_time)
                },
                
                id = f"{record.commit_time} - {record.lsn}"
            )
            
            
            return True
    cur.consume_stream(consume)
    
    
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("Ingestor Crashed : ", e)
            time.sleep(5)



#this will be reading WAL and converts to protobuf and pushes to redis stream and time ordered ID ..
