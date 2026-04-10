import json
import random
import gevent
import time
import math
import uuid
from locust import HttpUser, task, between, LoadTestShape
from gevent.lock import Semaphore
from locust import events
from datetime import datetime

BASE_HEADERS = {
    'X-M2M-Origin': 'SM',
    'X-M2M-RVI': '4',
    'Accept': 'application/json'
}


def build_headers():
    headers = BASE_HEADERS.copy()
    headers['X-M2M-RI'] = f"rqi-{uuid.uuid4().hex}"
    return headers

class StepLoadShape(LoadTestShape):
    step_time = 60
    step_load = 5
    spawn_rate = 10
    time_limit = 7200

    def tick(self):
       run_time = self.get_run_time()

       if run_time > self.time_limit:
           return None

       current_step = math.floor(run_time / self.step_time) + 1

       # Calculate the remainder when dividing current_step by 6 (to get multiples of 10)
       remainder = current_step % 6
        
       # Calculate the adjusted current_step
       adjusted_step = current_step + (6 - remainder) if remainder != 0 else current_step
        
       return (adjusted_step * self.step_load, self.spawn_rate)


max_users = 500
users_waiting = 0
event = gevent.event.Event()
lock = Semaphore()



class MyUser(HttpUser):
    host = 'http://10.2.16.116:7601'
    wait_time = between(1, 1)
    nodes_data = None

    def on_start(self):
        self.start_time = time.time()
        self.all_nodes = []

        with open('nodes.json') as f:
            self.nodes_data = json.load(f)

        for node_type, node_items in self.nodes_data.items():
            for item in node_items:
                self.all_nodes.append((node_type, item)) 

    @task
    def increase_users(self):
        global users_waiting
        global event

        # Calculate the time in seconds elapsed since the start of the minute
        seconds_elapsed = datetime.now().second

        # Check if the seconds elapsed matches the desired intervals
        if seconds_elapsed in [0, 10, 20, 30, 40, 50]:
            with lock:
                users_waiting += 1
                print(f"{users_waiting} users waiting... ({users_waiting}/{max_users})")
                if users_waiting >= self.environment.runner.user_count:
                    print("All users are ready!")
                    event.set()

            event.wait()  # Wait for the event to be cleared before proceeding
            time.sleep(10)

            user_num = self.environment.runner.user_count
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')

            print(f"User {user_num} - Time: {current_time}")

            node_type, item = random.choice(self.all_nodes)
            url = f"/mn-cse-tenant-a/{node_type.upper() if node_type.upper().startswith('AE-') else 'AE-' + node_type.upper()}/{item}/Data"
            print(f"Sending request at: {current_time}")

            self.client.get(url, headers=build_headers())

            with lock:
                users_waiting -= 1
                if users_waiting == 0:
                    event.clear()
