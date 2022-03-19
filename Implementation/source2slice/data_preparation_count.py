import os

import tqdm


def calculate(project='linux_data'):
    post_path = '/home/anderson/Documents/siamese_dataset/' + project
    origin_path = '/home/anderson/Documents/origin_siamese_dataset/' + project
    delete_num = 0
    change_label_num = 0
    add_cve_num = 0
    add_file_num = 0
    for cve in tqdm.tqdm(os.listdir(os.path.join(post_path, 'fix'))):
        post_fix_files = os.listdir(os.path.join(post_path, 'fix', cve))
        post_vul_files = os.listdir(os.path.join(post_path, 'vul', cve))
        if not os.path.exists(os.path.join(origin_path, 'fix', cve)):
            add_cve_num += 1
            add_file_num += len(post_vul_files) + len(post_fix_files)
            continue
        origin_fix_files = os.listdir(os.path.join(origin_path, 'fix', cve))
        origin_vul_files = os.listdir(os.path.join(origin_path, 'vul', cve))
        delete_num += len(origin_vul_files) + len(origin_fix_files) - len(post_vul_files) - len(post_fix_files)
        for fix_file in post_fix_files:
            if not fix_file in origin_fix_files and fix_file in origin_vul_files:
                change_label_num += 1
        for vul_file in post_vul_files:
            if not vul_file in origin_vul_files and vul_file in origin_fix_files:
                change_label_num += 1

    print(project + ' delete_num:' + str(delete_num) + ' change_label_num:' + str(change_label_num))
    print(project + ' add cve num: ' + str(add_cve_num) + ' add file num: ' + str(add_file_num))


def cwe_to_cve():
    f = open('data/cve_to_cwe')
    cwe2cve = dict()
    for line in f.readlines():
        if line.startswith("//"):
            continue
        items = line.split(' ')
        cve = items[0].strip()
        for i in range(1, len(items)):
            cwe = items[i].strip()
            if cwe in cwe2cve:
                cwe2cve[cwe].append(cve)
            else:
                cwe2cve[cwe] = [cve]
    cwe_count = 0
    cve_count = 0
    for key, value in cwe2cve.items():
        cwe_count += 1
        cve_count += len(value)
        print(key + ':' + str(len(value)))
    print('cwe count: ' + str(cwe_count) + ' cve count: ' + str(cve_count))
    return cwe2cve


def cve_to_cwe():
    f = open('data/cve_to_cwe')
    cve2cwe = dict()
    for line in f.readlines():
        if line.startswith("//"):
            continue
        items = line.split(' ')
        cve = items[0].strip()
        for i in range(1, len(items)):
            cwe = items[i].strip()
            if cve in cve2cwe:
                cve2cwe[cve].append(cwe)
            else:
                cve2cwe[cve] = [cwe]
    return cve2cwe


def main():
    calculate(project='linux_data')
    calculate(project='openssl_data')

    cwe2cve = cwe_to_cve()
    print cwe2cve
    cve2cwe = cve_to_cwe()
    print cve2cwe


if __name__ == "__main__":
    main()
