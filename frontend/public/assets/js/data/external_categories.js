/* eslint-disable */
/**
 * external_categories.js — External Engine V2
 * Frozen categories + recognizers + seed gazetteers + helpers.
 *
 * Integration notes (unchanged):
 *  - Engine treats 1–6 token anchors as candidates.
 *  - A term qualifies if ANY is true:
 *      (1) Exact match in the External Bucket (right panel)
 *      (2) Exact match in a category gazetteer (seeds + promoted terms)
 *      (3) Match to a category recognizer regex (provisional)
 *  - Rejections/caps/spacing windows are enforced in app.js.
 */

/* -----------------------------------------------------------
   1) FROZEN CATEGORIES (keep in sync with recognizers)
   ----------------------------------------------------------- */

export const EXTERNAL_CATEGORY_WHITELIST = [
  // ——— Geography, Places, Environment (1–80) ———
  'Countries',
  'Continents',
  'Capital cities',
  'Major world cities',
  'US states',
  'Canadian provinces and territories',
  'Australian states and territories',
  'Indian states and union territories',
  'Chinese provinces and regions',
  'Administrative regions (global)',
  'Rivers',
  'Lakes',
  'Seas and oceans',
  'Gulfs and bays',
  'Straits and channels',
  'Mountain ranges',
  'Mountains and peaks',
  'Volcanoes',
  'Islands and archipelagos',
  'Peninsulas',
  'Deserts',
  'Forests',
  'Savannas and grasslands',
  'Wetlands',
  'Glaciers and ice sheets',
  'Coral reefs',
  'Caves and karst systems',
  'Waterfalls',
  'Deltas and estuaries',
  'Fjords',
  'Ecoregions',
  'Biomes',
  'Climate zones',
  'Time zones',
  'Urban neighborhoods',
  'Metropolitan areas',
  'Rural settlements',
  'UNESCO World Heritage Sites',
  'National parks',
  'Nature reserves',
  'Biosphere reserves',
  'Protected area categories',
  'Ramsar sites',
  'Geologic eras and periods',
  'Rock types',
  'Mineral types',
  'Soil types',
  'Landforms',
  'Tectonic plates',
  'Earthquakes and fault systems',
  'Hydrologic features',
  'Watersheds and river basins',
  'Aquifers and groundwater systems',
  'Atmospheric circulation features',
  'Ocean currents',
  'El Niño–La Niña phenomena',
  'Drought indices',
  'Wildfire classifications',
  'Air quality indices',
  'Water quality parameters',
  'Environmental treaties',
  'Pollutants and contaminants',
  'Waste management methods',
  'Recycling processes',
  'Sustainability frameworks',
  'Renewable energy sources',
  'Nonrenewable energy sources',
  'Carbon accounting concepts',
  'Ecosystem services',
  'Endangered species lists',
  'Invasive species lists',
  'Conservation status categories',
  'Habitat fragmentation concepts',
  'Wildlife corridors',
  'Nature-based solutions',
  'Climate adaptation strategies',
  'Climate mitigation strategies',
  'Disaster risk reduction concepts',
  'Early warning systems',
  'Resilience frameworks',
  'Urban ecology concepts',
  'Blue-green infrastructure',

  // ——— Astronomy & Space (81–110) ———
  'Constellations',
  'Stars and stellar classes',
  'Planets',
  'Dwarf planets',
  'Natural satellites (moons)',
  'Asteroids',
  'Comets',
  'Meteors and meteor showers',
  'Galaxies',
  'Nebulae',
  'Space missions and probes',
  'Space telescopes',
  'Launch vehicles and rockets',
  'Space agencies',
  'Orbital mechanics concepts',
  'Exoplanets',
  'Astronomical observatories',
  'Cosmology concepts',
  'Radio astronomy terms',
  'Astrobiology concepts',
  'Space weather phenomena',
  'Planetary geology',
  'Satellite systems',
  'GNSS constellations',
  'Space law and policy',

  // ——— Biology: Taxonomy & Life Sciences (111–170) ———
  'Taxonomic ranks',
  'Species concepts',
  'Animal phyla',
  'Mammal families',
  'Bird families',
  'Reptile families',
  'Amphibian families',
  'Fish families',
  'Insect orders',
  'Arachnid groups',
  'Plant families',
  'Flowering plant orders',
  'Conifers and gymnosperms',
  'Ferns and allies',
  'Mosses and liverworts',
  'Fungi groups',
  'Lichens',
  'Microalgae and phytoplankton',
  'Corals and cnidarians',
  'Sponges (Porifera)',
  'Echinoderms',
  'Mollusks',
  'Annelids',
  'Arthropods (overview)',
  'Cephalopods',
  'Species interactions',
  'Population ecology terms',
  'Community ecology terms',
  'Ecosystem ecology terms',
  'Landscape ecology concepts',
  'Restoration ecology methods',
  'Biodiversity indicators',

  // ——— Human Anatomy & Physiology (171–205) ———
  'Organ systems',
  'Human organs',
  'Skeletal anatomy',
  'Muscular anatomy',
  'Nervous system structures',
  'Endocrine system hormones',
  'Cardiovascular structures',
  'Respiratory structures',
  'Digestive system structures',
  'Renal and urinary structures',
  'Reproductive system structures',
  'Sensory organs',
  'Blood components',
  'Immune system components',
  'Dermatologic structures',
  'Developmental stages',
  'Anatomical planes and positions',
  'Histology tissue types',
  'Homeostasis mechanisms',
  'Physiology measurements',
  'Medical imaging modalities',
  'Anesthesia types',

  // ——— Genetics, Molecular & Cell Biology (206–250) ———
  'DNA and RNA types',
  'Genes and alleles',
  'Chromosomal abnormalities',
  'Mendelian inheritance patterns',
  'Genetic disorders',
  'Genotyping methods',
  'Sequencing technologies',
  'CRISPR and gene editing concepts',
  'Gene expression mechanisms',
  'Transcription and translation',
  'Epigenetics concepts',
  'Proteins and enzymes',
  'Protein domains and motifs',
  'Metabolic pathways',
  'Signal transduction pathways',
  'Cell cycle phases',
  'Cell organelles',
  'Stem cell types',
  'Immunogenetics concepts',
  'Population genetics terms',
  'Phylogenetics concepts',
  'Bioinformatics concepts',
  'Omics fields',
  'Biomarkers',
  'Molecular diagnostics',

  // ——— Infectious Disease & Public Health (251–295) ———
  'Bacteria groups',
  'Archaea groups',
  'Viruses and viral families',
  'Fungi (pathogenic)',
  'Parasites and protozoa',
  'Prions',
  'Infectious disease syndromes',
  'Routes of transmission',
  'Antimicrobial resistance mechanisms',
  'Disinfection and sterilization methods',
  'Vaccines and immunization schedules',
  'Viral hepatitis types',
  'Respiratory pathogens',
  'Enteric pathogens',
  'Vector-borne diseases',
  'Zoonotic diseases',
  'Healthcare-associated infections',
  'Public health surveillance terms',
  'Outbreak investigation terms',
  'Epidemiologic measures',
  'Quarantine and isolation concepts',
  'Laboratory test panels',
  'Point-of-care tests',
  'Diagnostic culture methods',
  'Antigen and antibody tests',

  // ——— Clinical Medicine (296–350) ———
  'Clinical specialties',
  'Medical subspecialties',
  'Primary symptoms and signs',
  'Syndromes (non-infectious)',
  'Diagnostic criteria sets',
  'Clinical scoring systems',
  'Physical examination maneuvers',
  'Lab test analytes',
  'Imaging findings',
  'Differential diagnosis frameworks',
  'Medical devices (general)',
  'Therapeutic procedures',
  'Rehabilitation modalities',
  'Nutrition therapy concepts',
  'Psychological therapies',
  'Complementary and integrative therapies',
  'Palliative care concepts',
  'Emergency medicine protocols',
  'Critical care concepts',
  'Anesthesiology concepts',
  'Pain types and scales',
  'Oncology tumor types',
  'Radiation therapy concepts',
  'Transplant medicine concepts',
  'Pharmacokinetics and pharmacodynamics',
  'Drug classes (ATC-like, non-coded)',
  'Generic drug names',
  'Biologics and biosimilars',
  'Vaccines (therapeutic and prophylactic)',
  'Herbal medicines',
  'Over-the-counter medicines',
  'Prescription drug forms',
  'Routes of administration',
  'Adverse drug reactions (types)',
  'Drug interactions (mechanistic)',
  'Black box warnings (themes)',
  'Contraindications (common)',
  'Therapeutic drug monitoring targets',
  'Antibiotic stewardship concepts',
  'Analgesics and antipyretics',
  'Antidepressant classes',
  'Antihypertensives classes',
  'Antidiabetics classes',
  'Anticoagulants and antiplatelets',
  'Asthma and COPD therapies',
  'Gastrointestinal therapies',
  'Dermatologic therapies',
  'Ophthalmic therapies',
  'Otolaryngologic therapies',
  'Pediatric dosing concepts',

  // ——— Psychology & Behavioral Sciences (351–380) ———
  'Psychological constructs',
  'Psychiatric disorders (DSM-style, non-coded)',
  'Psychotherapy modalities',
  'Behavioral therapies',
  'Neurodevelopmental conditions',
  'Neurocognitive disorders',
  'Mood disorders',
  'Anxiety disorders',
  'Trauma- and stressor-related disorders',
  'Personality disorders',
  'Sleep disorders (clinical)',
  'Addiction and substance use concepts',
  'Psychological testing instruments',
  'Neuropsychological tests',
  'Mindfulness and meditation practices',
  'Stress physiology concepts',
  'Human development stages',
  'Family therapy concepts',
  'Group dynamics concepts',
  'Social psychology phenomena',
  'Cognitive biases',
  'Learning theories',
  'Motivation theories',
  'Emotion theories',
  'Psychometrics concepts',
  'Educational psychology concepts',
  'Special education concepts',
  'Child development milestones',
  'Work and organizational psychology',

  // ——— Food, Nutrition & Agriculture (381–420) ———
  'Macronutrients',
  'Micronutrients',
  'Vitamins and minerals',
  'Dietary patterns',
  'Special diets (clinical)',
  'Food groups',
  'Food-borne illnesses',
  'Food preservation methods',
  'Food processing methods',
  'Culinary techniques',
  'Spices and herbs',
  'Fermented foods',
  'Functional foods',
  'Nutrition assessment tools',
  'Anthropometric measures',
  'Glycemic index concepts',
  'Food allergies and intolerances',
  'Enteral and parenteral nutrition',
  'Infant feeding practices',
  'Sports nutrition concepts',
  'Hydration strategies',
  'Food labeling terms',
  'Sustainable agriculture practices',
  'Organic farming concepts',
  'Food security concepts',
  'Crop types',
  'Horticulture categories',
  'Agroforestry systems',
  'Soil amendments and fertilizers',
  'Irrigation methods',
  'Integrated pest management concepts',
  'Aquaculture systems',
  'Fisheries management terms',
  'Livestock breeds (generic groups)',
  'Dairy production concepts',
  'Apiculture concepts',
  'Agroecology concepts',
  'Rangeland management',
  'Sustainable forestry practices',
  'Watershed management concepts',
  'Erosion control methods',

  // ——— Chemistry, Physics, Materials (421–455) ———
  'Periodic table groups (plain names)',
  'Chemical elements',
  'Chemical bonding concepts',
  'Organic functional groups',
  'Polymers and plastics types',
  'Composite materials',
  'Ceramics and glasses',
  'Metals and alloys groups',
  'Corrosion types',
  'Electrochemistry concepts',
  'Catalysis concepts',
  'Chemical reaction types',
  'Laboratory techniques (chemistry)',
  'Analytical chemistry methods',
  'Spectroscopy methods',
  'Chromatography methods',
  'Nanomaterials types',
  'Battery chemistries',
  'Fuel types',
  'Paints and coatings types',
  'Adhesives and sealants',
  'Industrial gases',
  'Green chemistry principles',
  'Process safety concepts',
  'Material fatigue and failure modes',
  'Thermodynamics concepts',
  'Classical mechanics concepts',
  'Electromagnetism concepts',
  'Optics concepts',
  'Quantum concepts',
  'Statistical mechanics concepts',
  'Solid-state physics concepts',
  'Fluid dynamics concepts',
  'Acoustics concepts',
  'Nuclear physics concepts',

  // ——— Math, CS, Data, Cyber (456–490) ———
  'Mathematical fields',
  'Algebra concepts',
  'Calculus concepts',
  'Geometry concepts',
  'Topology concepts',
  'Number theory concepts',
  'Probability concepts',
  'Statistics concepts',
  'Numerical methods',
  'Operations research concepts',
  'Chaos and dynamical systems',
  'Control theory concepts',
  'Signal processing concepts',
  'Information theory concepts',
  'Computer architecture concepts',
  'Operating system concepts',
  'Networking concepts (non-protocol lists)',
  'Database concepts',
  'Data modeling concepts',
  'Data structures (generic)',
  'Algorithms (generic)',
  'Machine learning tasks',
  'Evaluation metrics (ML)',
  'Model validation concepts',
  'Feature engineering concepts',
  'Neural network architectures (generic)',
  'Natural language processing tasks',
  'Computer vision tasks',
  'Reinforcement learning concepts',
  'Software development lifecycles',
  'Testing methodologies',
  'DevOps concepts',
  'Cloud service models',
  'Virtualization and containers (generic)',
  'API design concepts',
  'Cybersecurity concepts (high-level)',
  'Digital identity concepts',
  'Data governance concepts',
  'Data privacy concepts',
  'Cryptography concepts',
  'Secure software design principles',
  'Incident response concepts',
  'Threat modeling concepts',
  'Security testing methodologies',
  'Security compliance frameworks',
  'Digital forensics concepts',

  // ——— Engineering, Built Env, Transport, Econ, Law (491–500) ———
  'Mechanical components (generic)',
  'Manufacturing processes',
  'Quality management frameworks',
  'Reliability engineering concepts',
  'Lean and Six Sigma concepts',
  'Additive manufacturing concepts',
  'Metrology concepts',
  'Industrial automation components',
  'Robotics concepts',
  'Human factors and ergonomics',
  'Systems engineering concepts',
  'Project management frameworks',
  'Risk management frameworks',
  'Supply chain concepts',
  'Logistics concepts',
  'Maintenance strategies',
  'Asset management concepts',
  'Facility management concepts',
  'Building services engineering',
  'HVAC concepts',
  'Civil engineering structures',
  'Geotechnical concepts',
  'Transportation engineering concepts',
  'Water resources engineering',
  'Coastal engineering concepts',
  'Architectural styles',
  'Building materials (generic)',
  'Construction methods (generic)',
  'Structural systems (generic)',
  'Sustainable building practices',
  'Building performance metrics',
  'Urban planning theories',
  'Zoning and land-use concepts',
  'Transit-oriented development concepts',
  'Public space typologies',
  'Green building certifications',
  'Energy efficiency measures',
  'Smart city concepts',
  'Urban design elements',
  'Landscape architecture elements',
  'Heritage conservation concepts',
  'Disaster-resilient design concepts',
  'Accessibility design concepts',
  'Wayfinding and signage concepts',
  'Housing typologies',
  'Informal settlement concepts',
  'Urban governance frameworks',
  'Cultural landscape concepts',
  'Participatory planning methods',
  'Urban ecology design elements',
  'Roadway classifications',
  'Rail systems (generic)',
  'Maritime transport concepts',
  'Aviation concepts (non-aircraft codes)',
  'Public transit modes',
  'Micromobility modes',
  'Traffic engineering concepts',
  'Transport safety concepts',
  'Intelligent transport systems',
  'Logistics hubs and nodes',
  'Freight transport modes',
  'Port operations concepts',
  'Air traffic management concepts',
  'Vehicle powertrains (generic)',
  'Alternative fuels (transport)',
  'Autonomous vehicle concepts',
  'Telematics concepts',
  'Transportation demand management',
  'Parking management strategies',
  'Last-mile delivery concepts',
  'Cold chain logistics',
  'Supply chain visibility concepts',
  'Customs and trade facilitation concepts',
  'Incoterms (general categories)',
  'Humanitarian logistics concepts',
  'Macroeconomic indicators',
  'Microeconomic concepts',
  'International trade concepts',
  'Development economics concepts',
  'Behavioral economics concepts',
  'Public finance concepts',
  'Monetary policy concepts',
  'Fiscal policy concepts',
  'Banking concepts (retail and commercial)',
  'Payments concepts (non-brands)',
  'Financial markets',
  'Asset classes',
  'Investment strategies (generic)',
  'Risk management (financial)',
  'Insurance concepts',
  'Actuarial concepts',
  'Corporate finance concepts',
  'Accounting concepts',
  'Auditing concepts',
  'Taxation concepts (generic)',
  'Financial reporting frameworks',
  'ESG investing concepts',
  'Sustainable finance instruments',
  'Fintech concepts',
  'Financial crime typologies',
  'Laws and acts',
  'Treaties and conventions',
  'Regulatory citations',
  'Court cases',
  'Standards and specs ids',
  'Protocols / formats'
];

/** Lowered, de-duped set for fast lookups */
export const EXTERNAL_CATEGORY_SET = new Set(
  EXTERNAL_CATEGORY_WHITELIST.map(s => String(s || '').toLowerCase().trim()).filter(Boolean)
);

/* -----------------------------------------------------------
   2) RECOGNIZERS (open-world “door 2” patterns)
   ----------------------------------------------------------- */

export const CATEGORY_RECOGNIZERS = {
  // Geography / nature
  'lakes': [
    String.raw`(?<!\w)\b(?:Lake|Laguna|Lac|Lago)\s+[A-Z][\p{L}\p{M}\-’.() ]{2,}\b`,
  ],
  'rivers': [
    String.raw`\b(?:[A-Z][\p{L}\p{M}\-’.]+)\s+(?:River|Río|Rivière|Fluss)\b`,
    String.raw`\b(?:River|Río|Rivière|Fluss)\s+[A-Z][\p{L}\p{M}\-’.]+\b`,
  ],
  'mountains and peaks': [
    String.raw`(?<!\w)\b(?:Mount|Mt\.?)\s+[A-Z][\p{L}\p{M}\-’.() ]{1,}\b`,
    String.raw`\b[A-Z][\p{L}\p{M}\-’.() ]+\s+(?:Peak|Pico|Pic|Pointe)\b`,
  ],
  'seas and oceans': [
    String.raw`\b(?:Gulf|Sea|Ocean|Bay|Strait|Channel)\s+of\s+[A-Z][\p{L}\p{M}\-’.() ]+\b`,
    String.raw`\b(?:North|South|East|West|Arctic|Atlantic|Pacific|Indian)\s+(?:Ocean|Sea)\b`,
  ],
  'islands and archipelagos': [
    String.raw`\b(?:Island|Isle|Isla|Île)\s+[A-Z][\p{L}\p{M}\-’.() ]+\b`,
    String.raw`\b[A-Z][\p{L}\p{M}\-’.() ]+\s+(?:Islands|Archipelago)\b`,
  ],
  'national parks': [
    String.raw`\b[A-Z][\p{L}\p{M}\-’.() ]+\s+National\s+Park\b`,
  ],
  'deserts': [
    String.raw`\b[A-Z][\p{L}\p{M}\-’.() ]+\s+Desert\b`,
  ],

  // Political / legal
  'laws and acts': [
    String.raw`\b[A-Z][\p{L}\p{M}’\-.\s]+(?:Act|Law|Code|Ordinance)\b(?:\s+\d{4})?`,
  ],
  'treaties and conventions': [
    String.raw`\b(?:Convention|Treaty|Pact|Accord)\s+(?:of|on)\s+[A-Z][\p{L}\p{M}’().\-\s]+\b`,
  ],
  'regulatory citations': [
    String.raw`\b\d+\s*CFR\s+\d+(?:\.\d+)*\b`,
    String.raw`\bArticle\s+\d+[a-z]?\s+(?:GDPR|CCPA|HIPAA|SOX)\b`,
  ],
  'court cases': [
    // Tighten sides to >= 3 letters to reduce sports headline noise
    String.raw`\b[A-Z][\p{L}\p{M}\-’.]{2,}\s+v\.?\s+[A-Z][\p{L}\p{M}\-’.]{2,}\b`,
  ],

  // Standards / protocols / specs
  'standards and specs ids': [
    String.raw`\b(?:ISO|IEC|IEEE|EN|BS|ASTM|NIST|RFC)\s*[-:]?\s*\d{2,5}(?:[:\-]\d{2,4})?(?:\s*v(?:ersion)?\.?\s*\d+(?:\.\d+)*)?\b`,
  ],
  'protocols / formats': [
    String.raw`\b(?:OAuth\s*2(?:\.0)?|OpenID\s+Connect|OpenAPI|GraphQL|gRPC|SAML|JWT|HTTP\/[23]|WebSocket|JSON\s+Schema)\b`,
  ],

  // Astronomy
  'planets': [
    String.raw`\b(?:Mercury|Venus|Earth|Mars|Jupiter|Saturn|Uranus|Neptune)\b`,
  ],
  'dwarf planets': [
    String.raw`\b(?:Pluto|Eris|Haumea|Makemake|Ceres)\b`,
  ],
  'space missions and probes': [
    String.raw`\b(?:Project|Mission|Probe|Orbiter|Lander)\s+[A-Z][\p{L}\p{M}\-’.() ]+\b`,
    String.raw`\b(?:Apollo|Voyager|Pioneer|Mariner|Viking|Cassini|Juno|Rosetta|Hayabusa|Chandrayaan|Artemis)\b`,
  ],

  // Biology / medicine (generic and safe)
  // NOTE: Recognizer key below ("bacterial species") will only run if you later add
  //       "Bacterial species" (or rename to an existing category) in the whitelist.
  'bacterial species': [
    String.raw`\b[A-Z][a-z]+(?:\s+[a-z]{3,}){1,2}\b`,
  ],
  'viruses and viral families': [
    String.raw`\b[A-Z][a-z]+(?:virus|viridae)\b`,
    String.raw`\bSARS[-–]?CoV[-–]?2|HIV[-–]?\d|HBV|HCV|HPV\b`,
  ],
  'primary symptoms and signs': [
    String.raw`\b(?:fe\w*r|cough|dyspnea|nausea|vomiting|diarrhea|rash|headache|dizziness|fatigue)\b`,
  ],
  'drug classes (atc-like, non-coded)': [
    String.raw`\b(?:beta[-\s]?blockers?|ace[-\s]?inhibitors?|arbs?|statins?|ssris?|snris?|benzodiazepines?|opioids?)\b`,
  ],
  'routes of administration': [
    String.raw`\b(?:oral|sublingual|buccal|intravenous|intramuscular|subcutaneous|topical|inhalation|rectal|vaginal)\b`,
  ],

  // Chemistry / materials
  'chemical elements': [
    String.raw`\b(?:Hydrogen|Helium|Lithium|Beryllium|Boron|Carbon|Nitrogen|Oxygen|Fluorine|Neon|Sodium|Magnesium|Aluminum|Silicon|Phosphorus|Sulfur|Chlorine|Argon|Potassium|Calcium)\b`,
  ],
  'polymers and plastics types': [
    String.raw`\b(?:PET|HDPE|PVC|LDPE|PP|PS|PC|PMMA|PTFE)\b`,
  ],

  // Finance / economics
  'macroeconomic indicators': [
    String.raw`\b(?:GDP|CPI|PPI|unemployment\s+rate|inflation\s+rate|interest\s+rate|trade\s+balance)\b`,
  ],
  'financial markets': [
    String.raw`\b(?:commodity|bond|equity|derivatives?)\s+market\b`,
  ],

  // Transportation / engineering
  'vehicle powertrains (generic)': [
    // Guard ICE with optional transport context to avoid the agency collision
    String.raw`(?:(?:vehicle|engine|powertrain|drivetrain)\W+)?\b(?:ICE|diesel|hybrid|plug[-\s]?in\s*hybrid|battery[-\s]?electric|fuel[-\s]?cell)\b`,
  ],
  'public transit modes': [
    String.raw`\b(?:bus|tram|light\s*rail|metro|subway|commuter\s*rail|ferry)\b`,
  ],

  // Culture / heritage
  'architectural styles': [
    String.raw`\b(?:Gothic|Baroque|Renaissance|Neoclassical|Brutalist|Modernist|Postmodern)\b`,
  ],
  'unesco world heritage sites': [
    String.raw`\b[A-Z][\p{L}\p{M}\-’.() ]+\s+(?:UNESCO\s+)?World\s+Heritage\b`,
  ],
};

/* -----------------------------------------------------------
   3) Gazetteer seeds (door 1)
   ----------------------------------------------------------- */

export const CATEGORY_GAZETTEER_SEEDS = {
  'countries': [
    'Ghana','Kenya','Nigeria','South Africa','Egypt','Ethiopia','Tanzania','Uganda','Rwanda','Namibia',
    'Morocco','Algeria','Tunisia','Senegal','Ivory Coast','United States','Canada','Mexico','Brazil','Argentina',
    'United Kingdom','France','Germany','Italy','Spain','Netherlands','Sweden','Norway','Denmark','Finland',
    'China','Japan','South Korea','India','Pakistan','Bangladesh','Indonesia','Philippines','Vietnam','Thailand',
    'Australia','New Zealand','Turkey','Saudi Arabia','United Arab Emirates','Qatar','Israel','Russia','Ukraine','Poland'
  ],
  'us states': [
    'Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia',
    'Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland',
    'Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
    'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina',
    'South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'
  ],
  'planets': ['Mercury','Venus','Earth','Mars','Jupiter','Saturn','Uranus','Neptune'],
  'dwarf planets': ['Pluto','Eris','Haumea','Makemake','Ceres'],
  'continents': ['Africa','Antarctica','Asia','Europe','North America','Oceania','South America'],
  'time zones': ['UTC','GMT','CET','EET','BST','IST','WAT','EAT','PST','MST','CST','EST','AKST','HST','AEST','ACST','AWST'],
  'chemical elements': [
    'Hydrogen','Helium','Lithium','Beryllium','Boron','Carbon','Nitrogen','Oxygen','Fluorine','Neon',
    'Sodium','Magnesium','Aluminum','Silicon','Phosphorus','Sulfur','Chlorine','Argon','Potassium','Calcium'
  ],
  'routes of administration': [
    'oral','sublingual','buccal','intravenous','intramuscular','subcutaneous','topical','inhalation','rectal','vaginal'
  ],
  'drug classes (atc-like, non-coded)': [
    'beta blocker','ace inhibitor','arb','statin','ssri','snri','benzodiazepine','opioid'
  ],
  'polymers and plastics types': ['PET','HDPE','PVC','LDPE','PP','PS','PC','PMMA','PTFE'],
  'public transit modes': ['bus','tram','light rail','metro','subway','commuter rail','ferry'],
  'vehicle powertrains (generic)': ['diesel','hybrid','plug-in hybrid','battery electric','fuel cell','ICE'],
  'architectural styles': ['Gothic','Baroque','Renaissance','Neoclassical','Brutalist','Modernist','Postmodern'],
  'financial markets': ['equity market','bond market','derivatives market','commodity market'],
  'macroeconomic indicators': ['GDP','CPI','PPI','unemployment rate','inflation rate','interest rate','trade balance']
};

/* -----------------------------------------------------------
   4) Helpers (with caching + dev-time alignment warnings)
   ----------------------------------------------------------- */

export const normalizeCategoryName = (name) =>
  String(name || '').toLowerCase().trim();

/** Cache: compiled recognizers per category */
const __recognizerCache = new Map();
/** Cache: Set-gazetteers per category */
const __gazetteerSetCache = new Map();

/** Lower-cased gazetteer list for a category (always returns an array) */
export function gazetteerFor(categoryName) {
  const k = normalizeCategoryName(categoryName);
  const list = CATEGORY_GAZETTEER_SEEDS[k] || [];
  return list.map(s => String(s || '').toLowerCase().trim()).filter(Boolean);
}

/** Internal: get (and cache) a Set for faster O(1) lookup */
function gazetteerSetFor(categoryName) {
  const k = normalizeCategoryName(categoryName);
  if (__gazetteerSetCache.has(k)) return __gazetteerSetCache.get(k);
  const set = new Set(gazetteerFor(k));
  __gazetteerSetCache.set(k, set);
  return set;
}

/** Compiled recognizers for a category (safe, unicode, cached) */
export function recognizersFor(categoryName) {
  const k = normalizeCategoryName(categoryName);
  if (__recognizerCache.has(k)) return __recognizerCache.get(k);

  const patterns = CATEGORY_RECOGNIZERS[k] || [];
  const out = [];
  for (const pat of patterns) {
    try {
      out.push(new RegExp(pat, 'iu'));
    } catch {
      // ignore bad regex
    }
  }
  __recognizerCache.set(k, out);
  return out;
}

/** Exact lookup within a category’s gazetteer (phrase should be normalized first) */
export function inCategoryGazetteer(categoryName, phraseNormalized) {
  const set = gazetteerSetFor(categoryName);
  return set.has(String(phraseNormalized || '').toLowerCase().trim());
}
// --- persistence for promoted terms (localStorage) ---
// Backward-compatible storage: support BOTH the original key & the accidental alt key,
// and BOTH payload shapes ({ map: {...} } and flat { ... }).

const LC_KEY_PRIMARY = 'lc_external_promotions_v1'; // canonical (old UI expects this)
const LC_KEY_LEGACY  = 'lc_extcat_promotions_v1';   // alt used in the new code by mistake

function getLocalStorageSafe() {
  try {
    if (typeof window !== 'undefined' && window && window.localStorage) return window.localStorage;
    if (typeof localStorage !== 'undefined') return localStorage;
  } catch { /* noop */ }
  return null;
}

/** Accepts { map: {...} } or flat { ... } and normalizes to { [normalizedCat]: [terms...] } */
function normalizePromotionObject(obj) {
  const src = (obj && typeof obj === 'object' && !Array.isArray(obj))
    ? (obj.map && typeof obj.map === 'object' ? obj.map : obj)
    : {};

  const out = {};
  for (const [cat, arr] of Object.entries(src)) {
    const k = normalizeCategoryName(cat);
    if (!k) continue;
    if (!Array.isArray(arr)) continue;

    out[k] = out[k] || [];
    const seen = new Set(out[k].map(s => String(s).toLowerCase().trim()));
    for (const t of arr) {
      const v = String(t || '').trim();
      if (!v) continue;
      const low = v.toLowerCase();
      if (!seen.has(low)) {
        out[k].push(v);
        seen.add(low);
      }
    }
  }
  return out;
}

function readJson(ls, key) {
  try {
    const raw = ls.getItem(key);
    if (!raw) return {};
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

/** Load promotions from BOTH keys, merge, and return a normalized map */
function loadPromotionsUnified() {
  const ls = getLocalStorageSafe();
  if (!ls) return {};

  const primaryObj = readJson(ls, LC_KEY_PRIMARY);
  const legacyObj  = readJson(ls, LC_KEY_LEGACY);

  // Normalize each then merge
  const primaryMap = normalizePromotionObject(primaryObj);
  const legacyMap  = normalizePromotionObject(legacyObj);

  const merged = {};
  for (const m of [primaryMap, legacyMap]) {
    for (const [cat, list] of Object.entries(m)) {
      const k = normalizeCategoryName(cat);
      merged[k] = merged[k] || [];
      const seen = new Set(merged[k].map(s => String(s).toLowerCase().trim()));
      for (const t of list) {
        const v = String(t || '').trim();
        if (!v) continue;
        const low = v.toLowerCase();
        if (!seen.has(low)) {
          merged[k].push(v);
          seen.add(low);
        }
      }
    }
  }
  return merged;
}

/** Save to BOTH keys to keep old + new UIs happy */
function savePromotionsUnified(map) {
  const ls = getLocalStorageSafe();
  if (!ls) return;

  // Canonicalize
  const normalized = normalizePromotionObject({ map: map });

  try { ls.setItem(LC_KEY_PRIMARY, JSON.stringify({ map: normalized })); } catch {}
  try { ls.setItem(LC_KEY_LEGACY,  JSON.stringify(normalized)); } catch {}
}

// Load once on module init
let __promotionsMap = loadPromotionsUnified();

/** Merge a promotions map into gazetteer seeds (whitelist-aware, de-duped) */
function mergePromotionsIntoSeeds(map) {
  try {
    for (const [catName, list] of Object.entries(map || {})) {
      const k = normalizeCategoryName(catName);
      if (!k) continue;

      // only hydrate categories we actually support
      if (!EXTERNAL_CATEGORY_SET.has(k)) continue;

      CATEGORY_GAZETTEER_SEEDS[k] = CATEGORY_GAZETTEER_SEEDS[k] || [];
      const seed = CATEGORY_GAZETTEER_SEEDS[k];
      const seen = new Set(seed.map(s => String(s).toLowerCase().trim()));

      for (const term of (list || [])) {
        const v = String(term || '').trim();
        if (!v) continue;
        const low = v.toLowerCase();
        if (!seen.has(low)) {
          seed.push(v);
          seen.add(low);
        }
      }

      // refresh O(1) lookup cache for this category
      __gazetteerSetCache.set(k, new Set(gazetteerFor(k)));
    }
  } catch { /* best effort */ }
}

/** Promote a provisional term to a category’s gazetteer at runtime (and persist) */
export function promoteToGazetteer(categoryName, term) {
  const k = normalizeCategoryName(categoryName);
  if (!k) return false;

  // Only promote into known categories
  if (!EXTERNAL_CATEGORY_SET.has(k)) return false;

  const val = String(term || '').trim();
  if (!val) return false;

  CATEGORY_GAZETTEER_SEEDS[k] = CATEGORY_GAZETTEER_SEEDS[k] || [];
  const exists = CATEGORY_GAZETTEER_SEEDS[k].some(
    s => String(s).toLowerCase().trim() === val.toLowerCase()
  );
  if (!exists) CATEGORY_GAZETTEER_SEEDS[k].push(val);

  // update lookup cache
  __gazetteerSetCache.set(k, new Set(gazetteerFor(k)));

  // update in-memory promotions and persist to BOTH keys
  __promotionsMap[k] = Array.from(new Set([...( __promotionsMap[k] || [] ), val]));
  savePromotionsUnified(__promotionsMap);
  return true;
}

/** Optional helper: for "Download" buttons — returns the canonical payload shape */
export function exportPromotionsSnapshot() {
  // Return the canonical shape { map: { cat: [terms] } }
  return { map: JSON.parse(JSON.stringify(__promotionsMap || {})) };
}

/** Optional helper: for "Upload" buttons — validate and replace promotions */
export function importPromotionsSnapshot(payload) {
  const next = normalizePromotionObject(payload); // accepts { map: {...} } or flat { ... }
  __promotionsMap = next;
  savePromotionsUnified(__promotionsMap);
  mergePromotionsIntoSeeds(__promotionsMap);
  return true;
}

// Hydrate on module load
mergePromotionsIntoSeeds(__promotionsMap);


/* Dev guard: surface misalignments where recognizer keys are not in whitelist
   (These recognizers will be ignored by app.js until you add the matching category). */
(function devAlignmentGuard(){
  try {
    const env = typeof process !== 'undefined' && process && process.env && process.env.NODE_ENV;
    if (env && env !== 'production') {
      const wl = new Set(EXTERNAL_CATEGORY_WHITELIST.map(s => s.toLowerCase()));
      const missing = Object.keys(CATEGORY_RECOGNIZERS).filter(k => !wl.has(k.toLowerCase()));
      if (missing.length) {
        // eslint-disable-next-line no-console
        console.warn('[external_categories] Recognizer keys not present in whitelist (won’t be evaluated until added):', missing);
      }
    }
  } catch { /* noop */ }
})();

export default {
  EXTERNAL_CATEGORY_WHITELIST,
  EXTERNAL_CATEGORY_SET,
  CATEGORY_RECOGNIZERS,
  CATEGORY_GAZETTEER_SEEDS,
  normalizeCategoryName,
  gazetteerFor,
  recognizersFor,
  inCategoryGazetteer,
  promoteToGazetteer,
};
