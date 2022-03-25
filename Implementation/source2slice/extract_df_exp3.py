## coding:utf-8
from Implementation.source2slice.every_type_graph.tree import Tree
from joern.all import JoernSteps
from igraph import *
from access_db_operate import *
from slice_op import *
from py2neo.packages.httpstream import http

http.socket_timeout = 9999
import tqdm
import os


def get_slice_ciretion(store_filepath, list_result, count, func_name, startline, filepath_all):
    list_for_line = []
    statement_line = 0
    vulnline_row = 0
    list_write2file = []

    for node in list_result:
        if node['type'] == 'Function':
            if not os.path.isfile(node['filepath']):
                continue
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0]) - 1
            code = content[raw].strip()

            new_code = ""
            if code.find("#define") != -1:
                list_write2file.append(code + ' ' + str(raw + 1) + '\n')
                continue

            while len(code) >= 1 and code[-1] != ')' and code[-1] != '{':
                if code.find('{') != -1:
                    index = code.index('{')
                    new_code += code[:index].strip()
                    list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                    break

                else:
                    new_code += code + '\n'
                    raw += 1
                    code = content[raw].strip()
                    # print "raw", raw, code

            else:
                new_code += code
                new_code = new_code.strip()
                if new_code[-1] == '{':
                    new_code = new_code[:-1].strip()
                    list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                    # list_line.append(str(raw+1))
                else:
                    list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                    # list_line.append(str(raw+1))

        elif node['type'] == 'Condition':
            raw = int(node['location'].split(':')[0]) - 1
            if raw in list_for_line:
                continue
            else:
                # print node['type'], node['code'], node['name']
                if not os.path.isfile(node['filepath']):
                    continue
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                code = content[raw].strip()
                pattern = re.compile("(?:if|while|for|switch)")
                # print code
                res = re.search(pattern, code)
                if res == None:
                    raw = raw - 1
                    code = content[raw].strip()
                    new_code = ""

                    while (code[-1] != ')' and code[-1] != '{'):
                        if code.find('{') != -1:
                            index = code.index('{')
                            new_code += code[:index].strip()
                            list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                            # list_line.append(str(raw+1))
                            list_for_line.append(raw)
                            break

                        else:
                            new_code += code + '\n'
                            list_for_line.append(raw)
                            raw += 1
                            code = content[raw].strip()

                    else:
                        new_code += code
                        new_code = new_code.strip()
                        if new_code[-1] == '{':
                            new_code = new_code[:-1].strip()
                            list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                            # list_line.append(str(raw+1))
                            list_for_line.append(raw)

                        else:
                            list_for_line.append(raw)
                            list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                            # list_line.append(str(raw+1))

                else:
                    res = res.group()
                    if res == '':
                        print filepath_all + ' ' + func_name + " error!"
                        exit()

                    elif res != 'for':
                        new_code = res + ' ( ' + node['code'] + ' ) '
                        list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                        # list_line.append(str(raw+1))

                    else:
                        new_code = ""
                        if code.find(' for ') != -1:
                            code = 'for ' + code.split(' for ')[1]

                        while code != '' and code[-1] != ')' and code[-1] != '{':
                            if code.find('{') != -1:
                                index = code.index('{')
                                new_code += code[:index].strip()
                                list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))
                                list_for_line.append(raw)
                                break

                            elif code[-1] == ';' and code[:-1].count(';') >= 2:
                                new_code += code
                                list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))
                                list_for_line.append(raw)
                                break

                            else:
                                new_code += code + '\n'
                                list_for_line.append(raw)
                                raw += 1
                                code = content[raw].strip()

                        else:
                            new_code += code
                            new_code = new_code.strip()
                            if new_code[-1] == '{':
                                new_code = new_code[:-1].strip()
                                list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))
                                list_for_line.append(raw)

                            else:
                                list_for_line.append(raw)
                                list_write2file.append(new_code + ' ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))

        elif node['type'] == 'Label':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0]) - 1
            code = content[raw].strip()
            list_write2file.append(code + ' ' + str(raw + 1) + '\n')
            # list_line.append(str(raw+1))

        elif node['type'] == 'ForInit':
            continue

        elif node['type'] == 'Parameter':
            if list_result[0]['type'] != 'Function':
                row = node['location'].split(':')[0]
                list_write2file.append(node['code'] + ' ' + str(row) + '\n')
                # list_line.append(row)
            else:
                continue

        elif node['type'] == 'IdentifierDeclStatement':
            if node['code'].strip().split(' ')[0] == "undef":
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                raw = int(node['location'].split(':')[0]) - 1
                code1 = content[raw].strip()
                list_code2 = node['code'].strip().split(' ')
                i = 0
                while i < len(list_code2):
                    if code1.find(list_code2[i]) != -1:
                        del list_code2[i]
                    else:
                        break
                code2 = ' '.join(list_code2)

                list_write2file.append(code1 + ' ' + str(raw + 1) + '\n' + code2 + ' ' + str(raw + 2) + '\n')

            else:
                list_write2file.append(node['code'] + ' ' + node['location'].split(':')[0] + '\n')

        elif node['type'] == 'ExpressionStatement':
            row = int(node['location'].split(':')[0]) - 1
            if row in list_for_line:
                continue

            if node['code'] in ['\n', '\t', ' ', '']:
                list_write2file.append(node['code'] + ' ' + str(row + 1) + '\n')
                # list_line.append(row+1)
            elif node['code'].strip()[-1] != ';':
                list_write2file.append(node['code'] + '; ' + str(row + 1) + '\n')
                # list_line.append(row+1)
            else:
                list_write2file.append(node['code'] + ' ' + str(row + 1) + '\n')
                # list_line.append(row+1)

        elif node['type'] == "Statement":
            row = node['location'].split(':')[0]
            list_write2file.append(node['code'] + ' ' + str(row) + '\n')
            # list_line.append(row+1)

        else:
            # print node['name'], node['code'], node['type'], node['filepath']
            if node['location'] is None or not os.path.isfile(node['filepath']):
                continue
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            row = int(node['location'].split(':')[0]) - 1
            code = content[row].strip()
            if row in list_for_line:
                continue

            else:
                list_write2file.append(node['code'] + ' ' + str(row + 1) + '\n')
                # list_line.append(str(row+1))

    f = open(os.path.join(store_filepath, "critrion.txt"), 'a')
    f.write(str(count) + ' ' + filepath_all + ' ' + func_name + ' ' + startline + '\n')
    f.close()


def get_slice_file_sequence(store_filepath, list_result, count, func_name, startline, filepath_all):
    # print 'get_slice_file_sequence'
    list_for_line = []
    statement_line = 0
    vulnline_row = 0
    list_write2file = []

    for node in list_result:
        if node['type'] == 'Function':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0]) - 1
            code = content[raw].strip()

            new_code = ""
            if code.find("#define") != -1:
                list_write2file.append(code + ' ! ' + str(raw + 1) + '\n')
                continue

            while len(code) >= 1 and code[-1] != ')' and code[-1] != '{':
                if code.find('{') != -1:
                    index = code.index('{')
                    new_code += code[:index].strip()
                    list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                    break

                else:
                    new_code += code + '\n'
                    raw += 1
                    code = content[raw].strip()
                    # print "raw", raw, code

            else:
                new_code += code
                new_code = new_code.strip()
                if new_code[-1] == '{':
                    new_code = new_code[:-1].strip()
                    list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                    # list_line.append(str(raw+1))
                else:
                    list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                    # list_line.append(str(raw+1))

        elif node['type'] == 'Condition':
            # print 'condition'
            raw = int(node['location'].split(':')[0]) - 1
            if raw in list_for_line:
                continue
            else:
                # print node['type'], node['code'], node['name']
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                code = content[raw].strip()
                pattern = re.compile("(?:if|while|for|switch)")
                # print code
                res = re.search(pattern, code)
                if res == None:
                    print 'NOne'
                    raw = raw
                    # print content[raw]
                    code = content[raw].strip()
                    new_code = ""
                    # counn = code.find('{')
                    # print counn
                    # if code!="":
                    # print code
                    while (code != '' and code[-1] != ')' and code[-1] != '{'):
                        if code.find('{') != -1:
                            index = code.index('{')
                            new_code += code[:index].strip()
                            list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                            # list_line.append(str(raw+1))
                            list_for_line.append(raw)
                            break

                        else:
                            new_code += code + '\n'
                            list_for_line.append(raw)
                            raw += 1
                            code = content[raw].strip()
                            # print content[raw]


                    else:
                        new_code += code
                        new_code = new_code.strip()
                        if new_code[-1] == '{':
                            new_code = new_code[:-1].strip()
                            list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                            # list_line.append(str(raw+1))
                            list_for_line.append(raw)

                        else:
                            list_for_line.append(raw)
                            list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                            # list_line.append(str(raw+1))

                else:
                    res = res.group()
                    if res == '':
                        print filepath_all + ' ' + func_name + " error!"
                        exit()

                    elif res != 'for':
                        new_code = res + ' ( ' + node['code'] + ' ) '
                        list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                        # list_line.append(str(raw+1))

                    else:
                        new_code = ""
                        if code.find(' for ') != -1:
                            code = 'for ' + code.split(' for ')[1]

                        while code != '' and code[-1] != ')' and code[-1] != '{':
                            if code.find('{') != -1:
                                index = code.index('{')
                                new_code += code[:index].strip()
                                list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))
                                list_for_line.append(raw)
                                break

                            elif code[-1] == ';' and code[:-1].count(';') >= 2:
                                new_code += code
                                list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))
                                list_for_line.append(raw)
                                break

                            else:
                                new_code += code + '\n'
                                list_for_line.append(raw)
                                raw += 1
                                code = content[raw].strip()

                        else:
                            new_code += code
                            new_code = new_code.strip()
                            if new_code[-1] == '{':
                                new_code = new_code[:-1].strip()
                                list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))
                                list_for_line.append(raw)

                            else:
                                list_for_line.append(raw)
                                list_write2file.append(new_code + ' ! ' + str(raw + 1) + '\n')
                                # list_line.append(str(raw+1))

        elif node['type'] == 'Label':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0]) - 1
            code = content[raw].strip()
            list_write2file.append(code + ' ! ' + str(raw + 1) + '\n')
            # list_line.append(str(raw+1))

        elif node['type'] == 'ForInit':
            continue

        elif node['type'] == 'Parameter':
            if list_result[0]['type'] != 'Function':
                row = node['location'].split(':')[0]
                list_write2file.append(node['code'] + ' ! ' + str(row) + '\n')
                # list_line.append(row)
            else:
                continue

        elif node['type'] == 'IdentifierDeclStatement':
            if node['code'].strip().split(' ')[0] == "undef":
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                raw = int(node['location'].split(':')[0]) - 1
                code1 = content[raw].strip()
                list_code2 = node['code'].strip().split(' ')
                i = 0
                while i < len(list_code2):
                    if code1.find(list_code2[i]) != -1:
                        del list_code2[i]
                    else:
                        break
                code2 = ' '.join(list_code2)

                list_write2file.append(code1 + ' ! ' + str(raw + 1) + '\n' + code2 + ' ! ' + str(raw + 2) + '\n')

            else:
                list_write2file.append(node['code'] + ' ! ' + node['location'].split(':')[0] + '\n')

        elif node['type'] == 'ExpressionStatement':
            row = int(node['location'].split(':')[0]) - 1
            if row in list_for_line:
                continue

            if node['code'] in ['\n', '\t', ' ', '']:
                list_write2file.append(node['code'] + ' ! ' + str(row + 1) + '\n')
                # list_line.append(row+1)
            elif node['code'].strip()[-1] != ';':
                list_write2file.append(node['code'] + '; ! ' + str(row + 1) + '\n')
                # list_line.append(row+1)
            else:
                list_write2file.append(node['code'] + ' ! ' + str(row + 1) + '\n')
                # list_line.append(row+1)

        elif node['type'] == "Statement":
            row = node['location'].split(':')[0]
            list_write2file.append(node['code'] + ' ! ' + str(row) + '\n')
            # list_line.append(row+1)

        else:
            # print node['name'], node['code'], node['type'], node['filepath']
            if node['location'] == None:
                continue
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            row = int(node['location'].split(':')[0]) - 1
            code = content[row].strip()
            if row in list_for_line:
                continue

            else:
                list_write2file.append(node['code'] + ' ! ' + str(row + 1) + '\n')
                # list_line.append(str(row+1))
    f = open(store_filepath, 'a')
    path = filepath_all.split('/')[-1]
    # f.write(str(count) + ' ' + filepath_all + ' ' + func_name + ' ' + startline + '\n')
    integename = func_name.split('=')[0]
    # integen = integename.split(' ')[-2]
    # f.write(path + '/(' +startline+ ',' + func_name + ')' +  '\n')
    f.write(path + '/(' + startline + ',' + integename + ')' + '\n')
    list_write2file2 = list(set(list_write2file))
    list_write2file2.sort(key=list_write2file.index)
    for wb in list_write2file2:
        f.write(wb)
    # f.write(label+ '\n')
    f.write('--------------finish--------------\n')
    f.close()


def program_slice(pdg, startnodesID, slicetype,
                  testID, slice_id):  # process startnodes as a list, because main func has many different arguments
    list_startnodes = []
    if pdg is False or pdg is None:
        return [], [], []
    for node in pdg.vs:
        # print node['functionId']
        if node['name'] in startnodesID:
            list_startnodes.append(node)

    if list_startnodes == []:
        return [], [], []

    if slicetype == 0:  # backwords
        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        print start_name
        startline_path = list_startnodes[0]['filepath']
        results_back = program_slice_backwards(pdg, list_startnodes)

        not_scan_func_list = []
        results_back, temp = process_cross_func(results_back, testID, 1, results_back, not_scan_func_list,
                                                slice_id=slice_id)

        return [results_back], start_line, startline_path

    elif slicetype == 1:  # forwords
        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        print start_name
        startline_path = list_startnodes[0]['filepath']
        results_for = program_slice_forward(pdg, list_startnodes)

        not_scan_func_list = []
        results_for, temp = process_cross_func(results_for, testID, 1, results_for, not_scan_func_list, slice_id)

        return [results_for], start_line, startline_path

    elif slicetype == 2:  # bi_direction
        # print "start extract backwords dataflow!"

        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_back = program_slice_backwards(pdg, list_startnodes)  # results_back is a list of nodes

        results_for = program_slice_forward(pdg, list_startnodes)

        _list_name = []
        for node_back in results_back:
            _list_name.append(node_back['name'])

        for node_for in results_for:
            if node_for['name'] in _list_name:
                continue
            else:
                results_back.append(node_for)

        results_back = sortedNodesByLoc(results_back)

        iter_times = 0
        start_list = [[results_back, iter_times]]
        i = 0
        not_scan_func_list = []
        list_cross_func_back, not_scan_func_list = process_crossfuncs_back_byfirstnode(start_list, testID, i,
                                                                                       not_scan_func_list)
        list_results_back = [l[0] for l in list_cross_func_back]

        all_result = []
        for results_back in list_results_back:
            index = 1
            for a_node in results_back:
                if a_node['name'] == start_name:
                    break
                else:
                    index += 1

            list_to_crossfunc_back = results_back[:index]
            list_to_crossfunc_for = results_back[index:]

            list_to_crossfunc_back, temp = process_cross_func(list_to_crossfunc_back, testID, 0, list_to_crossfunc_back,
                                                              not_scan_func_list, slice_id=slice_id)

            list_to_crossfunc_for, temp = process_cross_func(list_to_crossfunc_for, testID, 1, list_to_crossfunc_for,
                                                             not_scan_func_list, slice_id=slice_id)

            all_result.append(list_to_crossfunc_back + list_to_crossfunc_for)

        return all_result, start_line, startline_path
    else:  # mvp slice
        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_back = program_slice_backwards(pdg, list_startnodes)  # results_back is a list of nodes

        # results_for = program_slice_mvp_forward(pdg, list_startnodes, list_startnodes[0]['name'])
        results_for = program_slice_forward(pdg, list_startnodes)
        _list_name = []
        for node_back in results_back:
            _list_name.append(node_back['name'])

        for node_for in results_for:
            if node_for['name'] in _list_name:
                continue
            else:
                results_back.append(node_for)

        results_back = sortedNodesByLoc(results_back)

        iter_times = 0
        start_list = [[results_back, iter_times]]
        i = 0
        not_scan_func_list = []
        list_cross_func_back, not_scan_func_list = process_crossfuncs_back_byfirstnode(start_list, testID, i,
                                                                                       not_scan_func_list)
        list_results_back = [l[0] for l in list_cross_func_back]

        all_result = []
        for results_back in list_results_back:
            index = 1
            for a_node in results_back:
                if a_node['name'] == start_name:
                    break
                else:
                    index += 1

            list_to_crossfunc_back = results_back[:index]
            list_to_crossfunc_for = results_back[index:]

            list_to_crossfunc_back, temp = process_cross_func(list_to_crossfunc_back, testID, 0, list_to_crossfunc_back,
                                                              not_scan_func_list, slice_id=slice_id)

            list_to_crossfunc_for, temp = process_cross_func(list_to_crossfunc_for, testID, 1, list_to_crossfunc_for,
                                                             not_scan_func_list, slice_id=slice_id)

            all_result.append(list_to_crossfunc_back + list_to_crossfunc_for)

        return all_result, start_line, startline_path


'''
store_slice_path 
load_point_path start point
store_record_path record path 
store_real_path label
'''


def api_slice(store_slice_path, load_point_path, store_record_path, record_type, store_real_path, slice_id, db):
    count = 1
    store_filepath = store_slice_path
    f = open(load_point_path, 'rb')
    dict_unsliced_sensifunc = pickle.load(f)
    f.close()
    for key in tqdm.tqdm(dict_unsliced_sensifunc.keys(),
                         desc='sensitive api slice'):  # key is testID u'fix/CVE-2011-1927'
        dictlist = []
        idx = 0
        for _t in dict_unsliced_sensifunc[key]:
            if _t not in dictlist:
                dictlist.append(_t)
            else:
                continue
        for _t in dictlist:
            recordtemp = []
            list_sensitive_funcid = _t[0]
            pdg_funcid = _t[1]
            sensitive_funcname = _t[2]
            filename = getFuncFile(db=db, func_id=int(pdg_funcid))
            vul_line = str(filepath_to_line_dict[filename])
            label = 0
            ast_g = drawAstTreeGraph(db, getASTEdges(db, pdg_funcid), pdg_funcid)
            if sensitive_funcname.find("main") != -1:
                continue  # todo
            else:
                slice_dir = 2  # forwards and backwards
                pdg = getFuncPDGById(key, pdg_funcid, slice_id)
                if not pdg:
                    print 'api error'
                    exit()
                list_code, startline, startline_path = program_slice(pdg, list_sensitive_funcid, slice_dir, key,
                                                                     slice_id=slice_id)
                # print len(list_code)
                if not list_code:
                    fout = open("data/slice/api_error.txt", 'a')
                    fout.write(sensitive_funcname + ' ' + str(list_sensitive_funcid) + ' found nothing! \n')
                    fout.close()
                else:
                    _list = list_code[0]
                    functionlist = []
                    for node in _list:
                        functionID = node['functionId']
                        functionlist.append(functionID)
                    for m in range(len(_list)):
                        if m == len(_list) - 1:
                            continue
                        elif _list[m]['functionId'] != _list[m + 1]['functionId']:
                            d = dict()
                            d['sid'] = str(_list[m]['name'])
                            if _list[m]['location'] is None:
                                d['spro'] = {'type': str(_list[m]['type']),
                                             'code': str(_list[m]['code']),
                                             'lineNo': 'None',
                                             'ast_tree': sub_ast_tree(ast_g, _list[m])}
                            else:
                                if str(_list[m]['location'].split(':')[0]) == vul_line:
                                    label = 1
                                d['spro'] = {'type': str(_list[m]['type']),
                                             'code': str(_list[m]['code']),
                                             'lineNo': str(_list[m]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, _list[m])}
                            d['eid'] = str(_list[m + 1]['name'])
                            if _list[m + 1]['location'] is None:
                                d['epro'] = {'type': str(_list[m + 1]['type']),
                                             'code': str(_list[m + 1]['code']),
                                             'lineNo': 'None',
                                             'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                            else:
                                if str(_list[m + 1]['location'].split(':')[0]) == vul_line:
                                    label = 1
                                d['epro'] = {'type': str(_list[m + 1]['type']),
                                             'code': str(_list[m + 1]['code']),
                                             'lineNo': str(_list[m + 1]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                            d['label'] = str(4)
                            recordtemp.append(d)

                    functionlist = set(functionlist)
                    pdg_set = []
                    for functionID in functionlist:
                        pdg = getFuncPDGById(key, functionID, slice_id=slice_id)
                        pdg_set.append(pdg)
                    get_slice_ciretion(store_filepath, _list, count, sensitive_funcname, startline,
                                       startline_path)
                    for pdg in pdg_set:
                        i = 0
                        while i < pdg.vcount():
                            # if pdg.vs[i]['type'] == 'IdentifierDeclStatement' and pdg.vs[i] not in _list:
                            #     _list.append(pdg.vs[i])
                            if pdg.vs[i]['type'] == 'Parameter' and pdg.vs[i] not in _list:
                                _list.append(pdg.vs[i])
                            i = i + 1
                        listname = []
                        for listnode in _list:
                            listname.append(listnode['name'])
                        i = 0
                        while i < pdg.ecount():
                            if pdg.vs[pdg.es[i].source]['name'] in listname and pdg.vs[pdg.es[i].target][
                                'name'] in listname \
                                    and pdg.vs[pdg.es[i].source]['location'] != None and pdg.vs[pdg.es[i].target][
                                'location'] != None:
                                # print pdg.vs[pdg.es[i].source]['name'], pdg.vs[pdg.es[i].target]['name']
                                d = dict()
                                d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
                                d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']),
                                             'code': str(pdg.vs[pdg.es[i].source]['code']),
                                             'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].source])}
                                d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
                                # if pdg.vs[pdg.es[i].target]['location'] == None:
                                #    print pdg.vs[pdg.es[i].target]
                                d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                                             'code': str(pdg.vs[pdg.es[i].target]['code']),
                                             'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].target])}
                                d['label'] = str(pdg.es[i]['label'])
                                if str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]) == vul_line or \
                                        str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]) == vul_line:
                                    label = 1
                                recordtemp.append(d)
                            i = i + 1
                        count += 1
                if len(recordtemp) == 0:
                    print 'api norecord'
                    # print len(pdg_set)
            path = os.path.join(store_record_path, key)
            all_type_path = os.path.join(all_test_type_path, key, filename.split("/")[-1], record_type)
            if key.split('/')[0] == 'fix':
                label = 0
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(all_type_path):
                os.makedirs(all_type_path)
            record_file = open(os.path.join(path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, record_file)
            record_file.close()
            all_type_record_file = open(os.path.join(all_type_path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, all_type_record_file)
            all_type_record_file.close()
            idx += 1


def return_slice(store_slice_path, load_point_path, store_record_path, record_type, store_real_path, slice_id, db):
    count = 1
    store_filepath = store_slice_path
    f = open(load_point_path, 'rb')
    dict_unsliced_pointers = pickle.load(f)
    f.close()

    l = ['CVE-2015-4521', 'CVE-2015-4482', 'CVE-2016-2824', 'CVE-2015-4487', 'CVE-2014-2894', 'CVE-2015-4484',
         'CVE-2016-4002', 'CVE-2015-2729', 'CVE-2015-4500', 'CVE-2015-4501', 'CVE-2016-5238', 'CVE-2014-5263',
         'CVE-2015-2726', 'CVE-2013-4526', 'CVE-2014-0223', 'CVE-2013-4527', 'CVE-2016-2814', 'CVE-2015-7178',
         'CVE-2015-7179', 'CVE-2013-4530', 'CVE-2013-4533', 'CVE-2015-8662', 'CVE-2015-7176', 'CVE-2016-1714',
         'CVE-2015-7174', 'CVE-2015-7175', 'CVE-2016-9104', 'CVE-2016-5280', 'CVE-2016-9101', 'CVE-2016-9103',
         'CVE-2016-2819', 'CVE-2016-2818', 'CVE-2015-0829', 'CVE-2016-4952', 'CVE-2015-4511', 'CVE-2015-4512',
         'CVE-2015-4517', 'CVE-2014-9676', 'CVE-2013-6399', 'CVE-2016-8910', 'CVE-2013-0866', 'CVE-2013-4542',
         'CVE-2015-3395', 'CVE-2016-6351', 'CVE-2016-9923', 'CVE-2013-0860', 'CVE-2016-1957', 'CVE-2016-1956',
         'CVE-2013-7020', 'CVE-2013-7021', 'CVE-2016-1953', 'CVE-2016-1952', 'CVE-2013-0868', 'CVE-2014-8541',
         'CVE-2016-1970', 'CVE-2014-9319', 'CVE-2014-8542', 'CVE-2016-7421', 'CVE-2014-8544', 'CVE-2014-8547',
         'CVE-2016-7161', 'CVE-2014-7937', 'CVE-2015-1872', 'CVE-2014-9317', 'CVE-2014-9316', 'CVE-2014-7933',
         'CVE-2016-5258', 'CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107',
         'CVE-2016-4453', 'CVE-2015-7203', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5256', 'CVE-2016-5257',
         'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2015-4504', 'CVE-2016-7170', 'CVE-2016-5278', 'CVE-2015-7180',
         'CVE-2016-1981', 'CVE-2016-8909', 'CVE-2016-2836', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182',
         'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779',
         'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-4493', 'CVE-2015-0825', 'CVE-2015-0824', 'CVE-2016-2837',
         'CVE-2015-0826', 'CVE-2016-5254', 'CVE-2016-4441', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2013-4149',
         'CVE-2015-7198', 'CVE-2015-7199', 'CVE-2015-2710', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023',
         'CVE-2013-0845', 'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668']
    for key in tqdm.tqdm(dict_unsliced_pointers.keys(), desc='return slice'):  # key is testID(fix/CVE-2008-2136)
        if key.split('/')[1] in l:
            continue
        idx = 0
        dictlist = []
        for _t in dict_unsliced_pointers[key]:
            if _t not in dictlist:
                dictlist.append(_t)
            else:
                continue
        for _t in dictlist:
            recordtemp = []
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            pointers_name = str(_t[2])
            filename = getFuncFile(db=db, func_id=pdg_funcid)
            vul_line = str(filepath_to_line_dict[filename])
            ast_g = drawAstTreeGraph(db, getASTEdges(db, pdg_funcid), pdg_funcid)
            slice_dir = 0
            label = 0
            pdg = getFuncPDGById(key, pdg_funcid, slice_id=slice_id)
            if not pdg:
                print 'return error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key,
                                                                 slice_id=slice_id)

            if list_code == []:
                fout = open("data/slice/return_error.txt", 'a')
                fout.write(pointers_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                _list = list_code[0]
                # get_slice_file_sequence(store_filepath, _list, count, pointers_name, startline, startline_path)
                get_slice_ciretion(store_filepath, _list, count, pointers_name, startline,
                                   startline_path)
                functionlist = []
                for node in _list:
                    functionID = node['functionId']
                    functionlist.append(functionID)
                for m in range(len(_list)):
                    if m == len(_list) - 1:
                        continue
                    elif _list[m]['functionId'] != _list[m + 1]['functionId']:
                        d = dict()
                        d['sid'] = str(_list[m]['name'])
                        if _list[m]['location'] is None:
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        else:
                            if str(_list[m]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': str(_list[m]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        d['eid'] = str(_list[m + 1]['name'])

                        if _list[m + 1]['location'] is None:
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        else:
                            if str(_list[m+1]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': str(_list[m + 1]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        d['label'] = str(4)
                        recordtemp.append(d)
                functionlist = set(functionlist)
                pdg_set = []
                for functionID in functionlist:
                    pdg = getFuncPDGById(key, functionID, slice_id=slice_id)
                    pdg_set.append(pdg)

                for pdg in pdg_set:
                    i = 0
                    # pdg = getFuncPDGById(key, pdg_funcid)
                    while i < pdg.vcount():
                        # if pdg.vs[i]['type'] == 'IdentifierDeclStatement' and pdg.vs[i] not in _list:
                        #     _list.append(pdg.vs[i])
                        if pdg.vs[i]['type'] == 'Parameter' and pdg.vs[i] not in _list:
                            _list.append(pdg.vs[i])
                        i = i + 1
                    listname = []
                    for listnode in _list:
                        listname.append(listnode['name'])
                        # print listname
                    i = 0
                    while i < pdg.ecount():
                        if pdg.vs[pdg.es[i].source]['name'] in listname and pdg.vs[pdg.es[i].target]['name'] in listname \
                                and pdg.vs[pdg.es[i].source]['location'] != None and pdg.vs[pdg.es[i].target][
                            'location'] != None:
                            # print pdg.vs[pdg.es[i].source]['name'], pdg.vs[pdg.es[i].target]['name']
                            d = dict()
                            d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
                            d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']),
                                         'code': str(pdg.vs[pdg.es[i].source]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].source])}
                            d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
                            d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                                         'code': str(pdg.vs[pdg.es[i].target]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].target])}
                            d['label'] = str(pdg.es[i]['label'])
                            if str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]) == vul_line or \
                                    str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]) == vul_line:
                                label = 1
                            recordtemp.append(d)
                        i = i + 1
                    count += 1
            path = os.path.join(store_record_path, key)
            all_type_path = os.path.join(all_test_type_path, key, filename.split("/")[-1], record_type)
            if key.split('/')[0] == 'fix':
                label = 0
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(all_type_path):
                os.makedirs(all_type_path)
            record_file = open(os.path.join(path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, record_file)
            record_file.close()
            all_type_record_file = open(os.path.join(all_type_path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, all_type_record_file)
            all_type_record_file.close()
            idx += 1


def param_slice(store_slice_path, load_point_path, store_record_path, record_type, store_real_path, slice_id, db):
    count = 1
    store_filepath = store_slice_path
    f = open(load_point_path, 'rb')
    dict_unsliced_pointers = pickle.load(f)
    f.close()

    l = ['CVE-2015-4521', 'CVE-2015-4482', 'CVE-2016-2824', 'CVE-2015-4487', 'CVE-2014-2894', 'CVE-2015-4484',
         'CVE-2016-4002', 'CVE-2015-2729', 'CVE-2015-4500', 'CVE-2015-4501', 'CVE-2016-5238', 'CVE-2014-5263',
         'CVE-2015-2726', 'CVE-2013-4526', 'CVE-2014-0223', 'CVE-2013-4527', 'CVE-2016-2814', 'CVE-2015-7178',
         'CVE-2015-7179', 'CVE-2013-4530', 'CVE-2013-4533', 'CVE-2015-8662', 'CVE-2015-7176', 'CVE-2016-1714',
         'CVE-2015-7174', 'CVE-2015-7175', 'CVE-2016-9104', 'CVE-2016-5280', 'CVE-2016-9101', 'CVE-2016-9103',
         'CVE-2016-2819', 'CVE-2016-2818', 'CVE-2015-0829', 'CVE-2016-4952', 'CVE-2015-4511', 'CVE-2015-4512',
         'CVE-2015-4517', 'CVE-2014-9676', 'CVE-2013-6399', 'CVE-2016-8910', 'CVE-2013-0866', 'CVE-2013-4542',
         'CVE-2015-3395', 'CVE-2016-6351', 'CVE-2016-9923', 'CVE-2013-0860', 'CVE-2016-1957', 'CVE-2016-1956',
         'CVE-2013-7020', 'CVE-2013-7021', 'CVE-2016-1953', 'CVE-2016-1952', 'CVE-2013-0868', 'CVE-2014-8541',
         'CVE-2016-1970', 'CVE-2014-9319', 'CVE-2014-8542', 'CVE-2016-7421', 'CVE-2014-8544', 'CVE-2014-8547',
         'CVE-2016-7161', 'CVE-2014-7937', 'CVE-2015-1872', 'CVE-2014-9317', 'CVE-2014-9316', 'CVE-2014-7933',
         'CVE-2016-5258', 'CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107',
         'CVE-2016-4453', 'CVE-2015-7203', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5256', 'CVE-2016-5257',
         'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2015-4504', 'CVE-2016-7170', 'CVE-2016-5278', 'CVE-2015-7180',
         'CVE-2016-1981', 'CVE-2016-8909', 'CVE-2016-2836', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182',
         'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779',
         'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-4493', 'CVE-2015-0825', 'CVE-2015-0824', 'CVE-2016-2837',
         'CVE-2015-0826', 'CVE-2016-5254', 'CVE-2016-4441', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2013-4149',
         'CVE-2015-7198', 'CVE-2015-7199', 'CVE-2015-2710', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023',
         'CVE-2013-0845', 'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668']
    for key in tqdm.tqdm(dict_unsliced_pointers.keys(), desc='parameter slice'):  # key is testID
        if key.split("/")[1] in l:
            continue
        idx = 0
        dictlist = []
        for _t in dict_unsliced_pointers[key]:
            if _t not in dictlist:
                dictlist.append(_t)
            else:
                continue
        for _t in dictlist:
            recordtemp = []
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            pointers_name = str(_t[2])
            filename = getFuncFile(db=db, func_id=pdg_funcid)
            vul_line = str(filepath_to_line_dict[filename])
            ast_g = drawAstTreeGraph(db, getASTEdges(db, pdg_funcid), pdg_funcid)
            slice_dir = 1
            label = 0
            pdg = getFuncPDGById(key, pdg_funcid, slice_id)
            if not pdg:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key, slice_id)

            if not list_code:
                fout = open("data/slice/param_error.txt", 'a')
                fout.write(pointers_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                _list = list_code[0]
                # get_slice_file_sequence(store_filepath, _list, count, pointers_name, startline, startline_path)
                # '''
                get_slice_ciretion(store_filepath, _list, count, pointers_name, startline,
                                   startline_path)
                functionlist = []
                for node in _list:
                    functionID = node['functionId']
                    functionlist.append(functionID)
                for m in range(len(_list)):
                    if m == len(_list) - 1:
                        continue
                    elif (_list[m]['functionId'] != _list[m + 1]['functionId']):
                        # call_functionID = _list[m+1]['functionId']
                        d = dict()
                        d['sid'] = str(_list[m]['name'])
                        if _list[m]['location'] is None:
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        else:
                            if str(_list[m]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': str(_list[m]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        d['eid'] = str(_list[m + 1]['name'])
                        if _list[m + 1]['location'] == None:
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        else:
                            if str(_list[m+1]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': str(_list[m + 1]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        d['label'] = str(4)
                        recordtemp.append(d)
                    else:
                        continue
                functionlist = set(functionlist)
                pdg_set = []
                for functionID in functionlist:
                    pdg = getFuncPDGById(key, functionID, slice_id)
                    pdg_set.append(pdg)
                for pdg in pdg_set:
                    i = 0
                    while i < pdg.vcount():
                        # if pdg.vs[i]['type'] == 'IdentifierDeclStatement' and pdg.vs[i] not in _list:
                        #     _list.append(pdg.vs[i])
                        if pdg.vs[i]['type'] == 'Parameter' and pdg.vs[i] not in _list:
                            _list.append(pdg.vs[i])
                        i = i + 1
                    listname = []
                    for listnode in _list:
                        listname.append(listnode['name'])
                    i = 0
                    while i < pdg.ecount():
                        if pdg.vs[pdg.es[i].source]['name'] in listname and pdg.vs[pdg.es[i].target]['name'] in listname \
                                and pdg.vs[pdg.es[i].source]['location'] is not None and pdg.vs[pdg.es[i].target][
                            'location'] != None:
                            # print pdg.vs[pdg.es[i].source]['name'], pdg.vs[pdg.es[i].target]['name']
                            d = dict()
                            d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
                            d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']),
                                         'code': str(pdg.vs[pdg.es[i].source]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].source])}
                            d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
                            # if pdg.vs[pdg.es[i].target]['location'] == None:
                            #   print pdg.vs[pdg.es[i].target]
                            d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                                         'code': str(pdg.vs[pdg.es[i].target]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].target])}
                            d['label'] = str(pdg.es[i]['label'])
                            if str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]) == vul_line or \
                                    str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]) == vul_line:
                                label = 1
                            recordtemp.append(d)
                        i = i + 1
            path = os.path.join(store_record_path, key)
            all_type_path = os.path.join(all_test_type_path, key, filename.split("/")[-1], record_type)
            if key.split('/')[0] == 'fix':
                label = 0
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(all_type_path):
                os.makedirs(all_type_path)
            record_file = open(os.path.join(path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, record_file)
            record_file.close()
            all_type_record_file = open(os.path.join(all_type_path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, all_type_record_file)
            all_type_record_file.close()
            idx += 1


def pointers_slice(store_slice_path, load_point_path, store_record_path, record_type, store_real_path, slice_id, db):
    count = 0
    store_filepath = store_slice_path
    f = open(load_point_path, 'rb')
    dict_unsliced_pointers = pickle.load(f)
    f.close()

    l = ['CVE-2015-4521', 'CVE-2015-4482', 'CVE-2016-2824', 'CVE-2015-4487', 'CVE-2014-2894', 'CVE-2015-4484',
         'CVE-2016-4002', 'CVE-2015-2729', 'CVE-2015-4500', 'CVE-2015-4501', 'CVE-2016-5238', 'CVE-2014-5263',
         'CVE-2015-2726', 'CVE-2013-4526', 'CVE-2014-0223', 'CVE-2013-4527', 'CVE-2016-2814', 'CVE-2015-7178',
         'CVE-2015-7179', 'CVE-2013-4530', 'CVE-2013-4533', 'CVE-2015-8662', 'CVE-2015-7176', 'CVE-2016-1714',
         'CVE-2015-7174', 'CVE-2015-7175', 'CVE-2016-9104', 'CVE-2016-5280', 'CVE-2016-9101', 'CVE-2016-9103',
         'CVE-2016-2819', 'CVE-2016-2818', 'CVE-2015-0829', 'CVE-2016-4952', 'CVE-2015-4511', 'CVE-2015-4512',
         'CVE-2015-4517', 'CVE-2014-9676', 'CVE-2013-6399', 'CVE-2016-8910', 'CVE-2013-0866', 'CVE-2013-4542',
         'CVE-2015-3395', 'CVE-2016-6351', 'CVE-2016-9923', 'CVE-2013-0860', 'CVE-2016-1957', 'CVE-2016-1956',
         'CVE-2013-7020', 'CVE-2013-7021', 'CVE-2016-1953', 'CVE-2016-1952', 'CVE-2013-0868', 'CVE-2014-8541',
         'CVE-2016-1970', 'CVE-2014-9319', 'CVE-2014-8542', 'CVE-2016-7421', 'CVE-2014-8544', 'CVE-2014-8547',
         'CVE-2016-7161', 'CVE-2014-7937', 'CVE-2015-1872', 'CVE-2014-9317', 'CVE-2014-9316', 'CVE-2014-7933',
         'CVE-2016-5258', 'CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107',
         'CVE-2016-4453', 'CVE-2015-7203', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5256', 'CVE-2016-5257',
         'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2015-4504', 'CVE-2016-7170', 'CVE-2016-5278', 'CVE-2015-7180',
         'CVE-2016-1981', 'CVE-2016-8909', 'CVE-2016-2836', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182',
         'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779',
         'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-4493', 'CVE-2015-0825', 'CVE-2015-0824', 'CVE-2016-2837',
         'CVE-2015-0826', 'CVE-2016-5254', 'CVE-2016-4441', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2013-4149',
         'CVE-2015-7198', 'CVE-2015-7199', 'CVE-2015-2710', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023',
         'CVE-2013-0845', 'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668']
    for key in tqdm.tqdm(dict_unsliced_pointers.keys(), desc='pointers slice'):  # key is testID
        if key.split('/')[1] in l:
            continue
        idx = 0
        dictlist = []
        for _t in dict_unsliced_pointers[key]:
            if _t not in dictlist:
                dictlist.append(_t)
        for _t in dictlist:
            recordtemp = []
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            pointers_name = str(_t[2])
            filename = getFuncFile(db=db, func_id=pdg_funcid)
            vul_line = str(filepath_to_line_dict[filename])
            ast_g = drawAstTreeGraph(db, getASTEdges(db, pdg_funcid), pdg_funcid)
            slice_dir = 2
            label = 0
            pdg = getFuncPDGById(key, pdg_funcid, slice_id)
            if not pdg:
                print 'pointers error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key, slice_id)

            if not list_code:
                fout = open("data/slice/pointers_error.txt", 'a')
                fout.write(pointers_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                _list = list_code[0]
                get_slice_ciretion(store_filepath, _list, count, pointers_name, startline, startline_path)
                functionlist = []
                for node in _list:
                    functionID = node['functionId']
                    functionlist.append(functionID)
                for m in range(len(_list)):
                    if m == len(_list) - 1:
                        continue
                    elif _list[m]['functionId'] != _list[m + 1]['functionId']:
                        # call_functionID = _list[m+1]['functionId']
                        d = dict()
                        d['sid'] = str(_list[m]['name'])
                        if _list[m]['location'] is None:
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        else:
                            if str(_list[m]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': str(_list[m]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        d['eid'] = str(_list[m + 1]['name'])
                        if _list[m + 1]['location'] is None:
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        else:
                            if str(_list[m+1]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': str(_list[m + 1]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        d['label'] = str(4)
                        recordtemp.append(d)
                    else:
                        continue
                functionlist = set(functionlist)
                pdg_set = []
                for functionID in functionlist:
                    pdg = getFuncPDGById(key, functionID, slice_id)
                    pdg_set.append(pdg)
                for pdg in pdg_set:
                    i = 0
                    while i < pdg.vcount():
                        # if pdg.vs[i]['type'] == 'IdentifierDeclStatement' and pdg.vs[i] not in _list:
                        #     _list.append(pdg.vs[i])
                        if pdg.vs[i]['type'] == 'Parameter' and pdg.vs[i] not in _list:
                            _list.append(pdg.vs[i])
                        i = i + 1
                    listname = []
                    for listnode in _list:
                        listname.append(listnode['name'])
                    i = 0
                    while i < pdg.ecount():
                        if pdg.vs[pdg.es[i].source]['name'] in listname and pdg.vs[pdg.es[i].target]['name'] in listname \
                                and pdg.vs[pdg.es[i].source]['location'] != None and pdg.vs[pdg.es[i].target][
                            'location'] != None:
                            #  pdg.vs[pdg.es[i].source]['name'], pdg.vs[pdg.es[i].target]['name']
                            d = dict()
                            d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
                            d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']),
                                         'code': str(pdg.vs[pdg.es[i].source]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].source])}
                            d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
                            # if pdg.vs[pdg.es[i].target]['location'] == None:
                            # print pdg.vs[pdg.es[i].target]
                            d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                                         'code': str(pdg.vs[pdg.es[i].target]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].target])}
                            d['label'] = str(pdg.es[i]['label'])
                            if str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]) == vul_line or \
                                    str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]) == vul_line:
                                label = 1
                            recordtemp.append(d)
                        i = i + 1
                    if len(recordtemp) == 0:
                        print 'pointers norecord'
                        print len(pdg_set)
            path = os.path.join(store_record_path, key)
            all_type_path = os.path.join(all_test_type_path, key, filename.split("/")[-1], record_type)
            if key.split('/')[0] == 'fix':
                label = 0
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(all_type_path):
                os.makedirs(all_type_path)
            record_file = open(os.path.join(path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, record_file)
            record_file.close()
            all_type_record_file = open(os.path.join(all_type_path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, all_type_record_file)
            all_type_record_file.close()
            idx += 1


def arrays_slice(store_slice_path, load_point_path, store_record_path, record_type, store_real_path, slice_id, db):
    count = 0
    store_filepath = store_slice_path
    f = open(load_point_path, 'rb')
    dict_unsliced_pointers = pickle.load(f)
    f.close()
    l = ['CVE-2010-2068', 'CVE-2015-1158', 'CVE-2006-1530', 'CVE-2012-2802', 'CVE-2010-4165', 'CVE-2014-3523',
         'CVE-2012-6062', 'CVE-2013-1672', 'CVE-2007-4997', 'CVE-2013-4082', 'CVE-2012-4186', 'CVE-2013-4512',
         'CVE-2013-6450', 'CVE-2011-2534', 'CVE-2014-1690', 'CVE-2011-2536', 'CVE-2012-2319', 'CVE-2012-0957',
         'CVE-2011-3936', 'CVE-2004-1151', 'CVE-2013-4929', 'CVE-2010-3296', 'CVE-2011-4102', 'CVE-2012-5668',
         'CVE-2011-4100', 'CVE-2011-1959', 'CVE-2012-3969', 'CVE-2012-1183', 'CVE-2011-0726', 'CVE-2013-0756',
         'CVE-2004-0535', 'CVE-2010-2495', 'CVE-2012-2393', 'CVE-2015-3811', 'CVE-2012-2776', 'CVE-2009-2909',
         'CVE-2014-3633', 'CVE-2014-1508', 'CVE-2011-2529', 'CVE-2014-3537', 'CVE-2012-1947', 'CVE-2013-0844',
         'CVE-2012-1942', 'CVE-2014-0195', 'CVE-2012-4293', 'CVE-2012-4292', 'CVE-2008-1390', 'CVE-2011-0021',
         'CVE-2012-3991', 'CVE-2007-4521', 'CVE-2009-0746', 'CVE-2011-1147', 'CVE-2012-5240', 'CVE-2013-2634',
         'CVE-2014-8133', 'CVE-2006-2778', 'CVE-2012-4288', 'CVE-2015-0253', 'CVE-2012-0444', 'CVE-2013-1726',
         'CVE-2013-7112', 'CVE-2006-1856', 'CVE-2013-0850', 'CVE-2011-3623', 'CVE-2013-1582', 'CVE-2013-1732',
         'CVE-2014-8884', 'CVE-2013-0772', 'CVE-2014-9374', 'CVE-2014-1497', 'CVE-2014-0221', 'CVE-2013-1696',
         'CVE-2011-1833', 'CVE-2013-1693', 'CVE-2013-0872', 'CVE-2012-2790', 'CVE-2012-2791', 'CVE-2012-2796',
         'CVE-2012-0477', 'CVE-2012-2652', 'CVE-2006-4790', 'CVE-2013-0867', 'CVE-2013-4932', 'CVE-2013-0860',
         'CVE-2014-3511', 'CVE-2014-3510', 'CVE-2013-0868', 'CVE-2014-8541', 'CVE-2014-2739', 'CVE-2014-9319',
         'CVE-2006-4813', 'CVE-2014-8544', 'CVE-2011-3973', 'CVE-2013-1848', 'CVE-2014-9316', 'CVE-2012-1594',
         'CVE-2013-1573', 'CVE-2012-0068', 'CVE-2015-0833', 'CVE-2010-1748', 'CVE-2012-0067', 'CVE-2011-3362',
         'CVE-2014-3182', 'CVE-2013-5641', 'CVE-2013-5642', 'CVE-2011-3484', 'CVE-2013-6891', 'CVE-2014-8712',
         'CVE-2014-8713', 'CVE-2014-8714', 'CVE-2013-4534', 'CVE-2010-2431', 'CVE-2014-8412', 'CVE-2011-1175',
         'CVE-2012-5237', 'CVE-2011-1173', 'CVE-2012-5238', 'CVE-2014-4611', 'CVE-2015-0564', 'CVE-2014-5271',
         'CVE-2011-0055', 'CVE-2014-3470', 'CVE-2014-8643', 'CVE-2015-0204', 'CVE-2014-2286', 'CVE-2012-6537',
         'CVE-2011-3945', 'CVE-2011-3944', 'CVE-2011-2896', 'CVE-2010-2955', 'CVE-2013-2495', 'CVE-2013-4931',
         'CVE-2013-4933', 'CVE-2012-2775', 'CVE-2013-4934', 'CVE-2013-4936', 'CVE-2011-4594', 'CVE-2014-6424',
         'CVE-2013-0311', 'CVE-2011-4598', 'CVE-2006-2935', 'CVE-2011-4352', 'CVE-2012-1184', 'CVE-2005-3356',
         'CVE-2012-6059', 'CVE-2012-6058', 'CVE-2011-3950', 'CVE-2014-9672', 'CVE-2010-2803', 'CVE-2013-7011',
         'CVE-2013-3674', 'CVE-2009-0676', 'CVE-2013-6380', 'CVE-2009-2768', 'CVE-2015-3008', 'CVE-2013-0796',
         'CVE-2009-2484', 'CVE-2013-4264', 'CVE-2013-4928', 'CVE-2014-8542', 'CVE-2012-6540', 'CVE-2015-0228',
         'CVE-2013-7008', 'CVE-2013-7009']
    for key in tqdm.tqdm(dict_unsliced_pointers.keys(), desc='arrays use slice'):  # key is testID
        if key.split('/')[1] in l:
            continue
        dictlist = []
        idx = 0
        for _t in dict_unsliced_pointers[key]:
            if _t not in dictlist:
                dictlist.append(_t)
        for _t in dictlist:
            recordtemp = []
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            arrays_name = str(_t[2])
            filename = getFuncFile(db=db, func_id=pdg_funcid)
            vul_line = str(filepath_to_line_dict[filename])
            ast_g = drawAstTreeGraph(db, getASTEdges(db, pdg_funcid), pdg_funcid)
            label = 0
            slice_dir = 2
            pdg = getFuncPDGById(key, pdg_funcid, slice_id)
            if not pdg:
                print 'array error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key, slice_id)

            if not list_code:
                fout = open("data/slice/array_error.txt", 'a')
                fout.write(arrays_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                _list = list_code[0]
                get_slice_ciretion(store_filepath, _list, count, arrays_name, startline, startline_path)
                functionlist = []
                for node in _list:
                    functionID = node['functionId']
                    functionlist.append(functionID)
                for m in range(len(_list)):
                    if m == len(_list) - 1:
                        continue
                    elif _list[m]['functionId'] != _list[m + 1]['functionId']:
                        # call_functionID = _list[m+1]['functionId']
                        d = dict()
                        d['sid'] = str(_list[m]['name'])
                        if _list[m]['location'] is None:
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        else:
                            if str(_list[m]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': str(_list[m]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        d['eid'] = str(_list[m + 1]['name'])
                        if _list[m + 1]['location'] is None:
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        else:
                            if str(_list[m+1]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': str(_list[m + 1]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        d['label'] = str(4)
                        recordtemp.append(d)
                functionlist = set(functionlist)
                pdg_set = []
                for functionID in functionlist:
                    pdg = getFuncPDGById(key, functionID, slice_id)
                    pdg_set.append(pdg)
                my_count = 0
                for pdg in pdg_set:
                    if my_count > 3:
                        break
                    i = 0
                    # pdg = getFuncPDGById(key, pdg_funcid)
                    while i < pdg.vcount():
                        # if pdg.vs[i]['type'] == 'IdentifierDeclStatement' and pdg.vs[i] not in _list:
                        #     _list.append(pdg.vs[i])
                        if pdg.vs[i]['type'] == 'Parameter' and pdg.vs[i] not in _list:
                            _list.append(pdg.vs[i])
                        i = i + 1
                    listname = []
                    for listnode in _list:
                        listname.append(listnode['name'])
                    i = 0
                    while i < pdg.ecount():
                        if pdg.vs[pdg.es[i].source]['name'] in listname and pdg.vs[pdg.es[i].target]['name'] in listname \
                                and pdg.vs[pdg.es[i].source]['location'] != None and pdg.vs[pdg.es[i].target][
                            'location'] != None:
                            # print pdg.vs[pdg.es[i].source]['name'], pdg.vs[pdg.es[i].target]['name']
                            d = dict()
                            d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
                            d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']),
                                         'code': str(pdg.vs[pdg.es[i].source]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].source])}
                            d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
                            # if pdg.vs[pdg.es[i].target]['location'] == None:
                            #    print pdg.vs[pdg.es[i].target]
                            d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                                         'code': str(pdg.vs[pdg.es[i].target]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].target])}
                            d['label'] = str(pdg.es[i]['label'])
                            if str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]) == vul_line or \
                                    str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]) == vul_line:
                                label = 1
                            recordtemp.append(d)
                        i = i + 1
                        my_count += 1
            path = os.path.join(store_record_path, key)
            all_type_path = os.path.join(all_test_type_path, key, filename.split("/")[-1], record_type)
            if key.split('/')[0] == 'fix':
                label = 0
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(all_type_path):
                os.makedirs(all_type_path)
            record_file = open(os.path.join(path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, record_file)
            record_file.close()
            all_type_record_file = open(os.path.join(all_type_path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, all_type_record_file)
            all_type_record_file.close()
            idx += 1


def integeroverflow_slice(store_slice_path, load_point_path, store_record_path, record_type, store_real_path, slice_id,
                          db):
    count = 0
    store_filepath = store_slice_path
    f = open(load_point_path, 'rb')
    dict_unsliced_expr = pickle.load(f)
    f.close()
    l = ['CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107', 'CVE-2016-4453',
         'CVE-2015-4475', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5257', 'CVE-2015-7220', 'CVE-2015-7221',
         'CVE-2016-5278', 'CVE-2016-1981', 'CVE-2015-2726', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182',
         'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779',
         'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-7203', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2015-7199',
         'CVE-2015-2710', 'CVE-2016-4952', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023', 'CVE-2013-0845',
         'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668']
    for key in tqdm.tqdm(dict_unsliced_expr.keys(), desc='integer overflow slice'):  # key is testID
        if key.split('/')[1] in l:
            continue
        dictlist = []
        idx = 0
        for _t in dict_unsliced_expr[key]:
            if _t not in dictlist:
                dictlist.append(_t)
        for _t in dictlist:
            recordtemp = []
            list_expr_funcid = _t[0]
            pdg_funcid = _t[1]
            expr_name = str(_t[2])
            filename = getFuncFile(db=db, func_id=pdg_funcid)
            vul_line = str(filepath_to_line_dict[filename])
            ast_g = drawAstTreeGraph(db, getASTEdges(db, pdg_funcid), pdg_funcid)
            slice_dir = 2
            label = 0
            pdg = getFuncPDGById(key, pdg_funcid, slice_id)
            if not pdg:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_expr_funcid, slice_dir, key, slice_id)

            if not list_code:
                fout = open("data/slice/integeroverflow_error.txt", 'a')
                fout.write(expr_name + ' ' + str(list_expr_funcid) + ' found nothing! \n')
                fout.close()
            else:
                _list = list_code[0]
                get_slice_ciretion(store_filepath, _list, count, expr_name, startline, startline_path)
                functionlist = []
                for node in _list:
                    functionID = node['functionId']
                    functionlist.append(functionID)
                for m in range(len(_list)):
                    if m == len(_list) - 1:
                        continue
                    elif (_list[m]['functionId'] != _list[m + 1]['functionId']):
                        # call_functionID = _list[m+1]['functionId']
                        d = dict()
                        d['sid'] = str(_list[m]['name'])
                        if _list[m]['location'] is None:
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        else:
                            if str(_list[m]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['spro'] = {'type': str(_list[m]['type']),
                                         'code': str(_list[m]['code']),
                                         'lineNo': str(_list[m]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m])}
                        d['eid'] = str(_list[m + 1]['name'])
                        if _list[m + 1]['location'] is None:
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': 'None',
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        else:
                            if str(_list[m + 1]['location'].split(':')[0]) == vul_line:
                                label = 1
                            d['epro'] = {'type': str(_list[m + 1]['type']),
                                         'code': str(_list[m + 1]['code']),
                                         'lineNo': str(_list[m + 1]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                        d['label'] = str(4)
                        recordtemp.append(d)
                    else:
                        continue
                functionlist = set(functionlist)
                pdg_set = []
                for functionID in functionlist:
                    pdg = getFuncPDGById(key, functionID, slice_id)
                    pdg_set.append(pdg)
                for pdg in pdg_set:
                    i = 0
                    while i < pdg.vcount():
                        # if pdg.vs[i]['type'] == 'IdentifierDeclStatement' and pdg.vs[i] not in _list:
                        #     _list.append(pdg.vs[i])
                        if pdg.vs[i]['type'] == 'Parameter' and pdg.vs[i] not in _list:
                            _list.append(pdg.vs[i])
                        i = i + 1
                    listname = []
                    for listnode in _list:
                        listname.append(listnode['name'])
                    i = 0
                    while i < pdg.ecount():
                        if pdg.vs[pdg.es[i].source]['name'] in listname and pdg.vs[pdg.es[i].target]['name'] in listname \
                                and pdg.vs[pdg.es[i].source]['location'] != None and pdg.vs[pdg.es[i].target][
                            'location'] != None:
                            # print pdg.vs[pdg.es[i].source]['name'], pdg.vs[pdg.es[i].target]['name']
                            d = dict()
                            d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
                            d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']),
                                         'code': str(pdg.vs[pdg.es[i].source]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].source])}
                            d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
                            # if pdg.vs[pdg.es[i].target]['location'] == None:
                            #    print pdg.vs[pdg.es[i].target]
                            d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                                         'code': str(pdg.vs[pdg.es[i].target]['code']),
                                         'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]),
                                         'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].target])}
                            d['label'] = str(pdg.es[i]['label'])
                            if str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]) == vul_line or \
                                    str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]) == vul_line:
                                label = 1
                            recordtemp.append(d)
                        i = i + 1
                    count += 1
            path = os.path.join(store_record_path, key)
            all_type_path = os.path.join(all_test_type_path, key, filename.split("/")[-1], record_type)
            if key.split('/')[0] == 'fix':
                label = 0
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(all_type_path):
                os.makedirs(all_type_path)
            record_file = open(os.path.join(path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, record_file)
            record_file.close()
            all_type_record_file = open(os.path.join(all_type_path, str(label) + "_record" + str(idx) + ".pkl"), 'wb')
            pickle.dump(recordtemp, all_type_record_file)
            all_type_record_file.close()
            idx += 1


def mvp_slice(store_slice_path, load_point_path, store_record_path, store_real_path, slice_id, db):
    count = 1
    store_filepath = store_slice_path
    f = open(load_point_path, 'rb')
    dict_unsliced_mvp = pickle.load(f)
    f.close()
    for key in tqdm.tqdm(dict_unsliced_mvp.keys(), desc='mvp slice'):  # key is testID u'fix/CVE-2011-1927'
        dictlist = []
        idx = 0
        for _t in dict_unsliced_mvp[key]:
            if _t not in dictlist:
                dictlist.append(_t)
            else:
                continue
        for _t in dictlist:
            recordtemp = []
            list_slice_start_node_ids = _t[0]
            pdg_funcid = _t[1]
            sensitive_funcname = _t[2]
            ast_g = drawAstTreeGraph(db, getASTEdges(db, pdg_funcid), pdg_funcid)
            if sensitive_funcname.find("main") != -1:
                continue  # todo
            else:
                slice_dir = 3  # mvp slice
                pdg = getFuncPDGById(key, pdg_funcid, slice_id)
                if not pdg:
                    print key + 'not found pdg error'
                    exit()
                list_code, startline, startline_path = program_slice(pdg, list_slice_start_node_ids, slice_dir, key,
                                                                     slice_id=slice_id)
                if not list_code:
                    fout = open("data/slice_no_result_error.txt", 'a')
                    fout.write(
                        key + ':' + sensitive_funcname + ' ' + str(list_slice_start_node_ids) + ' found nothing! \n')
                    fout.close()
                else:
                    _list = list_code[0]
                    functionlist = []
                    for node in _list:
                        functionID = node['functionId']
                        functionlist.append(functionID)
                    for m in range(len(_list)):
                        if m == len(_list) - 1:
                            continue
                        elif _list[m]['functionId'] != _list[m + 1]['functionId']:
                            d = dict()
                            d['sid'] = str(_list[m]['name'])
                            if _list[m]['location'] is None:
                                d['spro'] = {'type': str(_list[m]['type']),
                                             'code': str(_list[m]['code']),
                                             'lineNo': 'None',
                                             'ast_tree': sub_ast_tree(ast_g, _list[m])}
                            else:
                                d['spro'] = {'type': str(_list[m]['type']),
                                             'code': str(_list[m]['code']),
                                             'lineNo': str(_list[m]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, _list[m])}
                            d['eid'] = str(_list[m + 1]['name'])
                            if _list[m + 1]['location'] is None:
                                d['epro'] = {'type': str(_list[m + 1]['type']),
                                             'code': str(_list[m + 1]['code']),
                                             'lineNo': 'None',
                                             'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                            else:
                                d['epro'] = {'type': str(_list[m + 1]['type']),
                                             'code': str(_list[m + 1]['code']),
                                             'lineNo': str(_list[m + 1]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, _list[m + 1])}
                            d['label'] = str(4)  # cross function call
                            recordtemp.append(d)

                    functionlist = set(functionlist)
                    pdg_set = []
                    for functionID in functionlist:
                        pdg = getFuncPDGById(key, functionID, slice_id=slice_id)
                        pdg_set.append(pdg)
                    get_slice_ciretion(store_filepath, _list, count, sensitive_funcname, startline,
                                       startline_path)
                    for pdg in pdg_set:
                        i = 0
                        while i < pdg.vcount():
                            # if pdg.vs[i]['type'] == 'IdentifierDeclStatement' and pdg.vs[i] not in _list:
                            #     _list.append(pdg.vs[i])
                            if pdg.vs[i]['type'] == 'Parameter' and pdg.vs[i] not in _list:
                                _list.append(pdg.vs[i])
                            i = i + 1
                        listname = []
                        for listnode in _list:
                            listname.append(listnode['name'])
                        i = 0
                        while i < pdg.ecount():
                            if pdg.vs[pdg.es[i].source]['name'] in listname and pdg.vs[pdg.es[i].target][
                                'name'] in listname \
                                    and pdg.vs[pdg.es[i].source]['location'] != None and pdg.vs[pdg.es[i].target][
                                'location'] != None:
                                # print pdg.vs[pdg.es[i].source]['name'], pdg.vs[pdg.es[i].target]['name']
                                d = dict()
                                d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
                                d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']),
                                             'code': str(pdg.vs[pdg.es[i].source]['code']),
                                             'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].source])}
                                d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
                                # if pdg.vs[pdg.es[i].target]['location'] == None:
                                #    print pdg.vs[pdg.es[i].target]
                                d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                                             'code': str(pdg.vs[pdg.es[i].target]['code']),
                                             'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0]),
                                             'ast_tree': sub_ast_tree(ast_g, pdg.vs[pdg.es[i].target])}
                                d['label'] = str(pdg.es[i]['label'])
                                recordtemp.append(d)
                            i = i + 1
                        count += 1
                    if len(recordtemp) == 0:
                        print key + ': recordtemp is empty,pdg_set is :' + len(pdg_set)
            path = os.path.join(store_record_path, key)
            if key.split('/')[0] == 'vul':
                label = 1
            else:
                label = 0
            if not os.path.exists(path):
                os.makedirs(path)

            file_name = ""
            if list_slice_start_node_ids is not None:
                file_name += list_slice_start_node_ids[0]
            file_name += "_" + pdg_funcid + "_" + sensitive_funcname + "_" + str(label) + \
                         "_record_" + str(idx) + ".pkl"
            record_file = open(os.path.join(path, file_name), 'wb')
            pickle.dump(recordtemp, record_file)
            record_file.close()
            idx += 1


def sub_ast_tree(g, top_node):
    idx2node = dict()
    node2idx = dict()
    nodeId2idx = dict()
    edge_dict = dict()
    for i in range(len(g.vs)):
        idx2node[i] = g.vs[i]
        node2idx[g.vs[i]] = i
        nodeId2idx[int(g.vs[i]['name'])] = i

    for edge in g.es:
        idx1 = edge.source
        idx2 = edge.target
        if idx1 in edge_dict:
            edge_dict[idx1].append(idx2)
        else:
            edge_dict[idx1] = [idx2]

    if not int(top_node['name']) in nodeId2idx:
        root = Tree(_idx=0)
        root.ast_type = top_node['type']
        if not top_node['type'] in ast_type_dict:
            ast_type_dict[top_node['type']] = len(ast_type_dict)
        root.code = top_node['code']
        return root
    node = idx2node[nodeId2idx[int(top_node['name'])]]
    root = Tree(_idx=0)
    tree_idx = 1
    root.ast_type = node['type']
    if not node['type'] in ast_type_dict:
        ast_type_dict[node['type']] = len(ast_type_dict)
    root.code = node['code']
    q = queue.Queue()
    q.put([root, node])
    # flag = False
    while not q.empty():
        curr = q.get()
        if node2idx[curr[1]] in edge_dict:
            for next_idx in edge_dict[node2idx[curr[1]]]:
                next = idx2node[next_idx]
                child = Tree(tree_idx)
                tree_idx += 1
                child.ast_type = next['type']
                if not next['type'] in ast_type_dict:
                    ast_type_dict[next['type']] = len(ast_type_dict)
                child.code = next['code']
                curr[0].add_child(child)
                q.put([child, next])
                # print 'yes ok'
                # flag = True
        else:
            curr[0].ast_type = curr[0].code
            if not curr[0].code in ast_type_dict:
                ast_type_dict[curr[0].code] = len(ast_type_dict)
            curr[0].is_leaf = True
    # if flag:
    #     print(root.children)
    #     print(root.ast_type)
    #     print(root.code)
    return root


def main(slice_id=1):
    global ast_type_dict
    global filepath_to_line_dict

    ast_type_dict = pickle.load(open('data/ast_type_dict.pkl'))
    filepath_to_line_dict = pickle(open('data/filepath_to_line_dict.pkl'))
    i = slice_id
    # record path
    record_path = "/home/anderson/Desktop/locator_record/" + str(slice_id)

    # all six type path
    global all_test_type_path
    all_test_type_path = record_path + "/all_test_type_record/"
    if not os.path.exists(all_test_type_path):
        os.makedirs(all_test_type_path)

    # api path
    api_type = "api_record"
    api_path = record_path + "/" + api_type + "/"
    if not os.path.exists(api_path):
        os.makedirs(api_path)

    # points path
    points_type = "pointers_record"
    pointers_path = record_path + "/pointers_record/"
    if not os.path.exists(pointers_path):
        os.makedirs(pointers_path)

    # array use path
    array_use_type = "array_use_record"
    array_use_path = record_path + "/array_use_record/"
    if not os.path.exists(array_use_path):
        os.makedirs(array_use_path)

    # integer overflow path
    integer_overflow_type = "integer_overflow_record"
    integer_overflow_path = record_path + "/integer_overflow_record/"
    if not os.path.exists(integer_overflow_path):
        os.makedirs(integer_overflow_path)

    # parameter use path
    parameter_use_type = "parameter_use_record"
    parameter_use_path = record_path + "/parameter_use_record/"
    if not os.path.exists(parameter_use_path):
        os.makedirs(parameter_use_path)

    # return path
    return_type = "return_record"
    return_path = record_path + "/return_record/"
    if not os.path.exists(return_path):
        os.makedirs(return_path)

    # mvp path
    mvp_vul_path = record_path + "/mvp_vul_record/"
    if not os.path.exists(mvp_vul_path):
        os.makedirs(mvp_vul_path)

    # all points path
    load_point_path = "/home/anderson/Desktop/locator_point/" + str(i)

    api_point_path = load_point_path + "/sensifunc_slice_points.pkl"
    pointers_point_path = load_point_path + "/pointuse_slice_points.pkl"
    array_use_point_path = load_point_path + "/arrayuse_slice_points.pkl"
    integer_overflow_point_path = load_point_path + "/integeroverflow_slice_points.pkl"
    parameter_use_point_path = load_point_path + "/param_slice_points.pkl"
    return_point_path = load_point_path + "/return_slice_points.pkl"
    mvp_vul_point_path = load_point_path + "/mvp_vul_points.pkl"
    j = JoernSteps()
    j.connectToDatabase()
    # all slices
    api_slice(store_slice_path=api_path,
              load_point_path=api_point_path,
              store_record_path=api_path,
              record_type=api_type,
              store_real_path=api_path, slice_id=i, db=j)
    pointers_slice(store_slice_path=pointers_path,
                   load_point_path=pointers_point_path,
                   store_record_path=pointers_path,
                   record_type=points_type,
                   store_real_path=pointers_path,
                   slice_id=i, db=j)
    arrays_slice(store_slice_path=array_use_path,
                 load_point_path=array_use_point_path,
                 store_record_path=array_use_path,
                 record_type=array_use_type,
                 store_real_path=array_use_path,
                 slice_id=i, db=j)
    integeroverflow_slice(store_slice_path=integer_overflow_path,
                          load_point_path=integer_overflow_point_path,
                          store_record_path=integer_overflow_path,
                          record_type=integer_overflow_type,
                          store_real_path=integer_overflow_path,
                          slice_id=i, db=j)
    param_slice(store_slice_path=parameter_use_path,
                load_point_path=parameter_use_point_path,
                store_record_path=parameter_use_path,
                record_type=parameter_use_type,
                store_real_path=parameter_use_path,
                slice_id=i, db=j)
    return_slice(store_slice_path=return_path,
                 load_point_path=return_point_path,
                 store_record_path=return_path,
                 record_type=return_type,
                 store_real_path=return_path,
                 slice_id=i, db=j)
    # mvp_slice(store_slice_path=mvp_vul_path,
    #           load_point_path=mvp_vul_point_path,
    #           store_record_path=mvp_vul_path,
    #           store_real_path=mvp_vul_path,
    #           slice_id=i, db=j)
    pickle.dump(ast_type_dict, open('data/ast_type_dict.pkl', 'wb'))


if __name__ == "__main__":
    main(slice_id=4)
