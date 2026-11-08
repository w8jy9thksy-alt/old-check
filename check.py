import os, re, html, sys, urllib.request

URL = "https://www.olg-duesseldorf.nrw.de/aufgaben/referendarabteilung/09_weiter_info/index.php"
TOPIC = os.environ["NTFY_TOPIC"]


def notify(title, msg, prio="urgent"):
    req = urllib.request.Request(
        "https://ntfy.sh/" + TOPIC,
        data=msg.encode("utf-8"),
        headers={"Title": title, "Priority": prio, "Click": URL, "Tags": "rotating_light"},
    )
    urllib.request.urlopen(req, timeout=30)


def main():
    if os.environ.get("TEST") == "true":
        notify("Test OK", "Die Benachrichtigung funktioniert.", "default")
        return

    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        print("Abruf fehlgeschlagen:", e)
        sys.exit(0)

    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    text = re.sub(r"\s+", " ", text).lower()

    a = text.find("kurzfristig zu besetzende ausbildungsplätze")
    b = text.find("bei interesse an einem der angebotenen")
    if a == -1 or b == -1 or b < a:
        notify("Referendariat: Seite geaendert", "Struktur der OLG-Seite hat sich geaendert. Bitte pruefen!")
        return

    section = text[a:b]
    keine_plaetze = "es stehen derzeit keine plätze zur verfügung" in section
    alle_bezirke_leer = section.count("keine freien plätze") >= 6
    if not (keine_plaetze and alle_bezirke_leer):
        notify("Referendariat: Platz frei?", "Auf der OLG-Seite hat sich bei den Restplaetzen etwas geaendert. Sofort pruefen und mailen!")


main()
