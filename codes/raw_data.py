import json
from models import DecodeComment, DecodeSubmission

data = []
with open("./raw/legaladvice.json", "r") as fp:
    raw = json.load(fp)
    for d in raw:
        data.append(DecodeSubmission(d))

for sub in data:
    for comment in sub.comments:
        print(comment.body)
