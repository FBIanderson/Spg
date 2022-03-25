## coding:utf-8
import os.path

from access_db_operate import *
import tqdm


def get_all_sensitiveAPI(db):
    fin = open("data/sensitive_func.pkl", 'rb')
    list_sensitive_funcname = pickle.load(fin)
    fin.close()
    co = 0
    _dict = {}
    print ('get_all_sensitiveAPI')
    # print list_sensitive_funcname
    for func_name in tqdm.tqdm(list_sensitive_funcname):
        list_callee_cfgnodeID = []
        if func_name.find('main') != -1:
            list_main_func = []
            list_mainfunc_node = getFunctionNodeByName(db, func_name)
            # print list_mainfunc_node
            if list_mainfunc_node != []:
                file_path = getFuncFile(db, list_mainfunc_node[0]._id)
                testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
                for mainfunc in list_mainfunc_node:
                    list_parameters = get_parameter_by_funcid(db, mainfunc._id)

                    if list_parameters != []:
                        list_callee_cfgnodeID.append(
                            [testID, ([str(v) for v in list_parameters], str(mainfunc._id), func_name)])

                    else:
                        continue

        else:
            list_callee_id = get_calls_id(db, func_name)
            # print list_callee_id
            if list_callee_id == []:
                continue

            for _id in list_callee_id:
                cfgnode = getCFGNodeByCallee(db, _id)
                if cfgnode != None:
                    file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
                    testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
                    list_callee_cfgnodeID.append(
                        [testID, ([str(cfgnode._id)], str(cfgnode.properties['functionId']), func_name)])
                    # print list_callee_cfgnodeID
                    # print 'finish'
        if list_callee_cfgnodeID != []:
            for _l in list_callee_cfgnodeID:
                if _l[0] in _dict.keys():
                    _dict[_l[0]].append(_l[1])
                else:
                    _dict[_l[0]] = [_l[1]]

        else:
            continue

    return _dict


def get_all_pointer(db):
    _dict = {}
    list_pointers_node = get_pointers_node(db)
    print ('get_all_pointer')
    for cfgnode in tqdm.tqdm(list_pointers_node):
        file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
        testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
        pointer_defnode = get_def_node(db, cfgnode._id)
        pointer_name = []
        for node in pointer_defnode:
            name = node.properties['code'].replace('*', '').strip()
            if name not in pointer_name:
                pointer_name.append(name)

        if testID in _dict.keys():
            _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), pointer_name))
        else:
            _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), pointer_name)]

    return _dict


def get_all_array(db):
    _dict = {}
    list_arrays_node = get_arrays_node(db)

    print ('get_all_array')
    for cfgnode in tqdm.tqdm(list_arrays_node):
        file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
        testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
        array_defnode = get_def_node(db, cfgnode._id)
        array_name = []
        for node in array_defnode:
            name = node.properties['code'].replace('[', '').replace(']', '').replace('*', '').strip()
            if name not in array_name:
                array_name.append(name)

        if testID in _dict.keys():
            _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), array_name))
        else:
            _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), array_name)]

    return _dict


def get_all_pointer_use(db):
    _dict = {}
    list_pointers_node = get_pointers_node(db)

    # print ('get_all_pointer_use')
    for cfgnode in tqdm.tqdm(list_pointers_node):
        file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
        testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
        pointer_defnode = get_def_node(db, cfgnode._id)
        _temp_list = []
        for node in pointer_defnode:
            name = node.properties['code'].strip()
            list_usenodes = get_all_use_bydefnode(db, node._id)
            list_defnodes = get_all_def_bydefnode(db, node._id)

            i = 0
            while i < len(list_defnodes):
                if list_defnodes[i]._id == cfgnode._id:
                    del list_defnodes[i]
                else:
                    i += 1

            list_usenodes += list_defnodes
            # print len(list_usenodes)
            for i in list_usenodes:
                if str(i).find("location") == -1:
                    list_usenodes.remove(i)
            loc_list = []
            final_list = []
            # print list_usenodes
            for i in list_usenodes:
                # print(i)
                if 'location' in str(i):
                    if 'location:' in str(i):
                        location = str(i).split(",type:")[0].split("location:")[1][1:-1].split(":")
                        count = int(location[0])
                        loc_list.append(count)
                    else:
                        loc_list.append(0)
            # print loc_list
            if len(loc_list) != 0:
                a = loc_list.index(max(loc_list))
                final_list.append(list_usenodes[a])
            for use_node in final_list:
                if use_node._id in _temp_list:
                    continue
                else:
                    _temp_list.append(use_node._id)

                if testID in _dict.keys():
                    _dict[testID].append(([str(use_node._id)], str(use_node.properties['functionId']), name))
                else:
                    _dict[testID] = [([str(use_node._id)], str(use_node.properties['functionId']), name)]
    return _dict


def get_all_pointer_use_new(db):
    _dict = {}
    list_pointers_node = get_pointers_node(db)

    # print ('get_all_pointer_use')
    for cfgnode in tqdm.tqdm(list_pointers_node):
        file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
        testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
        name = cfgnode.properties['code'].strip()
        if testID in _dict.keys():
            _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), name))
        else:
            _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), name)]
    return _dict


def get_all_parameter_use(db):
    _dict = {}
    list_param_node = get_param_node(db)
    for cfgnode in tqdm.tqdm(list_param_node):
        file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
        testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
        name = cfgnode.properties['code'].strip()
        if testID in _dict.keys():
            _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), name))
        else:
            _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), name)]
    return _dict


def get_all_return_use(db):
    _dict = {}
    list_return_node = get_return_node(db)
    for cfgnode in tqdm.tqdm(list_return_node):
        file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
        testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
        name = cfgnode.properties['code'].strip()
        if testID in _dict.keys():
            _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), name))
        else:
            _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), name)]
    return _dict


def get_all_array_use(db):
    _dict = {}
    list_arrays_node = get_arrays_node(db)
    # print (get_all_array_use)
    for cfgnode in tqdm.tqdm(list_arrays_node):
        file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
        testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
        array_defnode = get_def_node(db, cfgnode._id)

        _temp_list = []
        for node in array_defnode:
            name = node.properties['code'].strip()
            list_usenodes = get_all_use_bydefnode(db, node._id)
            list_defnodes = get_all_def_bydefnode(db, node._id)

            i = 0
            while i < len(list_defnodes):
                if list_defnodes[i]._id == cfgnode._id:
                    del list_defnodes[i]
                else:
                    i += 1

            list_usenodes += list_defnodes

            for use_node in list_usenodes:
                if use_node._id in _temp_list:
                    continue
                else:
                    _temp_list.append(use_node._id)

                if testID in _dict.keys():
                    _dict[testID].append(([str(use_node._id)], str(use_node.properties['functionId']), name))
                else:
                    _dict[testID] = [([str(use_node._id)], str(use_node.properties['functionId']), name)]

    return _dict


def get_all_integeroverflow_point(db):
    _dict = {}
    list_exprstmt_node = get_exprstmt_node(db)
    print ('get_all_integeroverflow_point')
    for cfgnode in tqdm.tqdm(list_exprstmt_node):
        if cfgnode.properties['code'].find(' = ') > -1:
            code = cfgnode.properties['code'].split(' = ')[-1]
            pattern = re.compile("((?:_|[A-Za-z])\w*(?:\s(?:\+|\-|\*|\/)\s(?:_|[A-Za-z])\w*)+)")
            result = re.search(pattern, code)

            if result is None:
                continue
            else:
                file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
                testID = file_path.split('/')[-3] + '/' + file_path.split('/')[-2]  # vul + CWExxxx-xxxx
                name = cfgnode.properties['code'].strip()

                if testID in _dict.keys():
                    _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), name))
                else:
                    _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), name)]

        else:
            code = cfgnode.properties['code']
            pattern = re.compile("(?:\s\/\s(?:_|[A-Za-z])\w*\s)")
            result = re.search(pattern, code)
            if result is None:
                continue

            else:
                file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
                testID = file_path.split('/')[-2]
                name = cfgnode.properties['code'].strip()

                if testID in _dict.keys():
                    _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), name))
                else:
                    _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), name)]

    return _dict


def get_all_delete_statements(db):
    pass


def get_all_vul_points(db):
    fin = open("data/cve_vul_characters", 'rb')
    cve2sensitiveKey = {}
    for line in fin:
        line = line.rstrip()
        words = line.split("@")
        key = words[0]
        value = []
        for i in range(1, len(words)):
            value.append(words[i])
        cve2sensitiveKey[key] = value
    fin.close()
    _dict = {}
    print ('get_all_vul_points')
    for cve, sensitiveWords in tqdm.tqdm(cve2sensitiveKey.items()):
        func_nodes = getFuncNodeInTestID(db, cve)
        if not func_nodes:
            continue
        for func_node in func_nodes:
            filepath = getFuncFile(db, func_node._id)
            if 'fix' in filepath:
                curr = 'fix/' + cve
            else:
                curr = 'vul/' + cve
            nodes = getAllNodesByFuncNode(db, func_node._id)
            cnt = 0
            node_queue = []
            for sensitiveWord in sensitiveWords:
                for node in nodes:
                    if cnt > 10:
                        break
                    if sensitiveWord in node['code']:
                        if node['type'] == 'Function':
                            cnt += 1
                            if curr in _dict.keys():
                                _dict[curr].append(([str(node._id)], str(node.properties['functionId']), sensitiveWord))
                            # _dict[cve].append(node._id)
                            else:
                                _dict[curr] = [([str(node._id)], str(node.properties['functionId']), sensitiveWord)]
                        else:
                            node_queue.append((node, sensitiveWord))
                        break
            while (curr not in _dict or len(_dict[curr]) < 50) and len(node_queue) > 0:
                node, sensitiveWord = node_queue.pop()
                if curr in _dict.keys():
                    _dict[curr].append(([str(node._id)], str(node.properties['functionId']), sensitiveWord))
                # _dict[cve].append(node._id)
                else:
                    _dict[curr] = [([str(node._id)], str(node.properties['functionId']), sensitiveWord)]

    return _dict


def get_all_mvp_vul_points(db):
    fin = open("data/cve_vul_characters", 'rb')
    filepath_to_line = dict()
    cve2sensitiveKey = {}
    for line in fin:
        line = line.rstrip()
        words = line.split("@")
        key = words[0]
        value = []
        for i in range(1, len(words)):
            value.append(words[i])
        cve2sensitiveKey[key] = value
    fin.close()
    _dict = {}
    print ('get_all_vul_points')
    for cve, sensitiveWords in tqdm.tqdm(cve2sensitiveKey.items()):
        func_nodes = getFuncNodeInTestID(db, cve)
        if not func_nodes:
            continue
        for func_node in func_nodes:
            filepath = getFuncFile(db, func_node._id)
            f = open(filepath, 'rb')
            lines = f.readlines()
            sensitive_rows = []
            sensitive_lines = []
            for sensitiveWord in sensitiveWords:
                if len(sensitive_rows) > 0:
                    break
                for i in range(len(lines)):
                    line = lines[i]
                    if sensitiveWord in line:
                        sensitive_rows.append(i + 1)
                        filepath_to_line[filepath] = i + 1
                        sensitive_lines.append(line)
                        break
            if 'fix' in filepath:
                curr = 'fix/' + cve
            else:
                curr = 'vul/' + cve
            nodes = getAllNodesByFuncNode(db, func_node._id)
            cnt = 0
            for node in nodes:
                if node['location'] is not None and int(node['location'].split(":")[0]) in sensitive_rows:
                    cnt += 1
                    if curr in _dict.keys():
                        _dict[curr].append(([str(node._id)], str(node.properties['functionId']), sensitive_lines[0]))
                    else:
                        _dict[curr] = [([str(node._id)], str(node.properties['functionId']), sensitive_lines[0])]
            if cnt > 0:
                record_file = open('data/points_get_record.txt', 'a')
                record_file.write(curr + '/' + filepath.split('/')[-1] + " row ")
                for temp in sensitive_rows:
                    record_file.write(" " + str(temp))
                for line in sensitive_lines:
                    record_file.write(" " + line)
                continue
            error_file = open('data/points_get_error.txt', 'a')
            error_file.write(curr + '/' + filepath.split('/')[-1] + " row not found \n")
            cnt = 0
            node_queue = []
            for sensitiveWord in sensitiveWords:
                for node in nodes:
                    if cnt > 10:
                        break
                    if sensitiveWord in node['code']:
                        if node['type'] == 'Function':
                            cnt += 1
                            if curr in _dict.keys():
                                _dict[curr].append(([str(node._id)], str(node.properties['functionId']), sensitiveWord))
                            else:
                                _dict[curr] = [([str(node._id)], str(node.properties['functionId']), sensitiveWord)]
                        else:
                            node_queue.append((node, sensitiveWord))
                        break
            while (curr not in _dict or len(_dict[curr]) < 50) and len(node_queue) > 0:
                node, sensitiveWord = node_queue.pop()
                if curr in _dict.keys():
                    _dict[curr].append(([str(node._id)], str(node.properties['functionId']), sensitiveWord))
                else:
                    _dict[curr] = [([str(node._id)], str(node.properties['functionId']), sensitiveWord)]
    pickle.dump(filepath_to_line, open('data/filepath_to_line_dict.pkl', 'wb'))
    return _dict


"""
get the start point of each function
"""


def main(slice_id=1):
    j = JoernSteps()
    j.connectToDatabase()

    # slice start point
    path = "/home/anderson/Desktop/locator_point/" + str(slice_id)
    if not os.path.exists(path):
        os.makedirs(path)

    # _dict = get_all_sensitiveAPI(j)
    # f = open(path + "/sensifunc_slice_points.pkl", 'wb')
    # pickle.dump(_dict, f, True)
    # f.close()

    # _dict = get_all_pointer_use_new(j)
    # f = open(path + "/pointuse_slice_points_new.pkl", 'wb')
    # pickle.dump(_dict, f, True)
    # f.close()
    #
    # _dict = get_all_array_use(j)
    # f = open(path + "/arrayuse_slice_points.pkl", 'wb')
    # pickle.dump(_dict, f, True)
    # f.close()
    #
    # _dict = get_all_integeroverflow_point(j)
    # f = open(path + "/integeroverflow_slice_points_new.pkl", 'wb')
    # pickle.dump(_dict, f, True)
    # f.close()
    #
    # _dict = get_all_parameter_use(j)
    # f = open(path + "/param_slice_points_new.pkl", 'wb')
    # pickle.dump(_dict, f, True)
    # f.close()
    #
    # _dict = get_all_return_use(j)
    # f = open(path + "/return_slice_points_new.pkl", 'wb')
    # pickle.dump(_dict, f, True)
    # f.close()

    _dict = get_all_mvp_vul_points(j)
    f = open(path + "/mvp_vul_points.pkl", 'wb')
    pickle.dump(_dict, f, True)
    f.close()

    # print _dict
    # for key in _dict:
    #     print(key)


if __name__ == '__main__':
    main(slice_id=4)
