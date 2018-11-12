# import json
from csv import DictWriter
import os
# from models import DecodeComment, DecodeSubmission

# data = []
# with open("./raw/legaladvice.json", "r") as fp:
#     raw = json.load(fp)
#     for d in raw:
#         data.append(DecodeSubmission(d))

def cleanColumns(columns):
    if len(columns) < 3:
        return columns
        
    temp = columns[2]
    columns[2] = columns[0]
    columns[0] = temp

    return columns

def writeNodesToCsv(filename, columns, data):
    writer = DictWriter(filename, fieldnames = columns, restval = "na")
    writer.writeheader()
    
    for obj in data:
        if "body" in obj.__dict__:
            obj.__dict__["body"] = "" # remove the body text
        writer.writerow(obj.__dict__)

def cleanCsv(i_stream, o_stream):
    with open(i_stream,"r") as fp:
        with open(o_stream,"w") as fp2:
            first = True
            lines = fp.readlines()
        
            for line in lines:
                if first:
                    first = False
                    line = line.replace(',id_0','')
                    line = line.replace(',body','')
                else:
                    line = line.replace(',,',',')

                if line.isspace():
                    continue
                fp2.write(line)
    
    os.remove(i_stream)

    

    
    
