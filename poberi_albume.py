import requests
import os.path
import re

vzorec_bloka = re.compile(
    r'<div id="pos.*?">\s*</div>\s*</div>',
    flags=re.DOTALL
)

vzorec_albuma = re.compile(
    r'<div class="topcharts_position">(?P<mesto>\d+)<span class="topcharts_position_desktop">.*?'
    r'<div class="topcharts_item_title"><a href="(?P<povezava>.*?)" '
    r'class="release" title="[Album\d+]">(?P<Album>.*?)</a></div>.*?'
    r'class="artist">(?P<Izvajalec>.*?)</a></div>'
)

def ime_datoteke(st_strani):
    return f"najpopularnejsi-albumi-{st_strani}.html"

for st_strani in range(1, 126):
    if os.path.isfile("/analiza-podatkov/najpopularnejsi-albumi-{st_strani}.html") == False:
        url = (
            f"https://rateyourmusic.com/charts/popular/album/all-time/exc:live,archival/{st_strani}/#results"
        )
        print(f"Zajemam {url}")
        response = requests.get(url)
        vsebina = response.text
        with open(ime_datoteke(st_strani), 'w') as datoteka:
            datoteka.write(vsebina)
