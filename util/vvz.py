from .config import *
from datetime import datetime
import pymongo
import lorem 
from collections import OrderedDict

def makemodulname(modul_id):
    m = vvz_modul.find_one({"_id": modul_id})
    s = ", ".join([x["kurzname"] for x in list(vvz_studiengang.find({"_id": { "$in" : m["studiengang"]}}))])
    return f"{m['name_de']} ({s})"

def makeanforderungname(anforderung_id):
    a = vvz_anforderung.find_one({"_id": anforderung_id})
    k = vvz_anforderungkategorie.find_one({ "_id": a["anforderungskategorie"]})["name_de"]
    return f"{a['name_de']} ({k})"

# Die Funktion fasst zB Mo, 8-10, HS Rundbau, Albertstr. 21 \n Mi, 8-10, HS Rundbau, Albertstr. 21 \n 
# zusammen in
# Mo, Mi, 8-10, HS Rundbau, Albertstr. 21 \n Mi, 8-10, HS Rundbau, Albertstr. 21
def make_zeitraum(veranstaltung):
    res = []
    for termin in veranstaltung["woechentlicher_termin"]:
        if termin['wochentag'] !="":
            # key, raum, zeit, person, kommentar
            key = termin['key'] if termin['key'] != "" else "Raum und Zeit"
            # Raum und Gebäude mit Url, zB Hs II.
            r = vvz_raum.find_one({ "_id": termin["raum"]})
            g = vvz_gebaeude.find_one({ "_id": r["gebaeude"]})
            if g["url"] == "":
                raum = ", ".join([r["name_de"], g["name_de"]])
            else:
                raum = ", ".join([r['name_de'], f"\href{{{g['url']}}}{{{g['name_de']}}}"])
            # zB Vorlesung: Montag, 8-10, HSII, Albertstr. 23a
            zeit = f"{str(termin['start'].hour)}{': '+str(termin['start'].minute) if termin['start'].minute > 0 else ""}--{str(termin['ende'].hour)}{': '+str(termin['ende'].minute) if termin['ende'].minute > 0 else ""}"
            # zB Mo, 8-10
            tag = weekday[termin['wochentag']]
            # person braucht man, wenn wir dann die Datenbank geupdated haben.
            person = ", ".join([f"{vvz_person.find_one({"_id": x})["vorname"]} {vvz_person.find_one({"_id": x})["name"]}"for x in termin["person"]])
            kommentar = rf"\newline{termin["kommentar"]}" if termin["kommentar"] != "" else ""
            new = [key, tag, zeit, raum, person, kommentar]
            if key in [x[0] for x in res]:
                new.pop(0)
                i = [x[0] for x in res].index(key)
                res[i] = (res[i] + new)
                res[i].reverse()
                res[i] = list(OrderedDict.fromkeys(res[i]))
                res[i].reverse()
            else:
                res.append(new)
    for termin in veranstaltung["einmaliger_termin"]:
        if termin['key'] !="":
            # Raum und Gebäude mit Url.
            r = vvz_raum.find_one({ "_id": termin["raum"]})
            g = vvz_gebaeude.find_one({ "_id": r["gebaeude"]})
            if g["url"] == "":
                raum = ", ".join([r["name_de"], g["name_de"]])
            else:
                raum = ", ".join([r['name_de'], f"\href{{{g['url']}}}{{{g['name_de']}}}"])
            # zB Vorlesung: Montag, 8-10, HSII, Albertstr. 23a
            startdatum = termin['startdatum'].strftime("%d.%m.")
            if termin['startdatum'] != termin['enddatum']:
                enddatum = termin['enddatum'].strftime("%d.%m.")
                datum = " bis ".join([startdatum, enddatum])
            else:
                datum = startdatum
            if termin['startzeit'] is not None:
                zeit = f"{str(termin['startzeit'].hour)}{': '+str(termin['startzeit'].minute) if termin['startzeit'].minute > 0 else ""}--{str(termin['endzeit'].hour)}{': '+str(termin['endzeit'].minute) if termin['endzeit'].minute > 0 else ""}"
            else:
                zeit = ""
            # person braucht man, wenn wir dann die Datenbank geupdated haben.
            person = ", ".join([f"{vvz_person.find_one({"_id": x})["vorname"]} {vvz_person.find_one({"_id": x})["name"]}"for x in termin["person"]])
            kommentar = rf"\newline{termin["kommentar"]}" if termin["kommentar"] != "" else ""
            new = [key, datum, zeit, raum, person, kommentar]
            res.append(new)
    res = [f"{x[0]}: {(', '.join([z for z in x if z !='' and x.index(z)!=0]))}" for x in res]
    return res

cluster = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mongo_db_vvz = cluster["vvz"]

vvz_anforderung = mongo_db_vvz["anforderung"]
vvz_anforderungkategorie = mongo_db_vvz["anforderungkategorie"]
vvz_code = mongo_db_vvz["code"]
vvz_gebaeude = mongo_db_vvz["gebaeude"]
vvz_rubrik = mongo_db_vvz["rubrik"]
vvz_modul = mongo_db_vvz["modul"]
vvz_person = mongo_db_vvz["person"]
vvz_raum = mongo_db_vvz["raum"]
vvz_semester = mongo_db_vvz["semester"]
vvz_studiengang = mongo_db_vvz["studiengang"]
vvz_veranstaltung = mongo_db_vvz["veranstaltung"]

def makedata(sem_shortname):
    sem_id = vvz_semester.find_one({"kurzname": sem_shortname})["_id"]

    rubriken = list(vvz_rubrik.find({"semester": sem_id, "hp_sichtbar": True}, sort=[("rang", pymongo.ASCENDING)]))

    data = {}
    data["rubriken"] = []

    for rubrik in rubriken:
        r_dict = {}
        r_dict["titel"] = rubrik["titel_de"]
        r_dict["veranstaltung"] = []
        veranstaltungen = list(vvz_veranstaltung.find({"rubrik": rubrik["_id"]}))
        # This for-loop needs to be commented out once the content is there!
        for veranstaltung in veranstaltungen:        
            vvz_veranstaltung.update_one({"_id": veranstaltung["_id"]}, { "$set": {"inhalt_de": lorem.paragraph(), "literatur_de": lorem.sentence(), "vorkenntnisse_de": lorem.sentence(), "kommentar_latex": lorem.sentence()}})
        veranstaltungen = list(vvz_veranstaltung.find({"rubrik": rubrik["_id"]}))
        for veranstaltung in veranstaltungen:
            v_dict = {}
            v_dict["titel"] = veranstaltung["name_de"]
            v_dict["dozent"] = ", ".join([f"{vvz_person.find_one({"_id": x})["vorname"]} {vvz_person.find_one({"_id": x})["name"]}"for x in veranstaltung["dozent"]])

            assistent = ", ".join([f"{vvz_person.find_one({"_id": x})["vorname"]} {vvz_person.find_one({"_id": x})["name"]}"for x in veranstaltung["assistent"]])
            if assistent:
                v_dict["person"] = ", Assistenz: ".join([v_dict["dozent"], assistent])
            else:
                v_dict["person"] = v_dict["dozent"]
            # raumzeit ist der Text, der unter der Veranstaltung im kommentierten VVZ steht.
            v_dict["raumzeit"] = make_zeitraum(veranstaltung)
            v_dict["inhalt"] = veranstaltung["inhalt_de"]
            v_dict["literatur"] = veranstaltung["literatur_de"]
            v_dict["vorkenntnisse"] = r"Man erhält so leicht, dass $x_{1/2} = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$" # veranstaltung["vorkenntnisse_de"]
            v_dict["kommentar"] = veranstaltung["kommentar_latex_de"]
            v_dict["verwendbarkeit_modul"] = [{"id": str(x), "titel": makemodulname(x)} for x in veranstaltung["verwendbarkeit_modul"]]
            v_dict["verwendbarkeit_anforderung"] = [{"id": str(x), "titel": makeanforderungname(x)} for x in veranstaltung["verwendbarkeit_anforderung"]]
            v_dict["verwendbarkeit"] = [{"modul": str(x["modul"]), "anforderung": str(x["anforderung"])} for x in veranstaltung["verwendbarkeit"]]
            r_dict["veranstaltung"].append(v_dict)

        data["rubriken"].append(r_dict)
    return data

# Für die Kommentare:
# Momentan gibt es so etwas wie: '4-stündige Vorlesung mit 2-stündiger Übung' oder 'Vorlesung mit Praktischer Übung', was jeweils direkt unter der Veranstaltung selbst steht. Ist das wichtig (dann muss es als Feld ins vvz) oder nicht?
# Ein wöchentlicher Termin wird nur dann angezeigt wenn er einen Wochentag hat. Wenn er einen Wochentag hat, wird davon ausgegangen, dass er auch eine Uhrzeit hat.
# 8:00 wird als 8 ausgegeben, aber 8:15 als 8:15. 
# Braucht einmaliger_termin noch eine true/false-Variable, je nachdem ob er in den Kommentaren auftauchen soll? 

