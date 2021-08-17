import bottle
import os
from model_uporabnikov import Uporabnik

PISKOTEK_UPORABNISKO_IME = "uporabnisko_ime"
SKRIVNOST = "to ni nobena skrivnost"

def shrani_stanje(uporabnik):
    uporabnik.v_datoteko()


def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie(
        PISKOTEK_UPORABNISKO_IME, secret=SKRIVNOST
    )
    if uporabnisko_ime:
        return podatki_uporabnika(uporabnisko_ime)
    else:
        bottle.redirect("/prijava/")


def podatki_uporabnika(uporabnisko_ime):
    return Uporabnik.iz_datoteke(uporabnisko_ime)


@bottle.get("/")
def zacetna_stran():
    bottle.redirect("/seznam/")


@bottle.get("/registracija/")
def registracija_get():
    return bottle.template("registracija.html", napaka=None)


@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!")
    try:
        Uporabnik.registracija(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(
            PISKOTEK_UPORABNISKO_IME, uporabnisko_ime, path="/", secret=SKRIVNOST
        )
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template(
            "registracija.html", napaka=e.args[0]
        )


@bottle.get("/prijava/")
def prijava_get():
    return bottle.template("prijava.html", napaka=None)


@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!")
    try:
        Uporabnik.prijava(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(
            PISKOTEK_UPORABNISKO_IME, uporabnisko_ime, path="/", secret=SKRIVNOST
        )
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template(
            "prijava.html", napaka=e.args[0]
        )

@bottle.post("/odjava/")
def odjava():
    bottle.response.delete_cookie(PISKOTEK_UPORABNISKO_IME, path="/")
    bottle.redirect("/")

@bottle.get("/seznam/")
def seznam():
    uporabnik=trenutni_uporabnik()
    return bottle.template(
        "seznam.html",nakup=uporabnik.nakup, uporabnik=uporabnik
    )

@bottle.get("/dodaj_racun/")
def dodaj_racun_get():
    trenutni_uporabnik()
    return bottle.template("dodaj_racun.html", napaka=None, sporocilo=None)

@bottle.post("/dodaj_racun/")
def dodaj_racun_post():
    uporabnik=trenutni_uporabnik()

    nalozeno = bottle.request.files.get('nalozeno')
    ime, koncnica = os.path.splitext(nalozeno.filename)

    print(koncnica)
    if koncnica not in ('.png', '.jpg', '.jpeg'):
        return bottle.template("dodaj_racun.html", napaka="Slika naj bo v formatu 'png', 'jpg' ali 'jpeg'.", sporocilo=None)

    pot = uporabnik.ime_racuna(uporabnik.uporabnisko_ime, uporabnik.stevilo_racunov, koncnica)
    uporabnik.stevilo_racunov+=1

    nalozeno.save(pot)

    return bottle.template("dodaj_racun.html", napaka=None, sporocilo="Slika uspešno naložena!")


if __name__ == '__main__':
    bottle.run(host="localhost", port="8080", reloader=True, debug=True)

