import keyboard
import pymongo
from os import system
    
client = pymongo.MongoClient("localhost", 27017)
db = client.linkedinbot
jobs = db.jobs
title_annotations = db.title_annotation

available_jobs = list(jobs.find({ "available": True }))
positions = list(set([ job["position"] for job in available_jobs ]))
positions.sort()

operations = [ 'y', 'n', 'q', 'w' ]

index = 0
while True:
    if index == len(positions):
        break
    position = positions[index]
    current = title_annotations.find_one({ "position": position })
    _ = system("clear")
    print(f"{index + 1}/{len(positions)}")
    print(position)
    if current is not None:
        index += 1
        continue

    operation = None
    while True:
        for op in operations:
            if keyboard.is_pressed(op):
                operation = op
                while keyboard.is_pressed(op):
                    pass
                break
        if operation is not None:
            break
    if operation == "y":
        print("Yes")
        title_annotations.insert_one({ "position": position, "annotation": True })
        index += 1
    elif operation == "n":
        print("No")
        title_annotations.insert_one({ "position": position, "annotation": False })
        index += 1
    elif operation == 'q':
        if index > 0:
            index -= 1
            title_annotations.delete_one({ "position": positions[index] })
    elif operation == 'w':
        index += 1
