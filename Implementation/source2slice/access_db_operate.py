## -*- coding: utf-8 -*-
from joern.all import JoernSteps
from igraph import *
from general_op import *
import tqdm
import pickle
from py2neo.packages.httpstream import http
http.socket_timeout = 9999

def get_all_use_bydefnode(db, node_id):
    query_str = "g.v(%d).in('USE')" % node_id
    results = db.runGremlinQuery(query_str)
    list_re = []
    for re in results:
        if re.properties['type'] == 'Statement':
            continue
        else:
            list_re.append(re)

    return list_re


def get_all_def_bydefnode(db, node_id):
    query_str = "g.v(%d).in('DEF')" % node_id
    results = db.runGremlinQuery(query_str)
    list_re = []
    for re in results:
        if re.properties['type'] == 'Statement':
            continue
        else:
            list_re.append(re)

    return list_re


def get_exprstmt_node(db):
    query_expr_str = "queryNodeIndex('type:ExpressionStatement')"
    #results = db.runGremlinQuery(query_expr_str)
    results_1 = db.runGremlinQuery(query_expr_str)

    query_iddecl_str = 'queryNodeIndex("type:IdentifierDeclStatement")'
    results_2 = db.runGremlinQuery(query_iddecl_str)

    results = results_1 + results_2

    return results


def get_param_node(db):
    query_param_str = 'queryNodeIndex("type:Parameter")'
    results = db.runGremlinQuery(query_param_str)
    list_param_node = []
    if results != []:
        for re in results:
            list_param_node.append(re)
    return list_param_node

def get_return_node(db):
    query_return_str = 'queryNodeIndex("type:ReturnStatement")'
    results = db.runGremlinQuery(query_return_str)
    list_return_node = []
    if results != []:
        for re in results:
            list_return_node.append(re)
    return list_return_node


def get_pointers_node(db):
    list_pointers_node = []
    query_iddecl_str = 'queryNodeIndex("type:IdentifierDeclStatement")'

    results = db.runGremlinQuery(query_iddecl_str)

    if results != []:
        for re in results:
            code = re.properties['code']
            if code.find(' = ') != -1:
                code = code.split(' = ')[0]

            if code.find('*') != -1:
                list_pointers_node.append(re)

    query_param_str = 'queryNodeIndex("type:Parameter")'
    results = db.runGremlinQuery(query_param_str)
    if results != []:
        for re in results:
            code = re.properties['code']
            if code.find(' = ') != -1:
                code = code.split(' = ')[0]
                
            if code.find('*') != -1:
                list_pointers_node.append(re)

    return list_pointers_node


def get_arrays_node(db):
    list_arrays_node = []
    query_iddecl_str = "queryNodeIndex('type:IdentifierDeclStatement')"
    results = db.runGremlinQuery(query_iddecl_str)
    if results != []:
        for re in results:
            code = re.properties['code']
            if code.find(' = ') != -1:
                code = code.split(' = ')[0]

            if code.find(' [ ') != -1:
                list_arrays_node.append(re)

    query_param_str = "queryNodeIndex('type:Parameter')"
    results = db.runGremlinQuery(query_param_str)
    if results != []:
        for re in results:
            code = re.properties['code']
            if code.find(' = ') != -1:
                code = code.split(' = ')[0]

            if code.find(' [ ') != -1:
                list_arrays_node.append(re)

    return list_arrays_node


def get_def_node(db, cfg_node_id):
    query_str = "g.v(%d).out('DEF')" % cfg_node_id
    results = db.runGremlinQuery(query_str)
    return results


def getFunctionNodeByName(db, funcname):
    query_str = "queryNodeIndex('type:Function AND name:%s')" % funcname
    results = db.runGremlinQuery(query_str)
    return results


def get_parameter_by_funcid(db, func_id):
    query_str = "g.v(%d).out('IS_FUNCTION_OF_CFG').out('CONTROLS').filter{ it.type == 'Parameter' }.id" % func_id
    results = db.runGremlinQuery(query_str)
    return results


def isNodeExist(g, nodeName):
    if not g.vs:
        return False
    else:
        return nodeName in g.vs['name']


def getALLFuncNode(db):
    query_str = "queryNodeIndex('type:Function')"
    results = db.runGremlinQuery(query_str)
    return results


def getFuncNode(db, func_name):
    query_str = 'getFunctionsByName("' + func_name + '")'
    func_node = db.runGremlinQuery(query_str)
    return func_node
    

def getFuncFile(db, func_id):
    query_str = "g.v(%d).in('IS_FILE_OF').filepath" % func_id
    ret = db.runGremlinQuery(query_str)
    #print ret
    return ret[0]

def getCFGNodes(db, func_id):
    query_str = 'queryNodeIndex("functionId:%s AND isCFGNode:True")' % func_id
    cfgNodes = db.runGremlinQuery(query_str)
    
    return cfgNodes


def getDDGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s AND isCFGNode:True').outE('REACHES')""" % (func_id)
    ddgEdges = db.runGremlinQuery(query_str)
    return ddgEdges

def getDDGEdges2(db, func_id):
    query_str = """queryNodeIndex('functionId:%s AND isCFGNode:True').outE('POST_DOM')""" % (func_id)
    ddgEdges = db.runGremlinQuery(query_str)
    return ddgEdges

def getCDGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s AND isCFGNode:True').outE('CONTROLS')""" % (func_id)
    cdgEdges = db.runGremlinQuery(query_str)
    return cdgEdges



def getCFGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s AND isCFGNode:True').outE('FLOWS_TO')""" % (func_id)
    cfgEdges = db.runGremlinQuery(query_str)
    return cfgEdges


def getASTEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('IS_AST_PARENT')""" % (func_id)
    ASTEdges = db.runGremlinQuery(query_str)
    return ASTEdges

def get_file(db,filepath):
    query = """queryNodeIndex('type:File').filter{it.filepath == '%s'}""" % (filepath)
    files = db.runGremlinQuery(query)
    return files

def get_functions(db, fileId, funcName):
    query="""g.v('%s').out('IS_FILE_OF').filter{it.type == 'Function' &&  it.name=='%s'}""" %(fileId, funcName)
    functions = db.runGremlinQuery(query)
    return functions

def edge_query(db,id):
    nodes = []
    query = """queryNodeIndex("functionId:%s").outE('CONTROLS')""" % (id)
    r0 = db.runGremlinQuery(query)
    query = """queryNodeIndex("functionId:%s").outE('REACHES')""" % (id)
    r1 = db.runGremlinQuery(query)
    query = """queryNodeIndex("functionId:%s").outE('FLOWS_TO')""" % (id)
    r2 = db.runGremlinQuery(query)
    query = """queryNodeIndex("functionId:%s").outE('POST_DOW')""" % (id)
    r3 = db.runGremlinQuery(query)
    r = r0 + r1 + r2 + r3
    for ri in r:
        s = r.nodes[0]
        e = r.nodes[1]
        nodes.append(s)
    return nodes

def getCALLEdges(db, func_id, funcnode, caller, callEdges):
    functionnode = funcnode
    filepath = getFuncFile(db,func_id)
    filename = filepath.split('/')[-1]
    filepath = filepath.strip(filename)
    dirlist = os.listdir(filepath)
    fileIds = []
    for dir in dirlist:
        fileIds += get_file(db,filepath + dir)
    child_query = """queryNodeIndex("functionId:%s").children()""" % (func_id)
    children = db.runGremlinQuery(child_query)
    for child in children:
        childcode = child.properties['code'].replace(' ', '').replace(';', '').replace('\t', '').replace('\n', '')
        if childcode == '':
            continue
        if child.properties['type'] == 'Callee' :
            # ??????????????????function
            code = str(child.properties['code'])
            # code_def: ??????function???ID
            code_def = []
            for fileId in fileIds:
                ret = get_functions(db,fileId.ref[5:], code)
                code_def += ret
            if len(code_def) == 0:
                continue
            # ??????????????????????????????ID?????????????????????caller??????????????????????????????
            real_callee = []
            for code_def_item in code_def:
                if int(code_def_item.ref[5:]) not in caller:
                    real_callee.append(code_def_item)
            if len(real_callee) != 0:
                caller.append(int(code_def_item.ref[5:]))
                parent_query = """g.v('%s').parents()""" % child.ref[5:]# get CallExpression
                parents = db.runGremlinQuery(parent_query)
                for i in parents:
                    calledge = []
                    if i.properties['functionId'] == func_id:
                        nodecode = i.properties['code']
                        node_id = i._id
                        query = """g.v('%s').parents()""" % node_id
                        realnode = db.runGremlinQuery(query)
                        calledge.append(realnode)
                        calledge.append(code_def_item)
                        callEdges.append(calledge)
                caller,valid_callees = getCALLEdges(db, int(code_def_item.ref[5:]), code_def_item, caller,callEdges)
    return caller, callEdges

def drawGraph(db, edges, func_entry_node, graph_type):
    g = Graph(directed=True)
    func_id = func_entry_node._id
    filepath = getFuncFile(db, func_id)

    calleEdges = []
    if len(calleEdges)!=0:
        for edge in calleEdges:
            if isNodeExist(g, edge[0]) == False:
                node_prop = {'code': edge[0].properties['code'], 'type': edge[0].properties['type'],
                             'location': edge[0].properties['location'], 'filepath': edge[0].properties['filepath'],
                             'functionId': str(edge[0].properties['functionId'])}
                g.add_vertex(edge[0], **node_prop)


    for edge in edges:
        if edge.start_node.properties['code'] == 'ENTRY':
            startNode = str(edge.start_node.properties['functionId'])
        else:
            startNode = str(edge.start_node._id)

        if edge.start_node.properties['code'] == 'ERROR':
            continue

        if isNodeExist(g, startNode) == False:
            if edge.start_node.properties['code'] == 'ENTRY':
                node_prop = {'code': func_entry_node.properties['name'], 'type': func_entry_node.properties['type'],
                         'location': func_entry_node.properties['location'], 'filepath':filepath, 'functionId':str(edge.start_node.properties['functionId'])}
            else:
                node_prop = {'code': edge.start_node.properties['code'], 'type': edge.start_node.properties['type'],
                         'location': edge.start_node.properties['location'], 'filepath':filepath, 'functionId':str(edge.start_node.properties['functionId'])}
            g.add_vertex(startNode, **node_prop)#id is 'name'

        endNode = str(edge.end_node._id)
        if isNodeExist(g, endNode) == False:
            if graph_type == 'pdg' and edge.end_node.properties['code'] == 'EXIT':
                continue

            if edge.end_node.properties['code'] == 'ERROR':
                continue

            node_prop = {'code': edge.end_node.properties['code'], 'type': edge.end_node.properties['type'],
                         'location': edge.end_node.properties['location'], 'filepath':filepath, 'functionId':str(edge.end_node.properties['functionId'])}
            g.add_vertex(endNode, **node_prop)
        if graph_type == 'pdg':
            edge_prop = {'var': edge.properties['var']}
        else:
            edge_prop = {'var': edge.properties['flowLabel']}
        if str(edge).find(':CONTROLS')!=-1:
            edge_prop['label'] = 0
        if str(edge).find(':REACHES')!=-1:
            edge_prop['label'] = 1
        if str(edge).find(':FLOWS_TO')!=-1:
            edge_prop['label'] = 2
        if str(edge).find(':IS_AST_PARENT')!=-1:
            edge_prop['label'] = 5
        if str(edge).find(':POST_DOM')!=-1:
            edge_prop['label'] = 6
        if edge_prop['label'] == None:
            print 'none'
        g.add_edge(startNode, endNode, **edge_prop)
        #print startNode, endNode
        #print g.es[-1].source, g.es[-1].target
        #print g.vs[g.es[-1].source]['name'],g.vs[g.es[-1].target]['name']
        #print edge.start_node.ref[5:],edge.end_node.ref[5:]

        #print 'finish'
    return g




def translatePDGByNode(db, func_node):
    func_id = func_node._id
    ddgEdges = getDDGEdges(db, func_id)
    #ddg2Edges = getDDGEdges2(db, func_id)
    cdgEdges = getCDGEdges(db, func_id)
    # caller = [func_id]
    calleEdges = []
    # caller, calleEdges = getCALLEdges(db, func_id,func_node,caller,calleEdges)
    # for id in caller:
    #     if id ==func_id:
    #         continue
    #     else:
    #         query = """g.v(%d)"""% id
    #         callernode = db.runGremlinQuery(query)
    #         translatePDGByNode(db, callernode)
    #Edges = ddgEdges + ddg2Edges + cdgEdges
    Edges = ddgEdges + cdgEdges
    graph_type = 'pdg'
    g = drawGraph(db, Edges, func_node, graph_type)
    return g

def translatePDGfullByNode(db, func_node):
    func_id = func_node._id
    ddgEdges = getDDGEdges(db, func_id)
    ddg2Edges = getDDGEdges2(db, func_id)
    cdgEdges = getCDGEdges(db, func_id)
    cfgEdges = getCFGEdges(db, func_id)
    # caller = [func_id]
    calleEdges = []
    # caller, calleEdges = getCALLEdges(db, func_id,func_node,caller,calleEdges)
    # for id in caller:
    #     if id ==func_id:
    #         continue
    #     else:
    #         query = """g.v(%d)"""% id
    #         callernode = db.runGremlinQuery(query)
    #         translatePDGByNode(db, callernode)
    #Edges = ddgEdges + ddg2Edges + cdgEdges
    Edges = ddgEdges + cdgEdges + ddg2Edges + cfgEdges
    graph_type = 'pdg'
    g = drawGraph(db, Edges, func_node, graph_type)
    return g


def translateCFGByNode(db, func_node):
    func_id = func_node._id
    Edges = getCFGEdges(db, func_id)
    graph_type = 'cfg'
    g = drawGraph(db, Edges, func_node, graph_type)
    return g

def translateCPGByNode(db, func_node):
    func_id = func_node._id
    ASTEdges = getASTEdges(db, func_id)
    CFGEdges = getCFGEdges(db, func_id)
    ddgEdges = getDDGEdges(db, func_id)
    ddg2Edges = getDDGEdges2(db, func_id)
    cdgEdges = getCDGEdges(db, func_id)
    Edges = ASTEdges+CFGEdges+ddgEdges+ddg2Edges+cdgEdges
    graph_type = 'cpg'
    g = drawGraph(db, Edges, func_node, graph_type)
    return g


def translateASTByNode(db, func_node):
    func_id = func_node._id
    Edges = getASTEdges(db, func_id)
    graph_type = 'ast'
    g = drawGraph(db, Edges, func_node, graph_type)
    return g

    
def getUSENodesVar(db, func_id):
    query = "g.v(%s).out('USE').code" % func_id
    ret = db.runGremlinQuery(query)
    if ret == []:
        return False
    else:
        return ret


def getDEFNodesVar(db, func_id):
    query = "g.v(%s).out('DEF').code" % func_id
    ret = db.runGremlinQuery(query)
    if ret == []:
        return False
    else:
        return ret


def getUseDefVarByPDG(db, pdg):
    dict_cfg2use = {}
    dict_cfg2def = {}
    #print pdg
    #need_to_addedge_node = []
    for node in pdg.vs:
        if node['type'] == 'Function':
            continue
            
        func_id = node['name']
        use_node = getUSENodesVar(db, func_id)
        def_node = getDEFNodesVar(db, func_id)

        if node['type'] == 'Statement':
            if def_node == False:
                code = node['code'].replace('\n', ' ')
                if code.find(" = ") != -1:
                    value = code.split(" = ")[0].strip().split(' ')
                    if value[-1] == ']':
                        newvalue = code.split(" [ ")[0].strip().split(' ')
                        if '->' in newvalue:
                            a_index = newvalue.index('->')
                            n_value = ' '.join([newvalue[a_index-1], '->', newvalue[a_index+1]])
                            newvalue[a_index-1] = n_value
                            del newvalue[a_index]
                            del newvalue[a_index]

                        def_node = newvalue

                    else:
                        if '->' in value:
                            a_index = value.index('->')
                            n_value = ' '.join([value[a_index-1], '->', value[a_index+1]])
                            ob_value = value[a_index-1]
                            value[a_index-1] = n_value
                            del value[a_index]
                            del value[a_index]
                            value.append(ob_value.replace('*', ''))

                        def_node = value

                    #need_to_addedge_node.append(node['name'])

            if use_node == False:
                if code.find(" = ") != -1:
                    value = code.split(" = ")[1].strip().split(' ')
                    newvalue = []
                    for v in value:
                        if v == '*' or v == '+' or v == '-' or v == '->' or v == '(' or v == ')' or v == '[' or v == ']' or v == '&' or v == '.' or v == '::' or v == ';' or v == ',':
                            continue
                        else:
                            newvalue.append(v.strip())

                else:
                    value = code.split(' ')
                    newvalue = []
                    for v in value:
                        if v == '*' or v == '+' or v == '-' or v == '->' or v == '(' or v == ')' or v == '[' or v == ']' or v == '&' or v == '.' or v == '::' or v == ';' or v == ',':
                            continue
                        else:
                            newvalue.append(v.strip())

                use_node = newvalue


        if use_node:
            use_node = [code.replace('*', '').replace('&', '').strip() for code in use_node]

        if def_node:
            def_node = [code.replace('*', '').replace('&', '').strip() for code in def_node]

        else:#add define node
            new_def_node = getReturnVarOfAPI(node['code'])#get modify value of api_func
            #if node['name'] == '2078':
            #    print ("new_def_node", new_def_node)

            if new_def_node:
                def_node = []
                for code in new_def_node:
                    new_code = code.replace('*', '').replace('&', '').strip()
                    def_node.append(new_code)

                    if new_code not in use_node:
                        use_node.append(new_code)

        if use_node:
            dict_cfg2use[node['name']] = use_node

        if def_node:
            dict_cfg2def[node['name']] = def_node

    return dict_cfg2use, dict_cfg2def


def getFuncNodeByFile(db, filenodeID):  
    query_str = 'g.v(%d).out("IS_FILE_OF")' % filenodeID
    results = db.runGremlinQuery(query_str)
    _list = []
    for re in results:
        if re.properties['type'] == 'Function':
            _list.append(re)
        else:
            continue

    return _list


def getAllFuncfileByTestID(db, testID):
    testID = '*/'+ testID + '/*'
    query_str = "queryNodeIndex('type:File AND filepath:%s').id" % testID
    results = db.runGremlinQuery(query_str)
    return results


def get_calls_id(db, func_name):
    query_str = 'getCallsTo("%s").id' % func_name
    results = db.runGremlinQuery(query_str)
    return results


def getCFGNodeByCallee(db, node_ast_id):
    #print "start"
    query_str = "g.v(%s).in('IS_AST_PARENT')" % node_ast_id
    results = db.runGremlinQuery(query_str)
    #print "end"
    if results == []:
        return None

    for node in results:
        if 'isCFGNode' in node.properties and node.properties['isCFGNode'] == 'True':
            return node
        else:
            node = getCFGNodeByCallee(db, node._id)
            #print node
    
    return node


def getCalleeNode(db, func_id):
    query_str = "queryNodeIndex('type:Callee AND functionId:%d')" % func_id
    results = db.runGremlinQuery(query_str)
    return results


def get_all_calls_node(db, testID):
    list_all_funcID = [node._id for node in getFuncNodeInTestID(db, testID)]
    #print ("list_all_funcID", list_all_funcID)
    #print ("lenth", len(list_all_funcID))
    #if len(list_all_funcID)>130:
    #    print (">100")
    #    return False
    list_all_callee_node = []
    for func_id in list_all_funcID:#allfile in a testID
        list_all_callee_node += getCalleeNode(db, func_id)

    if list_all_callee_node == []:
        return False
    else:
        return [(str(node._id), node.properties['code'], str(node.properties['functionId'])) for node in list_all_callee_node]


def getFuncNodeInTestID(db, testID):
    list_all_file_id = getAllFuncfileByTestID(db, testID)
    if list_all_file_id == []:
        return False

    list_all_func_node = []  

    for file_id in list_all_file_id:
        list_func_node = getFuncNodeByFile(db, file_id)
        list_all_func_node += list_func_node

    return list_all_func_node


def getClassByObjectAndFuncID(db, objectname, func_id):
    #print objectname, func_id
    all_cfg_node = getCFGNodes(db, func_id)
    for cfg_node in all_cfg_node:
        if cfg_node.properties['code'] == objectname and cfg_node.properties['type'] == 'Statement':
            #print (objectname, func_id, cfg_node.properties['code'], cfg_node._id)
            query_str_1 = "queryNodeIndex('type:Statement AND code:%s AND functionId:%s')" % (objectname, func_id)
            results_1 = db.runGremlinQuery(query_str_1)
            if results_1 == []:
                return False
            else:
                ob_cfgNode = results_1[0]

            location_row = ob_cfgNode.properties['location'].split(':')[0]

            query_str_2 = "queryNodeIndex('type:ExpressionStatement AND functionId:%s')" % func_id
            results_2 = db.runGremlinQuery(query_str_2)
            if results_2 == []:
                return False

            classname = False
            for node in results_2:
                #print (node.properties['location'].split(':')[0], location_row)
                if node.properties['location'].split(':')[0] == location_row:
                    classname = node.properties['code']
                    break
                
                else:
                    continue

            return classname

        elif cfg_node.properties['code'].find(' '+objectname+' = new') != -1:
            temp_value = cfg_node.properties['code'].split(' '+objectname+' = new')[1].replace('*', '').strip()
            if temp_value.split(' ')[0] != 'const':
                classname = temp_value.split(' ')[0]
            else:
                classname = temp_value.split(' ')[1]

            return classname


def getDeleteNode(db, func_id):
    query_str = "queryNodeIndex('code:delete AND functionId:%d')" % func_id
    results = db.runGremlinQuery(query_str)
    return results


def get_all_delete_node(db, testID):
    list_all_funcID = [node._id for node in getFuncNodeInTestID(db, testID)]
    #print ("list_all_funcID", list_all_funcID)

    list_all_delete_node = []
    for func_id in list_all_funcID:#allfile in a testID
        list_all_delete_node += getDeleteNode(db, func_id)

    if list_all_delete_node == []:
        return False
    else:
        return list_all_delete_node


def getDeclNode(db, func_id):
    query_str = "queryNodeIndex('type:IdentifierDeclStatement AND functionId:%d')" % func_id
    results = db.runGremlinQuery(query_str)
    return results


def get_all_iddecl_node(db, testID):
    list_all_funcID = [node._id for node in getFuncNodeInTestID(db, testID)]
    #print ("list_all_funcID", list_all_funcID)

    list_all_decl_node = []
    for func_id in list_all_funcID:#allfile in a testID
        list_all_decl_node += getDeclNode(db, func_id)

    if list_all_decl_node == []:
        return False
    else:
        return list_all_decl_node


def getCallGraph(db, testID):
    list_all_func_node = getFuncNodeInTestID(db, testID)
    #print "list_all_func_node", list_all_func_node
    if list_all_func_node == []:
        return False
    
    call_g = Graph(directed=True)
    #print(list_all_func_node)
    for func_node in list_all_func_node:
        #print('tqdm2')
        prop = {'funcname':func_node.properties['name'], 'type': func_node.properties['type'], 'filepath': func_node.properties['filepath']}
        call_g.add_vertex(str(func_node._id), **prop)
        #print(call_g)

    list_all_callee = get_all_calls_node(db, testID)#we must limit result in testID, it already get callee node
    #print '3 ', list_all_callee
    if list_all_callee == False:
        return False

    for func_node in list_all_func_node:
        function_name = func_node.properties['name']
        #print "function_name", function_name
        tag = False
        if function_name.find('::') != -1:#if is a function in class, have two problems
            func_name = function_name.split('::')[-1].strip()
            classname = function_name.split('::')[0].strip()

            if func_name == classname:#is a class::class, is a statementnode or a iddeclnode
                print (1)
                list_callee_id = []
                list_delete_node = get_all_delete_node(db, testID)
                if list_delete_node == False:
                    continue

                for node in list_delete_node:
                    functionID = node.properties["functionId"]
                    all_cfg_node = getCFGNodes(db, functionID)
                    delete_loc = node.properties['location'].split(':')[0]

                    for cfg_node in all_cfg_node:
                        if cfg_node.properties['location'] != None and cfg_node.properties['location'].split(':')[0] == delete_loc and cfg_node.properties['code'] != 'delete' and cfg_node.properties['code'] != '[' and cfg_node.properties['code'] != '[':
                            objectname = cfg_node.properties['code']
                            ob_classname = getClassByObjectAndFuncID(db, objectname, functionID)
                            pdg = getFuncPDGByfuncIDAndtestID(functionID, testID)
                            if pdg == False:
                                continue

                            if ob_classname == classname:
                                for p_n in pdg.vs:
                                    #print p_n['name'], str(node._id), str(cfg_node._id)
                                    if p_n['name'] == str(node._id):

                                        list_s = p_n.predecessors()
                                        for edge in pdg.es:
                                            if pdg.vs[edge.tuple[0]] in list_s and pdg.vs[edge.tuple[1]] == p_n and edge['var'] == objectname:
                                                #print (functionID, str(pdg.vs[edge.tuple[0]]['name']))
                                                list_callee_id.append((str(functionID), str(pdg.vs[edge.tuple[0]]['name'])))
                                            else:
                                                continue 

                                    elif p_n['name'] == str(cfg_node._id):
                                        list_s = p_n.predecessors()
                                        for edge in pdg.es:
                                            if pdg.vs[edge.tuple[0]] in list_s and pdg.vs[edge.tuple[1]] == p_n and edge['var'] == objectname:
                                                list_callee_id.append((functionID, str(pdg.vs[edge.tuple[0]]['name'])))
                                            else:
                                                continue  

                        else:
                            continue


                    else:
                        continue

            elif func_name.replace('~', '') == classname:#is a class::~class
                list_callee_id = []
                list_delete_node = get_all_delete_node(db, testID)
                if list_delete_node == False:
                    continue

                for node in list_delete_node:
                    functionID = node.properties["functionId"]
                    all_cfg_node = getCFGNodes(db, functionID)
                    delete_loc = node.properties['location'].split(':')[0]

                    for cfg_node in all_cfg_node:
                        if cfg_node.properties['location'] != None and cfg_node.properties['location'].split(':')[0] == delete_loc and cfg_node.properties['code'] != 'delete' and cfg_node.properties['code'] != '[' and cfg_node.properties['code'] != '[':
                            objectname = cfg_node.properties['code']
                            #print objectname

                            ob_classname = getClassByObjectAndFuncID(db, objectname, functionID)

                            if ob_classname == classname:
                                pdg = getFuncPDGByfuncIDAndtestID(functionID, testID)
                                if pdg == False:
                                    continue

                                for p_n in pdg.vs:
                                    if p_n['name'] == str(node._id):
                                        list_callee_id.append((functionID, str(node._id)))

                                    elif p_n['name'] == str(cfg_node._id):
                                        list_callee_id.append((functionID, str(cfg_node._id))) #delete and its object node

                        else:
                            continue


                    else:
                        continue

            else:
                #print (3)
                tag = 'func'
                list_callee_id = []
                for _t in list_all_callee:#_t is a tuple, _t[0] is nodeid, 1 is funcname, 2 is func_id
                    if _t[1].find('-> '+ func_name) != -1:#maybe is a class->funcname()
                        objectname = _t[1].split(' -> '+ func_name)[0].strip()
                        ob_classname = getClassByObjectAndFuncID(db, objectname, _t[2])

                        if ob_classname == classname:
                            list_callee_id.append(_t[0])

                        else:
                            continue
                        
                    else:
                        continue


        else:
            tag = 'func'
            list_callee_id = []
            for _t in list_all_callee:
                if _t[1] == function_name:
                    list_callee_id.append(_t[0])

        #print 4, list_callee_id
        if list_callee_id == []:
            continue

        else:
            #change ast node to cfgnode
            list_callee_CFGNode = []
            if tag == 'func':
                #print 'z'
                for node_id in list_callee_id:
                    #print 1
                    callee_cfgnode = getCFGNodeByCallee(db, node_id)
                    #print callee_cfgnode
                    #print 2

                    if callee_cfgnode == None:
                                                
                        print ('ERROR', callee_cfgnode)
                        continue
                    else:
                        list_callee_CFGNode.append(callee_cfgnode)

                #print 'x'
                for node in list_callee_CFGNode:
                    startNode = str(node.properties['functionId'])
                    endNode = str(func_node._id)
                    var = str(node._id)
                    call_g = addDataEdge(call_g, startNode, endNode, var)#var is callee node id
            else:
                #print 'y'
                for node in list_callee_id:
                    startNode = str(node[0])
                    endNode = str(func_node._id)
                    var = str(node[1])
                    call_g = addDataEdge(call_g, startNode, endNode, var)#var is callee node id


    return call_g


if __name__ == '__main__':
    j = JoernSteps()
    j.connectToDatabase()

    #pdg_db_path = "/home/zheng/Desktop/qemupdg/31/pdg_db"
    pdg_db_path = "/home/zheng/Desktop/locator_pdg/31/pdg_db"
    list_testID = os.listdir(pdg_db_path)
    #print (list_testID)    
    for testID in tqdm.tqdm(list_testID):
        #if testID != '69055':
        #    continue
        #if os.path.exists(os.path.join("/home/zheng/Desktop/qemudict/31/dict_call2cfgNodeID_funcID", str(testID))):
        if os.path.exists(os.path.join("/home/zheng/Desktop/locator_dict/31/dict_call2cfgNodeID_funcID", str(testID))):
            continue
        #print('start')
        call_g = getCallGraph(j, testID)
        #print (call_g)
        #print ('start 1')
        if call_g == False:
            print ('false')
            continue
        _dict = {}
        for edge in call_g.es:
            endnode = call_g.vs[edge.tuple[1]]
            if endnode['name'] not in _dict:
                _dict[endnode['name']] = [(edge['var'], call_g.vs[edge.tuple[0]]['name'])]
            else:
                _dict[endnode['name']].append((edge['var'], call_g.vs[edge.tuple[0]]['name']))
        if not os.path.exists(os.path.join("/home/zheng/Desktop/locator_dict/31/dict_call2cfgNodeID_funcID", str(testID))):
            #os.mkdir(os.path.join("/home/zheng/Desktop/qemudict/31/dict_call2cfgNodeID_funcID", str(testID)))
            os.mkdir(os.path.join("/home/zheng/Desktop/locator_dict/31/dict_call2cfgNodeID_funcID", str(testID)))
        filepath = os.path.join("/home/zheng/Desktop/locator_dict/31/dict_call2cfgNodeID_funcID", str(testID), "dict.pkl")
        #print (_dict)
        f = open(filepath, 'wb')
        pickle.dump(_dict, f, True)
        f.close()
