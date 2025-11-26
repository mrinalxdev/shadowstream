import grpc
from concurrent import futures
import time
import logging

import shadowstream_pb2
import shadowstream_pb2_grpc

class ReplayerService(shadowstream_pb2_grpc.ReplayerServicer):
    def ReplayEvent(self, request, context):
        
        #this part will be recieving the historical event and 'replays' it.
        #more over we can plug it and this would write to a target DB.

        job_id = request.job_id
        event = request.event
        v_time = request.virtual_time


        print(f"[job : {job_id}] replaying change on table '{event.table}'")
        print(f"-- time : {v_time}")
        print(f"-- lsn: {event.lsn}")


        for new_entry in event.new:
            print(f" +SET {new_entry.key} = {new_entry.value}")
        

        #a simple simulation process time based on job speed
        time.sleep(0.1)


        return shadowstream_pb2.ReplayResponse(success=True)
    


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    shadowstream_pb2_grpc.add_ReplayerServicer_to_server(ReplayerService(), server)
    server.add_insecure_port('[:]:50051')

    print('replayer service started on port 50051')

    server.start()

    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()