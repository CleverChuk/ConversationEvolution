# Author: Chukwubuikem Ume-Ugwa
# Purpose: Functions use to write nodes and edges to a csv file
#          using Neo4j schema specification

from csv import DictWriter
import os
from mapper_functions import getProperties

"""
@param 
    :type
    :description:
"""

class Neo4jGrapher:
    """
        Class used to write graph in Neo4j graph format
    """
    def writeEdgeHeaderFile(self, filename, has_type=True, property_keys=[], property_type=[]):
        """
            writes Neo4j relationship header to file
            creates file if it does not exist otherwise overwrite

            @param filename
                :type string
                :description: the name of the file or file path

            @param has_type
                :type boolean
                :description: say if the relationship is specified

            @param property_keys
                :type list
                :description: a list of edge properties

            @param property_type
                :type list
                :description: used to determine the data type of each edge property
        """
        header_1 = [":START_ID"] + property_keys
        header_1.append(":END_ID")

        # add data type to header
        # for i in range(len(property_keys)):
        #     s = "".join(list(str(type(property_type[i])))[8:][:-2])
        #     property_keys[i] = property_keys[i] + ":" + s.upper()

        header = [":START_ID"] + property_keys
        header.append(":END_ID")

        # check if the edge has a type label
        if has_type:
            header.append(":TYPE")
            header_1.append(":TYPE")

        filename = filename.split(".")
        filename = "."+filename[1] + "_header." + filename[2]
        fname = "./raw/temp.csv"

        with open(fname, "w") as fp:
            text = ",".join(header)
            fp.write(text)

        self.cleanCsv(fname, filename)

        return header_1


    def writeEdgesToFile(self, filename, data, rel=None, directed=False):
        """
            writes graph edges to file in the form
            Neo4j understands to the given filename
            creates file if it does not exist otherwise overwrite

            @param filename
                :type string
                :description: the name of the file or file path

            @param data
                :type list
                :description: list of edges, 

            @param rel
                :type string
                :description: relationship type

            @param directed
                :type boolean
                :description: specifies whether the edges are directed or not
        """
        if not isinstance(data, list):
            raise TypeError("data must be a list of edges")

        n = len(data[0])
        if n < 2:
            raise TypeError("each edge must have two nodes and a relationship")

        if (n == 3 and rel == None) or (rel != None and rel.isspace()):
            raise Exception("must rel cannot be None or empty")

        if n > 2:
            property_keys = list(data[0][2].keys())
            property_type = list(data[0][2].values())
            #  remove type from the header because its a duplicate
            for i in range(len(property_keys)):
                if property_keys[i] == 'type':
                    property_keys.pop(i)
                    break
            header = self.writeEdgeHeaderFile(
                filename, property_keys=property_keys, property_type=property_type)
        else:
            header = self.writeEdgeHeaderFile(filename, has_type=rel != None)

        with open(filename, "w", newline='') as fp:
            dictWriter = DictWriter(fp, header)
            dictWriter.writeheader()

            for edge in data:
                if len(edge) > 2:
                    node_1, node_2, property_keys = edge
                    relationship = property_keys.pop("type", rel)

                    d = {":START_ID": node_1.id, ":END_ID": node_2.id}
                    d.update(property_keys)
                    d[":TYPE"] = relationship

                else:
                    node_1, node_2 = edge
                    d = {":START_ID": node_1.id, ":END_ID": node_2.id}
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


    def writeNodeHeaderFile(self, filename, header, property_type):
        """
            writes header to the given filename
            creates file if it does not exist otherwise overwrite

            @param filename
                :type string
                :description: filename of file path

            @param header
                :type list
                :description: list of node attributes

            @param property_type
                :type list
                :description: list of node attribute property_type used to determine their data type
        """
        h = header[:-2]  # remove the type and id_0 column

        # add data type to header
        # v = property_type[:-2]
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
        if not isinstance(header, list):
            raise TypeError()

        filename = filename.split(".")
        filename = "." + filename[1][:-6] + "_node_header." + filename[2]
        fname = "./raw/temp.csv"

        with open(fname, "w") as fp:
            h[0] = ":ID"
            text = ",".join(h)
            fp.write(text)

        self.cleanCsv(fname, filename)

        return h


    def writeNodesToCsv(self, filename, data):
        """
            writes header plus the given nodes data
            to the given filename.

            @param filename
                :type string
                :description: filename or file path

            @param data 
                :type list
                :description: list of nodes
        """
        temp = "./raw/temp.csv"
        header = getProperties(data[0])
        with open(temp, "w") as file:
            writer = DictWriter(file, fieldnames=header, restval="na")
            v = list(data[0].__dict__.values())
            header = self.writeNodeHeaderFile(filename, header, v)

            file.write(",".join(header))
            file.write("\n")

            for obj in data:
                if "body" in obj.__dict__:
                    # remove the body text for a clean csv
                    obj.__dict__["body"] = ""
                writer.writerow(obj.__dict__)

        self.cleanCsv(temp, filename)


    def cleanCsv(self, input_fname, out_fname):
        """
            removes uunneeded headers and empty column
            from the csv.

            @param input_fname
                :type string
                :description: name of file to clean

            @param out_fname
                :type string
                :description: name of file to save output
        """
        with open(input_fname, "r") as fp:
            with open(out_fname, "w") as fp2:
                lines = fp.readlines()

                for line in lines:
                    line = line.replace(',id_0', '')
                    line = line.replace(',body', '')
                    line = line.replace(',,', ',')

                    if line.isspace():
                        continue

                    # remove trailing comma
                    c = line[-2]
                    if c == ',':
                        line = line[:-2] + '\n'
                    fp2.write(line)

        try:
            os.remove(input_fname)
        except:
            pass
