import re 
import pygame as pg
import io
from PIL import Image

uhlovodiky = ["meth","eth","prop","but","pent","hex","hept","okt","non","dek"]
cisla = ["mono","di","tri","tetra","penta","hexa","hepta","okta","nona","deka"]
nazvy_vazeb = ["en","yn"]

#uhlovodik = "3,4,6-tributyl-7-methyl-3,6-ethylokt-4-en-1-yn"


def get_uhlovodik(vstup):
    vstup = list(filter(None, re.split("[,-]+", vstup)))

    #osekání vstupu na hlavní část
    hlavni_retezec = 0
    hlavni_retezec_c = 0 #počet uhlovodíků v hlavní části (1,2)
    for i in vstup:
        c = 0
        for u in uhlovodiky:
            if u in i: 
                c+=1
        if c >= hlavni_retezec_c: 
            hlavni_retezec_c = c
            hlavni_retezec = i
    #nalezení hlavního uhlovodíku
    hlavni_uhlovodik = ""
    if hlavni_retezec_c > 1:
        highest_index = 0
        for i in uhlovodiky:
            index = hlavni_retezec.find(i)
            if index > highest_index:
                highest_index = index
        hlavni_uhlovodik = hlavni_retezec[highest_index:]
    else:
        hlavni_uhlovodik = hlavni_retezec
    #délka hlavního uhlovodíku
    hlavni_uhlovodik_delka = 0
    for i in uhlovodiky:
        if i in hlavni_uhlovodik:
            hlavni_uhlovodik_delka = uhlovodiky.index(i)+1
    #nalezení zbytků
    zbytky = []
    indexy_zbytku = []
    for i in range(vstup.index(hlavni_retezec)+1):
        if vstup[i].isdigit():
            indexy_zbytku.append(int(vstup[i]))
        else:
            nazev = vstup[i]
            for c in cisla:
                nazev = nazev.replace(c,"")
            if i == vstup.index(hlavni_retezec):
                nazev = nazev[:highest_index]
            #print(f"{nazev}: {indexy_zbytku}")
            delka = 0
            for u in uhlovodiky:
                if nazev[:-2] in u:
                    delka = uhlovodiky.index(u)+1

            zbytky.append({"nazev":nazev,"delka": delka,"pozice":indexy_zbytku, "smer": [-1 for i in range(len(indexy_zbytku))]})
            indexy_zbytku = []
    #nalezení vazeb
    index_vazeb = []
    vazby = []
    for i in range(vstup.index(hlavni_retezec)+1,len(vstup)):
        if vstup[i].isdigit():
            index_vazeb.append(int(vstup[i]))
        else:
            nazev = vstup[i]
            for c in cisla:
                nazev = nazev.replace(c,"")
            delka = nazvy_vazeb.index(nazev)+2
            
            #print(f"{nazev} ({delka}): {index_vazeb}")
            vazby.append({"nazev":nazev,"delka": delka,"pozice":index_vazeb})
            index_vazeb = []

    double_zbytky = []
    #nastavení směru vykreslení zbytku (když jsou 2)
    for i in zbytky:
        for j in i["pozice"]:
            c = 0
            to_change = {"index":0,"pos_index":0}
            for k in zbytky:
                for l in k["pozice"]:
                    if j == l:
                        c+=1
                        to_change = {"index":zbytky.index(k),"pos_index":k["pozice"].index(l)}
            if c > 1:
                zbytky[to_change["index"]]["smer"][to_change["pos_index"]] = 1

    #print(f"Hlavní řetězec: {hlavni_uhlovodik}, délka: {hlavni_uhlovodik_delka}")
    return [hlavni_uhlovodik_delka,zbytky,vazby]


def make_img(uhlovodik):
    hlavni_uhlovodik_delka,zbytky,vazby = get_uhlovodik(uhlovodik)

    pg.init()

    screen = pg.display.set_mode([500,500])

    done = False

    print(zbytky)

    screen.fill([255,255,255])

    #hlavní řetězec
    start_x, start_y = 50,225
    for i in range(hlavni_uhlovodik_delka-1):
        if i%2==0:
            pg.draw.line(screen, [0,0,0], [start_x+i*50,start_y], [start_x+i*50+50,start_y+50], 2)
        else:
            pg.draw.line(screen, [0,0,0], [start_x+i*50,start_y+50], [start_x+i*50+50,start_y], 2)
    #vazby
    off = 5

    for i in vazby:
        for x in range(len(i["pozice"])):
            for d in range(i["delka"]):
                real_x = start_x+50*(i["pozice"][x]-1)
                off = 5*-d
                if i["pozice"][x]%2 == 1:
                    pg.draw.line(screen, [0,0,0], [real_x+off,start_y-off] , [real_x+off+50,start_y-off+50], 2)
                else:
                    pg.draw.line(screen, [0,0,0], [real_x+off,start_y+off+50] , [real_x+off+50,start_y+off], 2)

    #zbytky
    z_size_start = 45 #délka první vazby
    z_normal_size = 35 #délka ostatních vazeb
    for i in zbytky:
        for x in range(len(i["pozice"])):
            for d in range(i["delka"]):

                smer = i["smer"][x]

                z_size = z_size_start if d == 0 else z_normal_size

                if d > 0:
                    real_x = start_x+50*(i["pozice"][x]-1)+z_size*smer+(z_size_start-z_normal_size)*smer
                else:
                    real_x = start_x+50*(i["pozice"][x]-1)

                if i["pozice"][x]%2 == 0:
                    if d>0: real_y = start_y+z_size*d+50+(z_size_start-z_normal_size)
                    else: real_y = start_y+z_size*d+50
                else:
                    if d>0: real_y = start_y-z_size*d-(z_size_start-z_normal_size)
                    else: real_y = start_y-z_size*d
                
                y_smer = 1 if i["pozice"][x]%2 == 0 else -1
                
                if d%2 == 1 and d > 0:
                    smer*=-1
                elif d > 0:
                    real_x+=z_size

                if d == 0:
                    pg.draw.line(screen, [0,0,0], [real_x,real_y] , [real_x+z_size*smer,real_y+z_size*y_smer], 2)
                else:
                    pg.draw.line(screen, [0,0,0], [real_x,real_y] , [real_x+z_size*smer,real_y+z_size*y_smer], 2)

    pg.display.update()    


    #imgStr = pg.image.tostring(screen,"RGBA")
    #return io.BytesIO(imgStr)
    # img = Image.frombytes("RGBA",(500,500), screen.get_buffer().raw)
    # #img = io.BytesIO(Image.frombytes("RGBA",(500,500), screen.get_buffer().raw).tobytes())
    # img.save("temp.png", format="png")
    # with open("temp.png","rb") as f:
    #     return io.BytesIO(f.read())
    imgStr = pg.image.tostring(screen,"RGBA")
    img = Image.frombytes("RGBA",(500,500), imgStr)
    img.save("temp.png", "png")
    with open("temp.png","rb") as f:
        return io.BytesIO(f.read())

#img = Image.frombytes("RGBA",(500,500), imgStr)
#f = io.StringIO()
#img.save("ahoj.png", "png")
#print(f.getvalue())

# print(make_img("3,4,6-tributyl-7-methyl-3,6-ethylokt-4-en-1-yn"))
# with open("f.png","wb") as f:
#     f.write(make_img("3,4,6-tributyl-7-methyl-3,6-ethylokt-4-en-1-yn").getvalue())

