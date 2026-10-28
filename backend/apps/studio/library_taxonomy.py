"""Small, authored browsing groups; edition/album provenance stays separate."""


def label(uz, ru, en):
    return {"uz": uz, "ru": ru, "en": en}


GROUPS = {
    "classical": label("Klassika", "Классика", "Classical"),
    "contemporary": label("Zamonaviy pianino", "Современное фортепиано", "Contemporary piano"),
    "film": label("Kino va seriallar", "Кино и сериалы", "Film and television"),
    "dorama": label("Doramalar", "Дорамы", "Dramas"),
    "anime": label("Anime", "Аниме", "Anime"),
    "epic": label("Epik musiqa", "Эпическая музыка", "Epic music"),
    "games": label("O‘yin musiqalari", "Музыка из игр", "Game music"),
    "songs": label("Qo‘shiqlar", "Песни", "Songs"),
    "folk": label("Xalq kuylari", "Народные мелодии", "Folk melodies"),
}

# A collection is a useful composer, artist or fictional world, not an opus,
# movement or album. The original edition collection remains in the API too.
COLLECTIONS = {
    "beethoven": ("classical", "Beethoven", ("ode-to-joy", "moonlight-sonata", "beethoven-moonlight-sonata-movement-3", "fur-elise")),
    "bach": ("classical", "Bach", ("prelude-c-major",)),
    "satie": ("classical", "Satie", ("gymnopedie-no-1",)),
    "chopin": ("classical", "Chopin", ("prelude-e-minor", "waltz-a-minor", "nocturne-op-9-no-2")),
    "mozart": ("classical", "Mozart", ("rondo-alla-turca",)),
    "debussy": ("classical", "Debussy", ("clair-de-lune",)),
    "handel-halvorsen": ("classical", "Handel / Halvorsen", ("passacaglia",)),
    "pachelbel": ("classical", "Pachelbel", ("pachelbel-canon-in-d",)),
    "yiruma": ("contemporary", "Yiruma", ("river-flows-in-you", "kiss-the-rain", "may-be")),
    "einaudi": ("contemporary", "Ludovico Einaudi", ("nuvole-bianche", "una-mattina", "experience", "i-giorni")),
    "de-senneville": ("contemporary", "Paul de Senneville", ("mariage-d-amour", "ballade-pour-adeline")),
    "peder-helland": ("contemporary", "Peder B. Helland", ("peder-b-helland-always",)),
    "maksim-mrvica": ("contemporary", "Maksim Mrvica", ("maksim-mrvica-croatian-rhapsody",)),
    "independent": ("contemporary", label("Alohida asarlar", "Отдельные произведения", "Independent pieces"), ("memories", "depression", "hate", "dream")),
    "romeo-juliet": ("film", "Romeo & Juliet", ("youth",)),
    "amelie": ("film", "Amélie", ("comptine", "la-valse-d-amelie")),
    "love-story": ("film", "Love Story", ("love-story",)),
    "interstellar": ("film", "Interstellar", ("cornfield-chase", "interstellar-main-theme")),
    "inception": ("film", "Inception", ("time",)),
    "pirates-of-the-caribbean": ("film", "Pirates of the Caribbean", ("hes-a-pirate", "pirates-of-the-caribbean-davy-jones")),
    "titanic": ("film", "Titanic", ("my-heart-will-go-on",)),
    "gladiator": ("film", "Gladiator", ("gladiator-honor-him-now-we-are-free",)),
    "frozen": ("film", "Frozen", ("frozen-let-it-go",)),
    "mohabbatein": ("film", "Mohabbatein", ("mohabbatein",)),
    "game-of-thrones": ("film", "Game of Thrones", ("game-of-thrones-main-theme",)),
    "la-la-land": ("film", "La La Land", ("mia-sebastians-theme",)),
    "schindlers-list": ("film", "Schindler’s List", ("schindlers-list",)),
    "chariots-of-fire": ("film", "Chariots of Fire", ("chariots-of-fire",)),
    "film-medleys": ("film", label("Film mavzulari", "Кинотемы", "Film themes"), ("the-last-of-the-mohicans", "horror-themes-medley")),
    "winter-sonata": ("dorama", "Winter Sonata", ("still", "star", "tears", "my-memory", "premonition", "winter-sonata-missing-you", "winter-sonata-from-the-beginning-until-now")),
    "all-in": ("dorama", "All in / Va-bank", ("all-in",)),
    "kara-sevda": ("dorama", "Kara Sevda", ("kara-sevda-anlatamam",)),
    "dae-jang-geum": ("dorama", "Dae Jang Geum", ("dae-jang-geum-apna",)),
    "naruto-boruto": ("anime", "Naruto / Boruto", ("naruto-senya", "naruto-hyouhaku-kokuten", "naruto-determination-gods-will", "naruto-i-have-seen-much", "naruto-man-of-the-world", "naruto-maisou-burial", "naruto-decision", "naruto-my-mother-and-my-father", "naruto-sadness-and-sorrow", "naruto-girei", "naruto-shutsujin", "boruto-spin-and-burst-reverse-situation", "naruto-the-raising-fighting-spirit", "naruto-wind")),
    "shiki": ("anime", "Shiki", ("shiki-epitaph", "shiki-day-and-night", "shiki-requiem", "shiki-blue-bell", "shiki-shi-ki", "shiki-eau-de-vie")),
    "fate": ("anime", "Fate/Stay Night", ("fate-stay-night-kodoku-na-junrei", "fate-stay-night-kishi-ou-no-hokori")),
    "studio-ghibli": ("anime", "Studio Ghibli", ("one-summers-day", "merry-go-round-of-life")),
    "two-steps-from-hell": ("epic", "Two Steps From Hell", ("two-steps-from-hell-night-queen", "two-steps-from-hell-victory", "two-steps-from-hell-unleashed", "two-steps-from-hell-heart-of-courage", "two-steps-from-hell-sariel", "two-steps-from-hell-evergreen", "two-steps-from-hell-star-sky", "thomas-bergersen-one-last-day", "thomas-bergersen-red", "thomas-bergersen-children-of-the-sun")),
    "ivan-torrent": ("epic", "Ivan Torrent", ("ivan-torrent-lion-heart",)),
    "end-of-silence": ("epic", "End of Silence", ("end-of-silence-entropy",)),
    "red-alert": ("games", "Command & Conquer: Red Alert 3", ("red-alert-3-soviet-march",)),
    "skyrim": ("games", "The Elder Scrolls V: Skyrim", ("skyrim-ancient-stones", "skyrim-from-past-to-present", "skyrim-dragonborn")),
    "hindi-songs": ("songs", label("Hind qo‘shiqlari", "Индийские песни", "Hindi songs"), ("tum-hi-ho",)),
    "beyonce": ("songs", "Beyoncé", ("beyonce-halo",)),
    "armstrong": ("songs", "Louis Armstrong", ("what-a-wonderful-world",)),
    "simon-garfunkel": ("songs", "Simon & Garfunkel", ("the-sound-of-silence",)),
    "traditional": ("folk", label("An’anaviy kuylar", "Традиционные мелодии", "Traditional melodies"), ("romance-damour", "ievan-polkka")),
}

WORK_COLLECTION = {code: collection_id for collection_id, (_, _, codes) in COLLECTIONS.items() for code in codes}


def taxonomy(code):
    collection_id = WORK_COLLECTION[code]
    group_id, title, _ = COLLECTIONS[collection_id]
    return {"library_group": {"id": group_id, "label": GROUPS[group_id]},
            "library_collection": {"id": collection_id, "label": title}}
