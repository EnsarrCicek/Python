import re
import unicodedata
from pathlib import Path

INPUT_PATH = "dataset_final_cleaned.txt"
OUTPUT_PATH = "dataset_final_cleaned_v2.txt"
PREVIEW_COUNT = 50

def strip_acc(s: str) -> str:
    s = s.replace("İ", "I").replace("ı", "i")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower().strip()

def normalize_spaces(s: str) -> str:
    s = s.replace("\u00A0", " ")
    return re.sub(r"\s+", " ", s).strip()

def clean_comment(text: str) -> str:
    return re.sub(r"\s*//.*$", "", text).strip()

def looks_like_label_line(line: str) -> bool:
    return line.strip().startswith("__label__")

def split_label_and_text(line: str):
    m = re.match(r"^(__label__\S+)\s+(.*)$", line.strip())
    if not m:
        return None, None
    return m.group(1), m.group(2)

META_PHRASES = {
    "evlendirme",
    "barinak",
    "idari hat",
    "temizlik isleri kalemi",
    "kultur kalem",
    "park ve bahceler",
    "hal mudurlugu",
    "avukat kalemi",
    "gelir sefligi 4059",
}

CONNECTIVE_ENDINGS = (
    "bagla", "baglar", "baglayin", "baglayiniz", "baglar misin", "baglar misiniz",
    "aktar", "aktarir", "aktarin", "aktariniz", "aktarir misin", "aktarir misiniz",
    "yonlendir", "yonlendirin", "yonlendirin", "yonlendiriniz",
    "gorusmek istiyorum", "gorusecegim", "hatta bagla", "hatta ver",
)

def is_phoney(s: str) -> bool:
    s2 = s.strip()
    if not s2:
        return True
    return bool(re.fullmatch(r"[\d\s()._+\-]+\.?", s2))

def is_meta_chunk(chunk: str) -> bool:
    raw = chunk.strip()
    if not raw:
        return True

    norm = strip_acc(raw).strip(" .;,:-_/()[]{}")

    if not norm:
        return True

    if is_phoney(raw):
        return True

    if re.fullmatch(r"[A-Z0-9_]+", raw):
        return True

    if norm in META_PHRASES:
        return True

    # "188’e bağlayın", "4166’ya bağlayın", "4205" gibi
    if re.search(r"\b\d{3,5}\b", norm) and re.search(r"\b(bagla|aktar|yonlendir|gorus)\w*", norm):
        return True

    # doğrudan meta yönlendirme parçası
    if any(x in norm for x in [
        "baglayin", "baglayin.", "baglar misiniz", "baglar misin",
        "aktarin", "aktarin.", "aktarir misiniz", "aktarir misin",
        "yonlendirin", "yonlendirin", "hatta aktar", "hatta bagla",
        "ile gorusmek istiyorum", "ile gorusecegim"
    ]):
        return True

    return False

def clean_semicolon_parts(text: str) -> str:
    parts = [normalize_spaces(p) for p in text.split(";")]
    parts = [p for p in parts if p]

    if not parts:
        return ""

    kept = [parts[0]]

    for p in parts[1:]:
        if is_meta_chunk(p):
            break
        kept.append(p)

    out = "; ".join(kept)
    out = normalize_spaces(out).strip(" ;")
    return out

def trim_trailing_meta(text: str) -> str:
    t = normalize_spaces(text)

    patterns = [
        # sonundaki "188'e bağlayın", "4166'ya bağlayın (4167 yedek)" vb.
        r"[;,:-]?\s*\(?\d{3,5}\)?(?:[’']?[a-zçğıöşü]+)?\s+(?:e|a)?\s*(?:bagla\w*|aktar\w*|yonlendir\w*).*$",
        # "Kaldırım İşleri (4069) ile görüşmek istiyorum" gibi tamamen yönlendirme cümlesi
        r"[;,:-]?\s*[A-ZA-Za-zÇĞİÖŞÜçğıöşü\s()0-9\-–]+ile\s+g[oö]r[uü]s?mek\s+istiyorum\.?$",
        # "evlendirmeye bağlayın" gibi son meta
        r"[;,:-]?\s*[a-zçğıöşü\s()0-9\-–]+(?:bagla\w*|aktar\w*|yonlendir\w*)\.?$",
    ]

    old = None
    while old != t:
        old = t
        for pat in patterns:
            t = re.sub(pat, "", t, flags=re.IGNORECASE).strip(" ;,.-")

    return normalize_spaces(t)

def is_low_value_text(text: str) -> bool:
    norm = strip_acc(text)

    if not norm:
        return True

    toks = re.findall(r"[a-z0-9çğıöşü]+", norm)

    if len(toks) == 0:
        return True

    # çok kısa / anlamsız tek başına kalan satırlar
    if len(toks) <= 2 and len(norm) < 25:
        bad_short = {
            "ilaclama talep ediyorum",
            "kaydi acin lutfen",
            "kaydı açın lütfen",
        }
        if norm in bad_short:
            return True

    return False

def maybe_fix_vidanjor(text: str) -> str:
    norm = strip_acc(text)

    # çok bozuk vidanjör varyantları
    replacements = [
        (r"\bvianj\s*r\b", "vidanjor"),
        (r"\bv[ıi]danj[oö]r['’]e\b", "vidanjöre"),
        (r"\br\s*gara\s+vianj\s*r\s+g\s*nderin\b", "vidanjör gönderin"),
        (r"\bvianj\s*r\s+birimine\s+ba\s+la\b", "vidanjör birimine bağla"),
        (r"\bvianj\s*r\s+hatt\s*na\s+ba\s+la\b", "vidanjör hattına bağla"),
        (r"\bvianjor\b", "vidanjor"),
    ]

    out = text
    for pat, rep in replacements:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)

    return normalize_spaces(out)

def is_too_corrupt_vidanjor(text: str) -> bool:
    norm = strip_acc(text)
    bads = [
        "vianj r birimine ba la",
        "vianj r hatt na ba la",
        "r gara vianj r g nderin",
    ]
    return any(b in norm for b in bads)

def final_phrase_cleanup(text: str) -> str:
    t = text

    # yalnız bırakılabilecek kısa meta parçaları temizle
    t = re.sub(r"\b(Evlendirme|barınak|Barınak|idari hat)\b\.?", "", t, flags=re.IGNORECASE)
    t = normalize_spaces(t).strip(" ;,.-")

    return t

def clean_line(line: str):
    original = line.rstrip("\n")
    stripped = original.strip()

    if not stripped:
        return None, "empty"

    if not looks_like_label_line(stripped):
        return None, "non_label"

    label, text = split_label_and_text(stripped)
    if not label:
        return None, "broken_label"

    text = clean_comment(text)
    text = clean_semicolon_parts(text)
    text = trim_trailing_meta(text)
    text = maybe_fix_vidanjor(text)
    text = final_phrase_cleanup(text)

    if is_too_corrupt_vidanjor(text):
        return None, "corrupt_vidanjor"

    if is_low_value_text(text):
        return None, "low_value"

    text = normalize_spaces(text).strip(" ;,.-")
    if not text:
        return None, "empty_after_clean"

    new_line = f"{label} {text}"
    changed = (new_line != original)
    return new_line, ("changed" if changed else "same")

def main():
    in_file = Path(INPUT_PATH)
    out_file = Path(OUTPUT_PATH)

    if not in_file.exists():
        print(f"HATA: Dosya bulunamadı -> {in_file.resolve()}")
        return

    lines = in_file.read_text(encoding="utf-8").splitlines()

    out_lines = []
    stats = {
        "same": 0,
        "changed": 0,
        "empty": 0,
        "non_label": 0,
        "broken_label": 0,
        "corrupt_vidanjor": 0,
        "low_value": 0,
        "empty_after_clean": 0,
    }
    preview = []

    for line in lines:
        result, status = clean_line(line)
        stats[status] = stats.get(status, 0) + 1

        if result is not None:
            out_lines.append(result)

        if len(preview) < PREVIEW_COUNT and status in {"changed", "non_label", "low_value", "corrupt_vidanjor"}:
            preview.append((status, line, result))

    out_file.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    remaining_semicolon = sum(1 for x in out_lines if ";" in x)
    remaining_nonlabel = sum(1 for x in out_lines if not x.startswith("__label__"))

    print("=" * 70)
    print("TEMİZLİK V2 TAMAMLANDI")
    print("=" * 70)
    print(f"Girdi : {in_file.resolve()}")
    print(f"Çıktı : {out_file.resolve()}")
    print(f"Toplam girdi satırı : {len(lines)}")
    print(f"Toplam çıktı satırı : {len(out_lines)}")
    print("-" * 70)
    for k, v in stats.items():
        print(f"{k:18}: {v}")
    print("-" * 70)
    print(f"Kalan ';' satırı      : {remaining_semicolon}")
    print(f"Kalan etiketsiz satır : {remaining_nonlabel}")
    print("=" * 70)

    print("\nÖRNEK DEĞİŞİKLİKLER:\n")
    for i, (status, old, new) in enumerate(preview, 1):
        print(f"[{i}] DURUM: {status}")
        print(f"ESKİ: {old}")
        print(f"YENİ: {new}")
        print("-" * 70)

if __name__ == "__main__":
    main()