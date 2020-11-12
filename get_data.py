import json
import data


out = {'goals': data.goals, 'teachers': data.teachers}
with open("data.txt", "w") as f:
    json.dump(out, f)
