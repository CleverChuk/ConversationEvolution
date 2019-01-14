if __name__ == "__main__":
    from create_data_for_d3 import (Query, D3helper)
    query = Query()

    data = query.all()
    # print(data[20].start_node)

    filename = "data.json"
    data = D3helper.transform(*data)

    D3helper.dumpJSON(filename, data)
