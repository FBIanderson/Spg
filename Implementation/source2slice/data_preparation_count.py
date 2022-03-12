import os

import tqdm


def calculate(project='linux_data'):
    post_path = '/home/anderson/Documents/siamese_dataset/' + project
    origin_path = '/home/anderson/Documents/origin_siamese_dataset/' + project
    delete_num = 0
    change_label_num = 0
    for cve in tqdm.tqdm(os.listdir(os.path.join(post_path, 'fix'))):
        post_fix_files = os.listdir(os.path.join(post_path, 'fix', cve))
        post_vul_files = os.listdir(os.path.join(post_path, 'vul', cve))
        origin_fix_files = os.listdir(os.path.join(origin_path, 'fix', cve))
        origin_vul_files = os.listdir(os.path.join(origin_path, 'vul', cve))
        delete_num += len(origin_vul_files) + len(origin_fix_files) - len(post_vul_files) - len(post_fix_files)
        for fix_file in post_fix_files:
            if not fix_file in origin_fix_files and fix_file in origin_vul_files:
                change_label_num += 1
        for vul_file in post_vul_files:
            if not vul_file in origin_vul_files and vul_file in origin_fix_files:
                change_label_num +=1

    print(project + ' delete_num:' + str(delete_num) + ' change_label_num:' + str(change_label_num))


def main():
    calculate(project='linux_data')
    calculate(project='openssl_data')


if __name__ == "__main__":
    main()
