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

def writeEdgeHeaderFile(filename, edgeProperties = []):
    header = [":START_ID"] + edgeProperties
    header.append(":END_ID")
    header.append(":TYPE")

    filename = filename.split(".")
    filename = "."+filename[1] + "_header." + filename[2]
    fname = "./raw/temp.csv"

    with open(fname,"w") as fp:
        text = ",".join(header)
        fp.write(text)
    
    cleanCsv(fname,filename)

    return header

def writeEdgesToFile(filename, data):
    if not isinstance(data, list):
        raise TypeError("data must be a list of edges")
    
    n = len(data[0])
    if n < 2:
        raise TypeError("each edge must have two nodes and an optional relationship")
    
    prop = list(data[0][2].keys())
    #  remove type from the header because its a duplicate
    for i in range(len(prop)):
        if prop[i] == 'type':
            prop.pop(i)
            break
    header = writeEdgeHeaderFile(filename, prop)

    with open(filename, "w", newline='') as fp:
        dictWriter = DictWriter(fp,header)
        for edge in data:
            if len(edge) > 2:
                node_1 , node_2 , prop = edge
                relationship = prop.pop("type","none")

                d = {":START_ID":node_1.id, ":END_ID":node_2.id}
                d.update(prop)
                d[":TYPE"] = relationship
            else:
                node_1 , node_2 = edge
                relationship = "NOT SPECIFIED"

                d = {":START_ID":node_1.id, ":END_ID":node_2.id}
                d[":TYPE"] = relationship

            dictWriter.writerow(d)

def writeNodeHeaderFile(filename, header):
    h = header[:-2]
    h.append(":LABEL")
    if '.' not in filename:
        raise Exception("invalid file name format")
    if not isinstance(header,list):
        raise TypeError()

    filename = filename.split(".")
    filename = "."+filename[1][:-4] + "_node_header." + filename[2]

    fname = "./raw/temp.csv"

    with open(fname,"w") as fp:
        h[0] = h[0]+":ID"
        text = ",".join(h)
        fp.write(text)
    
    cleanCsv(fname,filename)



def writeNodesToCsv(file, columns, data):
    writer = DictWriter(file, fieldnames = columns, restval = "na")
    writeNodeHeaderFile(file.name,columns)
    
    for obj in data:
        if "body" in obj.__dict__:
            obj.__dict__["body"] = "" # remove the body text for a clean csv
        writer.writerow(obj.__dict__)

def cleanCsv(i_stream, o_stream):
    with open(i_stream,"r") as fp:
        with open(o_stream,"w") as fp2:
            lines = fp.readlines()
        
            for line in lines:
                line = line.replace(',id_0','')
                line = line.replace(',body','')                    
                line = line.replace(',,',',')

                if line.isspace():
                    continue
                
                # remove trailing comma
                c = line[-2]
                if c == ',':
                    line = line[:-2]+ '\n'
                fp2.write(line)
    
    os.remove(i_stream)

    

    
    
