# -*- coding: utf8 -*-
import json

MAKSIMALEN_ROK=10 * 365
MAKSIMALNA_MASA=9999
NI_DEFINIRANO="-----"

def preveri_cas_uporabe(cas_uporabe):
    if( isinstance(cas_uporabe, int)):
        if( cas_uporabe>0 and cas_uporabe <= MAKSIMALEN_ROK):
                return True
        else:
            raise ValueError("Cas uporabe je negativen, nič ali pa presega maksimalen rok.")
    else:
        raise ValueError("Cas_uporabe ni število.")
def preveri_maso(masa):
    #preveri da je masa pozitivno celo število in je manjša ali enaka omejitvi
    if masa == NI_DEFINIRANO:
        return True
    if isinstance(masa, int):
        if(masa>0 and masa<=MAKSIMALNA_MASA):
            return True
        else:
            return False
    else:
        return False

tip_zivila={
    "svež izdelek": 3,
    "mlečni izdelek in jajca": 3 * 7,
    "suh izdelek": 365 * 2,
    "pijača": 365 * 1,
    "konzervirana hrana" : 365 * 5,
    "zamrznjen izdelek" : 6 * 30,
    "ostalo": NI_DEFINIRANO,
}
#Zivilo je podatkovna baza. Hrani imena zivil v staticni spremenljivki "Zivilo.zivila" . V bazi je za vsako zivilo nekaj kljucnih besed po kateri prepoznamo. Npr. za pšenično moko sta potrebni besedi "pše" in "moka". Namreč na računih je pogosto prisotno krajšanje besed, saj je prostor omejen. Potrebno je previdno izbiranje krajših ključnih besed, saj obstaja možnost napačnega identificiranja živil iz niza (iz računa).
class Zivilo:
    VSA_ZIVILA="vsa_zivila.txt"
    zivila=[]

    def __init__(self, ime, kljucne_besede=None, tip="ostalo", cas_uporabe=NI_DEFINIRANO):
        if isinstance(ime, str):
            self.ime=ime
        else:
            raise ValueError("Ime zivila ni niz.")

        #Preveri ali tip zivila obstaja in ga shrani kot atribut
        if tip in tip_zivila:
            self.tip=tip
            self.cas_uporabe=tip_zivila[tip]
        else:
            raise ValueError("Tip zivila {tip} ne obstaja.")

        #Posamezna zivila nekega tipa imajo lahko različen cas uporabe kot tip katerega so. 
        if cas_uporabe != NI_DEFINIRANO:
            if preveri_cas_uporabe(cas_uporabe):
                self.cas_uporabe=cas_uporabe


        if kljucne_besede is None:
            self.kljucne_besede=[]
        else:
            self.kljucne_besede=[]
            #preveri da so kljucne besede res seznam nizev
            if isinstance(kljucne_besede, list):
                if all([isinstance(beseda, str) for beseda in kljucne_besede]):
                    for beseda in kljucne_besede:
                        self.kljucne_besede+=[beseda.lower()]
                else:
                    raise ValueError("Neka kljucna beseda ni niz.")
            else:
                raise ValueError("Kljucne besede niso seznam.")
    
    def __eq__(self, other):
        if isinstance(other,Zivilo):
            return (self.ime==other.ime and 
            self.kljucne_besede==other.kljucne_besede and 
            self.tip==other.tip and 
            self.cas_uporabe==other.cas_uporabe)
        else:
            return False

    def __str__(self):
        return f'{self.ime} je tipa {self.tip} in ima cas uporabe {self.cas_uporabe} dni. Najdemo ga po besed -i/-ah {self.kljucne_besede}'

    def dodaj_kljucno_besedo(self, beseda):
        if isinstance(beseda, str):
            self.kljucne_besede+=[beseda]
        else:
            raise ValueError("Ključna beseda ni niz.")

    def je_to_zivilo(self, niz):
        if isinstance(niz, str):
            for kljucna_beseda in self.kljucne_besede:
                if kljucna_beseda not in niz:
                    return False
            return True
        else:
            raise ValueError("Obdelovan podatek ni niz pri izvajanju funkcije je_to_zivilo.")

    def v_slovar(self):
        return {
            "ime" : self.ime,
            "kljucne_besede" : self.kljucne_besede,
            "tip" : self.tip,
            "cas_uporabe" : self.cas_uporabe
        }
    @staticmethod
    def iz_slovarja(slovar):
        return Zivilo(slovar["ime"], 
        slovar["kljucne_besede"], 
        slovar["tip"], 
        slovar["cas_uporabe"])

    @staticmethod
    def dobi_zivilo_iz_imena(ime):
        for zivilo in Zivilo.zivila:
            if zivilo.ime==ime:
                return zivilo
        
        raise ValueError(f"Ime '{ime}' ne ustreza nobenemu živilu v bazi.")

    @classmethod
    def nalozi_v_datoteko(cls, ime_datoteke=VSA_ZIVILA):
        with open(ime_datoteke, "w") as datoteka:
            slovarji =[]
            for zivilo in cls.zivila:
                slovarji+=[zivilo.v_slovar()]
            json.dump(slovarji, datoteka, ensure_ascii=True, indent=4)

    @classmethod
    def nalozi_iz_datoteke(cls, ime_datoteke=VSA_ZIVILA):
        with open(ime_datoteke) as datoteka:
            slovarji = json.load(datoteka)
            for slovar in slovarji:
                cls.iz_slovarja(slovar)

#ob zagonu nalozi podatke iz vsa_zivila.txt
Zivilo.nalozi_iz_datoteke()

############################################################

import datetime

NI_V_BAZI="ni najden v bazi"

#Nakup_zivila hrani maso in datum nakupa. Na podlagi tipa zivila izracuna se rok uporabe. Omogoča pretvorbo v slovar(in nazaj).
class Nakup_zivila:
    def __init__(self, zivilo, masa=NI_DEFINIRANO, datum_nakupa=NI_DEFINIRANO, datum_roka=NI_DEFINIRANO):
        if isinstance(zivilo, Zivilo):
            self.zivilo=zivilo
        else:
            raise ValueError("zivilo ni primer razreda Zivilo.")

        #dodaj maso ce ustreza kriterijem
        if preveri_maso(masa):
            self.masa=masa
        else:
            self.masa=NI_DEFINIRANO

        #dodaj datum roka in datuma nakupa ce sta definirana drugače vzemi današnji datum za datum nakupa in mu prištej rok uporabe za datum roka
        if datum_nakupa == NI_DEFINIRANO:
            self.datum_nakupa=datetime.datetime.now().date()
        else:
            if isinstance(datum_nakupa, datetime.date):
                self.datum_nakupa=datum_nakupa
            else:
                raise ValueError("datum_nakupa ni primer razreda datetime.date.")

        if datum_roka == NI_DEFINIRANO:
            self.datum_roka=self.datum_nakupa + datetime.timedelta(days=self.zivilo.cas_uporabe)
        else:
            if isinstance(datum_nakupa, datetime.date):
                self.datum_roka=datum_roka
            else:
                raise ValueError("datum_nakupa ni primer razreda datetime.date.")    
    
    def __eq__(self, other):
        if isinstance(other, Nakup_zivila):
            return (self.zivilo==other.zivilo and
            self.masa==other.masa and
            self.datum_nakupa==other.datum_nakupa and
            self.datum_roka==other.datum_roka)
        else:
            return False

    #preveri ali je pretecena hrana
    def preteceno(self):
        danes=datetime.datetime.now().date()
        return self.datum_roka < danes

    def v_slovar(self):
        return {
            "zivilo": self.zivilo.v_slovar(),
            "masa": self.masa,
            "datum_nakupa": self.datum_nakupa.isoformat(), 
            "datum_roka": self.datum_roka.isoformat()
        }
    
    @staticmethod
    def iz_slovarja(slovar):
        return Nakup_zivila(Zivilo.iz_slovarja(slovar["zivilo"]), 
        slovar["masa"], 
        datetime.date.fromisoformat(slovar["datum_nakupa"]), 
        datetime.date.fromisoformat(slovar["datum_roka"]))

    def __lt__(self, other):
        return self.datum_roka>other.datum_roka

#Importaj regex za iskanje mase oblike:  številka + "g|G"
import re
def najdi_maso(niz):
    if isinstance(niz, str):
        #iščemo podniz oblike številka +"g"
        rezultat=re.search("[0-9]{1,4}(g|G)", niz)
        if rezultat is not None:
            #ce obstaja masa jo pretvori v int
            levi, desni=rezultat.span()
            masa=int(niz[levi : (desni-1)])
            return masa

        #iščemo podniz oblike številka +"kg"
        rezultat=re.search("[0-9,.]{1,4}(kg|KG|Kg|kG)", niz)
        if rezultat is not None:
            levi, desni=rezultat.span()
            masa_niz=niz[levi : (desni-2)]
            try:
                masa=float(masa_niz)
                #pomnoži s 1000, ker hranimo maso v gramih
                masa*=1000
                return int(masa)
            except:
                pass
                 
        return NI_DEFINIRANO
    else:
        raise ValueError("Argument posredovan funkciji najdi_maso ni niz.")

# gre čez vsa živila in pogleda ali ustreza. Pomankljivost je slaba časovna zahtevnost O(len(Zivilo.zivila))
def nakup_zivila_iz_niza(niz):
    if isinstance(niz, str):
        #gre čez vsa živila v podatkovni bazi in preveri ali so vse ključne besede vsebovane v nizu
        for zivilo in Zivilo.zivila:
            #vzame prvega ki ga najde
            if zivilo.je_to_zivilo(niz):
                masa=najdi_maso(niz)
                if preveri_maso(masa):
                    return Nakup_zivila(zivilo, masa)
                else:
                    Nakup_zivila(zivilo)
        
        #če ne ustreza nobenemu
        return NI_V_BAZI
    else:
        raise ValueError("Argument posredovan funkciji nakup_iz_niza ni niz.")

############################################################
#Hrani seznam nakupljenih živil  in pa kdaj se je ta nakup zgodil (predvideva kar trenuten datum). Omogoča pretvorbo v slovar (in nazaj).
class Nakup:
    def __init__(self, nakupljena_zivila=None, datum_ustvarjanja=NI_DEFINIRANO):
        if nakupljena_zivila is None:
            self.nakupljena_zivila=[]
        elif isinstance(nakupljena_zivila, list):
            if all([isinstance(nakupljeno_zivilo, Nakup_zivila) for nakupljeno_zivilo in nakupljena_zivila]):
                self.nakupljena_zivila=nakupljena_zivila
            else:
                raise ValueError("Seznam nakupljenih števil vsebuje element, ki ni primer razreda Nakup_zivila")
        else:
            raise ValueError("Nakupljena zivila niso seznam ali None pri ustvarjanju Nakup-a.")
        
        if datum_ustvarjanja == NI_DEFINIRANO:
            self.datum_ustvarjanja=datetime.datetime.now().date()
        else:
            if isinstance(datum_ustvarjanja, datetime.date):
                self.datum_ustvarjanja=datum_ustvarjanja
            else:
                raise ValueError("datum_ustvarjanja je definiran ampak ni primer razred datime.date.")
    
    def odstrani(self, izbrano):
        #izbrano je indeks nakupljenega živila
        if len(self.nakupljena_zivila)>izbrano:
            self.nakupljena_zivila.pop(izbrano)
        else:
            raise ValueError(f"Seznam ne vsebuje elementa {izbrano}.")

    def v_slovar(self):
        nakupljena_zivila_v_slovar=[]
        for nakupljeno_zivilo in self.nakupljena_zivila:
            nakupljena_zivila_v_slovar+=[nakupljeno_zivilo.v_slovar()]

        return {
            "nakupljena_zivila": nakupljena_zivila_v_slovar, 
            "datum_ustvarjanja": self.datum_ustvarjanja.isoformat() #datum pretvorimo v isoformat za shranjevanje v besedilo
        }
    
    @staticmethod
    def iz_slovarja(slovar):
        nakupljena_zivila_iz_slovarja=[]
        for nakupljeno_zivilo_v_slovar in slovar["nakupljena_zivila"]:
            nakupljena_zivila_iz_slovarja+=[Nakup_zivila.iz_slovarja(nakupljeno_zivilo_v_slovar)]
        
        return Nakup(nakupljena_zivila_iz_slovarja, datetime.date.fromisoformat(slovar["datum_ustvarjanja"]))

    #definiramo seštevanje dveh nakupov za lažje obdelovanje
    def __add__(self, other):
        if isinstance(other, Nakup_zivila):
            return Nakup(self.nakupljena_zivila + [other], self.datum_ustvarjanja)
        elif isinstance(other, Nakup):
            nov_datum=min(self.datum_ustvarjanja, other.datum_ustvarjanja)
            return Nakup(self.nakupljena_zivila + other.nakupljena_zivila, nov_datum)
        else:
            return self

#na seznamu nizov izvede nakup_zivila_iz_niza
def nakup_iz_vrstic(vrstice):
    nakupljena_zivila=[]
    for vrstica in vrstice:
        mozen_nakup_zivila=nakup_zivila_iz_niza(vrstica)
        if mozen_nakup_zivila != NI_V_BAZI:
            nakupljena_zivila+=[mozen_nakup_zivila]

    return Nakup(nakupljena_zivila)