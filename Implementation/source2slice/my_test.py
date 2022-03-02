import pickle
load_point_path = "/home/anderson/Desktop/locator_point/" +"1"
api_point_path = load_point_path + "/sensifunc_slice_points.pkl"
return_point_path = load_point_path + "/return_slice_points_new.pkl"
f = open(api_point_path, 'rb')
f = open(return_point_path,'rb')
content = pickle.load(f)
print(type(content))
for key in content:
    print(key)
    value = content[key]
    for val in value:
        print(val)
        print(type(val))
