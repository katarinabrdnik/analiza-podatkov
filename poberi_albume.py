import requests
import os.path
import re
import orodja

STEVILO_STRANI = 125
STEVILO_ALBUMOV_NA_STRAN = 40

vzorec_bloka = re.compile(
    r'<div id="pos\d\d?\d?\d?"'
    r'.*?'
    r'class="linkfire_container lazyload">',  
    flags=re.DOTALL
)

vzorec_albuma = re.compile(
    r'<div class="topcharts_position">(?P<mesto>\d+)<span class="topcharts_position_desktop">.*?'
    r'<div class="topcharts_item_title"><a href=".*?" '
    r'class="release" title="\[Album(?P<id>\d+)\]">(?P<naslov>.*?)</a></div>.*?'
    r'class="artist">(?P<izvajalec>.*?)</a></div>',
    flags=re.DOTALL
)

vzorec_datuma_izdaje = re.compile(
    r'<div class="topcharts_item_releasedate">(?P<datum_izdaje>.*?\d\d\d\d)\n'
)

vzorec_povprecna_ocena = re.compile(
    r'<span class="topcharts_stat topcharts_avg_rating_stat">(?P<povprecna_ocena>\d\.\d\d)</span>'
)

vzorec_stevila_ocen = re.compile(
    r'<span class="topcharts_stat topcharts_ratings_stat">(?P<stevilo_ocen>\d?\d?,?\d\d\d)</span>'
)

vzorec_stevila_kritik = re.compile(
    r'<span class="topcharts_stat topcharts_reviews_stat">(?P<stevilo_kritik>\d?\d?,?\d?\d)</span>'
)

vzorec_zanrov = re.compile(
    r'<a class="genre topcharts_item_genres" href="/genre/.*?/">(?P<zanr>.*?)</a>,?\s?</span>'
)

vzorec_sekundarnih_zanrov = re.compile(
    r'<a class="genre topcharts_item_secondarygenres" href="/genre/.*?/">(?P<sekundarni_zanr>.*?)</a>,?\s?</span>'
)

vzorec_oznake = re.compile(
    r'<span class="topcharts_item_descriptors">(?P<oznaka>\w+),?\s?</span>'
)

headers = {'User-Agent': 'My User Agent 1.0'}

def ime_datoteke(st_strani):
    return f"najpopularnejsi-albumi-{st_strani}.html"

#for st_strani in range(1, 126):
#    if os.path.isfile("/analiza-podatkov/pobrani_html/najpopularnejsi-albumi-{st_strani}.html") == False:
#        url = (
#            f"https://rateyourmusic.com/charts/popular/album/all-time/exc:live,archival/{st_strani}/#results"
#        )
#        print(f"Zajemam {url}")
#        response = requests.get(url, headers=headers)
#        vsebina = response.text
#        with open(ime_datoteke(st_strani), 'w') as datoteka:
#            datoteka.write(vsebina)

najdeni_albumi = 0

#s to zanko sem si pomagala, ko sem preverila, če vzorec najde dovolj podatkov
for stran in range(1, STEVILO_STRANI + 1):
    count = STEVILO_ALBUMOV_NA_STRAN
    datoteka = f'najpopularnejsi-albumi/najpopularnejsi-albumi-{stran}.html'
    vsebina = orodja.vsebina_datoteke(datoteka)

    for zadetek in re.finditer(vzorec_albuma, vsebina):
        najdeni_albumi += 1

#print(najdeni_albumi)

#print(najdeni_albumi)
#našlo je 5000 blokov, epsko!


def doloci_zanre(niz):
    zanri = []
    for zanr in vzorec_zanrov.finditer(niz):
        zanri.append(zanr.groupdict()['zanr'])
    return zanri

def doloci_sekundarne_zanre(niz):
    sekundarni_zanri = []
    for zanr in vzorec_sekundarnih_zanrov.finditer(niz):
        sekundarni_zanri.append(zanr.groupdict()['sekundarni_zanr'])
    return sekundarni_zanri

def doloci_oznake(niz):
    oznake = []
    for oznaka in vzorec_oznake.finditer(niz):
        oznake.append(oznaka.groupdict()['oznaka'])
    return oznake

def izloci_podatke_albuma(blok):
    album = vzorec_albuma.search(blok).groupdict()
    album['mesto'] = int(album['mesto'])
    album['id'] = int(album['id'])
    album['naslov'] = album['naslov']
    album['izvajalec'] = album['izvajalec']
    datum_izdaje = vzorec_datuma_izdaje.search(blok)
    if datum_izdaje: 
        album['datum izdaje'] = datum_izdaje['datum_izdaje']
    else:
        None
    povprecna_ocena = vzorec_povprecna_ocena.search(blok)
    if povprecna_ocena:
        album['povprecna ocena'] = povprecna_ocena['povprecna_ocena']
    else:
        album['povprecna ocena'] = None
    stevilo_ocen = vzorec_stevila_ocen.search(blok)
    album['stevilo ocen'] = stevilo_ocen['stevilo_ocen'].replace(',','') if stevilo_ocen else None
    string_kritik = str(vzorec_stevila_kritik.search(blok)['stevilo_kritik'])
    album['stevilo kritik'] = int(string_kritik.replace(',', ''))
    zanri = doloci_zanre(blok)
    if zanri != []:
        album['zanri'] = ', '.join(zanri)
    else:
        album['zanri'] = None
    sekundarni_zanri = doloci_sekundarne_zanre(blok)
    if sekundarni_zanri != []:
        album['sekundarni zanri'] = ', '.join(sekundarni_zanri)
    else:
        album['sekundarni zanri'] = None
    oznake = doloci_oznake(blok)
    if oznake != []:
        album['oznake'] = ', '.join(oznake)
    else:
        album['oznake'] = None
    return album

def albumi_na_strani(stran):
    ime_dat = f'najpopularnejsi-albumi/najpopularnejsi-albumi-{stran}.html'
    vsebina = orodja.vsebina_datoteke(ime_dat)
    for blok in vzorec_bloka.finditer(vsebina):
        yield izloci_podatke_albuma(blok.group(0))  #vrne celoten match

def izloci_zanre(albumi):
    zanri = []
    for album in albumi:
        str_zanri = album['zanri']
        if str_zanri == None:
            zanri = zanri
        else:
            for zanr in str_zanri.split(", "):
                zanri.append({'album' : album['id'], 'zanr' : zanr})
            zanri.sort(key=lambda zanr : (zanr['album'], zanr['zanr']))
    return zanri

def izloci_oznake(albumi):
    oznake = []
    for album in albumi:
        str_oznake = album['oznake']
        if str_oznake == None:
            oznake = oznake
        else:
            for oznaka in str_oznake.split(", "):
                oznake.append({'album' : album['id'], 'oznaka' : oznaka})
            oznake.sort(key=lambda oznaka: (oznaka['album'], oznaka['oznaka']))
    return oznake

albumi = []
for stran in range(1, 126):
    for album in albumi_na_strani(stran):
        albumi.append(album)
albumi.sort(key=lambda album: album['mesto'])
zanri = izloci_zanre(albumi)
oznake = izloci_oznake(albumi)
orodja.zapisi_json(albumi, 'obdelani-podatki/albumi.json')
orodja.zapisi_csv(
    albumi,
    ['mesto', 'id', 'naslov', 'izvajalec', 'datum izdaje', 'povprecna ocena', 'stevilo ocen',
    'stevilo kritik', 'zanri', 'sekundarni zanri', 'oznake'],
    'obdelani-podatki/albumi.csv'
)
#če hočem te pobrat, rabim najprej 'pop'-at ven odvečne podatke
orodja.zapisi_csv(
    albumi,
    ['mesto', 'id', 'naslov', 'izvajalec', 'datum izdaje', 'povprecna ocena'],
    'obdelani-podatki/albumi-osnovno.csv'
)
orodja.zapisi_csv(zanri, ['album', 'zanr'], 'obdelani-podatki/zanri.csv')
orodja.zapisi_csv(oznake, ['album', 'oznaka'], 'obdelani-podatki/oznake.csv')