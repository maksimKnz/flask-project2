import json
import data


emodji = {"travel": "⛱", "study": "🏫", "work": "🏢", "relocate": "🚜"}
out = {'goals': data.goals, 'teachers': data.teachers, 'emodji': emodji}
with open("data.txt", "w") as f:
    json.dump(out, f)
