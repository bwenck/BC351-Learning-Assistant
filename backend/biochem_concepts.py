# biochem_concepts.py
"""
Curated biochemical concept triggers + variants
Extend freely — app auto-uses updates
"""

BIO_CONCEPTS = {
    "cancer": {
        # 1️⃣ Uncontrolled cell division
        "uncontrolled cell division": [
            "uncontrolled cell proliferation",
            "uncontrolled proliferation",
            "uncontrolled growth",
            "unchecked cell division",
            "rapid cell division",
            "rapid proliferation",
            "cells divide without stopping",
            "cells divide uncontrollably",
        ],

        # 2️⃣ Cell cycle dysregulation (loss of control)
        "cell cycle dysregulation": [
            "loss of cell cycle control",
            "loss of growth regulation",
            "growth regulation is lost",
            "improper regulation of the cell cycle",
            "cell cycle checkpoints fail",
            "cell cycle control is disrupted",
            "regulatory checkpoints are bypassed",
        ],

        # 3️⃣ Genetic mutations as the underlying cause
        "genetic mutations": [
            "genetic mutations",
            "dna mutations",
            "changes in dna",
            "genomic changes",
            "mutations in key genes",
            "oncogene activation",
            "tumor suppressor loss",
            "mutation of tumor suppressor genes",
        ],

        # 4️⃣ Clonal expansion: one cell → many identical descendants
        "clonal expansion": [
            "clonal expansion",
            "clonal population",
            "clonal growth",
            "monoclonal colonies",
            "monoclonal population",
            "expansion of a single mutated cell",
            "clone of cells derived from one cell",
        ],

        # 5️⃣ Tumor formation as a mass of cells
        "tumor formation": [
            "formation of tumors",
            "tumor formation",
            "forms a tumor mass",
            "forms tumors",
            "neoplasm formation",
            "mass of cells forms",
            "cell mass",
            "tumor or cell mass",
        ],
        "apoptosis evasion": [
            "resists apoptosis", "avoid cell death", "anti-apoptotic"
        ],
        "angiogenesis": [
            "blood vessel growth", "new vasculature"
        ],
        "metastasis": [
            "invasion", "spread to other tissues"
        ],
    },

    "metabolism": {
        "glycolysis": [
            "embden meyerhof", "glucose breakdown", "pyruvate formation"
        ],
        "tca cycle": [
            "citric acid cycle", "krebs cycle"
        ],
        "oxidative phosphorylation": [
            "electron transport chain", "etc", "atp synthase"
        ],
        "enzyme kinetics": [
            "km", "vmax", "michaelis menten", "lineweaver burk"
        ],
    },

    "immunity": {
        "antigen": ["epitope"],
        "antibody": ["immunoglobulin", "igg", "iga", "igm"],
        "t cell": ["cd4", "cd8", "cytotoxic t lymphocyte"],
        "mhc": ["major histocompatibility", "hla"],
        "cytokines": ["il-2", "interleukin", "ifn-gamma"],
    },
}

