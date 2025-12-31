# biochem_concepts.py
"""
Curated biochemical concept triggers + variants
Extend freely — app auto-uses updates
"""

BIO_CONCEPTS = {
    "cancer": {
        # ---------------------------
        # Q1 concept keys
        # ---------------------------
        "uncontrolled proliferation": [
            "uncontrolled cell proliferation",
            "uncontrolled proliferation",
            "uncontrolled growth",
            "unchecked cell division",
            "rapid cell division",
            "rapid proliferation",
            "cells divide without stopping",
            "cells divide uncontrollably",
        ],

        "regulation breakdown": [
            "loss of cell cycle control",
            "loss of growth regulation",
            "growth regulation is lost",
            "improper regulation of the cell cycle",
            "cell cycle checkpoints fail",
            "cell cycle control is disrupted",
            "regulatory checkpoints are bypassed",
            "breakdown in regulation",
            "loss of proper regulation",
        ],

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

        "clonal expansion": [
            "clonal expansion",
            "clonal population",
            "clonal growth",
            "monoclonal colonies",
            "monoclonal population",
            "expansion of a single mutated cell",
            "clone of cells derived from one cell",
            "single cell gives rise to many",
        ],

        "tumor formation": [
            "formation of tumors",
            "tumor formation",
            "forms a tumor mass",
            "forms tumors",
            "neoplasm formation",
            "mass of cells forms",
            "cell mass",
            "tumor or cell mass",
            "tumor development",
        ],

        # ---------------------------
        # Q2 required_concepts
        # ---------------------------
        "histological classification": [
            "histological classification",
            "histology",
            "classified by histology",
            "microscopic appearance",
            "tissue microscopy",
            "pathology under the microscope",
        ],

        "benign": [
            "benign",
            "noninvasive",
            "does not invade",
            "localized growth",
            "not invasive",
        ],

        "malignant": [
            "malignant",
            "invasive",
            "invades",
            "can invade surrounding tissue",
            "can spread",
        ],

        "tissue origin": [
            "tissue origin",
            "tissue of origin",
            "cell type of origin",
            "where it started",
            "what tissue it comes from",
            "originating tissue",
        ],

        "carcinomas": [
            "carcinoma",
            "carcinomas",
            "epithelial cancer",
            "epithelium",
            "from epithelial tissue",
            "surface lining tissue",
        ],

        "sarcomas": [
            "sarcoma",
            "sarcomas",
            "connective tissue cancer",
            "mesenchymal",
            "bone cancer",
            "cartilage cancer",
            "muscle cancer",
            "from connective tissue",
        ],

        # ---------------------------
        # Q3 required_concepts
        # ---------------------------
        "clonal origin": [
            "clonal origin",
            "single cell origin",
            "arise from a single cell",
            "one cell gives rise",
            "monoclonal origin",
        ],

        "progressive changes": [
            "progressive changes",
            "accumulation of changes",
            "stepwise changes",
            "multiple changes over time",
            "progression of changes",
        ],

        "morphological progression": [
            "morphological progression",
            "morphology changes",
            "appearance changes",
            "histologic progression",
            "changes in tumor appearance",
            "increasingly abnormal appearance",
        ],

        "age correlation": [
            "age correlation",
            "increases with age",
            "more common with age",
            "risk increases with age",
            "age-related increase",
            "older individuals have higher risk",
        ],
    },

    "metabolism": {
        "glycolysis": ["embden meyerhof", "glucose breakdown", "pyruvate formation"],
        "tca cycle": ["citric acid cycle", "krebs cycle"],
        "oxidative phosphorylation": ["electron transport chain", "etc", "atp synthase"],
        "enzyme kinetics": ["km", "vmax", "michaelis menten", "lineweaver burk"],
    },

    "immunity": {
        "antigen": ["epitope"],
        "antibody": ["immunoglobulin", "igg", "iga", "igm"],
        "t cell": ["cd4", "cd8", "cytotoxic t lymphocyte"],
        "mhc": ["major histocompatibility", "hla"],
        "cytokines": ["il-2", "interleukin", "ifn-gamma"],
    },
}


