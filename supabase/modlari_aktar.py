"""
modlari_aktar.py - Yapay zeka talimatlarını sunucu fonksiyonuna aktarır

Site ile telefon uygulaması AYNI talimatları ve yanıt şemalarını kullanmalı;
bunlar elle iki yerde tutulursa zamanla ayrışır. Tek doğru nova_core.py'dir.
nova_core.py'deki bir talimatı değiştirdikten sonra bunu çalıştır:

    python supabase/modlari_aktar.py

supabase/functions/yapay-zeka/modlar.json yeniden yazılır; fonksiyonu tekrar yayınla.
"""
import json
import logging
import os
import sys

logging.disable(logging.WARNING)
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

import nova_core as nc  # noqa: E402

cikti = {
    "limitler": dict(nc.DAILY_LIMITS),
    "genel_limit": nc.GLOBAL_DAILY_LIMIT,
    "modeller": [nc.DEFAULT_MODEL] + [m for m in nc.YEDEK_MODELLER if m != nc.DEFAULT_MODEL],
    "gorsel_modeller": list(nc.GORSEL_MODELLER),
    "modlar": {},
}
for anahtar, mod in nc.MODES.items():
    cikti["modlar"][anahtar] = {
        "sistem": mod.system,
        "sicaklik": mod.temperature,
        "gorsel_gerekli": mod.needs_image,
        "sema": mod.schema.model_json_schema() if mod.schema is not None else None,
    }

hedef = os.path.join(KOK, "supabase", "functions", "yapay-zeka", "modlar.json")
with open(hedef, "w", encoding="utf-8") as f:
    json.dump(cikti, f, ensure_ascii=False, indent=1)
print(f"{len(cikti['modlar'])} mod yazıldı: {hedef}")


# ---------------------------------------------------------------------------
# Panele yapıştırmak için tek dosyalık kopyalar (supabase/panele_yapistir/)
# Supabase panelindeki düzenleyiciye tek dosya yapıştırmak en kolayı.
# ---------------------------------------------------------------------------
import re  # noqa: E402

def _tek_dosya(klasor, modlar_icerigi=None):
    fn = os.path.join(KOK, "supabase", "functions", klasor)
    cekirdek = open(os.path.join(fn, "cekirdek.ts"), encoding="utf-8").read()
    giris = open(os.path.join(fn, "index.ts"), encoding="utf-8").read()
    giris = re.sub(r'^import \{[^}]*\} from "\./cekirdek\.ts";\n', "", giris, flags=re.M)
    giris = re.sub(r'^import modlarJson from "\./modlar\.json".*\n', "", giris, flags=re.M)
    disari = "".join(re.findall(r'^import .* from "npm:.*\n', giris, flags=re.M))
    giris = re.sub(r'^import .* from "npm:.*\n', "", giris, flags=re.M)
    ek = ""
    if modlar_icerigi is not None:
        ek = "\n// ---- modlar.json (python supabase/modlari_aktar.py ile üretildi)\nconst modlarJson = " + modlar_icerigi + ";\n"
    metin = (f"// {klasor} - Supabase paneline yapıştırılacak tek dosya. ELLE DÜZENLEME;\n"
             "// supabase/functions altındaki dosyaları değiştirip modlari_aktar.py'yi çalıştır.\n\n"
             + disari + "\n" + cekirdek + ek + "\n// ---- index.ts\n" + giris)
    hedef_klasor = os.path.join(KOK, "supabase", "panele_yapistir")
    os.makedirs(hedef_klasor, exist_ok=True)
    yol = os.path.join(hedef_klasor, f"{klasor}.ts")
    open(yol, "w", encoding="utf-8").write(metin)
    print("tek dosya:", yol)

_tek_dosya("giris")
_tek_dosya("yapay-zeka", json.dumps(cikti, ensure_ascii=False))
