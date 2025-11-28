"""Produktkatalog för Bengtssons Trävaror.

Format: produktnamn: (pris i SEK, dimension i meter/kvm eller None för styckvaror)
"""

PRODUCTS = {
    # --- VIRKE / TRÄ ---
    "regel_45x45_3m": (35, 3.0),
    "regel_45x45_3.6m": (45, 3.6),
    "regel_45x45_4.2m": (55, 4.2),
    "regel_45x45_4.8m": (65, 4.8),
    "regel_45x70_3m": (45, 3.0),
    "regel_45x70_3.6m": (55, 3.6),
    "regel_45x70_4.2m": (65, 4.2),
    "regel_45x70_4.8m": (75, 4.8),
    "regel_45x95_3m": (65, 3.0),
    "regel_45x95_3.6m": (85, 3.6),
    "regel_45x95_4.2m": (105, 4.2),
    "regel_45x95_4.8m": (125, 4.8),
    "regel_45x120_3m": (70, 3.0),
    "regel_45x120_3.6m": (90, 3.6),
    "regel_45x120_4.2m": (110, 4.2),
    "regel_45x120_4.8m": (130, 4.8),
    "regel_45x145_3m": (80, 3.0),
    "regel_45x145_3.6m": (110, 3.6),
    "regel_45x145_4.2m": (140, 4.2),
    "regel_45x145_4.8m": (170, 4.8),
    "regel_45x170_3m": (90, 3.0),
    "regel_45x170_3.6m": (125, 3.6),
    "regel_45x170_4.2m": (160, 4.2),
    "regel_45x170_4.8m": (195, 4.8),
    "bräda_22x45": (25, 3.0),
    "bräda_22x70": (35, 3.6),
    "bräda_22x95": (45, 4.2),
    "bräda_22x120": (55, 4.8),
    "bräda_22x145_3m": (65, 3.0),
    "bräda_22x145_5.2m": (125, 5.2),
    "bräda_22x170": (35, 3.6),
    "bräda_22x195": (55, 4.2),
    "bräda_22x220": (75, 4.8),
    "regel_tryckimp_45x95": (65, 4.2),
    "bräda_tryckimp_22x120": (75, 4.8),

    # --- SKIVMATERIAL ---
    "plywood_12mm": (250, 2.0),
    "plywood_15mm": (320, 2.0),
    "plywood_18mm": (390, 2.0),
    "osb_11mm": (180, 2.0),
    "osb_15mm": (230, 2.0),
    "masonit_3mm": (90, 2.0),
    "spånskiva_16mm": (210, 2.0),
    "gipsskiva_13mm": (95, 2.0),
    "råspontlucka_21x95": (65, 1.5),

    # --- ISOLERING ---
    "isolering_mineralull_45mm": (320, 4.0),
    "isolering_mineralull_95mm": (520, 4.0),
    "isolering_mineralull_145mm": (780, 4.0),
    "isolering_träfiber_45mm": (420, 2.0),
    "isolering_träfiber_145mm": (950, 2.0),
    "isolering_glasull_95mm": (540, 4.0),

    # --- TAK / PANEL ---
    "takpapp_rulle": (420, 20),
    "takläkt_25x38_3m": (20, None),
    "råspont_21x95_3m": (65, 1.5),
    "innertakspanel_14x120_3m": (95, 2.0),

    # --- GOLV / INVÄNDIGT ---
    "golvspånskiva_22mm": (260, 2.0),
    "parkettgolv_ek": (420, 2.0),
    "laminatgolv_grå": (290, 2.0),
    "sockel_vit_12x56_3m": (45, None),
    "list_foder_12x56_3m": (40, None),

    # --- FÄSTDON ---
    "spiklåda_45mm": (220, None),
    "spiklåda_55mm": (250, None),
    "spiklåda_70mm": (300, None),
    "spiklåda_90mm": (360, None),
    "skruvlåda_trä_4x40": (240, None),
    "skruvlåda_trä_4x55": (260, None),
    "skruvlåda_trä_5x70": (290, None),
    "skruvlåda_trä_6x90": (390, None),
    "skruvlåda_trä_6x120": (490, None),
    "skruvlåda_gips_3.9x30": (190, None),
    "ankarskruv_5x40": (310, None),

    # --- ÖVRIGT ---
    "regelvinkel_90grad": (25, None),
    "plåtvinkel_förzinkad": (35, None),
    "byggplast_0.2mm": (450, 50),
    "trälim_1l": (110, None),
    "spikband_1m": (30, None),
    "betongblandning_25kg": (85, None),
}
