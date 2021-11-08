from joern.all import JoernSteps
from access_db_operate import *
import tqdm

def get_all_nodes(db):
    query_param_str = 'g.V()'
    results = db.runGremlinQuery(query_param_str)
    list_node = []
    if results != []:
        i =0
        for re in results:
            id = re._id
            type = re['type']
            print id, type
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
        for edge in results:
            src = edge.nodes[0]._id
            dst = edge.nodes[1]._id
            type = edge.type
            print src,dst,type
            if i >= 5:
                break
            i += 1
            list_node.append(edge)
    return list_node

def main():
    j = JoernSteps()
    j.connectToDatabase()
    # all_nodes = get_all_nodes(j)
    # print all_nodes
    all_edges = get_all_edges(j)
    print all_edges
    # all_func_nodes = getALLFuncNode(j)
    # for node in tqdm.tqdm(all_func_nodes):
    #     filename = getFuncFile(j, node._id).split('/')[-2]  # FFmpeg  file_name
    #     id = node._id
    #     label = 0  # 1 for vul, 0 for good
    #     # ast embedding
    #     ast_type = node.properties['type']
    #     all_ast_types = ['CallExpression','Callee','Function','ArgumentList',
    #                  'AssignmentExpr','IdentifierDeclStatement','Parameter','File']
    #     ast_embedding = 0
    #     for i in range(all_ast_types.__len__()):
    #         val = all_ast_types[i]
    #         if val == ast_type:
    #             ast_embedding = i+1

if __name__ == "__main__":
    main()