"""Script detection, romanization, fuzzy name keys and main-language detection."""
import re

LANGS = ("hi", "en", "kn", "te", "ta")
# Indic Unicode blocks share one layout (ISCII order), so one offset table romanizes all four.
SCRIPTS = {"hi": 0x0900, "kn": 0x0C80, "te": 0x0C00, "ta": 0x0B80}

_CONS = "k kh g gh n ch chh j jh n t th d dh n t th d dh n n p ph b bh m y r r l l l v sh sh s h".split()  # 0x15..0x39
_NUKTA = "q kh g z r rh f y".split()  # Devanagari 0x58..0x5F
_VSIGN = {0x3E: "aa", 0x3F: "i", 0x40: "ii", 0x41: "u", 0x42: "uu", 0x43: "ri", 0x44: "ri", 0x45: "e", 0x46: "e",
          0x47: "e", 0x48: "ai", 0x49: "o", 0x4A: "o", 0x4B: "o", 0x4C: "au"}
_VIND = {0x05: "a", 0x06: "aa", 0x07: "i", 0x08: "ii", 0x09: "u", 0x0A: "uu", 0x0B: "ri", 0x0C: "l", 0x0D: "e",
         0x0E: "e", 0x0F: "e", 0x10: "ai", 0x11: "o", 0x12: "o", 0x13: "o", 0x14: "au"}


def script_of(word: str):
    for ch in word:
        o = ord(ch)
        for lang, base in SCRIPTS.items():
            if base <= o < base + 0x80:
                return lang
    return "latin" if re.search("[a-z]", word.lower()) else None


def romanize(word: str) -> str:
    out, pending, lang = [], False, None
    for ch in word:
        o, base = ord(ch), None
        for l, b in SCRIPTS.items():
            if b <= o < b + 0x80:
                base, lang = b, l
                break
        if base is None:
            if pending:
                out.append("a")
                pending = False
            out.append(ch.lower())
            continue
        off = o - base
        if 0x15 <= off <= 0x39 or (lang == "hi" and 0x58 <= off <= 0x5F):
            if pending:
                out.append("a")
            out.append(_CONS[off - 0x15] if off <= 0x39 else _NUKTA[off - 0x58])
            pending = True
        elif off in _VSIGN:
            out.append(_VSIGN[off])
            pending = False
        elif off == 0x4D:  # virama: no inherent vowel
            pending = False
        elif off in _VIND or off in (0x01, 0x02, 0x03):
            if pending:
                out.append("a")
            pending = False
            out.append(_VIND.get(off) or ("h" if off == 0x03 else "n"))
    if pending and lang != "hi":  # Hindi drops the final inherent 'a' (रमेश = ramesh)
        out.append("a")
    return "".join(out)


_KEY_RULES = [("ksh", "ks"), ("chh", "c"), ("sh", "s"), ("ch", "c"), ("th", "t"), ("dh", "d"), ("ph", "f"),
              ("bh", "b"), ("kh", "k"), ("gh", "g"), ("jh", "j"), ("w", "v"), ("z", "j"), ("aa", "a"),
              ("ee", "i"), ("ii", "i"), ("oo", "u"), ("uu", "u"), ("ou", "u")]


def name_key(name: str) -> str:
    """Spelling-insensitive key: रमेश, ರಮೇಶ್, రమేష్, ரமேஷ், Ramesh all give 'rames'."""
    r = re.sub("[^a-z]", "", romanize(name.lower()))
    for a, b in _KEY_RULES:
        r = r.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", r)


def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# Romanized words that mark a language. Names, numbers and shared words count for nobody.
ROMAN_MARKERS = {
    "hi": set("""ne se ko ka ki ke hai hain tha thi liya liye lia diya diye dia mila mile mili udhaar udhar udhari
        kitna kitne kitni baaki baki haan haa han nahi nahin aaj kal abhi rupaye rupay wala wale wali jama kiya aur ji
        pe par sau hazaar hazar dedh dhai saade paune pehla pehle doosra dusra kya mein gaya diye lena dena hisaab
        hisab paise ek do teen char chaar paanch das bees tees chalees chalis pachaas sattar assi theek bolo
        naya grahak saamaan chahiye deni dena batao karo""".split()),
    "en": set("""took take taken gave give given paid pay payment credit balance how much what is the of owe owes
        does yes no on for to from and today yesterday first second third cancel save okay received has his her
        hundred thousand rupees who did order orders needs need it kg arrived new pending tell show number phone
        mobile as add update money collect collected collections week most me my""".split()),
    "kn": set("kottaru kotta kottidare kodi tagondru tegedukondaru saala eshtu baaki houdu illa modala".split()),
    "te": set("icharu ichadu ichindi theesukunnaru appu entha avunu kaadu modati".split()),
    "ta": set("koduthaar koduthan vaanginaar kadan evvalavu aama illai mudhal".split()),
}


def detect_language(text: str, current: str, gnani_code: str | None = None) -> str:
    """Main language = most words; Gnani's detected code breaks ties; short replies keep `current`."""
    counts = dict.fromkeys(LANGS, 0)
    for w in re.findall(r"\S+", text.lower()):
        s = script_of(w)
        if s in SCRIPTS:
            counts[s] += 1
        elif s == "latin":
            w = re.sub("[^a-z]", "", w)
            for lang, words in ROMAN_MARKERS.items():
                if w in words:
                    counts[lang] += 1
                    break
    if sum(counts.values()) < 2:
        native = [g for g in ("kn", "te", "ta") if counts[g]]
        return native[0] if native else current  # one Kannada/Telugu/Tamil-script word can only be that language
    top = max(counts.values())
    tied = [l for l in LANGS if counts[l] == top]
    g = (gnani_code or "").split("-")[0]
    if g in tied:
        return g
    return current if current in tied else tied[0]
