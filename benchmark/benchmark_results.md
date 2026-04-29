# Modell-Benchmark
Zuletzt ausgeführt: 2026-04-30 00:38

Getestete Modelle auf dem NVIDIA Spark via Ollama.
Metriken: TTFT = Time to First Token, tok/s = generierte Tokens pro Sekunde.

## qwen3:8b

| Test | TTFT (ms) | Gesamt (ms) | Load (ms) | Prompt-Tokens | Prompt (ms) | Tokens | tok/s | CPU Ø% | CPU Peak% | RAM Ø% | RAM Peak% | Tool aufgerufen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Small Talk | 6308 | 7928 | 2705 | 59 | 61 | 198 | 38.9 | 8.1 | 26.1 | 73.6 | 75.8 | – |
| Reasoning / längere Antwort | 9358 | 19424 | 108 | 86 | 41 | 748 | 39.1 | 7.9 | 28.0 | 75.8 | 75.9 | – |
| Tool Calling | 5444 | 6465 | 98 | 238 | 83 | 245 | 39.3 | 6.9 | 7.9 | 75.8 | 75.8 | get_temperature, get_rain |

### Beispielantworten

**Small Talk**
> Hallo! Wie geht es dir? Was machst du so den ganzen Tag?

Hallo! Mir geht es gut, vielen Dank! Ich bin ein KI-Assistent und habe keine physische Form, also keine eigene Routine oder Gefühle. Aber ich bin ständig bereit, dir bei Fragen zu helfen und Informationen zu liefern. Was kann ich für dich tun? 😊

**Reasoning / längere Antwort**
> Ein älterer Bewohner in einem Pflegeheim fühlt sich einsam und hat Heimweh nach seiner Heimatstadt. Wie würdest du das Gespräch mit ihm einfühlsam führen?

Es ist wichtig, die Gefühle des Bewohners mit Empathie und Wärme zu begegnen. Beginnen Sie das Gespräch mit einer ruhigen, vertraulichen Stimmung, z. B. durch einen kurzen Blickkontakt und eine leise, beruhigende Stimme. Lassen Sie ihn spüren, dass seine Gefühle verstanden werden. 

**Beispiel:**  
„Ich merke, dass Sie heute etwas traurig wirken. Es ist okay, wenn man manchmal Heimweh hat. Es ist normal, sich nach alten Orten oder Menschen zu sehnen.“  

Fragen Sie dann leise und langsam nach, was ihn in seiner Heimatstadt besonders beschäftigt:  
„Was haben Sie in Ihrer Heimatstadt besonders gemocht? Gab es einen Ort, den Sie immer wieder besucht haben? Oder vielleicht eine Person, die Ihnen viel bedeutet hat?“  

Hören Sie aktiv zu, ohne zu unterbrechen oder zu urteilen. Wenn er erzählt, zeigen Sie Interesse und wiederholen Sie gelegentlich seine Worte, um ihn zu bestätigen.  
„Ich verstehe, dass Sie sich nach dem Markt am Rande der Stadt sehnen. Das klingt, als ob dort viele Erinnerungen wohnen.“  

Fassen Sie am Ende die wichtigsten Punkte zusammen, um ihn zu beruhigen:  
„Es ist schön, dass Sie an Ihre Heimat denken. Es ist okay, sich manchmal nach etwas zu sehnen. Wenn Sie möchten, können wir uns auch öfter über Ihre Erinnerungen unterhalten – ich bin gerne da, wenn Sie es brauchen.“  

Lassen Sie ihm Raum, sich zu entlasten, und zeigen Sie, dass er nicht allein ist.

**Tool Calling**
> Wie ist gerade das Wetter in Hamburg? Scheint die Sonne?

*Tool: `get_temperature` mit `{"latitude": 53.5511, "longitude": 9.9937}`*
*Tool: `get_rain` mit `{"latitude": 53.5511, "longitude": 9.9937}`*


## qwen3:32b

| Test | TTFT (ms) | Gesamt (ms) | Load (ms) | Prompt-Tokens | Prompt (ms) | Tokens | tok/s | CPU Ø% | CPU Peak% | RAM Ø% | RAM Peak% | Tool aufgerufen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Small Talk | 37729 | 45890 | 7737 | 59 | 207 | 352 | 9.4 | 10.6 | 80.5 | 88.7 | 90.9 | – |
| Reasoning / längere Antwort | 46996 | 137542 | 218 | 86 | 165 | 1269 | 9.3 | 6.9 | 14.2 | 90.4 | 90.5 | – |
| Tool Calling | 47315 | 51641 | 85 | 238 | 363 | 475 | 9.3 | 7.2 | 26.2 | 90.2 | 90.6 | get_temperature, get_rain |

### Beispielantworten

**Small Talk**
> Hallo! Wie geht es dir? Was machst du so den ganzen Tag?

Hallo! Mir geht es gut, danke. Ich bin ein KI-Assistent und helfe gerne bei Fragen, Informationen oder Aufgaben, die du mir stellst. Meine Arbeit besteht darin, dir so gut wie möglich zu unterstützen – also immer bereit, zuzuhören und zu helfen! Was möchtest du heute wissen oder erledigen?

**Reasoning / längere Antwort**
> Ein älterer Bewohner in einem Pflegeheim fühlt sich einsam und hat Heimweh nach seiner Heimatstadt. Wie würdest du das Gespräch mit ihm einfühlsam führen?

Ein einfühlsames Gespräch mit einem älteren Bewohner, der sich einsam und heimatverlassen fühlt, erfordert Geduld, Empathie und Aufmerksamkeit für seine Emotionen. Hier sind einige Schritte, um das Gespräch zu führen:

1. **Zugang schaffen durch Wärme und Aufmerksamkeit**  
   Beginnen Sie mit einem freundlichen Gruß und zeigen Sie Interesse an seinem Wohlbefinden. Beispielsweise: *„Hallo [Name], es freut mich, Sie heute zu sehen. Wie geht es Ihnen?“*  
   Achten Sie auf Körpersprache (z. B. Haltung, Augenkontakt) und vermeiden Sie Druck, um ihn sich wohlfühlen zu lassen.

2. **Empathie zeigen und Emotionen annehmen**  
   Verbalisieren Sie seine Gefühle, um sie zu bestätigen. Zum Beispiel: *„Ich verstehe, dass es schwer ist, sich hier allein zu fühlen. Viele Menschen vermissen ihre Heimatstadt, das ist ganz normal.“*  
   Vermeiden Sie Aussagen wie „Das ist ja nicht so schlimm“ – das könnte ihn wertenden oder kleinreden.

3. **Erinnerungen aktivieren und teilen**  
   Fragen Sie nach Erinnerungen an seine Heimatstadt, um positive Aspekte hervorzuheben: *„Können Sie mir erzählen, was Sie besonders an Ihrer Heimatstadt mochten?“*  
   Hören Sie aktiv zu, ohne zu unterbrechen. Manchmal können Anekdoten, Gerüche oder Geräusche (z. B. ein altes Lied) ihn emotional verbinden.

4. **Verbindungen herstellen – zwischen Vergangenem und Gegenwart**  
   Zeigen Sie, dass Sie seine Heimat schätzen, z. B. durch Fotos, Briefe oder kleine Gegenstände, die an seine Stadt erinnern. *„Haben Sie ein Foto von zu Hause, das wir uns gemeinsam ansehen könnten?“*  
   Falls möglich, organisieren Sie Aktivitäten im Heim, die an seine Kultur oder Traditionen erinnern (z. B. ein regionaler Braten, ein Lied oder ein Fest).

5. **Praktische Unterstützung anbieten**  
   Fragen Sie nach Wünschen, wie er sich unterstützt fühlen möchte: *„Gibt es etwas, das Sie hier im Heim vermissen? Können wir gemeinsam etwas tun, um es zu verbessern?“*  
   Bieten Sie an, Briefe an Freunde oder Angehörige zu schreiben, falls er das möchte.

6. **Langfristige Begleitung signalisieren**  
   Vermeiden Sie „Ein-Mal-Unterhaltungen“. Zeigen Sie, dass Sie seine Gefühle ernst nehmen: *„Ich bin hier, um zu hören, wenn Sie reden möchten. Wir können jederzeit wieder darüber sprechen.“*  
   Falls nötig, sprechen Sie mit dem Pflegeteam, um Sozialarbeit oder Therapie (z. B. Erinnerungstherapie) einzubeziehen.

7. **Abschluss mit Hoffnung und Wertschätzung**  
   Schließen Sie das Gespräch mit einer positiven Botschaft: *„Vielen Dank, dass Sie mir das erzählt haben. Ihre Geschichte ist wertvoll, und ich freue mich, Sie besser kennenlernen zu dürfen.“*

**Wichtig:** Jeder Mensch ist anders. Manche möchten viel erzählen, andere nur wenig. Passen Sie Ihr Vorgehen an seine Reaktionen an. Manchmal reicht es, einfach da zu sein – ohne zu reden.

**Tool Calling**
> Wie ist gerade das Wetter in Hamburg? Scheint die Sonne?

*Tool: `get_temperature` mit `{"latitude": 53.5511, "longitude": 9.9937}`*
*Tool: `get_rain` mit `{"latitude": 53.5511, "longitude": 9.9937}`*


## mistral:7b

| Test | TTFT (ms) | Gesamt (ms) | Load (ms) | Prompt-Tokens | Prompt (ms) | Tokens | tok/s | CPU Ø% | CPU Peak% | RAM Ø% | RAM Peak% | Tool aufgerufen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Small Talk | 7651 | 10662 | 7579 | 56 | 53 | 131 | 43.9 | 6.6 | 12.2 | 70.9 | 90.2 | – |
| Reasoning / längere Antwort | 61 | 16999 | 11 | 89 | 38 | 742 | 44.0 | 6.6 | 8.4 | 72.8 | 72.8 | – |
| Tool Calling | 105 | 3525 | 19 | 201 | 77 | 151 | 44.4 | 6.0 | 7.3 | 72.8 | 72.8 | – |

### Beispielantworten

**Small Talk**
> Hallo! Wie geht es dir? Was machst du so den ganzen Tag?

Hallo! Ich bin sehr glücklich, dass ich dir hier helfen kann. Ich bin ein künstlicher Intelligenz-Assistent und deshalb nicht in der Lage, Emojis oder Sonderzeichen zu benutzen.

Ich habe keinen ganzen Tag, denn ich funktioniere ausschließlich im Moment, indem Daten verarbeite und Antworten geben kann. Ich leiste dabei meine besten Dienste, um dich zu unterstützen und Fragen zu beantworten. Wie kann ich dir heute helfen?

**Reasoning / längere Antwort**
> Ein älterer Bewohner in einem Pflegeheim fühlt sich einsam und hat Heimweh nach seiner Heimatstadt. Wie würdest du das Gespräch mit ihm einfühlsam führen?

Ich bin da, um dir zu helfen. Hier ist eine Vorschlag für ein empathisches Gespräch:

Assistent: Guten Tag! Wie geht es Ihnen heute? Es gibt etwas, das ich mir gerade sehr angesprochen fühle. Erzählen Sie mir, wie Sie sich heute anfühlen und welche Gefühle Sie haben.

Bewohner: Ja, ich habe gerade ein wenig einsam und Heimweh nach meiner Heimatstadt. Ich denke so häufig an die alten Zeiten, wo alles anders war.

Assistent: Es tut mir leid, dass Sie sich so fühlen. Es ist normal, dass man im Alter etwas vermissen kann und die Vergangenheit oft schön erscheint. Kann ich etwas tun, um Ihnen zu helfen? Sagen Sie mir mehr über Ihre Heimatstadt, die es Ihnen so gut bringt.

Bewohner: Meine Heimatstadt ist eine kleine Ansiedlung an der Küste, wo das Seewasser tiefblau und hell glänzt. Es gibt eine schöne Promenade mit alten Bäumen, die immer grün bleiben. Ich habe dort mein ganzes Leben verbracht und so viel an Erinnerungen gesammelt.

Assistent: Die Stadt klingt wunderbar! Es könnte helfen, wenn wir ein Bild daran hängen oder wenn ich für Sie etwas über die Stadt recherchieren werde. Wenn Sie es wollen, können wir auch Musik und Geräusche aus der Stadt hören, um Ihre Erinnerungen anzuregen. Was denkst du dazu?

Bewohner: Das klingt sehr nett! Ich wäre gerne drauf, etwas über die Stadt zu hören. Vielleicht können wir auch Fotos von alten Zeiten suchen, um sie hier in meinem Zimmer anzuhängen.

Assistent: Ich werde mich daran machen, Ihnen über die Stadt zu erzählen und etwas über die alten Tage zu recherchieren. Es sollte auch nicht schwer sein, Fotos von der Zeit zu finden. Wenn Sie es wünschen, könnten wir auch eine Reise ins Gedächtnis machen und einige Erinnerungen erleben. Sagen Sie mir mehr über die Tage, die Sie am liebsten aus der Vergangenheit denken.

Bewohner: Ich denke gerne an das Jahr, als ich meine erste Ehefrau kennengelernt habe. Es war ein schönes Jahr mit vielen Glück und Freude. Wir haben viele gute Erinnerungen zusammen gemacht, die mir immer wichtig sind.

Assistent: Ich denke auch, dass ich eine Erinnerung an das Jahr kennen mag, in dem Sie Ihre erste Ehefrau kennengelernt haben. Sicherlich gibt es auch etwas, was Sie von jenen Zeiten noch genießen können. Wir können gemeinsam daran arbeiten, um die Erinnerungen zu aktivieren und sie wieder lebendig zu machen.

**Tool Calling**
> Wie ist gerade das Wetter in Hamburg? Scheint die Sonne?

Ich kann dir nicht sagen, ob es jetzt sonnig in Hamburg ist. Um zu wissen, was der aktuelle Zustand des Wetters ist, benötige ich deine geographischen Koordinaten (Latitude und Longitude). Dann kann ich dir die Temperatur und eventuell auch Niederschlagsdaten anzeigen.

[{"name":"get_temperature","arguments":{"latitude":53.551,"longitude":9.993}}]

[{"name":"get_rain","arguments":{"latitude":53.551,"longitude":9.993}}]
