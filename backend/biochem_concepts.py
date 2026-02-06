# biochem_concepts.py
"""
Curated biochemical concept triggers + variants
Extend freely — app auto-uses updates

This file is formatted to keep concept synonyms grouped in the same order as Module 01 questions.
"""

BIO_CONCEPTS = {
    "cancer": {
        # ---------------------------
        # Module 01
        # ---------------------------
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

        "genetic/epigenetic changes": [
            "genetic epigenetic changes",
            "genetic/epigenetic changes",
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

        "hallmarks of cancer (overview)": [
            "overview",
            "hallmarks cancer overview",
            "hallmarks of cancer overview",
            "hallmarks of cancer  overview ",
            "hallmarks of cancer (overview)",
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

        "benign vs malignant vs metastatic": [
            "benign malignant metastatic",
            "benign vs malignant vs metastatic",
        ],

        "tissue origin": [
            "tissue origin",
            "tissue of origin",
            "cell type of origin",
            "where it started",
            "what tissue it comes from",
            "originating tissue",
        ],

        "tissue/cell of origin": [
            "tissue cell origin",
            "tissue cell of origin",
            "tissue/cell of origin",
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

        "melanoma/other special categories": [
            "melanoma other special categories",
            "melanoma/other special categories",
        ],

        "grading vs staging (big-picture)": [
            "big-picture",
            "grading staging picture",
            "grading vs staging big picture",
            "grading vs staging big-picture",
            "grading vs staging  big picture ",
            "grading vs staging (big picture)",
            "grading vs staging (big-picture)",
        ],

        # ---------------------------
        # Q3 required_concepts
        # ---------------------------
        "clonal origin": [
            "clonal origin",
            "single cell origin",
            "arise from a single cell",
            "progenitor cell",
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

        "progressive (multi-step) changes": [
            "multi-step",
            "progressive multi step changes",
            "progressive multi-step changes",
            "progressive  multi step  changes",
            "progressive (multi step) changes",
            "progressive (multi-step) changes",
        ],

        "morphological progression": [
            "morphological progression",
            "morphology changes",
            "morphologically",
            "appearance changes",
            "histologic progression",
            "changes in tumor appearance",
            "increasingly abnormal appearance",
        ],

        "morphological progression evidence": [
            "morphological progression evidence",
        ],

        "age correlation": [
            "age correlation",
            "increases with age",
            "more common with age",
            "risk increases with age",
            "age-related increase",
            "older individuals have higher risk",
        ],

        "age-incidence relationship": [
            "incidence relationship",
            "age incidence relationship",
            "age-incidence relationship",
        ],

        "mutation accumulation / selection": [
            "mutation accumulation selection",
            "mutation accumulation   selection",
            "mutation accumulation / selection",
        ],

        "precancerous lesions": [
            "precancerous lesions",
        ],

        # ---------------------------
        # Q4 required_concepts
        # ---------------------------
        "epidemiologic evidence": [
            "population studies",
            "epidemiology studies",
            "epidemiologic studies",
            "epidemiologic evidence",
        ],

        "environment/lifestyle influence": [
            "lifestyle factors",
            "environmental factors",
            "environment and lifestyle",
            "environment lifestyle influence",
            "environment/lifestyle influence",
        ],

        "geographic variation": [
            "geographic variation",
            "variation by location",
            "geographic differences",
            "geography affects cancer types",
        ],

        "migrant studies": [
            "emigration data",
            "migrant studies",
            "immigrant studies",
            "migration studies",
        ],

        "carcinogen categories (chemical/physical/lifestyle)": [
            "chemical",
            "physical",
            "lifestyle",
            "chemical carcinogens",
            "physical carcinogens",
            "lifestyle factors category",
            "carcinogen categories chemical physical lifestyle",
            "carcinogen categories chemical/physical/lifestyle",
            "carcinogen categories  chemical physical lifestyle ",
            "carcinogen categories (chemical physical lifestyle)",
            "carcinogen categories (chemical/physical/lifestyle)",
        ],

        "avoidability estimate (80–90%)": [
            "80–90%",
            "avoidability estimate",
            "avoidability estimate 80 90",
            "avoidability estimate 80-90%",
            "avoidability estimate  80 90  ",
            "avoidability estimate (80-90%)",
            "avoidability estimate (80–90%)",
        ],

        "protective mechanisms": [
            "protective mechanisms",
        ],

        "limits of identifying exact causes": [
            "limits identifying exact causes",
            "limits of identifying exact causes",
        ],

        # ---------------------------
        # Q5 required_concepts
        # ---------------------------
        "limitations of traditional therapies": [
            "older therapies limitations",
            "traditional treatments limited",
            "limits of chemotherapy radiation",
            "limitations traditional therapies",
            "limitations of traditional therapies",
        ],

        "targeting rapid proliferation (historical)": [
            "historical",
            "anti mitotic approach",
            "target rapid cell division",
            "targets proliferating cells",
            "targeting rapid proliferation historical",
            "targeting rapid proliferation  historical ",
            "targeting rapid proliferation (historical)",
        ],

        "molecular understanding shift (post-1975)": [
            "post-1975",
            "modern molecular view",
            "molecular basis discovered",
            "post 1975 molecular understanding",
            "molecular understanding shift 1975",
            "molecular understanding shift post 1975",
            "molecular understanding shift post-1975",
            "molecular understanding shift  post 1975 ",
            "molecular understanding shift (post 1975)",
            "molecular understanding shift (post-1975)",
        ],

        "targeted therapy example (Gleevec/imatinib)": [
            "Gleevec",
            "gleevec",
            "imatinib",
            "bcr abl inhibitor",
            "targeted therapy example Gleevec/imatinib",
            "targeted therapy example gleevec imatinib",
            "targeted therapy example gleevec/imatinib",
            "targeted therapy example  Gleevec imatinib ",
            "targeted therapy example (Gleevec imatinib)",
            "targeted therapy example (Gleevec/imatinib)",
            "targeted therapy example (gleevec imatinib)",
            "targeted therapy example (gleevec/imatinib)",
        ],

        "omics-guided specificity": [
            "genomics proteomics",
            "molecular profiling",
            "omics guided specificity",
            "omics-guided specificity",
            "omics based identification",
        ],

        "drug resistance": [
            "drug resistance",
        ],

        "combination therapy rationale": [
            "multi drug therapy",
            "combination therapy",
            "combination therapy rationale",
            "two or three drugs simultaneously",
        ],

        "early detection/prevention impact": [
            "early detection prevention impact",
            "early detection/prevention impact",
        ],

        "precision medicine": [
            "precision medicine",
        ],

        # ---------------------------
        # Q10 required_concepts
        # ---------------------------
        "targeted response in a subset of patients": [
            "subset responds",
            "partial response",
            "only some patients respond",
            "targeted response subset patients",
            "targeted response in a subset of patients",
        ],

        "initial efficacy vs acquired resistance": [
            "resistance after months",
            "initially effective then resistant",
            "acquired resistance after treatment",
            "initial efficacy acquired resistance",
            "initial efficacy vs acquired resistance",
        ],

        "oncogene addiction concept": [
            "oncogene addiction",
            "single driver dependence",
            "oncogene addiction concept",
            "dependent on single oncoprotein",
        ],

        "tumor heterogeneity": [
            "different subclones",
            "tumor heterogeneity",
            "heterogeneous tumors",
            "genetic heterogeneity",
        ],

        "hope vs concern balance": [
            "hope and worry",
            "mixed outcomes",
            "hope concern balance",
            "hope vs concern balance",
            "reason for hope and concern",
        ],

        "biomarker-driven treatment selection": [
            "biomarker driven treatment selection",
            "biomarker-driven treatment selection",
        ],

        "combination strategies": [
            "combination strategies",
        ],

        # ---------------------------
        # Q11 required_concepts
        # ---------------------------
        "cure vs control framing": [
            "control not cure",
            "cure control framing",
            "curable vs controllable",
            "cure vs control framing",
            "manage like chronic disease",
        ],

        "complexity and number of cancer-related genes": [
            "many cancer genes",
            "hundreds of cancer genes",
            "~300 cancer related genes",
            "complexity number cancer related genes",
            "complexity and number of cancer related genes",
            "complexity and number of cancer-related genes",
        ],

        "promise of targeted therapies": [
            "precision drugs",
            "specific inhibitors",
            "targeted treatments",
            "promise targeted therapies",
            "promise of targeted therapies",
        ],

        "multi-drug therapy rationale": [
            "multiple targets",
            "multi drug approach",
            "multi drug therapy rationale",
            "multi-drug therapy rationale",
            "combination therapy reduces resistance",
        ],

        "omics/personalized medicine": [
            "precision oncology",
            "personalized medicine",
            "omics personalized medicine",
            "omics/personalized medicine",
            "omics tools for individual cancer",
        ],

        "realistic cautious optimism": [
            "realistic cautious optimism",
        ],

        "historical perspective on progress": [
            "historical perspective progress",
            "historical perspective on progress",
        ],

        "future research directions": [
            "future research directions",
        ],

    },

    "drug_design": {
        # ---------------------------
        # Q6 required_concepts
        # ---------------------------
        "start with an active compound": [
            "start active compound",
            "start with an active compound",
        ],

        "identify key active features (pharmacophore/active moiety)": [
            "active moiety",
            "pharmacophore",
            "identify active features pharmacophore active moiety",
            "identify key active features pharmacophore active moiety",
            "identify key active features pharmacophore/active moiety",
            "identify key active features  pharmacophore active moiety ",
            "identify key active features (pharmacophore active moiety)",
            "identify key active features (pharmacophore/active moiety)",
        ],

        "systematic structure modification": [
            "systematic structure modification",
        ],

        "test activity of analogs": [
            "test activity analogs",
            "test activity of analogs",
        ],

        "interpret structure–activity relationships": [
            "interpret structure activity relationships",
            "interpret structure-activity relationships",
            "interpret structure–activity relationships",
        ],

        "Paul Ehrlich and 'magic bullet'": [
            "paul ehrlich magic bullet",
            "paul ehrlich and magic bullet",
            "Paul Ehrlich and  magic bullet ",
            "Paul Ehrlich and 'magic bullet'",
            "paul ehrlich and 'magic bullet'",
        ],

        # ---------------------------
        # Q7 required_concepts
        # ---------------------------
        "in silico / computer-aided drug design": [
            "silico computer aided drug design",
            "in silico computer aided drug design",
            "in silico computer-aided drug design",
            "in silico   computer aided drug design",
            "in silico   computer-aided drug design",
            "in silico / computer aided drug design",
            "in silico / computer-aided drug design",
        ],

        "active-site modeling from structure data": [
            "active site modeling structure data",
            "active site modeling from structure data",
            "active-site modeling from structure data",
        ],

        "combinatorial chemistry": [
            "combinatorial chemistry",
        ],

        "large libraries": [
            "large libraries",
        ],

        "high-throughput screening": [
            "high throughput screening",
            "high-throughput screening",
        ],

        "cost/time reduction mechanisms": [
            "cost time reduction mechanisms",
            "cost/time reduction mechanisms",
        ],

        "lead optimization": [
            "lead optimization",
        ],

        # ---------------------------
        # Q8 required_concepts
        # ---------------------------
        "low molecular weight advantages": [
            "molecular weight advantages",
            "low molecular weight advantages",
        ],

        "tumor/cell penetration": [
            "tumor cell penetration",
            "tumor/cell penetration",
        ],

        "synthesis/manufacturing feasibility": [
            "synthesis manufacturing feasibility",
            "synthesis/manufacturing feasibility",
        ],

        "druggable targets": [
            "druggable targets",
        ],

        "enzyme active sites as binding clefts": [
            "enzyme active sites binding clefts",
            "enzyme active sites as binding clefts",
        ],

        "key target examples (tyrosine kinases, receptors)": [
            "receptors",
            "tyrosine kinases",
            "target examples tyrosine kinases receptors",
            "key target examples tyrosine kinases receptors",
            "key target examples  tyrosine kinases  receptors ",
            "key target examples (tyrosine kinases, receptors)",
        ],

        "non-druggable example idea (Ras active site)": [
            "Ras active site",
            "ras active site",
            "druggable example idea active site",
            "non druggable example idea ras active site",
            "non-druggable example idea Ras active site",
            "non-druggable example idea ras active site",
            "non druggable example idea  Ras active site ",
            "non druggable example idea (Ras active site)",
            "non druggable example idea (ras active site)",
            "non-druggable example idea (Ras active site)",
            "non-druggable example idea (ras active site)",
        ],

        "pharmacokinetics basics": [
            "pharmacokinetics basics",
        ],

        "selectivity/toxicity balance": [
            "selectivity toxicity balance",
            "selectivity/toxicity balance",
        ],

        "selectivity vs potency tradeoff": [
            "selectivity potency tradeoff",
            "selectivity vs potency tradeoff",
        ],

    },

    "drug_development": {
        # ---------------------------
        # Q9 required_concepts
        # ---------------------------
        "target inhibition assays": [
            "target inhibition assays",
        ],

        "cell-based efficacy/specificity testing": [
            "cell based efficacy specificity testing",
            "cell based efficacy/specificity testing",
            "cell-based efficacy specificity testing",
            "cell-based efficacy/specificity testing",
        ],

        "in vivo models (optional)": [
            "optional",
            "vivo models optional",
            "in vivo models optional",
            "in vivo models  optional ",
            "in vivo models (optional)",
        ],

        "nude mouse xenografts": [
            "nude mouse xenografts",
        ],

        "pharmacodynamics/pharmacokinetics and side effects": [
            "pharmacodynamics pharmacokinetics side effects",
            "pharmacodynamics pharmacokinetics and side effects",
            "pharmacodynamics/pharmacokinetics and side effects",
        ],

        "clinical trial phases (I/II/III)": [
            "I",
            "i",
            "II",
            "ii",
            "III",
            "iii",
            "clinical trial phases",
            "clinical trial phases I/II/III",
            "clinical trial phases i ii iii",
            "clinical trial phases i/ii/iii",
            "clinical trial phases  I II III ",
            "clinical trial phases (I II III)",
            "clinical trial phases (I/II/III)",
            "clinical trial phases (i ii iii)",
            "clinical trial phases (i/ii/iii)",
        ],

        "comparison to standard of care": [
            "comparison standard care",
            "comparison to standard of care",
        ],

        "toxicity vs efficacy tradeoff": [
            "toxicity efficacy tradeoff",
            "toxicity vs efficacy tradeoff",
        ],

    },

    "biochem_basics": {
        # ---------------------------
        # Q12 concept keys
        # ---------------------------
        "four macromolecule classes (proteins, lipids, saccharides, nucleic acids)": [
            "lipids",
            "proteins",
            "saccharides",
            "nucleic acids",
            "four macromolecule classes proteins lipids saccharides nucleic acids",
            "four macromolecule classes  proteins  lipids  saccharides  nucleic acids ",
            "four macromolecule classes (proteins, lipids, saccharides, nucleic acids)",
        ],

        "monomer building blocks (amino acids, fatty acids, monosaccharides, nucleotides)": [
            "amino acids",
            "fatty acids",
            "nucleotides",
            "monosaccharides",
            "monomer building blocks amino acids fatty acids monosaccharides nucleotides",
            "monomer building blocks  amino acids  fatty acids  monosaccharides  nucleotides ",
            "monomer building blocks (amino acids, fatty acids, monosaccharides, nucleotides)",
        ],

        "polymer/macromolecule relationships": [
            "polymer macromolecule relationships",
            "polymer/macromolecule relationships",
        ],

        "examples of each class in cells": [
            "examples each class cells",
            "examples of each class in cells",
        ],

        # ---------------------------
        # Q13 concept keys
        # ---------------------------
        "major elements in cells (C, H, O, N)": [
            "C",
            "H",
            "N",
            "O",
            "c",
            "h",
            "n",
            "o",
            "major elements cells",
            "major elements in cells C H O N",
            "major elements in cells c h o n",
            "major elements in cells  C  H  O  N ",
            "major elements in cells (C, H, O, N)",
            "major elements in cells (c, h, o, n)",
        ],

        "water abundance": [
            "water abundance",
        ],

        "organic vs inorganic components": [
            "organic inorganic components",
            "organic vs inorganic components",
        ],

        "valence": [
            "valence",
        ],

        "electronegativity": [
            "electronegativity",
        ],

        "covalent bonding dominance": [
            "covalent bonding dominance",
        ],

        "polar vs nonpolar covalent bonds": [
            "polar nonpolar covalent bonds",
            "polar vs nonpolar covalent bonds",
        ],

        "Earth crust vs cell composition idea": [
            "earth crust cell composition idea",
            "Earth crust vs cell composition idea",
            "earth crust vs cell composition idea",
        ],

        "phosphate chemistry (P in PO4)": [
            "P in PO4",
            "p in po4",
            "phosphate chemistry",
            "phosphate chemistry P in PO4",
            "phosphate chemistry p in po4",
            "phosphate chemistry  P in PO4 ",
            "phosphate chemistry (P in PO4)",
            "phosphate chemistry (p in po4)",
        ],

        # ---------------------------
        # Q14 concept keys
        # ---------------------------
        "water as most abundant molecule": [
            "water abundant molecule",
            "water as most abundant molecule",
        ],

        "dipole/polarity": [
            "dipole polarity",
            "dipole/polarity",
        ],

        "hydrogen bonding capacity": [
            "hydrogen bonding capacity",
        ],

        "amphoteric behavior (acid/base)": [
            "acid",
            "base",
            "amphoteric behavior acid base",
            "amphoteric behavior acid/base",
            "amphoteric behavior  acid base ",
            "amphoteric behavior (acid base)",
            "amphoteric behavior (acid/base)",
        ],

        "autoionization to hydronium/hydroxide": [
            "autoionization hydronium hydroxide",
            "autoionization to hydronium hydroxide",
            "autoionization to hydronium/hydroxide",
        ],

        "relationship to solvent properties": [
            "relationship solvent properties",
            "relationship to solvent properties",
        ],

        # ---------------------------
        # Q15 concept keys
        # ---------------------------
        "hydrogen bonding with polar molecules": [
            "hydrogen bonding polar molecules",
            "hydrogen bonding with polar molecules",
        ],

        "water-water hydrogen bonding network": [
            "water water hydrogen bonding network",
            "water-water hydrogen bonding network",
        ],

        "high specific heat": [
            "high specific heat",
        ],

        "high surface tension": [
            "high surface tension",
        ],

        "high boiling point / liquid at room temp": [
            "high boiling point liquid room temp",
            "high boiling point liquid at room temp",
            "high boiling point   liquid at room temp",
            "high boiling point / liquid at room temp",
        ],

        "solvent behavior": [
            "solvent behavior",
        ],

        "temperature stability for life": [
            "temperature stability life",
            "temperature stability for life",
        ],

        # ---------------------------
        # Q16 concept keys
        # ---------------------------
        "carbon tetravalence (4 covalent bonds)": [
            "4 covalent bonds",
            "carbon tetravalence covalent bonds",
            "carbon tetravalence 4 covalent bonds",
            "carbon tetravalence  4 covalent bonds ",
            "carbon tetravalence (4 covalent bonds)",
        ],

        "single/double/triple bonds": [
            "single double triple bonds",
            "single/double/triple bonds",
        ],

        "tetrahedral geometry & rotation (single bonds)": [
            "single bonds",
            "tetrahedral geometry rotation single bonds",
            "tetrahedral geometry & rotation single bonds",
            "tetrahedral geometry   rotation  single bonds ",
            "tetrahedral geometry & rotation (single bonds)",
        ],

        "planarity & restricted rotation (double/triple bonds)": [
            "double",
            "triple bonds",
            "planarity restricted rotation double triple bonds",
            "planarity & restricted rotation double/triple bonds",
            "planarity   restricted rotation  double triple bonds ",
            "planarity & restricted rotation (double triple bonds)",
            "planarity & restricted rotation (double/triple bonds)",
        ],

        "polymer formation & stability": [
            "polymer formation stability",
            "polymer formation   stability",
            "polymer formation & stability",
        ],

        "branched structures & functional groups": [
            "branched structures functional groups",
            "branched structures   functional groups",
            "branched structures & functional groups",
        ],

        "rings and resonance": [
            "rings resonance",
            "rings and resonance",
        ],

        "carbon's balance of stability and reactivity in water": [
            "carbon balance stability reactivity water",
            "carbon s balance of stability and reactivity in water",
            "carbon's balance of stability and reactivity in water",
        ],

        # ---------------------------
        # Q17 concept keys
        # ---------------------------
        "electronegativity order (O > N > C > H)": [
            "O > N > C > H",
            "o > n > c > h",
            "electronegativity order",
            "electronegativity order o n c h",
            "electronegativity order O > N > C > H",
            "electronegativity order o > n > c > h",
            "electronegativity order  O   N   C   H ",
            "electronegativity order (O > N > C > H)",
            "electronegativity order (o > n > c > h)",
        ],

        "polar covalent bonds": [
            "polar covalent bonds",
        ],

        "nonpolar covalent bonds": [
            "nonpolar covalent bonds",
        ],

        "functional group polarity": [
            "functional group polarity",
        ],

        "consequences for solubility and interactions": [
            "consequences solubility interactions",
            "consequences for solubility and interactions",
        ],

        "partial charges and hydrogen bonding": [
            "partial charges hydrogen bonding",
            "partial charges and hydrogen bonding",
        ],

        # ---------------------------
        # Q19 concept keys
        # ---------------------------
        "limited set of building blocks": [
            "limited building blocks",
            "limited set of building blocks",
        ],

        "conservation through evolution": [
            "conservation through evolution",
        ],

        "functional sufficiency (selection for best function)": [
            "selection for best function",
            "functional sufficiency selection best function",
            "functional sufficiency selection for best function",
            "functional sufficiency  selection for best function ",
            "functional sufficiency (selection for best function)",
        ],

        "historical contingency/path dependence": [
            "historical contingency path dependence",
            "historical contingency/path dependence",
        ],

        "energy/chemistry constraints": [
            "energy chemistry constraints",
            "energy/chemistry constraints",
        ],

        "modular reuse to build diversity": [
            "modular reuse build diversity",
            "modular reuse to build diversity",
        ],

        "metabolic cost and robustness": [
            "metabolic cost robustness",
            "metabolic cost and robustness",
        ],

    },

    "amino_acids": {
        "amino pKa 9.2": [
            "amino 9.2",
            "amino group 9.2",
            "alpha amino 9.2",
            "alpha amino group 9.2",
            "alpha amino pka 9.2",
            "ammonium 9.2",
            "ammonium group 9.2",
            "n terminus amino 9.2",
            "n terminal amino 9.2",
            "amino terminus 9.2",
            "amino is 9.2",
            "nh3 9.2",
            "nh3+ 9.2",
            "nh3 pka 9.2",
            "nh3 is 9.2",
            "nh3+ pka 9.2",
            "nh3+ is 9.2",
        ],

        "carboxyl pKa 1.8": [
            "carboxyl 1.8",
            "carboxyl group 1.8",
            "alpha carboxyl 1.8",
            "alpha carboxyl group 1.8",
            "alpha carboxyl pKa 1.8",
            "c terminus carboxyl 1.8",
            "c terminal carboxyl 1.8",
            "carboxyl terminus 1.8",
            "carboxyl is 1.8",
            "carboxylic acid 1.8",
            "carboxylic acid group 1.8",
            "cooh 1.8",
            "cooh pka 1.8",
            "cooh is 1.8",
        ],

    },

    "acid_base": {
        "net charge equals 0": [
            "net charge is 0",
            "overall net charge is 0",
            "overall charge is 0",
            "net charge 0",
            "neutral net charge",
            "overall charge is neutral",
            "net charge is neutral",
            "no net charge",
            "uncharged overall",
            "overall neutral",
            "zwitterion (net 0)",
        ],

    },

    "metabolism": {
        "enzyme kinetics": [
            "km",
            "vmax",
            "michaelis menten",
            "lineweaver burk",
        ],

        "glycolysis": [
            "embden meyerhof",
            "glucose breakdown",
            "pyruvate formation",
        ],

        "oxidative phosphorylation": [
            "electron transport chain",
            "etc",
            "atp synthase",
        ],

        "tca cycle": [
            "citric acid cycle",
            "krebs cycle",
        ],

    },

    "immunity": {
        "antibody": [
            "immunoglobulin",
            "igg",
            "iga",
            "igm",
        ],

        "antigen": [
            "epitope",
        ],

        "cytokines": [
            "il-2",
            "interleukin",
            "ifn-gamma",
        ],

        "mhc": [
            "major histocompatibility",
            "hla",
        ],

        "t cell": [
            "cd4",
            "cd8",
            "cytotoxic t lymphocyte",
        ],

    },
}