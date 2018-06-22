#!/usr/bin/env python

#
# Script to remove loops from rivers
#
# Example: 
#     /---------\ 
# ----+         \--+--------    => ----+            +--------
#     \------------/                   \------------/

def remove_loops(river):
    loops = []
    for i in range(0,len(river['paths'])):
        for j in range(0,len(river['paths'])):
            if i!=j:
                j_has_start_of_i = False
                j_has_end_of_i = False
                for k in range(0,len(river['paths'][j])):
                    if river['paths'][i][0]==river['paths'][j][k]:
                        j_has_start_of_i = True
                    if river['paths'][i][-1]==river['paths'][j][k]:
                        j_has_end_of_i = True
                if j_has_start_of_i and j_has_end_of_i:
                    loops.append(i)
                    print 'path %d is a loop of %d' % (i,j)
    newpaths = []
    for i in range(0,len(river['paths'])):
        if i not in loops:
            newpaths.append(river['paths'][i])
    #print '%s: path: %d->%d points: %d->%d' % (river['name'].encode('latin1'),len(river['paths']),len(newpaths),sum(map(len,river['paths'])),sum(map(len,newpaths)))
    river['paths'] = newpaths

def main():
    input_filename = 'rivers-merged.json'
    output_filename = 'rivers-merged-cleaned.json'

    import json

    with open(input_filename,'r') as f:
        rivers = json.load(f)

    for river in rivers:
        remove_loops(river)

    with open(output_filename,'w') as f:
        json.dump(rivers,f)

if __name__=='__main__':
    main()
