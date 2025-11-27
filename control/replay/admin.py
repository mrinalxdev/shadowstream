
import redis
import grpc
from django.contrib import admin, messages
from .models import ReplayJob

import shadowstream_pb2
import shadowstream_pb2_grpc

REDIS_STREAM = "shadowstream:events"
@admin.action(description="run selected replay job")
def run_replay_job(modeladmin, request, queryset):

    try :
        r = redis.from_url("redis://redis:6379/0")
    except Exception as e:
        messages.error(request, f"Could not connect to redis : {e}")
        return 
    

    #connecting to grpc replayer layer 

    channel = grpc.insecure_channel('localhost:50051')
    stub = shadowstream_pb2_grpc.ReplayerStub(channel)



    for job in queryset:
        job.status = "running"

        #converting datetime to millisecond timestamps for redis id range
        start_ms = int(job.start_time.timestamp() * 1000)
        end_ms = int(job.end_time.timestamp() * 1000)



        #fetching the range from redis stream
        #xrange stream start end

        events = r.xrange(REDIS_STREAM, min=start_ms, max=end_ms)


        count = 0
        try :
            for message_id, data in events:

                #this will contain the serialized protobuf
                #than its suppose to construct the replay request with
                #a specific structure I guess
                #than we can have a to send a stub to gRPC server 
                #like a request ......
                pb_payload = data.get(b'payload')


                if not pb_payload:
                    continue

                change_record = shadowstream_pb2.ChangeRecord()
                change_record.ParseFromString(pb_payload)


                req = shadowstream_pb2.ReplayRequest(
                    job_id =str(job.id),
                    event=change_record,
                    virtual_time=change_record.commit_time
                )

                stub.ReplayEvent(req)
                count += 1
            
            job.status="completed"
            messages.success(request, f"Job {job.id} replayed {count} events successfully")
        
        except grpc.RpcError as e:
            job.status = "failed"
            messages.error(request, f"gRPC error : {e}")

        

        job.save()

@admin.register(ReplayJob)
class ReplayJobAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "speed_factor", "status")
    actions = [run_replay_job]

