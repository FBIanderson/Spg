## coding:utf-8
from Implementation.source2slice.access_db_operate import *
import copy
import tqdm
from Implementation.source2slice.general_op import *
from py2neo.packages.httpstream import http
http.socket_timeout = 9999


def main(slice_id):
    j = JoernSteps()
    j.connectToDatabase()
    all_func_node = getALLFuncNode(j)
    record = []
    label = []
    for node in tqdm.tqdm(all_func_node):
        testID = getFuncFile(j, node._id).split('/')[-2]
        store_file_name = node.properties['name'] + '_' + str(node._id)
        pdg_path = os.path.join("/home/zheng/Desktop/qemupdg/"+str(slice_id)+"/pdg_db", testID,store_file_name)
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
        elif pdg.vcount() != 0:
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

    store_record_path = '/home/zheng/Desktop/QEMU_PDG_record/'+str(slice_id)+'/JOERNrecord.txt'
    store_real_path = '/home/zheng/Desktop/QEMU_PDG_record/'+str(slice_id)+'/JOERNreal-mvd.txt'
    for r in record:
        with open(store_record_path, 'a+') as record_file:
                for ri in r:
                    record_file.write(str(ri) + '\n')
                record_file.write('--------------finish--------------\n')
    for l in label:
        with open(store_real_path, 'a+') as label_file:
                    label_file.write(str(l) + '\n')


if __name__ == '__main__':
    main(9)


