from joern.all import JoernSteps


def get_all_nodes(db):
    query_param_str = 'g.V()'
    results = db.runGremlinQuery(query_param_str)
    list_node = []
    if results != []:
        i =0
        for re in results:
            if i>=5:
                break
            i+=1
            list_node.append(re)
    return list_node

def get_all_edges(db):
    query_param_str = 'g.E()'
    results = db.runGremlinQuery(query_param_str)
    list_node = []
    if results != []:
        i = 0
        for re in results:
            if i >= 5:
                break
            i += 1
            list_node.append(re)
    return list_node

def main():
    j = JoernSteps()
    j.connectToDatabase()
    # all_nodes = get_all_nodes(j)
    # print all_nodes
    all_edges = get_all_edges(j)
    print all_edges
if __name__ == "__main__":
    main()