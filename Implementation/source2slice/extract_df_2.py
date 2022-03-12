## coding:utf-8
import os.path

from joern.all import JoernSteps
from igraph import *
from access_db_operate import *
from slice_op import *
from py2neo.packages.httpstream import http
http.socket_timeout = 9999
import tqdm

def get_slice_file_sequence(store_filepath, list_result, count, func_name, startline, filepath_all):
    list_for_line = []
    statement_line = 0
    vulnline_row = 0
    list_write2file = []

    for node in list_result:    
        if node['type'] == 'Function':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0])-1
            code = content[raw].strip()

            new_code = ""
            if code.find("#define") != -1:
                list_write2file.append(code + ' ' + str(raw+1) + '\n')
                continue

            while (len(code) >= 1 and code[-1] != ')' and code[-1] != '{'):
                if code.find('{') != -1:
                    index = code.index('{')
                    new_code += code[:index].strip()
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                    break

                else:
                    new_code += code + '\n'
                    raw += 1
                    code = content[raw].strip()
                    #print "raw", raw, code

            else:
                new_code += code
                new_code = new_code.strip()
                if new_code[-1] == '{':
                    new_code = new_code[:-1].strip()
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                    #list_line.append(str(raw+1))
                else:
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                    #list_line.append(str(raw+1))

        elif node['type'] == 'Condition':
            raw = int(node['location'].split(':')[0])-1
            if raw in list_for_line:
                continue
            else:
                #print node['type'], node['code'], node['name']
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                code = content[raw].strip()
                pattern = re.compile("(?:if|while|for|switch)")
                #print code
                res = re.search(pattern, code)
                if res == None:
                    raw = raw - 1
                    code = content[raw].strip()
                    new_code = ""

                    while (code[-1] != ')' and code[-1] != '{'):
                        if code.find('{') != -1:
                            index = code.index('{')
                            new_code += code[:index].strip()
                            list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                            #list_line.append(str(raw+1))
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
                            list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                            #list_line.append(str(raw+1))
                            list_for_line.append(raw)

                        else:
                            list_for_line.append(raw)
                            list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                            #list_line.append(str(raw+1))

                else:
                    res = res.group()
                    if res == '':
                        print filepath_all + ' ' + func_name + " error!"
                        exit()

                    elif res != 'for':
                        new_code = res + ' ( ' + node['code'] + ' ) '
                        list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                        #list_line.append(str(raw+1))

                    else:
                        new_code = ""
                        if code.find(' for ') != -1:
                            code = 'for ' + code.split(' for ')[1]

                        while code != '' and code[-1] != ')' and code[-1] != '{':
                            if code.find('{') != -1:
                                index = code.index('{')
                                new_code += code[:index].strip()
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                #list_line.append(str(raw+1))
                                list_for_line.append(raw)
                                break

                            elif code[-1] == ';' and code[:-1].count(';') >= 2:
                                new_code += code
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                #list_line.append(str(raw+1))
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
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                #list_line.append(str(raw+1))
                                list_for_line.append(raw)

                            else:
                                list_for_line.append(raw)
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                #list_line.append(str(raw+1))
        
        elif node['type'] == 'Label':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0])-1
            code = content[raw].strip()
            list_write2file.append(code + ' ' + str(raw+1) + '\n')
            #list_line.append(str(raw+1))

        elif node['type'] == 'ForInit':
            continue

        elif node['type'] == 'Parameter':
            if list_result[0]['type'] != 'Function':
                row = node['location'].split(':')[0]
                list_write2file.append(node['code'] + ' ' + str(row) + '\n')
                #list_line.append(row)
            else:
                continue

        elif node['type'] == 'IdentifierDeclStatement':
            if node['code'].strip().split(' ')[0] == "undef":
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                raw = int(node['location'].split(':')[0])-1
                code1 = content[raw].strip()
                list_code2 = node['code'].strip().split(' ')
                i = 0
                while i < len(list_code2):
                    if code1.find(list_code2[i]) != -1:
                        del list_code2[i]
                    else:
                        break
                code2 = ' '.join(list_code2)

                list_write2file.append(code1 + ' ' + str(raw+1) + '\n' + code2 + ' ' + str(raw+2) + '\n')

            else:
                list_write2file.append(node['code'] + ' ' + node['location'].split(':')[0] + '\n')

        elif node['type'] == 'ExpressionStatement':
            row = int(node['location'].split(':')[0])-1
            if row in list_for_line:
                continue

            if node['code'] in ['\n', '\t', ' ', '']:
                list_write2file.append(node['code'] + ' ' + str(row+1) + '\n')
                #list_line.append(row+1)
            elif node['code'].strip()[-1] != ';':
                list_write2file.append(node['code'] + '; ' + str(row+1) + '\n')
                #list_line.append(row+1)
            else:
                list_write2file.append(node['code'] + ' ' + str(row+1) + '\n')
                #list_line.append(row+1)

        elif node['type'] == "Statement":
            row = node['location'].split(':')[0]
            list_write2file.append(node['code'] + ' ' + str(row) + '\n')
            #list_line.append(row+1)

        else:         
            #print node['name'], node['code'], node['type'], node['filepath']
            if node['location'] == None:
                continue
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            row = int(node['location'].split(':')[0])-1
            code = content[row].strip()
            if row in list_for_line:
                continue

            else:
                list_write2file.append(node['code'] + ' ' + str(row+1) + '\n')
                #list_line.append(str(row+1))

    f = open(store_filepath, 'a')
    f.write(str(count) + ' ' + filepath_all + ' ' + func_name + ' ' + startline + '\n')
    for wb in list_write2file:
        f.write(wb)
    f.write('------------------------------' + '\n')
    f.close()


def program_slice(pdg, startnodesID, slicetype, testID):#process startnodes as a list, because main func has many different arguments
    list_startnodes = []
    if pdg == False or pdg == None:
        return [], [], []
        
    for node in pdg.vs:
        #print node['functionId']
        if node['name'] in startnodesID:
            list_startnodes.append(node)

    if list_startnodes == []:
        return [], [], []

    if slicetype == 0:#backwords
        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_back = program_slice_backwards(pdg, list_startnodes)

        not_scan_func_list = []
        results_back, temp = process_cross_func(results_back, testID, 1, results_back, not_scan_func_list)


        return [results_back], start_line, startline_path

    elif slicetype == 1:#forwords
        #print "start extract forword dataflow!"
        print list_startnodes, startnodesID
        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_for = program_slice_forward(pdg, list_startnodes)

        not_scan_func_list = []
        results_for, temp = process_cross_func(results_for, testID, 1, results_for, not_scan_func_list)

        return [results_for], start_line, startline_path

    else:#bi_direction
        #print "start extract backwords dataflow!"

        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_back = program_slice_backwards(pdg, list_startnodes)#results_back is a list of nodes

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
        list_cross_func_back, not_scan_func_list = process_crossfuncs_back_byfirstnode(start_list, testID, i, not_scan_func_list)
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

            list_to_crossfunc_back, temp = process_cross_func(list_to_crossfunc_back, testID, 0, list_to_crossfunc_back, not_scan_func_list)

            list_to_crossfunc_for, temp = process_cross_func(list_to_crossfunc_for, testID, 1, list_to_crossfunc_for, not_scan_func_list)

            all_result.append(list_to_crossfunc_back + list_to_crossfunc_for)
  

        return all_result, start_line, startline_path


def api_slice():
    count = 1
    store_filepath = "/home/anderson/Desktop/locator_slice/apislice/"+str(i)+"/"
    if not os.path.exists(store_filepath):
        os.makedirs(store_filepath)
    store_filepath = os.path.join(store_filepath,"api_slices.txt")
    #store_filepath = "C/test_data/31/api_slices.txt"
    f = open("/home/anderson/Desktop/locator_point/"+str(i)+"/sensifunc_slice_points.pkl", 'rb')
    dict_unsliced_sensifunc = pickle.load(f)
    f.close()
    l = ['CVE-2013-1573']
    for key in tqdm.tqdm(dict_unsliced_sensifunc.keys()):#key is testID
        #print key
        if key in l:
            continue
        for _t in dict_unsliced_sensifunc[key]:
            list_sensitive_funcid = _t[0]
            pdg_funcid = _t[1]
            sensitive_funcname = _t[2]

            if sensitive_funcname.find("main") != -1:
                continue #todo
            else:
                slice_dir = 2
                pdg = getFuncPDGById(key, pdg_funcid)
                if pdg == False:
                    print 'error'
                    exit()

                list_code, startline, startline_path = program_slice(pdg, list_sensitive_funcid, slice_dir, key)
                #print len(list_code)

                if list_code == []:
                    fout = open("error.txt", 'a')
                    fout.write(sensitive_funcname + ' ' + str(list_sensitive_funcid) + ' found nothing! \n')
                    fout.close()
                else:
                    #for _list in list_code:
                    _list = list_code[0]
                    get_slice_file_sequence(store_filepath, _list, count, sensitive_funcname, startline, startline_path)
                    count += 1

def pointers_slice():
    count = -1
    store_filepath = "/home/anderson/Desktop/locator_slice/pointslice/"+str(i)+"/"
    if not os.path.exists(store_filepath):
        os.makedirs(store_filepath)
    store_filepath = os.path.join(store_filepath,"pointersuse_slices.txt")
    f = open("/home/anderson/Desktop/locator_point/"+str(i)+"/pointuse_slice_points_new.pkl", 'rb')
    dict_unsliced_pointers = pickle.load(f)
    #print dict_unsliced_pointers
    f.close()

    l = ['CVE-2015-4521', 'CVE-2015-4482', 'CVE-2016-2824', 'CVE-2015-4487', 'CVE-2014-2894', 'CVE-2015-4484', 'CVE-2016-4002', 'CVE-2015-2729', 'CVE-2015-4500', 'CVE-2015-4501', 'CVE-2016-5238', 'CVE-2014-5263', 'CVE-2015-2726', 'CVE-2013-4526', 'CVE-2014-0223', 'CVE-2013-4527', 'CVE-2016-2814', 'CVE-2015-7178', 'CVE-2015-7179', 'CVE-2013-4530', 'CVE-2013-4533', 'CVE-2015-8662', 'CVE-2015-7176', 'CVE-2016-1714', 'CVE-2015-7174', 'CVE-2015-7175', 'CVE-2016-9104', 'CVE-2016-5280', 'CVE-2016-9101', 'CVE-2016-9103', 'CVE-2016-2819', 'CVE-2016-2818', 'CVE-2015-0829', 'CVE-2016-4952', 'CVE-2015-4511', 'CVE-2015-4512', 'CVE-2015-4517', 'CVE-2014-9676', 'CVE-2013-6399', 'CVE-2016-8910', 'CVE-2013-0866', 'CVE-2013-4542', 'CVE-2015-3395', 'CVE-2016-6351', 'CVE-2016-9923', 'CVE-2013-0860', 'CVE-2016-1957', 'CVE-2016-1956', 'CVE-2013-7020', 'CVE-2013-7021', 'CVE-2016-1953', 'CVE-2016-1952', 'CVE-2013-0868', 'CVE-2014-8541', 'CVE-2016-1970', 'CVE-2014-9319', 'CVE-2014-8542', 'CVE-2016-7421', 'CVE-2014-8544', 'CVE-2014-8547', 'CVE-2016-7161', 'CVE-2014-7937', 'CVE-2015-1872', 'CVE-2014-9317', 'CVE-2014-9316', 'CVE-2014-7933', 'CVE-2016-5258', 'CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107', 'CVE-2016-4453', 'CVE-2015-7203', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5256', 'CVE-2016-5257', 'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2015-4504', 'CVE-2016-7170', 'CVE-2016-5278', 'CVE-2015-7180', 'CVE-2016-1981', 'CVE-2016-8909', 'CVE-2016-2836', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182', 'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779', 'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-4493', 'CVE-2015-0825', 'CVE-2015-0824', 'CVE-2016-2837', 'CVE-2015-0826', 'CVE-2016-5254', 'CVE-2016-4441', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2013-4149', 'CVE-2015-7198', 'CVE-2015-7199', 'CVE-2015-2710', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023', 'CVE-2013-0845', 'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668','CVE-2013-1573', 'CVE-2015-2716', 'CVE-2015-2739', 'CVE-2016-2532','CVE-2016-2522']
    #l = []
    for key in tqdm.tqdm(dict_unsliced_pointers.keys()):#key is testID
        print key
        count = count + 1
        if count <=321:
            continue

        if key in l:
            continue

        for _t in dict_unsliced_pointers[key]:
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            #print key, pdg_funcid
            pointers_name = str(_t[2])


            slice_dir = 2
            pdg = getFuncPDGById(key, pdg_funcid)
            if pdg == False:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key)

            if list_code == []:
                fout = open("error.txt", 'a')
                fout.write(pointers_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                #for _list in list_code:
                _list = list_code[0]
                get_slice_file_sequence(store_filepath, _list, count, pointers_name, startline, startline_path)
                count += 1


def arrays_slice():
    count = -1
    store_filepath = "/home/anderson/Desktop/locator_slice/arrayslice/"+str(i)+"/"
    if not os.path.exists(store_filepath):
        os.makedirs(store_filepath)
    store_filepath = os.path.join(store_filepath,"arraysuse_slices.txt")
    f = open("/home/anderson/Desktop/locator_point/"+str(i)+"/arrayuse_slice_points.pkl", 'rb')
    dict_unsliced_pointers = pickle.load(f)
    f.close()
    #l = ['CVE-2010-2068', 'CVE-2015-1158', 'CVE-2006-1530', 'CVE-2012-2802', 'CVE-2010-4165', 'CVE-2014-3523', 'CVE-2012-6062', 'CVE-2013-1672', 'CVE-2007-4997', 'CVE-2013-4082', 'CVE-2012-4186', 'CVE-2013-4512', 'CVE-2013-6450', 'CVE-2011-2534', 'CVE-2014-1690', 'CVE-2011-2536', 'CVE-2012-2319', 'CVE-2012-0957', 'CVE-2011-3936', 'CVE-2004-1151', 'CVE-2013-4929', 'CVE-2010-3296', 'CVE-2011-4102', 'CVE-2012-5668', 'CVE-2011-4100', 'CVE-2011-1959', 'CVE-2012-3969', 'CVE-2012-1183', 'CVE-2011-0726', 'CVE-2013-0756', 'CVE-2004-0535', 'CVE-2010-2495', 'CVE-2012-2393', 'CVE-2015-3811', 'CVE-2012-2776', 'CVE-2009-2909', 'CVE-2014-3633', 'CVE-2014-1508', 'CVE-2011-2529', 'CVE-2014-3537', 'CVE-2012-1947', 'CVE-2013-0844', 'CVE-2012-1942', 'CVE-2014-0195', 'CVE-2012-4293', 'CVE-2012-4292', 'CVE-2008-1390', 'CVE-2011-0021', 'CVE-2012-3991', 'CVE-2007-4521', 'CVE-2009-0746', 'CVE-2011-1147', 'CVE-2012-5240', 'CVE-2013-2634', 'CVE-2014-8133', 'CVE-2006-2778', 'CVE-2012-4288', 'CVE-2015-0253', 'CVE-2012-0444', 'CVE-2013-1726', 'CVE-2013-7112', 'CVE-2006-1856', 'CVE-2013-0850', 'CVE-2011-3623', 'CVE-2013-1582', 'CVE-2013-1732', 'CVE-2014-8884', 'CVE-2013-0772', 'CVE-2014-9374', 'CVE-2014-1497', 'CVE-2014-0221', 'CVE-2013-1696', 'CVE-2011-1833', 'CVE-2013-1693', 'CVE-2013-0872', 'CVE-2012-2790', 'CVE-2012-2791', 'CVE-2012-2796', 'CVE-2012-0477', 'CVE-2012-2652', 'CVE-2006-4790', 'CVE-2013-0867', 'CVE-2013-4932', 'CVE-2013-0860', 'CVE-2014-3511', 'CVE-2014-3510', 'CVE-2013-0868', 'CVE-2014-8541', 'CVE-2014-2739', 'CVE-2014-9319', 'CVE-2006-4813', 'CVE-2014-8544', 'CVE-2011-3973', 'CVE-2013-1848', 'CVE-2014-9316', 'CVE-2012-1594', 'CVE-2013-1573', 'CVE-2012-0068', 'CVE-2015-0833', 'CVE-2010-1748', 'CVE-2012-0067', 'CVE-2011-3362', 'CVE-2014-3182', 'CVE-2013-5641', 'CVE-2013-5642', 'CVE-2011-3484', 'CVE-2013-6891', 'CVE-2014-8712', 'CVE-2014-8713', 'CVE-2014-8714', 'CVE-2013-4534', 'CVE-2010-2431', 'CVE-2014-8412', 'CVE-2011-1175', 'CVE-2012-5237', 'CVE-2011-1173', 'CVE-2012-5238', 'CVE-2014-4611', 'CVE-2015-0564', 'CVE-2014-5271', 'CVE-2011-0055', 'CVE-2014-3470', 'CVE-2014-8643', 'CVE-2015-0204', 'CVE-2014-2286', 'CVE-2012-6537', 'CVE-2011-3945', 'CVE-2011-3944', 'CVE-2011-2896', 'CVE-2010-2955', 'CVE-2013-2495', 'CVE-2013-4931', 'CVE-2013-4933', 'CVE-2012-2775', 'CVE-2013-4934', 'CVE-2013-4936', 'CVE-2011-4594', 'CVE-2014-6424', 'CVE-2013-0311', 'CVE-2011-4598', 'CVE-2006-2935', 'CVE-2011-4352', 'CVE-2012-1184', 'CVE-2005-3356', 'CVE-2012-6059', 'CVE-2012-6058', 'CVE-2011-3950', 'CVE-2014-9672', 'CVE-2010-2803', 'CVE-2013-7011', 'CVE-2013-3674', 'CVE-2009-0676', 'CVE-2013-6380', 'CVE-2009-2768', 'CVE-2015-3008', 'CVE-2013-0796', 'CVE-2009-2484', 'CVE-2013-4264', 'CVE-2013-4928', 'CVE-2014-8542', 'CVE-2012-6540', 'CVE-2015-0228', 'CVE-2013-7008', 'CVE-2013-7009']
    l = ['CVE-2013-1573','CVE-2015-2716', 'CVE-2015-2739', 'CVE-2014-6424', 'CVE-2016-1957','CVE-2016-1956']
    for key in tqdm.tqdm(dict_unsliced_pointers.keys()):#key is testID
        #print key
        count = count+1
        # if count<=111:
        #     continue
        if key in l:
            continue

        for _t in dict_unsliced_pointers[key]:
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            #print pdg_funcid
            arrays_name = str(_t[2])


            slice_dir = 2
            pdg = getFuncPDGById(key, pdg_funcid)
            if pdg == False:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key)

            if list_code == []:
                fout = open("error.txt", 'a')
                fout.write(arrays_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                #for _list in list_code:
                _list = list_code[0]
                get_slice_file_sequence(store_filepath, _list, count, arrays_name, startline, startline_path)
                count += 1


def integeroverflow_slice():
    count = -1
    store_filepath = "/home/anderson/Desktop/locator_slice/integeslice/"+str(i)+"/"
    if not os.path.exists(store_filepath):
        os.makedirs(store_filepath)
    store_filepath = os.path.join(store_filepath,"integeroverflow_slices.txt")
    f = open("/home/anderson/Desktop/locator_point/"+str(i)+"/integeroverflow_slice_points_new.pkl", 'rb')
    # store_filepath = "/home/zheng/Desktop/locator_slice/arrayslice/31/arraysuse_slices.txt"
    # f = open("/home/zheng/Desktop/locator_point/31/arrayuse_slice_points.pkl", 'rb')
    dict_unsliced_expr = pickle.load(f)
    f.close()

    l = ['CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107', 'CVE-2016-4453', 'CVE-2015-4475', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5257', 'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2016-5278', 'CVE-2016-1981', 'CVE-2015-2726', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182', 'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779', 'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-7203', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2015-7199', 'CVE-2015-2710', 'CVE-2016-4952', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023', 'CVE-2013-0845', 'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668', 'CVE-2013-1573', 'CVE-2015-2716', 'CVE-2015-2739', 'CVE-2016-2532']
    for key in tqdm.tqdm(dict_unsliced_expr.keys()):#key is testID
        #print key
        if key in l:
            continue
        for _t in dict_unsliced_expr[key]:
            list_expr_funcid = _t[0]
            pdg_funcid = _t[1]
            #print pdg_funcid
            expr_name = str(_t[2])


            slice_dir = 2
            pdg = getFuncPDGById(key, pdg_funcid)
            if pdg == False:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_expr_funcid, slice_dir, key)

            if list_code == []:
                fout = open("error.txt", 'a')
                fout.write(expr_name + ' ' + str(list_expr_funcid) + ' found nothing! \n')
                fout.close()
            else:
                #for _list in list_code:
                _list = list_code[0]
                get_slice_file_sequence(store_filepath, _list, count, expr_name, startline, startline_path)
                count += 1
     

if __name__ == "__main__":
    i = 18
    api_slice()
    pointers_slice()
    arrays_slice()
    integeroverflow_slice()
