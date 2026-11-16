from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO
from model.prezzo_DTO import Prezzo

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultato =[]
        for distributore in self._distributori:
            prezzi_mese=[]

            prezzi = distributore.get_prezzi()

            for prezzo in prezzi:
                if prezzo.data.month == mese:
                    prezzi_mese.append(prezzo.prezzo_litro)

            if len(prezzi_mese) !=0 :
                prezzo_totale =0
                for prezzo in prezzi_mese:
                    prezzo_totale += prezzo

                prezzo_medio_mese= prezzo_totale / len(prezzi_mese)
                risultato.append((distributore.nome, prezzo_medio_mese))

            if len(risultato) == 0:
                return None

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """

        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:#controllo se il costo è ancora -1 (quindi ancora nessune sequenza ) o se èla sequenza meno costosa
                self.__costo_ottimo = costo_corrente#se la sequenza costa meno ho un nuvo costo corrente
                self.__sequenza_ottima = sequenza_parziale.copy()#mi segno la sequenza meno costosa
            return

        for distributore in prezzi_settimana:#controllo i vari distributori
            prezzo = prezzi_settimana[distributore][giorno - 1]#prendo i prezzi di quel distributore in quel determinato gioro
            costo_giorno = prezzo * 100#calcolo il costo su 100 litri

            if (ultimo_distributore is not None
                    and distributore != ultimo_distributore):
                costo_giorno += 5 #se cambio distributore aumento di 5 il costo

            sequenza_parziale.append(distributore)#aggiungo il distributore alla lista

            self.__ricorsione(sequenza_parziale, giorno + 1, distributore,costo_corrente + costo_giorno, prezzi_settimana)
            sequenza_parziale.pop()


    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_per_distributore={}#contiene i prezzi dei primi 7 gioni con chiavel'id distributore
        for distributore in self._distributori:#per ciascun distrubutore che ho
            prezzi_per_distributore [distributore.id]= []#genero una chiave con l'id dei distributori
            prezzi = distributore.get_prezzi()#tramite la funzione associa ogni prezzo al distributore , quindi avro tutti i prezzi di quel distributore
            for prezzo in prezzi:#itaros ui prezzi
                if prezzo.data.month == mese and prezzo.data.day<=7:#controllo i prezzi in modo da prendere quelli dei primi 7 giorni
                    prezzi_per_distributore[distributore.id].append(prezzo.prezzo_litro)#se il prezzo va bene lo aggiungo al dizionario con chiave il distributore

        return prezzi_per_distributore
