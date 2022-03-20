def main():
    import pickle
    data = pickle.load(open('source2slice/data/mvp_ast.pkl'))
    print(data)
if __name__ == '__main__':
    main()