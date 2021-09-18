from model import Nakup, Nakup_zivila, Zivilo, preveri_maso
import bottle
import os

from bralnik import dobi_besedilo, dovoljeni_formati
from model_uporabnikov import Uporabnik

PISKOTEK_UPORABNISKO_IME = "uporabnisko_ime"
SKRIVNOST = "to ni nobena skrivnost"


def shrani_stanje(uporabnik):
    uporabnik.v_datoteko()

# pomožna funkcija za preverjanje piškotka


def trenutno_uporabnisko_ime():
    return bottle.request.get_cookie(
        PISKOTEK_UPORABNISKO_IME, secret=SKRIVNOST
    )


def trenutni_uporabnik():
    uporabnisko_ime = trenutno_uporabnisko_ime()
    if uporabnisko_ime:
        return podatki_uporabnika(uporabnisko_ime)
    else:
        bottle.redirect("/prijava/")


def podatki_uporabnika(uporabnisko_ime):
    return Uporabnik.iz_datoteke(uporabnisko_ime)

# povej kje so slike


@bottle.get("/img/<picture>")
def slike(picture):
    return bottle.static_file(picture, "img")


@bottle.get("/")
def zacetna_stran():
    if trenutno_uporabnisko_ime() is not None:
        bottle.redirect("/seznam/")
    else:
        return bottle.template("zacetna_stran.html")


@bottle.get("/registracija/")
def registracija_get():
    return bottle.template("registracija.html", napaka=None)


MINIMALNA_DOLZINA_GESLA = 4


@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    ponovljeno_geslo_v_cistopisu = bottle.request.forms.getunicode(
        "ponovljeno_geslo")

    if not uporabnisko_ime:
        return bottle.template(
            "registracija.html",
            napaka="Vnesi uporabniško ime!")

    # preveri dolžino
    if len(geslo_v_cistopisu) < MINIMALNA_DOLZINA_GESLA:
        return bottle.template(
            "registracija.html",
            napaka=f"Geslo ni ustrezno! Dolgo naj bo vsaj {MINIMALNA_DOLZINA_GESLA} znake.")

    # preveri da se gesli ujemata
    if ponovljeno_geslo_v_cistopisu != geslo_v_cistopisu:
        return bottle.template(
            "registracija.html",
            napaka="Gesli se ne ujemata!")

    try:
        Uporabnik.registracija(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(
            PISKOTEK_UPORABNISKO_IME,
            uporabnisko_ime,
            path="/",
            secret=SKRIVNOST)
        bottle.redirect("/seznam/")
    except ValueError as e:
        return bottle.template(
            "registracija.html", napaka=e.args[0]
        )


@bottle.get("/prijava/")
def prijava_get():
    if trenutno_uporabnisko_ime() is not None:
        bottle.redirect("/seznam/")
    else:
        return bottle.template("prijava.html", napaka=None)


@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template(
            "registracija.html",
            napaka="Vnesi uporabniško ime!")
    try:
        Uporabnik.prijava(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(
            PISKOTEK_UPORABNISKO_IME,
            uporabnisko_ime,
            path="/",
            secret=SKRIVNOST)
        bottle.redirect("/seznam/")
    except ValueError as e:
        return bottle.template(
            "prijava.html", napaka=e.args[0]
        )


@bottle.get("/odjava/")
def odjava():
    uporabnik = trenutni_uporabnik()
    if uporabnik is not None:
        bottle.response.delete_cookie(PISKOTEK_UPORABNISKO_IME, path="/")

    bottle.redirect("/prijava/")


@bottle.get("/seznam/")
def seznam():
    uporabnik = trenutni_uporabnik()
    return bottle.template(
        "seznam.html", nakup=uporabnik.nakup, uporabnik=uporabnik, napaka=None
    )


@bottle.get("/dodaj_racun/")
def dodaj_racun_get():
    trenutni_uporabnik()
    return bottle.template("dodaj_racun.html", napaka=None, sporocilo=None)


@bottle.post("/dodaj_racun/")
def dodaj_racun_post():
    uporabnik = trenutni_uporabnik()

    # dobi datoteko
    nalozeno = bottle.request.files.get('nalozeno')
    ime, koncnica = os.path.splitext(nalozeno.filename)

    # preglej ali je v pravem formatu
    if koncnica not in dovoljeni_formati:
        return bottle.template(
            "dodaj_racun.html",
            napaka=f"Slika naj bo v formatu/ih {str(dovoljeni_formati)}.",
            sporocilo=None)

    # dobi ime datoteke v katero bomo shranili, računi so oštevilčeni z 0
    # naprej.
    pot = uporabnik.ime_racuna(
        uporabnik.uporabnisko_ime,
        uporabnik.stevilo_racunov,
        koncnica)

    try:
        nalozeno.save(pot)
    except ValueError as e:
        return bottle.template(
            "dodaj_racun.html", napaka=e.args[0], sporocilo=None
        )

    # preberi račun
    prebran_racun = dobi_besedilo(pot)
    # povečaj števec računov v primeru, da ni napak
    uporabnik.stevilo_racunov += 1

    # dodaj prepoznana živila v skupen nakup uporabnik
    dodaj_najdeno = Nakup.nakup_iz_vrstic(prebran_racun)
    uporabnik.nakup += dodaj_najdeno
    shrani_stanje(uporabnik)

    return bottle.template(
        "dodaj_racun.html",
        napaka=None,
        sporocilo=f"Slika uspešno naložena! Dodanih je bilo {len(dodaj_najdeno.nakupljena_zivila)} nakupljenih zivil.")


@bottle.get("/odstrani_nakupljeno/")
def odstrani_nakupljeno():
    uporabnik = trenutni_uporabnik()

    # v seznamu so izdelki oštevilčeni
    # POZOR: možna napaka če ima uporabnik odprtih več različic seznama
    id = int(bottle.request.query.id)

    # napako lahko ustavimo, a še vedno obstaja možnost, da zbrišemo napačen
    # izdelek
    if id < len(uporabnik.nakup.nakupljena_zivila):
        uporabnik.nakup.odstrani(id)
        shrani_stanje(uporabnik)
    else:
        return bottle.template(
            "seznam.html",
            nakup=uporabnik.nakup,
            uporabnik=uporabnik,
            napaka="Nekaj je šlo narobe pri odstranjevanju izdelka.")

    bottle.redirect('/seznam/')


@bottle.get("/dodaj_nakup_zivila/")
def dodaj_nakup_zivila():
    uporabnik = trenutni_uporabnik()

    # dobi izbrano iz "select"
    izbrano_zivilo = Zivilo.dobi_zivilo_iz_imena(
        bottle.request.query.getunicode("izbrano_zivilo"))

    masa = bottle.request.query.getunicode("masa")

    # preveri maso

    if masa.isnumeric() and preveri_maso(int(masa)):
        masa = int(masa)
        uporabnik.nakup += Nakup_zivila(izbrano_zivilo, masa)
        shrani_stanje(uporabnik)
        bottle.redirect('/seznam/')
    elif masa == "":
        uporabnik.nakup += Nakup_zivila(izbrano_zivilo)
        shrani_stanje(uporabnik)
        bottle.redirect('/seznam/')
    else:
        return bottle.template("seznam.html",
                               nakup=uporabnik.nakup,
                               uporabnik=uporabnik,
                               napaka="Masa naj bo pozitivno celo število.")


if __name__ == '__main__':
    bottle.run(host="0.0.0.0", port="8080")
