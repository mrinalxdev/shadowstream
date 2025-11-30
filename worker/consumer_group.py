import threading 
import time
from kafka import KafkaConsumer

import redis
from shadowstream_pb2 import ChangeRecord
import grpc


class ParallelConsumer:
    def __init__(self, group_id, num_consumers=3):
        self.group_id = group_id


        self.num_consumers = num_consumers

        self.redis = redis.from_url("redis://redis:6379/0")
        self.consumers = []

    
    def process_message(self, message, consumer_id):

        try:
            event = ChangeRecord()
            event.ParseFromString(message.value)


            print(f"[consume - {consumer_id}] processing : {event.table}@{event.commit_time}")

            if "users" in event.table:
                time.sleep(0.2)
            
            else :
                time.sleep(0.05)


            
            #marking the progress in redis
            self.redis.hincrby(f"consumer:{self.group_id}:progress", f"consumer_{consumer_id}", 1)

        

        except Exception as e :
            print(f"Consumer - {consumer_id} error : {e}")

    
    def start_consumer(self, consumer_id):

        consumer = KafkaConsumer (
            'shadowstream.archive',
            bootstrap_servers=['kafka:9092'],
            group_id=self.group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=None,
        )


        print(f"consumer - {consumer_id} started in group {self.group_id}")


        for message in consumer:
            self.process_message(message, consumer_id)
    

    def start_all(self):

        for i in range(self.num_consumers):
            thread = threading.Thread(target=self.start_consumer, args=(i,))


            thread.daemon = True

            self.consumers.append(thread)
            thread.start()
            self.consumers.append(thread)


            thread.start()
    

    def get_progress(self):

        return self.redis.hgetall(f"consumer : {self.group_id}:progress")
    


def main():

    analytics_consumers = ParallelConsumer("analytics-group", 2)
    backup_consumers = ParallelConsumer("backup-group", 1)


    print("starting analytics consumer group(2 consumers) ....")
    analytics_consumers.start_all()

    print("starting backup consumer group (1 consumer) ...")

    backup_consumers.start_all()



    #so now we will be monitoring the progress the whole time
    #which will be running in a loop 
    while True:
        time.sleep(5)

        print("analytics progress : ", analytics_consumers.get_progress())
        print("backup progress : ", backup_consumers.get_progress())


if __name__ == "__main__":
    main()
