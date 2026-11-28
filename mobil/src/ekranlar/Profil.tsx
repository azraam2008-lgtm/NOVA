// Profil.tsx - "Profil" sekmesi: bilgiler (tek sayfa), oruç modu, diyetisyen paylaşımı, tema, dil, çıkış
import React from "react";
import { View } from "react-native";
import { DILLER, aktifDil, t, type Dil } from "../dil";
import { hedefHesapla, type Veri } from "../hesap";
import { VARSAYILAN_TEMA } from "../tema";
import { Cip, Dugme, Kart, SayfaBasligi, Yazi } from "../bilesenler";
import { BilgilerKarti, OrucAyarlari, PaylasimKarti } from "./Ayarlar";
import { TemaSecici } from "./TemaSecici";

export function ProfilSayfasi(p: {
  veri: Veri; kullanici: string; temaSec: (ad: string) => void; dilSec: (d: Dil) => void; cikis: () => void;
  guncelle: (f: (v: Veri) => Veri) => Promise<void>;
}) {
  const pr = p.veri.profil;
  const h = hedefHesapla(pr);
  return (
    <View testID="sayfa-profil">
      <SayfaBasligi baslik={t("Profil")} alt={`@${p.kullanici}`} />

      <BilgilerKarti profil={pr} guncelle={p.guncelle} />
      <OrucAyarlari profil={pr} guncelle={p.guncelle} />
      <PaylasimKarti veri={p.veri} kullanici={p.kullanici} hedef={h.hedef} />

      <Kart>
        <Yazi s={{ fontWeight: "700", fontSize: 17, marginBottom: 12 }}>{t("Tema")}</Yazi>
        <TemaSecici secili={String(pr.tema ?? VARSAYILAN_TEMA)} sec={p.temaSec} />
      </Kart>

      <Kart>
        <Yazi s={{ fontWeight: "700", fontSize: 17, marginBottom: 12 }}>{t("Dil")}</Yazi>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
          {DILLER.map((d) => <Cip key={d.kod} testID={`dil-sec-${d.kod}`} yazi={d.ad} secili={aktifDil() === d.kod} bas={() => p.dilSec(d.kod)} />)}
        </View>
      </Kart>

      <Dugme testID="cikis" tur="yalin" yazi={t("Çıkış yap")} bas={p.cikis} />
      <Yazi tur="soluk" s={{ textAlign: "center", marginTop: 8 }}>{t("Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez. Hesaplamalar genel formüllere dayanan tahminlerdir.")}</Yazi>
    </View>
  );
}
