
def link_paths(paths_in):
    initial_len = sum(map(len,paths_in))
    for i in range(0,len(paths_in)):
        for j in range(0,len(paths_in)):
            if i!=j and len(paths_in[i])>0 and len(paths_in[j])>0 and paths_in[j][0] == paths_in[i][-1]:
                paths_in[i] += paths_in[j]
                paths_in[j] = []
            elif i!=j and len(paths_in[i])>0 and len(paths_in[j])>0 and paths_in[i][0] == paths_in[j][-1]:
                paths_in[j] += paths_in[i]
                paths_in[i] = []
    paths = filter(lambda path:len(path)>0,paths_in)
    assert(initial_len==sum(map(len,paths)))
    #print len(paths)
    return paths
