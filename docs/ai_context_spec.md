# Blue Dot Plot — AI Context Source Registry

## Purpose

This document defines the approved external sources that may be used by
the Blue Dot Plot AI Context research layer.

The registry is intentionally open-ended.

The project does not impose a fixed maximum number of sources. Additional
authoritative national, regional, scientific, or contextual sources may be
added when they provide relevant information that improves earthquake
context.

The AI research layer must use only sources listed in this registry.

---

# 1. Source Categories

Sources are divided into three primary categories.

## 1.1 Global Sources

Sources with global or international geographic coverage.

These sources provide information that is useful regardless of where an
earthquake occurs.

## 1.2 National / Regional Sources

Official or authoritative organizations responsible for earthquake
monitoring, seismic research, geological information, hazard assessment,
or related scientific information within a specific country or region.

These sources should receive priority when an earthquake occurs within
their geographic area of responsibility.

## 1.3 Contextual Sources

Sources that provide geographic, historical, scientific, or explanatory
context but are not necessarily the primary authority for the earthquake
itself.

Contextual sources must not override primary seismic information.

---

# 2. Authority and Evidence Rules

## 2.1 Primary earthquake facts

The Blue Dot Plot earthquake record remains the authoritative source for
the core event fields already stored in the project.

Examples:

- event ID
- magnitude
- magnitude type
- origin time
- latitude
- longitude
- depth
- place
- MMI
- CDI
- felt reports
- tsunami flag
- significance
- sequence membership

External sources are used to add context, not to replace these fields.

## 2.2 Source hierarchy

When multiple approved sources provide information about the same subject,
the following general hierarchy applies:

1. Blue Dot Plot verified event data
2. Relevant official national or regional agency
3. USGS
4. Other authoritative international seismic organizations
5. Scientific research organizations and observatories
6. Wikipedia and other contextual sources

This hierarchy is contextual rather than absolute.

For a country-specific question, the relevant national agency may provide
more detailed information than a global source.

## 2.3 Conflicting information

If approved sources disagree, the research layer must not silently choose
one value.

The system should:

- prefer the higher-authority source;
- preserve source attribution;
- avoid the disputed claim if the conflict cannot be resolved.

## 2.4 Missing evidence

If a source does not provide reliable information about a topic, the topic
must be omitted.

The AI must never fill missing evidence using general knowledge.

---

# 3. Global Sources

## 3.1 United States Geological Survey — USGS

Scope: Global

Authority: Primary scientific/governmental source

Use for:

- earthquake event information
- earthquake catalog
- seismicity
- earthquake sequences
- aftershock forecasts
- tectonic context
- faults
- ShakeMap
- Did You Feel It?
- earthquake impacts
- tsunami-related earthquake information
- earthquake science
- historical earthquakes
- earthquake hazards

Notes:

USGS is the primary global source for Blue Dot Plot earthquake event
information.

USGS data should normally be preferred when the same basic event parameter
is available from multiple global sources.

---

## 3.2 International Seismological Centre — ISC

Scope: Global

Authority: International scientific organization

Use for:

- global earthquake catalog information
- independent seismic bulletin information
- historical seismicity
- event associations
- seismic phases
- contributing national seismic agencies

Notes:

ISC is particularly useful as an independent international reference
catalog and for historical seismicity.

---

## 3.3 IRIS / SAGE

Scope: Global

Authority: Scientific research and data infrastructure

Use for:

- seismology
- plate tectonics
- fault systems
- seismic wave propagation
- earthquake mechanisms
- educational scientific context
- seismic data and waveform-related context

Notes:

IRIS was succeeded by the SAGE facility and associated infrastructure.
The source should be treated as a scientific context source rather than a
replacement for the primary earthquake catalog.

---

## 3.4 European-Mediterranean Seismological Centre — EMSC / CSEM

Scope: Europe, Mediterranean, surrounding regions; international

Authority: Regional/international seismological organization

Use for:

- European and Mediterranean earthquakes
- felt reports
- regional seismicity
- event information
- seismic sequences
- public earthquake observations

Priority:

High for earthquakes in Europe and the Mediterranean region.

---

## 3.5 NOAA

Scope: Global

Authority: U.S. governmental scientific agency

Use for:

- tsunami information
- tsunami observations
- tsunami warnings
- tsunami propagation
- historical tsunami context
- oceanographic context relevant to earthquake-generated tsunamis

Notes:

Use NOAA for tsunami-specific context when relevant.

---

# 4. Europe

## 4.1 Italy — INGV

Organization:

Istituto Nazionale di Geofisica e Vulcanologia

Scope: Italy and Mediterranean region

Authority: National scientific institution

Use for:

- Italian earthquake catalog
- seismic sequences
- Italian seismicity
- focal mechanisms
- ShakeMaps
- historical earthquakes
- seismic hazard
- Mediterranean seismicity
- earthquake reports
- volcanic and seismic context

Priority:

High for earthquakes in Italy and surrounding Mediterranean regions.

---

## 4.2 Italy — OGS

Organization:

Istituto Nazionale di Oceanografia e di Geofisica Sperimentale

Scope: Italy and northeastern Adriatic / Mediterranean

Authority: National research institution

Use for:

- regional seismicity
- seismic monitoring
- Adriatic and northeastern Italian seismicity
- geophysical context

---

## 4.3 France — ReNaSS / BCSF

Scope: France

Authority: National scientific seismic network

Use for:

- French earthquakes
- French seismicity
- historical seismicity
- local earthquake parameters
- regional seismic context

---

## 4.4 Germany — BGR / GEOFON / regional seismic networks

Scope: Germany and Central Europe

Use for:

- German seismicity
- Central European seismicity
- regional seismic monitoring
- seismic networks

---

## 4.5 Switzerland — Swiss Seismological Service

Organization:

Swiss Seismological Service at ETH Zurich

Scope: Switzerland and Alpine region

Use for:

- Swiss earthquakes
- Alpine seismicity
- earthquake sequences
- local seismic hazard
- historical seismicity

---

## 4.6 Greece — National Observatory of Athens / Institute of Geodynamics

Scope: Greece and eastern Mediterranean

Use for:

- Greek seismicity
- earthquake monitoring
- seismic sequences
- historical earthquakes
- eastern Mediterranean context

---

## 4.7 Iceland — Icelandic Meteorological Office

Scope: Iceland

Use for:

- Icelandic earthquakes
- volcanic-seismic activity
- seismic swarms
- volcanic context
- Reykjanes and Icelandic tectonic activity

---

## 4.8 United Kingdom — British Geological Survey

Scope: United Kingdom and surrounding region

Use for:

- UK earthquake catalog
- historical seismicity
- regional seismic context

---

## 4.9 Norway — NORSAR

Scope: Norway and northern Europe

Use for:

- Norwegian seismicity
- seismic monitoring
- regional seismicity

---

## 4.10 Portugal / Azores — IPMA

Organization:

Instituto Português do Mar e da Atmosfera

Scope:

Portugal, Azores, Atlantic region

Use for:

- Portuguese earthquakes
- Azores seismicity
- volcanic-seismic activity
- Atlantic regional context

---

## 4.11 Romania — National Institute for Earth Physics

Scope: Romania and surrounding Carpathian region

Use for:

- Romanian seismicity
- Vrancea earthquakes
- historical earthquakes
- regional seismicity

---

## 4.12 Poland — Institute of Geophysics, Polish Academy of Sciences

Scope: Poland

Use for:

- Polish seismicity
- regional seismic monitoring
- earthquake research

---

## 4.13 Serbia — Seismological Survey of Serbia

Scope: Serbia and Balkans

Use for:

- Serbian earthquakes
- Balkan seismicity
- historical seismicity
- regional context

---

## 4.14 Cyprus — Geological Survey Department

Scope: Cyprus and eastern Mediterranean

Use for:

- Cyprus seismicity
- eastern Mediterranean seismicity
- geological context

---

# 5. Turkey and Eastern Mediterranean

## 5.1 Turkey — AFAD

Organization:

Disaster and Emergency Management Presidency
Earthquake Department

Scope: Turkey

Authority: Official national governmental earthquake authority

Use for:

- earthquake catalog
- earthquake parameters
- historical earthquakes
- instrumental catalog
- focal mechanisms
- earthquake statistics
- felt information
- seismic hazard
- earthquake reports
- Turkey-specific earthquake context

Priority:

Very high for earthquakes in Turkey.

---

## 5.2 Turkey — KOERI

Organization:

Kandilli Observatory and Earthquake Research Institute

Scope: Turkey and surrounding region

Authority: Major national/regional scientific institution

Use for:

- Turkish seismicity
- earthquake monitoring
- earthquake catalog
- historical seismicity
- regional tectonics
- earthquake research

Priority:

High for Turkey and surrounding regions.

---

# 6. Asia

## 6.1 Japan — JMA

Organization:

Japan Meteorological Agency

Scope: Japan and surrounding region

Authority: Official national governmental agency

Use for:

- earthquake parameters
- seismic intensity
- earthquake monitoring
- tsunami information
- earthquake warnings
- Japanese seismicity
- historical earthquake information

Priority:

Very high for earthquakes in Japan.

---

## 6.2 Japan — NIED

Organization:

National Research Institute for Earth Science and Disaster Resilience

Scope: Japan

Authority: National research institute

Use for:

- seismic networks
- Hi-net
- K-NET
- KiK-net
- strong-motion data
- seismic research
- earthquake sequences
- ground motion
- earthquake engineering context

---

## 6.3 Japan — Earthquake Research Institute, University of Tokyo

Scope: Japan and global research

Authority: Academic research institution

Use for:

- earthquake science
- fault systems
- earthquake mechanisms
- tectonic context
- historical and scientific research

---

## 6.4 Indonesia — BMKG

Organization:

Badan Meteorologi, Klimatologi, dan Geofisika

Scope: Indonesia

Authority: Official national governmental agency

Use for:

- Indonesian earthquake information
- earthquake monitoring
- felt earthquakes
- intensity
- tsunami potential
- Indonesian seismicity
- earthquake parameters
- regional seismic context

Priority:

Very high for earthquakes in Indonesia.

---

## 6.5 Indonesia — PVMBG

Organization:

Pusat Vulkanologi dan Mitigasi Bencana Geologi

Scope: Indonesia

Authority: National geological institution

Use for:

- volcanic-seismic activity
- volcano-earthquake interactions
- volcanic hazards
- geological context

Priority:

High when an earthquake is associated with volcanic activity.

---

## 6.6 China — China Earthquake Administration

Organization:

China Earthquake Administration — CEA

Scope: China

Authority: Official national governmental earthquake authority

Use for:

- Chinese earthquake monitoring
- earthquake catalog
- seismicity
- earthquake reports
- earthquake hazard
- historical seismicity
- regional tectonic context

Priority:

Very high for earthquakes in China.

---

## 6.7 China — China Earthquake Networks Center

Organization:

CENC

Scope: China and surrounding region

Authority: National earthquake monitoring center

Use for:

- earthquake monitoring
- earthquake parameters
- rapid earthquake information
- Chinese seismic networks
- regional seismicity

---

## 6.8 China — Institute of Earthquake Forecasting

Organization:

Institute of Earthquake Forecasting, CEA

Scope: China / scientific research

Authority: National research institution

Use for:

- earthquake forecasting research
- earthquake predictability research
- seismicity analysis
- earthquake science
- scientific context

Important:

Forecasting research must never be converted into a prediction of a future
earthquake by the AI layer.

---

## 6.9 India — National Center for Seismology

Organization:

Ministry of Earth Sciences, Government of India

Scope: India

Authority: Official national governmental agency

Use for:

- Indian earthquake monitoring
- earthquake catalog
- regional seismicity
- earthquake reports
- aftershock monitoring
- swarm monitoring
- seismic hazard
- historical seismicity

---

## 6.10 Philippines — PHIVOLCS

Organization:

Philippine Institute of Volcanology and Seismology

Scope: Philippines

Authority: Official national governmental scientific agency

Use for:

- earthquakes
- seismicity
- earthquake monitoring
- volcanic-seismic activity
- tsunami information
- geological context

---

## 6.11 Taiwan — Central Weather Administration

Scope: Taiwan

Use for:

- earthquake monitoring
- seismic intensity
- tsunami information
- Taiwanese seismicity

---

## 6.12 South Korea — Korea Meteorological Administration

Scope: South Korea

Use for:

- Korean earthquake monitoring
- seismicity
- earthquake parameters
- regional seismic context

---

## 6.13 Nepal — National Seismological Center

Scope: Nepal and Himalayan region

Use for:

- Nepalese seismicity
- Himalayan earthquakes
- earthquake monitoring
- historical seismicity

---

## 6.14 Iran — International Institute of Earthquake Engineering and
Seismology

Organization:

IIEES

Scope: Iran and surrounding region

Use for:

- Iranian seismicity
- earthquake engineering
- seismic hazard
- earthquake research
- historical earthquakes

---

## 6.15 Iran — Geological Survey of Iran

Scope: Iran

Use for:

- geological context
- active faults
- regional tectonics
- seismicity

---

## 6.16 Kazakhstan — Kazakhstan National Data Center

Scope: Kazakhstan and Central Asia

Use for:

- Central Asian seismicity
- earthquake monitoring
- seismic networks

---

## 6.17 Kyrgyzstan — Kyrgyz Seismic Network

Scope: Kyrgyzstan and Central Asia

Use for:

- Central Asian seismicity
- earthquake monitoring
- regional seismicity

---

# 7. Russia

## 7.1 Russia — Geophysical Survey of the Russian Academy of Sciences

Organization:

Geophysical Survey of the Russian Academy of Sciences — GS RAS

Scope: Russia

Authority: National scientific institution

Use for:

- Russian earthquake catalog
- seismic monitoring
- historical seismicity
- regional seismicity
- earthquake parameters
- seismic hazard research

Priority:

Very high for earthquakes in Russia.

---

## 7.2 Russia — Kamchatka Branch of GS RAS

Scope:

Kamchatka and the Russian Far East

Authority:

Regional branch of the Geophysical Survey of the Russian Academy of
Sciences

Use for:

- Kamchatka earthquakes
- Kuril-Kamchatka seismicity
- earthquake sequences
- aftershocks
- volcanic-seismic activity
- seismic hazard
- regional tectonic context

Priority:

Very high for Kamchatka and the Kuril region.

---

## 7.3 Russia — Institute of Volcanology and Seismology

Scope:

Kamchatka and Russian Far East

Use for:

- volcano-seismic activity
- volcanic eruptions
- earthquake-volcano relationships
- geological context
- Kamchatka seismicity

Important:

Scientific statements about causation between earthquakes and volcanic
activity must be supported explicitly by the source.

---

# 8. Americas

## 8.1 United States — USGS

See Global Sources.

For earthquakes in the United States, USGS remains the primary source.

---

## 8.2 United States — ANSS

Organization:

Advanced National Seismic System

Scope:

United States

Use for:

- U.S. seismic networks
- earthquake monitoring
- seismicity
- strong-motion information

---

## 8.3 United States — SCEC

Organization:

Southern California Earthquake Center

Scope:

Southern California / western United States

Use for:

- faults
- tectonic setting
- seismicity
- earthquake science
- earthquake scenarios

---

## 8.4 United States — California Geological Survey

Scope:

California

Use for:

- California faults
- seismic hazard
- earthquake geology
- regional seismicity

---

## 8.5 Mexico — SSN / UNAM

Organization:

Servicio Sismológico Nacional
Universidad Nacional Autónoma de México

Scope: Mexico

Use for:

- Mexican earthquake catalog
- seismicity
- earthquake monitoring
- historical seismicity
- regional tectonic context

---

## 8.6 Chile — Centro Sismológico Nacional

Organization:

Centro Sismológico Nacional, Universidad de Chile

Scope: Chile

Use for:

- Chilean earthquake monitoring
- earthquake catalog
- seismicity
- historical earthquakes
- subduction context

Priority:

Very high for Chile and the Chilean subduction zone.

---

## 8.7 Argentina — INPRES

Organization:

Instituto Nacional de Prevención Sísmica

Scope: Argentina

Use for:

- Argentine seismicity
- earthquake monitoring
- seismic hazard
- historical earthquakes

---

## 8.8 Peru — Instituto Geofísico del Perú

Scope:

Peru

Use for:

- Peruvian seismicity
- earthquake monitoring
- historical earthquakes
- subduction context
- volcanic-seismic activity

---

## 8.9 Ecuador — Instituto Geofísico, Escuela Politécnica Nacional

Scope:

Ecuador

Use for:

- Ecuadorian earthquakes
- seismicity
- volcanic-seismic activity
- regional tectonics

---

## 8.10 Colombia — Servicio Geológico Colombiano

Scope:

Colombia

Use for:

- Colombian seismicity
- earthquake monitoring
- geological context
- active faults

---

## 8.11 Costa Rica — OVSICORI / RSN

Scope:

Costa Rica and Central America

Use for:

- Costa Rican seismicity
- earthquake monitoring
- volcanic-seismic activity
- regional tectonic context

---

# 9. Oceania

## 9.1 New Zealand — GeoNet

Organization:

GeoNet / GNS Science

Scope: New Zealand

Use for:

- earthquake catalog
- seismicity
- felt earthquakes
- volcanic activity
- tsunami information
- earthquake sequences
- geological context

Priority:

Very high for New Zealand.

---

## 9.2 Australia — Geoscience Australia

Scope:

Australia and surrounding region

Use for:

- Australian earthquake catalog
- seismicity
- earthquake hazard
- historical earthquakes
- regional geological context

---

# 10. Africa and Middle East

## 10.1 South Africa — Council for Geoscience

Scope:

South Africa

Use for:

- South African seismicity
- earthquake monitoring
- geological context

---

## 10.2 Egypt — NRIAG

Organization:

National Research Institute of Astronomy and Geophysics

Scope:

Egypt and surrounding region

Use for:

- Egyptian seismicity
- earthquake monitoring
- historical earthquakes
- regional seismicity

---

## 10.3 Israel — Geophysical Institute of Israel

Scope:

Israel and surrounding region

Use for:

- Israeli seismicity
- Dead Sea Transform context
- earthquake monitoring
- historical earthquakes

---

## 10.4 Saudi Arabia — Saudi Geological Survey

Scope:

Saudi Arabia

Use for:

- Saudi Arabian seismicity
- geological context
- earthquake hazard

---

## 10.5 Morocco — National Institute of Geophysics

Scope:

Morocco and northwest Africa

Use for:

- Moroccan seismicity
- earthquake monitoring
- historical earthquakes

---

# 11. Contextual Sources

## 11.1 Wikipedia

Scope:

Global

Authority:

Secondary contextual source

Use for:

- geographic context
- historical context
- notable historical earthquakes
- regional history
- general background
- discovery of potentially relevant primary sources

Restrictions:

Wikipedia must not be treated as the primary authority for:

- earthquake magnitude
- earthquake location
- earthquake depth
- fault attribution
- damage
- casualties
- tsunami occurrence
- scientific causation
- earthquake prediction

When Wikipedia contains a useful scientific claim, the research layer should
preferably trace that claim to the cited primary or authoritative source.

---

# 12. Additional Scientific / Contextual Sources

## 12.1 Smithsonian Global Volcanism Program

Scope:

Global

Use for:

- volcanoes
- volcanic eruptions
- volcanic history
- volcano-seismic context

Use only when volcanic context is relevant to the earthquake.

---

## 12.2 Global Earthquake Model — GEM

Scope:

Global

Use for:

- seismic hazard
- exposure
- risk context
- global hazard models

GEM is a scientific/hazard modeling source rather than the primary source
for individual earthquake event parameters.

---

## 12.3 ORFEUS

Organization:

Observatories and Research Facilities for European Seismology

Scope:

Europe

Use for:

- European seismic data
- waveform infrastructure
- seismic networks
- regional scientific context

---

## 12.4 GEOSCOPE

Scope:

Global

Use for:

- global broadband seismic network information
- waveform and seismological research context

---

# 13. Topic Eligibility

Each source may support only certain types of claims.

The research layer must not assume that every source is suitable for every
topic.

Possible topic classes:

- event_information
- regional_seismicity
- historical_seismicity
- tectonic_setting
- plate_boundary
- fault_system
- earthquake_mechanism
- earthquake_sequence
- foreshocks_aftershocks
- felt_shaking
- intensity
- tsunami
- volcanic_activity
- geological_effects
- ground_motion
- human_impact
- infrastructure_impact
- geographic_context
- population_context
- seismic_hazard
- historical_significance
- scientific_context

A source should be queried only for topics for which it can provide
credible evidence.

---

# 14. Geographic Source Selection

The research layer should determine relevant national and regional sources
from the earthquake location.

Example:

Turkey:

- USGS
- ISC
- EMSC
- AFAD
- KOERI
- Wikipedia

Italy:

- USGS
- ISC
- EMSC
- INGV
- OGS
- Wikipedia

Japan:

- USGS
- ISC
- JMA
- NIED
- Earthquake Research Institute
- Wikipedia

Indonesia:

- USGS
- ISC
- EMSC
- BMKG
- PVMBG
- Wikipedia

Kamchatka:

- USGS
- ISC
- Geophysical Survey of RAS
- Kamchatka Branch of GS RAS
- Institute of Volcanology and Seismology
- Wikipedia

China:

- USGS
- ISC
- China Earthquake Administration
- CENC
- Institute of Earthquake Forecasting
- Wikipedia

Chile:

- USGS
- ISC
- Centro Sismológico Nacional
- EMSC
- Wikipedia

---

# 15. Evidence-First Requirement

The AI model must never receive unrestricted access to the web in the
production pipeline.

The intended architecture is:

Earthquake
→ source selection
→ approved source retrieval
→ evidence extraction
→ evidence package
→ LLM synthesis
→ output validation
→ stored summary

The LLM receives evidence, not arbitrary web search results.

---

# 16. No-Evidence Rule

For every topic:

If reliable evidence exists:

→ the topic may be used.

If reliable evidence does not exist:

→ the topic must be omitted.

The model must never transform:

"no information found"

into:

"probably..."

"likely..."

"this suggests..."

unless the supplied source explicitly supports that interpretation.

---

# 17. Prediction Restriction

Sources that conduct earthquake forecasting or prediction research may be
used for scientific context.

However:

- forecasts must not be presented as predictions by Blue Dot Plot;
- scientific research about predictability must not be converted into a
  prediction of a future earthquake;
- the AI must not state that a future earthquake will occur;
- the AI must not assign a probability of a future earthquake unless the
  project explicitly introduces a separate, scientifically defined
  forecasting product.

---

# 18. Registry Maintenance

This registry is expected to grow.

New sources may be added when they satisfy all of the following:

1. The organization is authoritative for its geographic or scientific
   domain.
2. The source provides information relevant to earthquake context.
3. The source can be independently identified and attributed.
4. The source provides sufficient evidence for reproducible research.
5. Its role in the AI Context layer can be clearly defined.

Adding a source does not automatically make every piece of information
from that source acceptable.

The source's geographic scope and topic eligibility must still be respected.

---

# 19. Current Initial Registry

The initial registry contains:

### Global

- USGS
- ISC
- IRIS / SAGE
- EMSC / CSEM
- NOAA

### Europe / Mediterranean

- INGV
- OGS
- ReNaSS / BCSF
- BGR / GEOFON / regional seismic networks
- Swiss Seismological Service
- National Observatory of Athens / Institute of Geodynamics
- Icelandic Meteorological Office
- British Geological Survey
- NORSAR
- IPMA
- National Institute for Earth Physics, Romania
- Institute of Geophysics, Polish Academy of Sciences
- Seismological Survey of Serbia
- Geological Survey of Cyprus

### Turkey

- AFAD
- KOERI

### Asia

- JMA
- NIED
- Earthquake Research Institute, University of Tokyo
- BMKG
- PVMBG
- China Earthquake Administration
- CENC
- Institute of Earthquake Forecasting
- National Center for Seismology, India
- PHIVOLCS
- Taiwan Central Weather Administration
- Korea Meteorological Administration
- National Seismological Center, Nepal
- IIEES
- Geological Survey of Iran
- Kazakhstan National Data Center
- Kyrgyz Seismic Network

### Russia

- Geophysical Survey of RAS
- Kamchatka Branch of GS RAS
- Institute of Volcanology and Seismology

### Americas

- ANSS
- SCEC
- California Geological Survey
- Servicio Sismológico Nacional / UNAM
- Centro Sismológico Nacional / Universidad de Chile
- INPRES
- Instituto Geofísico del Perú
- Instituto Geofísico, Escuela Politécnica Nacional
- Servicio Geológico Colombiano
- OVSICORI / RSN

### Oceania

- GeoNet / GNS Science
- Geoscience Australia

### Africa / Middle East

- Council for Geoscience, South Africa
- NRIAG, Egypt
- Geophysical Institute of Israel
- Saudi Geological Survey
- National Institute of Geophysics, Morocco

### Contextual / Scientific

- Wikipedia
- Smithsonian Global Volcanism Program
- Global Earthquake Model
- ORFEUS
- GEOSCOPE