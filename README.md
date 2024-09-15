# wp2-2023-starter

**Omschrijving:**

Deze webapplicatie is gemaakt voor het bedrijf 'Test-Correct'. Met deze applicatie kan de gebruiker inloggen, een notitie maken, een notitie bekijken, een lijst zien van alle notities (bestemd voor zijn rechten in de applicatie), deze lijst filteren, vragen genereren a.d.h.v. een gemaakte notitie en als admin (speciale rol) alle leraren zien en leraren toevoegen.
Deze webapplicatie is gecreeërd om het proces van toetsvragen maken te versimpelen en automatiseren.

**Start de webapplicatie:**

1. Creeër een virtual environment (kijk hieronder) en installeer het 'requirements.txt' bestand.
   1.1. Open de terminal
   1.2. Type het volgende commando: python -m pip -V
   1.3. Type het volgende commando: python -m pip install virtualenv
   1.4. Type het volgende commando: python -m virtualenv venv
   	"venv" is de naam voor de virtual environment, dit mag alles zijn.
   1.5. Type het volgende commando: venv/scripts/activate1.6. Type het laatste commando: pip install -r requirements.txt
2. Plaats je API-key (die de connectie met ChatGPT maakt) binnenin de "" in het 'config.py' bestand.
3. Zorg ervoor dat je de database niet in een andere applicatie open hebt staan. Is dit het geval, sluit deze dan.
4. Open het 'app.py'bestand en "run" het bestand.
5. De terminal zal zichzelf openen en het bestand "runnen". Wacht totdat je 'Running on http://127.0.0.1:5000' tussen twee gekleurde regels ziet.
6. Beweeg over '[http://127.0.0.1:5000](http://127.0.0.1:5000/)' en klik erop (terwijl je de 'Ctrl'-knop op je toetsenbord ingedrukt houdt).
7. De webbrowser opent en je kunt de webapplicatie starten door in te loggen.
8. Het kan nodig zijn om het 'hashscript.py' bestand te "runnen", zodat de wachtwoorden juist in de database staan.
9. Mocht je een schone database willen, open dan het 'database_generator.py' bestand en "run" deze. Deze kun je vinden in de 'database' folder in de 'lib' folder.

# Sourcelist

#### notes_form.html

 *HTML Input Types* . (z.d.). https://www.w3schools.com/html/html_form_input_types.asp

 *HTML style guide and coding conventions* . (z.d.). https://www.w3schools.com/html/html5_syntax.asp

#### notes_list.html

...
