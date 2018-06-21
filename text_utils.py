# -*- coding: utf8 -*-

# Tokens to be ignored, don't forget the trailing space
unsignificant_tokens = ("Rivière d'","Rivière de",'Rivière '," (Ruisseau d')","Ruisseau d'","Ruisseau de la ","Ruisseau de l'"," (Ruisseau de)",'Ruisseau de ',"Ruisseau du ",'Ruisseau ','Le ','La ',"L'","Rio del ","Rio ","Fiume ","Torrent d'","Torrent de ","Torrent ","Torrente Valle ","Torrente ")

def clean4fuzzy(i):
    return unicode(remove_tokens(i.encode('utf8'),unsignificant_tokens).lower().strip(),encoding='utf8')

def remove_tokens(s,tokens):
    for token in tokens:
        i = 0
        while i>-1:
            #i = unicode(s).find(unicode(token,encoding='utf8'))
            i = s.find(token)
            if i>-1:
                s=s[:i]+s[i+len(token):]
    return s
