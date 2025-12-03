"""Produktkatalog för Bengtssons Trävaror.

Format: produktnamn: (pris i SEK, dimension i meter/kvm eller None för styckvaror)

Priser uppdaterade december 2025 baserat på marknadspriser från Byggmax, Beijer m.fl.
"""

PRODUCTS = {
    # --- VIRKE / TRÄ ---
    # Reglar prissatta per styck baserat på ca 15-45 kr/m beroende på dimension
    "regel_45x45_3m": (55, 3.0),       # ~18 kr/m
    "regel_45x45_3.6m": (65, 3.6),     # ~18 kr/m
    "regel_45x45_4.2m": (75, 4.2),     # ~18 kr/m
    "regel_45x45_4.8m": (85, 4.8),     # ~18 kr/m
    "regel_45x70_3m": (75, 3.0),       # ~25 kr/m
    "regel_45x70_3.6m": (90, 3.6),     # ~25 kr/m
    "regel_45x70_4.2m": (105, 4.2),    # ~25 kr/m
    "regel_45x70_4.8m": (120, 4.8),    # ~25 kr/m
    "regel_45x95_3m": (95, 3.0),       # ~32 kr/m (C24)
    "regel_45x95_3.6m": (115, 3.6),    # ~32 kr/m
    "regel_45x95_4.2m": (135, 4.2),    # ~32 kr/m
    "regel_45x95_4.8m": (155, 4.8),    # ~32 kr/m
    "regel_45x120_3m": (115, 3.0),     # ~38 kr/m
    "regel_45x120_3.6m": (140, 3.6),   # ~38 kr/m
    "regel_45x120_4.2m": (160, 4.2),   # ~38 kr/m
    "regel_45x120_4.8m": (185, 4.8),   # ~38 kr/m
    "regel_45x145_3m": (130, 3.0),     # ~43 kr/m (C24)
    "regel_45x145_3.6m": (155, 3.6),   # ~43 kr/m
    "regel_45x145_4.2m": (180, 4.2),   # ~43 kr/m
    "regel_45x145_4.8m": (210, 4.8),   # ~43 kr/m
    "regel_45x170_3m": (150, 3.0),     # ~50 kr/m
    "regel_45x170_3.6m": (180, 3.6),   # ~50 kr/m
    "regel_45x170_4.2m": (210, 4.2),   # ~50 kr/m
    "regel_45x170_4.8m": (240, 4.8),   # ~50 kr/m
    "regel_45x195_3m": (175, 3.0),     # ~58 kr/m
    "regel_45x195_4.8m": (280, 4.8),   # ~58 kr/m

    # Brädor
    "bräda_22x95_3m": (45, 3.0),       # ~15 kr/m
    "bräda_22x120_3m": (55, 3.0),      # ~18 kr/m
    "bräda_22x145_3m": (65, 3.0),      # ~22 kr/m
    "bräda_22x145_4.8m": (105, 4.8),   # ~22 kr/m
    "bräda_22x170_3m": (75, 3.0),      # ~25 kr/m

    # Tryckimpregnerat (NTR-AB, ca 40-50% dyrare)
    "regel_tryckimp_45x95_3m": (145, 3.0),    # ~48 kr/m
    "regel_tryckimp_45x95_4.2m": (200, 4.2),  # ~48 kr/m
    "regel_tryckimp_45x145_3m": (195, 3.0),   # ~65 kr/m
    "bräda_tryckimp_22x120_3m": (95, 3.0),    # ~32 kr/m

    # --- SKIVMATERIAL ---
    # Priser per skiva (standardstorlek ca 2400x1200 = 2.88 kvm, avrundas till 2.0 kvm för enkelhet)
    "plywood_12mm": (349, 2.0),        # Konstruktionsplywood
    "plywood_15mm": (429, 2.0),
    "plywood_18mm": (499, 2.0),
    "osb_11mm": (219, 2.0),            # OSB3
    "osb_18mm": (329, 2.0),
    "masonit_3mm": (79, 2.0),
    "spånskiva_16mm": (189, 2.0),
    "spånskiva_22mm": (249, 2.0),
    "gipsskiva_13mm": (109, 2.0),      # Standard 900x2500
    "gipsskiva_13mm_våtrum": (159, 2.0),

    # --- ISOLERING ---
    # Priser per paket (täcker angiven yta i kvm)
    "isolering_mineralull_45mm": (289, 5.5),   # Isover/URSA
    "isolering_mineralull_95mm": (449, 4.3),
    "isolering_mineralull_120mm": (529, 3.4),
    "isolering_mineralull_145mm": (629, 2.7),
    "isolering_mineralull_195mm": (749, 2.0),
    "isolering_glasull_95mm": (399, 4.3),
    "isolering_träfiber_45mm": (549, 2.7),     # Dyrare men ekologiskt
    "isolering_träfiber_145mm": (1249, 1.8),

    # --- TAK / PANEL ---
    "takpapp_rulle_10m": (349, 10),    # YEP 2500, 1m bred
    "takpapp_rulle_20m": (649, 20),
    "underlagspapp_rulle": (289, 15),
    "takläkt_25x38_4.2m": (35, None),  # Per styck
    "takläkt_25x50_4.2m": (45, None),
    "råspont_21x95_3m": (69, None),    # Per styck, lös råspont
    "råspont_21x120_3m": (89, None),
    "råspont_21x145_3m": (109, None),
    # Råspontluckor (540mm bred, sammanfogad för snabbare takläggning)
    "råspontlucka_20x540_3.6m": (159, 1.94),   # ~82 kr/kvm
    "råspontlucka_20x540_4.2m": (189, 2.27),   # ~83 kr/kvm
    "råspontlucka_20x540_4.8m": (215, 2.59),   # ~83 kr/kvm
    "råspontlucka_23x540_3.6m": (189, 1.94),   # Tjockare, ~97 kr/kvm
    "råspontlucka_23x540_4.2m": (225, 2.27),
    "råspontlucka_23x540_4.8m": (259, 2.59),
    "ytterpanel_14x120_3m": (95, None),
    "ytterpanel_14x145_3m": (115, None),
    "innerpanel_14x95_3m": (75, None),
    "innerpanel_14x120_3m": (89, None),

    # --- GOLV ---
    "golvspånskiva_22mm": (159, 1.1),  # 620x1820mm = 1.13 kvm
    "parkettgolv_ek_3stav": (449, 2.2),
    "parkettgolv_ask": (529, 2.2),
    "laminatgolv_ek": (249, 2.0),
    "laminatgolv_grå": (219, 2.0),
    "undergolv_3mm": (89, 10.0),       # Rulle

    # --- LISTER ---
    "sockel_vit_12x56_2.4m": (79, None),
    "sockel_vit_14x70_2.4m": (99, None),
    "foder_vit_12x56_2.2m": (69, None),
    "taklist_vit_21x21_2.4m": (49, None),

    # --- FÄSTDON ---
    # Priser per låda/förpackning
    "spik_blank_50mm_5kg": (249, None),
    "spik_blank_75mm_5kg": (279, None),
    "spik_varmförz_75mm_5kg": (349, None),
    "skruv_trä_4x40_500st": (199, None),
    "skruv_trä_4x50_500st": (219, None),
    "skruv_trä_5x60_200st": (189, None),
    "skruv_trä_5x80_200st": (219, None),
    "skruv_trä_6x100_100st": (179, None),
    "skruv_trä_6x120_100st": (199, None),
    "skruv_gips_3.5x35_1000st": (149, None),
    "skruv_gips_3.5x45_500st": (129, None),
    "skruv_trall_4.5x55_250st": (249, None),  # A4 rostfri
    "skruv_trall_4.5x65_250st": (279, None),

    # --- BESLAG ---
    "vinkel_50x50x40": (12, None),
    "vinkel_70x70x55": (18, None),
    "vinkel_90x90x65": (25, None),
    "balksko_45x145": (35, None),
    "balksko_45x195": (45, None),
    "sparrplåt": (29, None),
    "universalankare": (22, None),

    # --- ÖVRIGT ---
    "byggplast_0.2mm_50kvm": (549, 50),
    "diffusionsspärr_25kvm": (449, 25),
    "trälim_750ml": (89, None),
    "trälim_3l": (249, None),
    "fogskum_750ml": (79, None),
    "betong_torr_25kg": (79, None),
    "betong_snabb_25kg": (119, None),
    "puts_vägg_25kg": (149, None),
}
