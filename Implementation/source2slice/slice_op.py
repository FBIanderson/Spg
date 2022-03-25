import queue
import tqdm

from access_db_operate import *
from general_op import *
from py2neo.packages.httpstream import http

http.socket_timeout = 9999


def sub_slice_backwards(startnode, list_node, not_scan_list):
    if startnode['name'] in not_scan_list:
        return list_node, not_scan_list

    else:
        list_node.append(startnode)
        not_scan_list.append(startnode['name'])

    predecessors = startnode.predecessors()

    if predecessors != []:
        for p_node in predecessors:
            list_node, not_scan_list = sub_slice_backwards(p_node, list_node, not_scan_list)

    return list_node, not_scan_list


def program_slice_backwards(pdg, list_startNode):  # startNode is a list
    list_all_node = []
    not_scan_list = []
    for startNode in list_startNode:
        list_node = [startNode]
        not_scan_list.append(startNode['name'])
        predecessors = startNode.predecessors()
        if predecessors != []:
            for p_node in predecessors:
                list_node, not_scan_list = sub_slice_backwards(p_node, list_node, not_scan_list)

        list_all_node += list_node

        # Add function define line
        if startNode['functionId'] in not_scan_list:
            continue
        for node in pdg.vs:
            if node['name'] == startNode['functionId']:
                list_all_node.append(node)
                not_scan_list.append(node['name'])
                break

    # print("list_all_node:", list_all_node)
    list_ordered_node = sortedNodesByLoc(list_all_node)

    _list_re = []
    a = 0
    while a < len(list_ordered_node):
        if list_ordered_node[a]['name'] not in _list_re:
            _list_re.append(list_ordered_node[a]['name'])
            a += 1
        else:
            del list_ordered_node[a]
    return list_ordered_node


def sub_slice_forward(startnode, list_node, not_scan_list):
    if startnode['name'] in not_scan_list:
        return list_node, not_scan_list

    else:
        list_node.append(startnode)
        not_scan_list.append(startnode['name'])

    successors = startnode.successors()
    if successors != []:
        for p_node in successors:
            list_node, not_scan_list = sub_slice_forward(p_node, list_node, not_scan_list)

    return list_node, not_scan_list


def program_slice_forward(pdg, list_startNode):  # startNode is a list of parameters, only consider data dependency
    pdg = del_ctrl_edge(pdg)

    list_all_node = []
    not_scan_list = []
    for startNode in list_startNode:
        list_node = [startNode]
        not_scan_list.append(startNode['name'])
        successors = startNode.successors()

        if successors != []:
            for p_node in successors:
                list_node, not_scan_list = sub_slice_forward(p_node, list_node, not_scan_list)

        list_all_node += list_node

    list_ordered_node = sortedNodesByLoc(list_all_node)

    a = 0
    _list_re = []
    while a < len(list_ordered_node):
        if list_ordered_node[a]['name'] not in _list_re:
            _list_re.append(list_ordered_node[a]['name'])
            a += 1
        else:
            del list_ordered_node[a]

    return list_ordered_node


def sub_slice_mvp_forward(startnode, list_node, not_scan_list, func_id):
    if startnode['name'] in not_scan_list:
        return list_node, not_scan_list
    else:
        list_node.append(startnode)
        not_scan_list.append(startnode['name'])
    j = JoernSteps()
    j.connectToDatabase()
    if startnode['type'] == 'ExpressionStatement' or startnode['type'] == 'Statement':
        ddgEdges = getDDGEdges(j, func_id) + getDDGEdges2(j, func_id)
        q = queue.Queue()
        q.put(startnode)
        while not q.empty():
            curr_node = q.get()
            list_node.append(curr_node)
            not_scan_list.append(curr_node['name'])
            temp = []
            for next_node in curr_node.successors():
                if next_node in not_scan_list:
                    continue
                for edge in ddgEdges:
                    u = edge.start_node
                    v = edge.end_node
                    uid = u.ref.split('/')[1]
                    vid = v.ref.split('/')[1]

                    if u['location'] is not None and u['location'].split(':')[0] == str(
                            19):  # and v['location'] is not None and v['location'].split(':')[0] == str(20):
                        temp.append(edge)
                    if v['location'] is not None and v['location'].split(':')[0] == str(20):
                        temp.append(edge)
                    if uid == curr_node['name'] and vid == next_node['name']:
                        q.put(next_node)
                    elif u['location'] is not None and v['location'] is not None and \
                            u['location'].split(':')[0] == curr_node['location'].split(':')[0] \
                            and v['location'].split(':')[0] == next_node['location'].split(":")[0]:
                        q.put(next_node)
    elif startnode['type'] == 'ReturnStatement':
        # No dependency exists between the return value and the statements after the return statement.
        # Therefore, there is no need for forward slicing.
        pass
    else:  # include 'Condition' statement 'IfStatement'  and others
        ddgEdges = getDDGEdges(j, func_id) + getDDGEdges2(j, func_id)
        # mvp backwards
        back_start_node_list = []  # variable or parameter
        back_visited_nodes = []
        q = queue.Queue()
        q.put(startnode)
        while not q.empty():
            curr_node = q.get()
            if curr_node['name'] in back_visited_nodes:
                continue
            back_visited_nodes.append(curr_node['name'])
            if curr_node['type'] in ['Parameter', 'ExpressionStatement', 'IdentifierDeclStatement']:
                back_start_node_list.append(curr_node)
            for prev_node in curr_node.predecessors():
                if prev_node['name'] in back_visited_nodes:
                    continue
                for edge in ddgEdges:
                    u = edge.start_node
                    v = edge.end_node
                    uid = u.ref.split('/')[1]
                    vid = v.ref.split('/')[1]

                    if uid == prev_node['name'] and vid == curr_node['name']:
                        q.put(prev_node)
                    elif u['location'] is not None and v['location'] is not None and \
                            u['location'].split(':')[0] == prev_node['location'].split(':')[0] \
                            and v['location'].split(':')[0] == curr_node['location'].split(":")[0]:
                        q.put(prev_node)
        if len(back_start_node_list) != 0:  # mvp forwards
            for node in back_start_node_list:
                q.put(node)
            while not q.empty():
                curr_node = q.get()
                list_node.append(curr_node)
                not_scan_list.append(curr_node['name'])
                for next_node in curr_node.successors():
                    if next_node in not_scan_list:
                        continue
                    for edge in ddgEdges:
                        u = edge.start_node
                        v = edge.end_node
                        uid = u.ref.split('/')[1]
                        vid = v.ref.split('/')[1]

                        if uid == curr_node['name'] and vid == next_node['name']:
                            q.put(next_node)
                        elif u['location'] is not None and v['location'] is not None and \
                                u['location'].split(':')[0] == curr_node['location'].split(':')[0] \
                                and v['location'].split(':')[0] == next_node['location'].split(":")[0]:
                            q.put(next_node)
        else:  # normal
            q = queue.Queue()
            q.put(startnode)
            while not q.empty():
                curr_node = q.get()
                list_node.append(curr_node)
                not_scan_list.append(curr_node['name'])
                for next_node in curr_node.successors():
                    if next_node in not_scan_list:
                        continue
                    q.put(next_node)

    return list_node, not_scan_list


def program_slice_mvp_forward(pdg, list_startNode,
                              func_id):  # startNode is a list of parameters, only consider data dependency
    # pdg = del_ctrl_edge(pdg)

    list_all_node = []
    not_scan_list = []
    for startNode in list_startNode:
        list_node = [startNode]
        # not_scan_list.append(startNode['name'])
        list_node, not_scan_list = sub_slice_mvp_forward(startNode, list_node, not_scan_list, func_id=func_id)
        list_all_node += list_node

    list_ordered_node = sortedNodesByLoc(list_all_node)

    # remove duplicate node
    a = 0
    _list_re = []
    while a < len(list_ordered_node):
        if list_ordered_node[a]['name'] not in _list_re:
            _list_re.append(list_ordered_node[a]['name'])
            a += 1
        else:
            del list_ordered_node[a]

    return list_ordered_node


def process_cross_func(to_scan_list, testID, slicetype, list_result_node, not_scan_func_list, slice_id):
    if to_scan_list == []:
        return list_result_node, not_scan_func_list

    for node in to_scan_list:
        if node['name'] in not_scan_func_list:
            continue

        ret = isNewOrDelOp(node, testID, slice_id)
        if ret:
            funcname = ret
            pdg = getFuncPDGByNameAndtestID(funcname, testID, slice_id)

            if not pdg:
                not_scan_func_list.append(node['name'])
                continue

            else:
                result_list = sortedNodesByLoc(pdg.vs)

                not_scan_func_list.append(node['name'])

                index = 0
                for result_node in list_result_node:
                    if result_node['name'] == node['name']:
                        break
                    else:
                        index += 1

                list_result_node = list_result_node[:index + 1] + result_list + list_result_node[index + 1:]

                list_result_node, not_scan_func_list = process_cross_func(result_list, testID, slicetype,
                                                                          list_result_node, not_scan_func_list,
                                                                          slice_id)


        else:
            ret = isFuncCall(node)  # if funccall ,if so ,return funcnamelist
            if ret:

                for funcname in ret:
                    if funcname.find('->') != -1:
                        real_funcname = funcname.split('->')[-1].strip()
                        objectname = funcname.split('->')[0].strip()

                        funcID = node['functionId']
                        src_pdg = getFuncPDGByfuncIDAndtestID(funcID, testID, slice_id=slice_id)
                        if src_pdg == False:
                            continue

                        classname = False
                        for src_pnode in src_pdg.vs:
                            if src_pnode['code'].find(objectname) != -1 and src_pnode['code'].find(' new ') != -1:
                                tempvalue = src_pnode['code'].split(' new ')[1].replace('*', '').strip()
                                if tempvalue.split(' ')[0] != 'const':
                                    classname = tempvalue.split(' ')[0]
                                else:
                                    classname = tempvalue.split(' ')[1]

                                break

                        if not classname:
                            continue

                        funcname = classname + ' :: ' + real_funcname
                        pdg = getFuncPDGByNameAndtestID_noctrl(funcname, testID, slice_id=slice_id)


                    elif funcname.find('.') != -1:
                        real_funcname = funcname.split('.')[-1].strip()
                        objectname = funcname.split('.')[0].strip()

                        funcID = node['functionId']
                        src_pdg = getFuncPDGByNameAndtestID_noctrl(funcID, testID, slice_id=slice_id)
                        if src_pdg == False:
                            continue
                        classname = False
                        for src_pnode in src_pdg.vs:
                            if src_pnode['code'].find(objectname) != -1 and src_pnode['code'].find(' new ') != -1:
                                tempvalue = src_pnode['code'].split(' new ')[1].replace('*', '').strip()
                                if tempvalue.split(' ')[0] != 'const':
                                    classname = tempvalue.split(' ')[0]
                                else:
                                    classname = tempvalue.split(' ')[1]

                                break

                        if classname == False:
                            continue

                        funcname = classname + ' :: ' + real_funcname
                        pdg = getFuncPDGByNameAndtestID(funcname, testID)

                    elif funcname.find('.') != -1:
                        real_funcname = funcname.split('.')[-1].strip()
                        objectname = funcname.split('.')[0].strip()

                        funcID = node['functionId']
                        src_pdg = getFuncPDGByfuncIDAndtestID(funcID, testID)
                        classname = False
                        for src_pnode in src_pdg.vs:
                            if src_pnode['code'].find(objectname) != -1 and src_pnode['code'].find(' new ') != -1:
                                tempvalue = src_pnode['code'].split(' new ')[1].replace('*', '').strip()
                                if tempvalue.split(' ')[0] != 'const':
                                    classname = tempvalue.split(' ')[0]
                                else:
                                    classname = tempvalue.split(' ')[1]

                                break

                        if classname == False:
                            continue

                        funcname = classname + ' :: ' + real_funcname
                        pdg = getFuncPDGByNameAndtestID(funcname, testID, slice_id)

                    else:
                        pdg = getFuncPDGByNameAndtestID(funcname, testID, slice_id)

                    if pdg == False:
                        not_scan_func_list.append(node['name'])
                        continue

                    else:
                        if slicetype == 0:
                            ret_node = []
                            for vertex in pdg.vs:
                                if vertex['type'] == 'ReturnStatement':
                                    ret_node.append(vertex)

                            result_list = program_slice_backwards(pdg, ret_node)
                            not_scan_func_list.append(node['name'])

                            index = 0
                            for result_node in list_result_node:
                                if result_node['name'] == node['name']:
                                    break
                                else:
                                    index += 1

                            list_result_node = list_result_node[:index + 1] + result_list + list_result_node[index + 1:]

                            list_result_node, not_scan_func_list = process_cross_func(result_list, testID, slicetype,
                                                                                      list_result_node,
                                                                                      not_scan_func_list,
                                                                                      slice_id=slice_id)
                        elif slicetype == 1:
                            param_node = []
                            FuncEntryNode = False
                            for vertex in pdg.vs:
                                if vertex['type'] == 'Parameter':
                                    param_node.append(vertex)
                                elif vertex['type'] == 'Function':
                                    FuncEntryNode = vertex

                            if param_node != []:
                                result_list = program_slice_forward(pdg, param_node)
                            else:
                                result_list = sortedNodesByLoc(pdg.vs)

                            not_scan_func_list.append(node['name'])
                            index = 0

                            for result_node in list_result_node:
                                if result_node['name'] == node['name']:
                                    break
                                else:
                                    index += 1

                            if FuncEntryNode:
                                result_list.insert(0, FuncEntryNode)

                            list_result_node = list_result_node[:index + 1] + result_list + list_result_node[index + 1:]

                            list_result_node, not_scan_func_list = process_cross_func(result_list, testID, slicetype,
                                                                                      list_result_node,
                                                                                      not_scan_func_list,
                                                                                      slice_id=slice_id)

    return list_result_node, not_scan_func_list


def process_crossfuncs_back_byfirstnode(list_tuple_results_back, testID, i, not_scan_func_list):
    # is not a good way in time, list_tuple_results_back=[(results_back, itertimes)]
    while i < len(list_tuple_results_back):
        iter_time = list_tuple_results_back[i][1]
        if iter_time == 3 or iter_time == -1:  # allow cross 3 funcs:
            i += 1
            continue

        else:
            list_node = list_tuple_results_back[i][0]

            if len(list_node) == 1:
                i += 1
                continue

            if list_node[1]['type'] == 'Parameter':
                func_name = list_node[0]['name']
                path = os.path.join('/home/zheng/Desktop/locator_dict/26/dict_call2cfgNodeID_funcID', testID,
                                    'dict.pkl')

                if not os.path.exists(path):
                    i += 1
                    continue

                fin = open(path, 'rb')
                # print testID
                _dict = pickle.load(fin)
                fin.close()

                if func_name not in _dict.keys():
                    list_tuple_results_back[i][1] = -1
                    i += 1
                    continue

                else:
                    list_cfgNodeID = _dict[func_name]
                    dict_func_pdg = getFuncPDGBynodeIDAndtestID(list_cfgNodeID, testID)
                    iter_time += 1
                    _new_list = []
                    for item in dict_func_pdg.items():
                        targetPDG = item[1]
                        startnode = []
                        for n in targetPDG.vs:
                            if n['name'] == item[0]:  # is id
                                startnode = [n]
                                break

                        if startnode == []:
                            continue
                        ret_list = program_slice_backwards(targetPDG, startnode)
                        not_scan_func_list.append(startnode[0]['name'])

                        ret_list = ret_list + list_node
                        _new_list.append([ret_list, iter_time])

                    if _new_list != []:
                        del list_tuple_results_back[i]
                        list_tuple_results_back = list_tuple_results_back + _new_list
                        list_tuple_results_back, not_scan_func_list = process_crossfuncs_back_byfirstnode(
                            list_tuple_results_back, testID, i, not_scan_func_list)
                    else:
                        list_tuple_results_back[i][1] = -1
                        i += 1
                        continue


            else:
                funcname = list_node[0]['code']
                if funcname.find("::") > -1:

                    path = os.path.join('/home/zheng/Desktop/locator_dict/26/dict_call2cfgNodeID_funcID', testID,
                                        'dict.pkl')  # get funname and it call place
                    fin = open(path, 'rb')
                    _dict = pickle.load(fin)
                    fin.close()

                    func_name = list_node[0]['name']
                    if func_name not in _dict.keys():
                        list_tuple_results_back[i][1] = -1
                        i += 1
                        continue

                    else:
                        list_cfgNodeID = _dict[func_name]
                        dict_func_pdg = getFuncPDGBynodeIDAndtestID(list_cfgNodeID, testID)

                        iter_time += 1
                        _new_list = []
                        for item in dict_func_pdg.items():
                            targetPDG = item[1]
                            startnode = []
                            for n in targetPDG.vs:
                                if n['name'] == item[0]:  # is id
                                    startnode = [n]
                                    break
                            if startnode == []:
                                continue
                            ret_list = program_slice_backwards(targetPDG, startnode)
                            not_scan_func_list.append(startnode[0]['name'])

                            ret_list = ret_list + list_node
                            _new_list.append([ret_list, iter_time])

                        if _new_list != []:
                            del list_tuple_results_back[i]
                            list_tuple_results_back = list_tuple_results_back + _new_list
                            list_tuple_results_back, not_scan_func_list = process_crossfuncs_back_byfirstnode(
                                list_tuple_results_back, testID, i, not_scan_func_list)

                        else:
                            list_tuple_results_back[i][1] = -1
                            i += 1
                            continue

                else:
                    i += 1
                    continue

    return list_tuple_results_back, not_scan_func_list


def get_readable_word_by_nodes(nodes, type):
    f = open(type, 'wb')
    for node in nodes:
        if node['location'] is not None:
            location = node['location'].split(':')
            row = location[0]
            col = location[1]
            print(row, ':', col)
            f.write(row + "_" + col + '\t')
        f.write(node['code'] + '\n')
    f.close()


def main():
    j = JoernSteps()
    j.connectToDatabase()

    func_node = getFunctionNodeByName(j, 'WDA_TxPacket')
    initpdg = translatePDGfullByNode(j, func_node[0])

    filename = getFuncFile(j, func_node[0]._id)
    # print(func_node[])
    testID = filename.split('/')[-3] + '/' + filename.split('/')[-2]  # vul + CWExxxx-xxxx
    pdg = getFuncPDGById(testID=testID, pdg_funcid=func_node[0]._id, slice_id=1)
    all_pdg_nodes = []
    condition_startNode = []
    return_startNode = []
    expresssion_startNode = []
    list_locationNode = []
    for node in pdg.vs:
        all_pdg_nodes.append(node)
        # if 'vdev_id >= wma_handle -> max_bssid' in node['code']: # test Condition and IfStatement
        #     list_startNode.append(node)
        # if 'vos_get_context' in node['code']: # test ExpressionStatement
        #     list_startNode.append(node)
        if node['location'] is not None and int(node['location'].split(':')[0]) == 19:
            expresssion_startNode.append(node)
        if node['location'] is not None and int(node['location'].split(':')[0]) == 14:
            condition_startNode.append(node)
        if node['location'] is not None and int(node['location'].split(':')[0]) == 11:
            return_startNode.append(node)
        if node['location'] is not None:
            list_locationNode.append(node)
        # print(node['code'])
    # all_nodes = getAllNodesByFuncNode(j, func_node[0]._id)

    # for node in all_nodes:
    #     # if 'vdev_id >= wma_handle -> max_bssid' in node['code']: # test Condition and IfStatement
    #     #     list_startNode.append(node)
    #     # if 'vos_get_context' in node['code']: # test ExpressionStatement
    #     #     list_startNode.append(node)
    #     if node['location'] is not None and int(node['location'].split(':')[0]) == 19:
    #         list_startNode.append(node)
    #     if node['location'] is not None:
    #         list_locationNode.append(node)
    #     print(node['code'])

    # list_startNode.append(func_node[0])

    # pdg
    # expression
    # res = program_slice_mvp_forward(pdg, list_startNode=expresssion_startNode, func_id=func_node[0]._id)
    # get_readable_word_by_nodes(res, type='pdg_expression_mvp')
    # res = program_slice_forward(pdg, list_startNode=expresssion_startNode)
    # get_readable_word_by_nodes(res, type='pdg_expression_normal')
    # # condition
    # res = program_slice_mvp_forward(pdg, list_startNode=condition_startNode, func_id=func_node[0]._id)
    # cond_back = program_slice_backwards(pdg,list_startNode=condition_startNode)
    # get_readable_word_by_nodes(sortedNodesByLoc(res+cond_back), type='pdg_condition_mvp')
    # res = program_slice_forward(pdg, list_startNode=condition_startNode)
    # get_readable_word_by_nodes(sortedNodesByLoc(res+cond_back), type='pdg_condition_normal')
    # # return
    # res = program_slice_mvp_forward(pdg, list_startNode=return_startNode, func_id=func_node[0]._id)
    # get_readable_word_by_nodes(res, type='pdg_return_mvp')
    # res = program_slice_forward(pdg, list_startNode=return_startNode)
    # get_readable_word_by_nodes(res, type='pdg_return_normal')

    # temp = []
    # for edge in initpdg.es:
    #     print(edge)
    #     u = initpdg.vs[edge.source]
    #     v = initpdg.vs[edge.target]

    # if u['location'] is not None and u['location'].split(':')[0] == str(
    #         19) and v['location'] is not None and v['location'].split(':')[0] == str(20):
    #     temp.append(edge)
    condition_startNode = []
    return_startNode = []
    expresssion_startNode = []
    for node in initpdg.vs:
        if node['location'] is not None and int(node['location'].split(':')[0]) == 19:
            expresssion_startNode.append(node)
        if node['location'] is not None and int(node['location'].split(':')[0]) == 25:
            condition_startNode.append(node)
        if node['location'] is not None and int(node['location'].split(':')[0]) == 11:
            return_startNode.append(node)
    # init pdg
    pdg = initpdg

    # res = program_slice_mvp_forward(pdg, list_startNode=expresssion_startNode, func_id=func_node[0]._id)
    # get_readable_word_by_nodes(res, type='initpdg_expression_mvp')
    res = program_slice_forward(pdg, list_startNode=expresssion_startNode)
    get_readable_word_by_nodes(res, type='initpdg_expression_normal')
    # condition
    # cond_back = program_slice_backwards(pdg, list_startNode=condition_startNode)
    # res = program_slice_forward(pdg, list_startNode=condition_startNode)
    # get_readable_word_by_nodes(sortedNodesByLoc(res + cond_back), type='initpdg_condition_normal')
    # res = program_slice_mvp_forward(pdg, list_startNode=condition_startNode, func_id=func_node[0]._id)
    # get_readable_word_by_nodes(sortedNodesByLoc(res+cond_back), type='initpdg_condition_mvp')

    # return
    # res = program_slice_forward(pdg, list_startNode=return_startNode)
    # del_ctrl_edge(pdg)
    # ret = program_slice_backwards(pdg,list_startNode=return_startNode)
    #
    # get_readable_word_by_nodes(ret,type='initpdg_return_back_normal_del')
    # get_readable_word_by_nodes(res, type='initpdg_return_normal')
    # res = program_slice_mvp_forward(pdg, list_startNode=return_startNode, func_id=func_node[0]._id)
    # get_readable_word_by_nodes(res, type='initpdg_return_mvp')


if __name__ == "__main__":
    main()
