# import copy
# import threading
# import time
# from fastapi import APIRouter
# from pydantic import conint
# from ..models.type_dict import Worker
# # from ..router import router

# api_router = APIRouter(prefix="/heartbeat")

# heartbeat_queue: list[Worker] = []


# @api_router.post("/")
# def heartbeat(worker: Worker):
#     heartbeat_queue.append(worker)


# def consume_loop():
#     while True:
#         worker_data = copy.deepcopy(heartbeat_queue)
#         router.update_worker_data(worker_data)
#         heartbeat_queue.clear()
#         time.sleep(1)

# thread = threading.Thread(target=consume_loop, daemon=True)
# thread.start()
