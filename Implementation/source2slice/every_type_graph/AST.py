## coding:utf-8
import queue

from Implementation.source2slice.access_db_operate import *
import copy
import tqdm
from Implementation.source2slice.general_op import *
from py2neo.packages.httpstream import http
from tree import Tree
http.socket_timeout = 9999


def generate_AST(slice_id):
    j = JoernSteps()
    j.connectToDatabase()
    #获取函数节点
    all_func_node = getALLFuncNode(j)
    for func_node in tqdm.tqdm(all_func_node):
        testID = getFuncFile(j, func_node._id).split('/')[-2]
        # path = os.path.join("/home/zheng/Desktop/qemuAST/"+str(slice_id)+"/AST_db", testID)
        store_file_name = func_node.properties['name'] + '_' + str(func_node._id)
        # store_path = os.path.join(path, store_file_name)
        # if os.path.exists(store_path):
        #     continue
        # if not os.path.exists(path):
        #     os.mkdir(path)
        # if not os.path.exists(store_path):
        #     os.mkdir(store_path)
        # AST = translateASTByNode(j, func_node)
        all_nodes = getAllNodesByFuncNode(j,func_node._id)
        g = drawAstTreeGraph(j, getASTEdges(j, func_node._id),func_node._id)
        idx2node = dict()
        node2idx = dict()
        # id2node = dict()
        edge_dict = dict()
        for i in range(len(g.vs)):
            idx2node[i] = g.vs[i]
            node2idx[g.vs[i]] = i
            # id2node[g.vs[i]._id] = g.vs[i]
        for edge in g.es:
            idx1 = edge.source
            idx2 = edge.target
            if idx1 in edge_dict:
                edge_dict[idx1].append(idx2)
            else:
                edge_dict[idx1] =[idx2]
        for n in all_nodes:
            if not n._id in idx2node:
                continue
            node = idx2node[n._id]
            root = Tree()
            root.type = node['type']
            root.code = node['code']
            q = queue.Queue()
            q.put([root,node])
            flag = False
            while not q.empty():
                curr = q.get()
                if node2idx[curr[1]] in edge_dict:
                    for next_idx in edge_dict[node2idx[curr[1]]]:
                        next = idx2node[next_idx]
                        child = Tree()
                        child.type = next['type']
                        child.code = next['code']
                        curr[0].add_child(child)
                        q.put([child,next])
                        print 'yes ok'
                        flag= True
                else:
                    curr[0].is_leaf = True
            if flag:
                print(root.children)
                print(root.type)
                print(root.code)
            # print(root)



def TransAST(slice_id):
    j = JoernSteps()
    j.connectToDatabase()
    all_func_node = getALLFuncNode(j)
    a = 0
    record = []
    label = []
    for node in tqdm.tqdm(all_func_node):
        testID = getFuncFile(j, node._id).split('/')[-2]
        store_file_name = node.properties['name'] + '_' + str(node._id)
        pdg_path = os.path.join("/home/zheng/Desktop/qemuAST/"+str(slice_id)+"/AST_db", testID,store_file_name)
        pdg = pickle.load(open(pdg_path))
        recordtemp = []
        for i in tqdm.tqdm(range(pdg.ecount())):
            d = dict()
            d['sid'] = str(pdg.vs[pdg.es[i].source]['name'])
            if pdg.vs[pdg.es[i].source]['location'] != None:
                d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']), 'code': str(pdg.vs[pdg.es[i].source]['code']),
                         'lineNo': str(pdg.vs[pdg.es[i].source]['location'].split(':')[0])}
            elif pdg.vs[pdg.es[i].source]['location'] == None:
                d['spro'] = {'type': str(pdg.vs[pdg.es[i].source]['type']), 'code': str(pdg.vs[pdg.es[i].source]['code']),
                         'lineNo': 'None'}
            d['eid'] = str(pdg.vs[pdg.es[i].target]['name'])
            if pdg.vs[pdg.es[i].target]['location'] != None:
                d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']),
                             'code': str(pdg.vs[pdg.es[i].target]['code']),
                             'lineNo': str(pdg.vs[pdg.es[i].target]['location'].split(':')[0])}
            elif pdg.vs[pdg.es[i].target]['location'] == None:
                d['epro'] = {'type': str(pdg.vs[pdg.es[i].target]['type']), 'code': str(pdg.vs[pdg.es[i].target]['code']),
                         'lineNo': 'None'}
            d['label'] = str(pdg.es[i]['label'])
            recordtemp.append(d)
        #print 1
        if pdg.vcount() == 0:
            filename = os.listdir('/home/zheng/Desktop/qemu_slice/'+str(slice_id)+'/'+testID)
            startline_path = '/home/zheng/Desktop/qemu_slice/'+str(slice_id)+'/'+testID+'/'+filename[0]
        else:
            startline_path = pdg.vs[1]['filepath']
        labelfile = startline_path
        labeltemp = labelfile.split('/')[-1]
        labeltemp = labeltemp.split('.')[0]
        labeltemp = labeltemp.split('_')[-1]
        labell = str(labelfile) + '\t' + str(labeltemp)
        #print 1
        if len(recordtemp) != 0:
            record.append(recordtemp)
            label.append(labell)

    store_record_path = '/home/zheng/Desktop/QEMU_AST_record/'+str(slice_id)+'/JOERNrecord.txt'
    store_real_path = '/home/zheng/Desktop/QEMU_AST_record/'+str(slice_id)+'/JOERNreal-mvd.txt'
    for r in record:
        with open(store_record_path, 'a+') as record_file:
                for ri in r:
                    record_file.write(str(ri) + '\n')
                record_file.write('--------------finish--------------\n')
    for l in label:
        with open(store_real_path, 'a+') as label_file:
                    label_file.write(str(l) + '\n')


if __name__ == '__main__':
    generate_AST(9)
    # TransAST(9)



