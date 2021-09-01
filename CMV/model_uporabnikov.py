import hashlib
import json
import random
import os

import model

class Uporabnik:

    def __init__(self, uporabnisko_ime, zasifrirano_geslo, nakup, stevilo_racunov=0):
        self.uporabnisko_ime = uporabnisko_ime
        self.zasifrirano_geslo = zasifrirano_geslo
        self.nakup = nakup
        self.stevilo_racunov=stevilo_racunov
    
    @staticmethod
    def prijava(uporabnisko_ime, geslo_v_cistopisu):
        uporabnik = Uporabnik.iz_datoteke(uporabnisko_ime)
        if uporabnik is None:
            raise ValueError("Uporabniško ime ne obstaja")
        elif uporabnik.preveri_geslo(geslo_v_cistopisu):
            return uporabnik        
        else:
            raise ValueError("Geslo je napačno")

    @staticmethod
    def ustvari_mapo(uporabnisko_ime):
        os.mkdir(f"uporabniki/{uporabnisko_ime}")
        os.mkdir(f"uporabniki/{uporabnisko_ime}/slike_racunov")
    
    @staticmethod
    def ime_racuna(uporabnisko_ime, indeks_racuna, koncnica):
        if koncnica[0]=='.':
            return f"uporabniki/{uporabnisko_ime}/slike_racunov/racun{indeks_racuna}{koncnica}"
        else:
            return f"uporabniki/{uporabnisko_ime}/slike_racunov/racun{indeks_racuna}.{koncnica}"

    @staticmethod
    def registracija(uporabnisko_ime, geslo_v_cistopisu):
        if Uporabnik.iz_datoteke(uporabnisko_ime) is not None:
            raise ValueError("Uporabniško ime že obstaja")
        else:
            Uporabnik.ustvari_mapo(uporabnisko_ime)
            zasifrirano_geslo = Uporabnik._zasifriraj_geslo(geslo_v_cistopisu)
            uporabnik = Uporabnik(uporabnisko_ime, zasifrirano_geslo, model.Nakup())
            uporabnik.v_datoteko()
            return uporabnik

    def _zasifriraj_geslo(geslo_v_cistopisu, sol=None):
        if sol is None:
            sol = str(random.getrandbits(32))
        posoljeno_geslo = sol + geslo_v_cistopisu
        h = hashlib.blake2b()
        h.update(posoljeno_geslo.encode(encoding="utf-8"))
        return f"{sol}${h.hexdigest()}"


    def v_slovar(self):
        return {
            "uporabnisko_ime": self.uporabnisko_ime,
            "zasifrirano_geslo": self.zasifrirano_geslo,
            "nakup": self.nakup.v_slovar(),
            "stevilo_racunov":self.stevilo_racunov
        }

    def v_datoteko(self):
        with open(
            Uporabnik.ime_uporabnikove_datoteke(self.uporabnisko_ime), "w+"
        ) as datoteka:
            json.dump(self.v_slovar(), datoteka, ensure_ascii=True, indent=4)

    def preveri_geslo(self, geslo_v_cistopisu):
        sol, _ = self.zasifrirano_geslo.split("$")
        return self.zasifrirano_geslo == Uporabnik._zasifriraj_geslo(geslo_v_cistopisu, sol)


    @staticmethod
    def ime_uporabnikove_datoteke(uporabnisko_ime):
        return f"uporabniki/{uporabnisko_ime}/{uporabnisko_ime}.json"

    @staticmethod
    def iz_slovarja(slovar):
        uporabnisko_ime = slovar["uporabnisko_ime"]
        zasifrirano_geslo = slovar["zasifrirano_geslo"]
        stevilo_racunov = slovar["stevilo_racunov"]
        nakup = model.Nakup.iz_slovarja(slovar["nakup"])
        return Uporabnik(uporabnisko_ime, zasifrirano_geslo, nakup, stevilo_racunov)

    @staticmethod
    def iz_datoteke(uporabnisko_ime):
        try:
            with open(Uporabnik.ime_uporabnikove_datoteke(uporabnisko_ime)) as datoteka:
                slovar = json.load(datoteka)
                return Uporabnik.iz_slovarja(slovar)
        except FileNotFoundError:
            return None
