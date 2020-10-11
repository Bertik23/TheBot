import re 
import io
from PIL import Image, ImageDraw

uhlovodiky = ["meth","eth","prop","but","pent","hex","hept","okt","non","dek"]
cisla = ["mono","di","tri","tetra","penta","hexa","hepta","okta","nona","deka"]
nazvy_vazeb = ["en","yn"]

uhlovodik = "3,6-diethyl-2,4-dimethyl-4-propylokta-1,7-dien"


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
                nazev = nazev.replace(hlavni_uhlovodik,"")

            #print(f"{nazev}: {indexy_zbytku}")
            delka = 0

            if nazev[-1] == "n": nazev = nazev[:-1] #nevim proč to tam dává 'n' a jsem línej to zjišťovat

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

    #velikost
    max_zbytek_top, max_zbytek_bot = 0,0
    add_padding_x = [0,0]
    for i in zbytky:
        for p in range(len(i["pozice"])):
            #padding stuff
            if i["pozice"][p] == 1:
                add_padding_x[0] = 50
            if i["pozice"][p] == hlavni_uhlovodik_delka and i["smer"][p] == 1:
                add_padding_x[1] = 50

            if i["pozice"][p]%2 == 1 and i["delka"] > max_zbytek_top:
                max_zbytek_top = i["delka"]
            elif i["delka"] > max_zbytek_bot:
                max_zbytek_bot = i["delka"]

    z_size_start = 45 #délka první vazby
    z_normal_size = 35 #délka ostatních vazeb

    padding_x = 20
    padding_y = 20

    start_x, start_y = padding_x+add_padding_x[0], padding_y+max_zbytek_top*z_normal_size+(z_size_start-z_normal_size)
    width = (hlavni_uhlovodik_delka-1)*50+padding_x*2+sum(add_padding_x)
    height = 2*padding_y + 50 + (max_zbytek_bot+max_zbytek_top)*z_normal_size+2*(z_size_start-z_normal_size)

    done = False

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    #hlavní řetězec
    
    for i in range(hlavni_uhlovodik_delka-1):
        if i%2==0:
            draw.line((start_x+i*50,start_y, start_x+i*50+50,start_y+50), fill=(0,0,0), width=2)
        else:
            draw.line((start_x+i*50,start_y+50, start_x+i*50+50,start_y), fill=(0,0,0), width=2)
    #vazby
    off = 5

    for i in vazby:
        for x in range(len(i["pozice"])):
            for d in range(i["delka"]):
                real_x = start_x+50*(i["pozice"][x]-1)
                off = 5*-d
                if i["pozice"][x]%2 == 1:
                    draw.line((real_x+off,start_y-off, real_x+off+50,start_y-off+50), fill=(0,0,0), width=2)
                else:
                    draw.line((real_x+off,start_y+off+50, real_x+off+50,start_y+off), fill=(0,0,0), width=2)

    #zbytky
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
                   real_x+=z_size*-smer

                if d == 0:
                    draw.line((real_x,real_y, real_x+z_size*smer,real_y+z_size*y_smer), fill=(0,0,0), width=2)
                else:
                    draw.line((real_x,real_y, real_x+z_size*smer,real_y+z_size*y_smer), fill=(0,0,0), width=2)
 


    img.save("temp.png", "png")
    with open("temp.png","rb") as f:
        return io.BytesIO(f.read())

#make_img(uhlovodik)