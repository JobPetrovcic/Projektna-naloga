# -*- coding: utf8 -*-
import json

MAKSIMALEN_ROK=10 * 365
MAKSIMALNA_MASA=10000
NI_DEFINIRANO="-----"
IME_DATOTEKE="C:/Users/job1p/Desktop/Projektna-naloga/model/vsa_zivila.txt"

def preveri_cas_uporabe(cas_uporabe):
    if( isinstance(cas_uporabe, int)):
        if( cas_uporabe>0 and cas_uporabe <= MAKSIMALEN_ROK):
                return True
        else:
            raise ValueError("Cas uporabe je negativen, nič ali pa presega maksimalen rok.")
    else:
        raise ValueError("Cas_uporabe ni število.")
def preveri_maso(masa):
    if masa == NI_DEFINIRANO:
        return True
    if isinstance(masa, int):
        if(masa>0 and masa<=MAKSIMALNA_MASA):
            return True
        else:
            raise ValueError("Masa je negativno število, nič ali pa presega maksimalno maso.")
    else:
        raise ValueError("Masa ni ustreznega tipa (NI_DEFINIRANO ali pa stevilo).")

tip_zivila={
    "svež": 3,
    "mlečni izdelek in jajca": 3 * 7,
    "suh": 365 * 2,
    "pijača": 365 * 1,
    "konzervirana hrana" : 365 * 5,
    "zamrznjen izdelek" : 6 * 30,
    "ostalo": NI_DEFINIRANO,
}

class Zivilo:
    zivila=[]

    def __init__(self, ime, kljucne_besede=None, tip="ostalo", cas_uporabe=NI_DEFINIRANO):
        #Preveri ali je tip zivila ime.
        if isinstance(ime, str):
            self.ime=ime
        else:
            raise ValueError("Ime zivila ni niz.")

        #Dodaj tip zivila
        if tip in tip_zivila:
            self.tip=tip
            self.cas_uporabe=tip_zivila[tip]
        else:
            raise ValueError("Ta tip zivila ne obstaja.")

        #Posamezna zivila nekega tipa imajo lahko različen cas uporabe kot tip katerega so. 
        if cas_uporabe != NI_DEFINIRANO:
            if preveri_cas_uporabe(cas_uporabe):
                self.cas_uporabe=cas_uporabe


        if kljucne_besede is None:
            kljucne_besede=[]
        else:
            self.kljucne_besede=[]
            if isinstance(kljucne_besede, list):
                if all([isinstance(beseda, str) for beseda in kljucne_besede]):
                    for beseda in kljucne_besede:
                        self.kljucne_besede+=[beseda.lower()]
                else:
                    raise ValueError("Neka kljucna beseda ni niz.")
            else:
                raise ValueError("Kljucne besede niso seznam.")

        #Dodaj v staticen seznam vseh zivil.
        Zivilo.zivila+=[self]
        Zivilo.nalozi_v_datoteko()

    def __str__(self):
        return f'{self.ime} je tipa {self.tip} in ima cas uporabe {self.cas_uporabe} dni. Najdemo ga po besed -i/-ah {self.kljucne_besede}'

    def dodaj_kljucno_besedo(self, beseda):
        if isinstance(beseda, str):
            self.kljucne_besede+=[beseda]
        else:
            raise ValueError("Kljucna beseda ni niz.")

    def je_to_zivilo(self, niz):
        if isinstance(niz, str):
            for kljucna_beseda in self.kljucne_besede:
                if kljucna_beseda not in niz:
                    return False
            return True
        else:
            raise ValueError("Obdelovan podatek ni niz pri izvajanju funkcije je_to_zivilo.")

    def v_slovar( self):
        return {
            "ime" : self.ime,
            "kljucne_besede" : self.kljucne_besede,
            "tip" : self.tip,
            "cas_uporabe" : self.cas_uporabe
        }
    @classmethod
    def iz_slovarja(cls, slovar):
        return cls(slovar["ime"], slovar["kljucne_besede"], slovar["tip"], slovar["cas_uporabe"])


    @classmethod
    def nalozi_v_datoteko(cls, ime_datoteke=IME_DATOTEKE):
        with open(ime_datoteke, "w") as datoteka:
            slovarji =[]
            for zivilo in cls.zivila:
                slovarji+=[zivilo.v_slovar()]
            json.dump(slovarji, datoteka, ensure_ascii=True, indent=4)

    @classmethod
    def nalozi_iz_datoteke(cls, ime_datoteke=IME_DATOTEKE):
        with open(ime_datoteke) as datoteka:
            slovarji = json.load(datoteka)
            for slovar in slovarji:
                cls.iz_slovarja(slovar)
    @classmethod
    def izpisi_vsa(cls):
        for zivilo in Zivilo.zivila:
            print(zivilo)


Zivilo.nalozi_iz_datoteke()
