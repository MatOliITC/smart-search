# Mappa dei chunk (CHUNK_SIZE 800, CHUNK_OVERLAP 150)

Id del chunk = `<document_id>-<chunk_index a 4 cifre>`. Se cambia il chunking, questa mappa va rifatta.

## f1 - Manuali di casa

| Id chunk | Documento | Contenuto |
|---|---|---|
| d1-0000 | pompa.txt (pompa di calore HP-9) | 1. Introduzione, 2. Installazione |
| d1-0001 | pompa.txt (pompa di calore HP-9) | 3. Funzionamento in inverno (brina, fino a -20 °C) |
| d1-0002 | pompa.txt (pompa di calore HP-9) | 4. Codici di errore (**E05** = blocco bassa temperatura), 5. Manutenzione |
| d3-0000 | caldaia_condensazione.txt (caldaia CB-24) | 1. Introduzione, 2. Pressione dell'impianto (1-1,5 bar, E10) |
| d3-0001 | caldaia_condensazione.txt (caldaia CB-24) | 3. Inverno e antigelo (E28 condensa ghiacciata) |
| d3-0002 | caldaia_condensazione.txt (caldaia CB-24) | 4. Codici di errore (**E05** = sonda di mandata guasta) |
| d3-0003 | caldaia_condensazione.txt (caldaia CB-24) | 5. Manutenzione |
| d4-0000 | condizionatore_split.txt (condizionatore AC-12) | 1. Introduzione, 2. Telecomando e modalità |
| d4-0001 | condizionatore_split.txt (condizionatore AC-12) | 3. Riscaldamento con il freddo (sotto -10 °C → **E05**, sbrinamento) |
| d4-0002 | condizionatore_split.txt (condizionatore AC-12) | 4. Codici di errore (**E05** = protezione bassa temperatura) |
| d4-0003 | condizionatore_split.txt (condizionatore AC-12) | 5. Pulizia e manutenzione |
| d5-0000 | pompa_di_calore_hp12.txt (scaldacqua HP-12) | 1. Descrizione, 2. Installazione |
| d5-0001 | pompa_di_calore_hp12.txt (scaldacqua HP-12) | 3. Freddo, 4. Antilegionella, 5. Codici (**E05** = anodo esaurito) |
| d5-0002 | pompa_di_calore_hp12.txt (scaldacqua HP-12) | 6. Manutenzione |

## f2 - Auto

| Id chunk | Documento | Contenuto |
|---|---|---|
| d2-0000 | tagliando_auto.txt (ibrida C-30) | 1. Tagliando (15.000 km / 12 mesi), 2. Pneumatici, 3. Batteria |
| d6-0000 | libretto_auto_diesel.txt (diesel D-50) | 1. Tagliando (30.000 km / 24 mesi), 2. Filtro DPF |
| d6-0001 | libretto_auto_diesel.txt (diesel D-50) | 3. Avviamento con il freddo, 4. Pneumatici |

## f3 - Casa in affitto (testi legali)

| Id chunk | Documento | Contenuto |
|---|---|---|
| d7-0000 | contratto_locazione.txt | Intestazione, Art. 1 Oggetto |
| d7-0001 | contratto_locazione.txt | Art. 2 Durata, rinnovo e recesso (sei mesi, raccomandata) |
| d7-0002 | contratto_locazione.txt | Art. 3 Canone (750 euro), **Art. 4 Deposito cauzionale** (2.250 euro) |
| d7-0003 | contratto_locazione.txt | Art. 5 Oneri accessori (chi paga cosa), **Art. 6 Animali** |
| d7-0004 | contratto_locazione.txt | Art. 7 Riconsegna |
| d8-0000 | regolamento_condominio.txt | Intestazione, Art. 1 Uso delle parti comuni |
| d8-0001 | regolamento_condominio.txt | Art. 2 Orari di silenzio, Art. 3 Lavori (preavviso dieci giorni) |
| d8-0002 | regolamento_condominio.txt | **Art. 4 Animali**, Art. 5 Rifiuti |
| d8-0003 | regolamento_condominio.txt | Art. 6 Ripartizione spese (70/30), Art. 7 Assemblea |

## f4 - Cartella "disordinata"

| Id chunk | Documento | Contenuto |
|---|---|---|
| d9-0000 | appunti_riunione.txt | Riunione 12/03 (deadline migrazione **4 aprile**, superata) |
| d9-0001 | appunti_riunione.txt | Riunione 19/03 (nuova deadline **5 aprile**, ram, export excel) |
| d10-0000 | ricette_nonna.txt | Tiramisù |
| d10-0001 | ricette_nonna.txt | Ragù (3 ore, olio) |
| d10-0002 | ricette_nonna.txt | Torta di mele (180 gradi, olio di semi) |
| d11-0000 | diario_viaggio_portogallo.txt | Giorni 1-2 Lisbona (volo in ritardo da Milano) |
| d11-0001 | diario_viaggio_portogallo.txt | Giorni 3-5 Sintra e Porto, spese totali (620 euro) |
