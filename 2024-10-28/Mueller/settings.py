# settings.py

URL = "https://www.mueller.at/sitemap/product/?index=2"

CLIENT_NAME = "tcs_aldi"
COUNTRY_NAME = "austria"
FREQUENCY = "weekly"
ITERATION = "1"  
PROJECT = "mueller"  

MONGO_URI = 'mongodb://localhost:27017/'  
DB_NAME = f"{CLIENT_NAME}_{COUNTRY_NAME}_{FREQUENCY}_{ITERATION}"
URL_COLLECTION = f"{PROJECT}_url"
DATA_COLLECTION = f"{PROJECT}_data"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}

SPECIAL_INFORMATION = {
    "anti-aging_care": "Anti-Aging-Pflege",
    "manufacturer": "Hersteller",
    "top_note": "Kopfnote",
    "effect": "Wirkung",
    "cable_length": "Kabel Länge",
    "consistency": "Konsistenz",
    "ophthalmologically_tested": "Ophthalmologisch getestet",
    "ruling": "Regelung",
    "license": "Lizenz",
    "washable_up_to": "Waschbar bis",
    "composer": "Komponist",
    "skin_type": "Hauttyp",
    "page_number": "Seitenzahl",
    "publication_date": "Veröffentlichungsdatum",
    "game_motivation": "Spielmotivation",
    "washable": "Waschbar",
    "foldable": "Faltbar",
    "length_in_cm": "Länge in cm",
    "automatic_shutdown": "Automatische Abschaltung",
    "scope_of_application": "Anwendungsbereich",
    "fragrance_note": "Duftnote",
    "fragrance_effect": "Duftwirkung",
    "seal_of_approval": "Prüfsiegel",
    "author": "Autor",
    "wine_rating": "Weinbewertung",
    "medium": "Medium",
    "capacity_in_l": "Kapazität in l",
    "publishing_year": "Erscheinungsjahr",
    "hair_type": "Haartyp",
    "cover_included": "Cover enthalten",
    "packaging_type": "Verpackungsart",
    "distribution": "Vertrieb",
    "award": "Auszeichnung",
    "mechanics": "Mechanik",
    "number_of_pieces": "Anzahl der Teile",
    "special_feed": "Spezialfutter",
    "alcohol_content": "Alkoholgehalt",
    "sun_protection_factor": "Sonnenschutzfaktor",
    "isbn": "ISBN",
    "back_width": "Rückenbreite",
    "opacity": "Opazität",
    "collection": "Kollektion",
    "vintage": "Jahrgang",
    "product_property": "Produkteigenschaft",
    "2-phase_care": "2-Phasen-Pflege",
    "with_lid": "Mit Deckel",
    "label": "Etikett",
    "template": "Vorlage",
    "height_in_cm": "Höhe in cm",
    "battery_type": "Batterietyp",
    "conductor": "Leiter",
    "waterproof": "Wasserdicht",
    "filling_material": "Füllmaterial",
    "genre": "Genre",
    "heart_note": "Herznote",
    "ph_skin_neutral": "pH-hautneutral",
    "depth_in_cm": "Tiefe in cm",
    "additives": "Zusatzstoffe",
    "sound_included": "Sound enthalten",
    "fragrance_concentration": "Duftkonzentration",
    "dosage_form": "Darreichungsform",
    "medical_device": "Medizinprodukt",
    "publisher": "Verlag",
    "target_group": "Zielgruppe",
    "motivation": "Motivation",
    "number_of_players": "Anzahl der Spieler",
    "drive_function_models": "Antriebsfunktionsmodelle",
    "feed_type": "Futtertyp",
    "particularities": "Besonderheiten",
    "energy_efficiency_class": "Energieeffizienzklasse",
    "line_width": "Linienbreite",
    "composition": "Zusammensetzung",
    "line_style": "Linienstil",
    "assembly_required": "Montage erforderlich",
    "freezer_safe": "Gefrierschrank geeignet",
    "providers": "Anbieter",
    "width_in_cm": "Breite in cm",
    "cover": "Cover",
    "analytical_components": "Analytische Komponenten",
    "package_contents": "Inhaltsstoffe",
    "electricity_system_model_railway": "Stromsystem Modellbahn",
    "application_note": "Anwendungsnotiz",
    "total_playing_time": "Gesamte Spielzeit",
    "warning_notice": "Warnhinweis",
    "edition": "Ausgabe",
    "base_note": "Basisnote",
    "dermatologically_tested": "Dermatologisch getestet",
    "special_function": "Sonderfunktion",
    "24h_care": "24h Pflege",
    "format": "Format",
    "enlargement": "Vergrößerung",
    "scope_of_delivery": "Lieferumfang",
    "language": "Sprache",
    "battery_operation_possible": "Betrieb mit Batterie möglich",
    "power_in_watts": "Leistung in Watt",
    "motif_group_puzzles": "Motivgruppe Puzzles",
    "age_rating": "Altersfreigabe",
    "illuminated": "Beleuchtet",
    "application_type": "Anwendungsart",
}
