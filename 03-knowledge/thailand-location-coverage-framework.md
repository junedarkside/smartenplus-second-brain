# Thailand + Cross-Border Location Coverage Framework

## Summary
Master reference set of Thailand (and cross-border) travel-relevant locations. Used to compute Reference layer of the gap matrix. Curated atomic note — evergreen.

## Context
SmartEnPlus focus = Thailand transport/activities/experiences. Audit 2026-06-28 expanded scope to Thailand + cross-border (Laos, Cambodia, Myanmar, Malaysia) per competitive baseline in [[business-development-thailand-platform-analysis]]. See [[products-live-catalog-audit]].

## Details

### Category 1 — International airports (IATA)

BKK · DMK · HKT · CNX · HDY · KBV · USM · HGN · UTH · NST · CEI · UBP · KOP · PHS · SNO · UNN · TDX · BAO · KKZ · NAW

First-class airports (filter rule) per [[station-type-airport-first-class-iata-restriction]]: BKK, DMK, HKT, CNX, HDY, KBV, USM.

### Category 2 — Domestic airports (smaller regional)

TDX (Mae Sot — cross-border gateway), NAW (Narathiwat), UNN (Ranong), UBP (Ubon Ratchathani), SNO (Sakon Nakhon), CEI (Chiang Rai), KOP (Nakhon Phanom), PHS (Phitsanulok), BAO (Buriram), KKZ (Krabi town, dual-role).

### Category 3 — SRT railway terminals

Hua Lamphong / Krung Thep Aphiwat (Bangkok), Chiang Mai, Ayutthaya, Surat Thani, Nakhon Si Thammarat, Hat Yai, Chumphon.

### Category 4 — Intercity bus terminals

Mo Chit · Ekkamai · Sai Tai (Bangkok). Arcade (Chiang Mai). Phra Phrom (Nakhon Si Thammarat). Boromma Trailokanat (Northern route).

### Category 5 — Ferry piers / ports

| Pier | Island / Region |
|---|---|
| Rassada | Phuket |
| Lipa Noi, Bang Rak, Nathon | Koh Samui |
| Mae Haad | Koh Tao |
| Saladan | Koh Lanta |
| Pak Bara, Thung Nang | Satun (Koh Lipe gateway) |
| Ton Sai, Ao Nang, Klong Jilad | Krabi |
| Donsak | Koh Phangan / Koh Samui (Surat Thani) |
| Chumphon | Koh Tao (sleeping ferry) |

### Category 6 — Tourist islands (no airport)

Koh Lipe · Koh Mook · Koh Libong · Koh Yao · Koh Chang · Koh Kood · Koh Mak · Koh Ngai · Koh Bulon · Koh Kradan.

### Category 7 — Top destination cities

Bangkok · Chiang Mai · Phuket · Krabi · Koh Samui · Pattaya · Hua Hin · Koh Phangan · Koh Tao · Pai · Ayutthaya · Sukhothai · Kanchanaburi · Khao Lak · Chiang Rai · Nakhon Si Thammarat · Hat Yai · Trang.

### Category 8 — National parks + UNESCO sites (activity hubs)

Khao Sok · Doi Inthanon · Erawan · Khao Yai · Ayutthaya Historical Park · Sukhothai Historical Park · Phi Phi · Similan Islands · Surin Islands · Railay.

### Category 9 — Cross-border hubs

| Border | Country | Cities |
|---|---|---|
| Laos | LA | Chiang Khong ↔ Huay Xai · Nong Khai ↔ Vientiane · Mukdahan ↔ Savannakhet |
| Cambodia | KH | Poipet ↔ Aranyaprathet · Hat Lek ↔ Koh Kong · O Smach ↔ Chong Sa Ngam |
| Myanmar | MM | Mae Sot ↔ Myawaddy · Mae Sai ↔ Tachileik · Ranong ↔ Kawthaung |
| Malaysia | MY | Sadao ↔ Bukit Kayu Hitam · Betong ↔ Pengkalan Hulu · Wang Prachan ↔ Wang Kelian |

## Decision
Use this reference set as the canonical "what should exist" layer for gap analysis. Compare against Live + Admin layers (see [[live-catalog-discovery-protocol]]). Update when new IATA codes added or cross-border routes emerge.

## Tradeoffs

- **Pro:** Comprehensive coverage of Thailand + bordering countries — supports cross-border audit per user scope.
- **Pro:** Categorized by transport mode (air/rail/bus/ferry) — enables gap pivots per hub type.
- **Con:** Reference set may include locations with near-zero demand — BD team must filter by query_count signal.
- **Con:** Some piers/airports have seasonal-only operators — gap may be seasonal, not structural.

## Related
- [[live-catalog-discovery-protocol]]
- [[three-layer-gap-coverage-matrix]]
- [[transportation-category-audit]]
- [[station-type-airport-first-class-iata-restriction]]
- [[business-development-thailand-platform-analysis]]
- [[products-live-catalog-audit]]