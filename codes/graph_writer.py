# Author: Chukwubuikem Ume-Ugwa
# Purpose: Functions use to write nodes and edges to a csv file
#          using Neo4j schema specification

from csv import DictWriter
import os
from mapper_functions import getProperties

def writeEdgeHeaderFile(filename, hasType = True, edgeProperties = [], values = []):
    """
        writes Neo4j relationship header plus the given
        edge properties to the given filename
        creates file if it does not exist otherwise overwrite

        :type filename : str
        :type edgeProperties: list, edge properties
        :type hasType : boolean, say if the relationship is specified
        :type values: list, used to determine the data type of each edge property
    """
    header_1 = [":START_ID"] + edgeProperties
    header_1.append(":END_ID")
    

    # add data type to header
    # for i in range(len(edgeProperties)):
    #     s = "".join(list(str(type(values[i])))[8:][:-2])
    #     edgeProperties[i] = edgeProperties[i] + ":" + s.upper()


    header = [":START_ID"] + edgeProperties
    header.append(":END_ID")
    
    # check if the edge has a type label
    if hasType:
        header.append(":TYPE")
        header_1.append(":TYPE")

    filename = filename.split(".")
    filename = "."+filename[1] + "_header." + filename[2]
    fname = "./raw/temp.csv"

    with open(fname,"w") as fp:
        text = ",".join(header)
        fp.write(text)
    
    cleanCsv(fname, filename)

    return header_1

def writeEdgesToFile(filename, data, rel = None, directed = False):
    """
        writes graph edges to file in the form
        Neo4j understands to the given filename
        creates file if it does not exist otherwise overwrite

        :type filename : str
        :type data: list of edges, 
        :type rel: str, relationship type
        :type directed: boolean, specifies whether the edges are directed or not
    """
    if not isinstance(data, list):
        raise TypeError("data must be a list of edges")
    
    n = len(data[0])
    if n < 2:
        raise TypeError("each edge must have two nodes and a relationship")

    if (n == 2 and rel == None) or (rel != None and rel.isspace()):
        raise Exception("must rel cannot be None or empty")

    if n > 2:
        prop = list(data[0][2].keys())
        values = list(data[0][2].values())
        #  remove type from the header because its a duplicate
        for i in range(len(prop)):
            if prop[i] == 'type':
                prop.pop(i)
                break
        header = writeEdgeHeaderFile(filename, edgeProperties = prop, values= values)
    else:
        header = writeEdgeHeaderFile(filename, hasType = rel != None)

    with open(filename, "w", newline='') as fp:
        dictWriter = DictWriter(fp,header)
        dictWriter.writeheader()

        for edge in data:
            if len(edge) > 2:
                node_1 , node_2 , prop = edge
                relationship = prop.pop("type", rel)
    
                d = {":START_ID":node_1.id, ":END_ID":node_2.id}
                d.update(prop)
                d[":TYPE"] = relationship

            else:
                node_1 , node_2 = edge
                d = {":START_ID":node_1.id, ":END_ID":node_2.id}
                if rel != None:
                    d[":TYPE"] = rel
           
            if directed:
                dictWriter.writerow(d)
            else:
                dictWriter.writerow(d)
                temp = d[":START_ID"]
                d[":START_ID"] = d[":END_ID"]
                
                d[":END_ID"] = temp
                dictWriter.writerow(d)

def writeNodeHeaderFile(filename, header, values):
    """
        writes header to the given filename
        creates file if it does not exist otherwise overwrite

        :type filename : str
        :type header: list
    """
    h = header[:-2] # remove the type and id_0 column

    # add data type to header
    # v = values[:-2]
    # for i in range(len(v)):
    #     s = "".join(list(str(type(v[i])))[8:][:-2])
    #     if s == "str":
    #         continue
    #     if s == "bool":
    #         s +="ean"
            
    #     h[i] = h[i] + ":" + s.upper()

    h.append(":LABEL")
    if '.' not in filename:
        raise Exception("invalid file name format")
    if not isinstance(header,list):
        raise TypeError()

    filename = filename.split(".")
    filename = "." + filename[1][:-4] + "_node_header." + filename[2]
    fname = "./raw/temp.csv"

    with open(fname,"w") as fp:
        h[0] = ":ID"
        text = ",".join(h)
        fp.write(text)
    
    cleanCsv(fname,filename)

    return h



def writeNodesToCsv(filename, data):
    """
        writes header plus the given nodes data
        to the given filename.

        :type filename : str
        :type header: list
        :type data : list
    """
    temp = "./raw/temp.csv"
    header = getProperties(data[0])
    with open(temp,"w") as file:
        writer = DictWriter(file, fieldnames = header, restval = "na")
        v = list(data[0].__dict__.values())
        header = writeNodeHeaderFile(filename, header, v)

        file.write(",".join(header))
        file.write("\n")
        
        for obj in data:
            if "body" in obj.__dict__:
                obj.__dict__["body"] = "" # remove the body text for a clean csv
            writer.writerow(obj.__dict__)
    
    cleanCsv(temp,filename)

def cleanCsv(i_stream, o_stream):
    """
        removes uunneeded headers and empty column
        from the csv.

        :type i_stream : str -> file to clean
        :type o_stream: str -> file to save output
    """
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
    
    try:
        os.remove(i_stream)
    except:
        pass


    
    
