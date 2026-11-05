# ADDENDUM-0001 – Room Modeling, Airflow and Heat Loss Calculations

- **Status:** Received from project owner, recorded verbatim in FND-001.
- **Relationship:** Extends `CODEX_START.md`. Section 9 below replaces the phase
  list of `CODEX_START.md` §11 from Phase 2 onwards (see `docs/roadmap/roadmap.md`).

---

## 1. Updated system objective

The system must not jump directly from geometry recognition to radiator placement.

After geometry recognition, it must identify, construct and validate building spaces (rooms) as first-class domain objects.

Every room must have a stable internal identity and a traceable relationship to its source geometry.

The system must support rooms originating from:

* Revit models.
* DXF architectural drawings.
* Future supported building data sources.

All source formats must be normalized into a shared domain model.

## 2. Mandatory processing pipeline

The intended processing pipeline is:

1. Import source geometry.
2. Recognize building elements and boundaries.
3. Detect and construct rooms.
4. Validate room geometry and topology.
5. Calculate room areas, heights and volumes.
6. Collect room-specific building physics and HVAC inputs.
7. Calculate room-specific ventilation airflow requirements.
8. Calculate room-specific heat losses.
9. Determine room-specific heating power requirements.
10. Generate radiator placement proposals.
11. Validate proposals.
12. Obtain user approval.
13. Apply approved changes to Revit.
14. Verify and audit the result.

Room construction and validation must be completed before room-specific calculations can be considered reliable.

## 3. Required domain models

Create and evolve the following domain concepts:

* `Building`
* `BuildingLevel`
* `Room`
* `RoomGeometry`
* `RoomBoundary`
* `BoundaryElement`
* `VentilationRequirement`
* `AirflowCalculation`
* `HeatLossCalculation`
* `HeatingRequirement`
* `RadiatorCandidate`

Do not create empty modules or implement all these models prematurely.

Implement them incrementally when their corresponding backlog tasks begin.

## 4. Room domain requirements

A Room must support at least:

* Stable internal ID.
* Room number, if available.
* Room name or usage classification, if available.
* Building and level references.
* Source reference and source type.
* Geometry reference.
* Floor area.
* Room height.
* Room volume.
* Boundary elements.
* Geometry validation status.
* Input data completeness status.

Do not assume that room numbers are unique or that all rooms have names.

Support uncertain room recognition. A room candidate must not automatically become a confirmed room without passing defined validation rules.

## 5. Airflow calculations

The system must calculate room-specific airflow requirements.

Support separate values for:

* Supply airflow.
* Extract airflow.
* Transfer airflow, where applicable.
* Calculation basis.
* Design assumptions.
* Input data provenance.
* Calculation method and version.
* Validation status.

Never invent airflow values or regulatory requirements.

The applicable Finnish regulations, standards, design criteria and their versions must be documented before compliance-related calculations are implemented.

The calculation engine must be deterministic and independently testable.

AI may assist in recognizing room usage and identifying missing inputs, but it must not replace the deterministic calculation engine.

## 6. Heat loss calculations

The system must calculate room-specific heat losses.

The calculation model must be capable of separating:

* External wall transmission losses.
* Window transmission losses.
* External door transmission losses.
* Roof and ceiling transmission losses.
* Floor and ground-related transmission losses.
* Ventilation-related heat losses.
* Infiltration-related heat losses.

The calculation engine must record:

* Input values.
* Input sources.
* Units.
* Calculation method.
* Method version.
* Intermediate results.
* Total heat loss.
* Missing inputs.
* Uncertainty or validation warnings.

Do not claim a verified heat loss when essential inputs are missing.

Do not silently replace missing U-values, temperatures, airflow rates or other engineering inputs with assumed values.

If estimates are supported later, label them explicitly as estimates and preserve the assumptions.

## 7. Heating requirement and radiator planning

Room-specific heat loss must be available as an input to the heating requirement calculation.

Radiator planning must not claim correct radiator sizing until the necessary design temperatures, radiator performance data and calculation method are available.

Keep these separate:

* Room heat loss.
* Required heating output.
* Selected radiator output.
* Radiator placement proposal.
* Final approved radiator selection.

## 8. Calculation architecture

Use deterministic, independently testable calculation services.

Separate:

* Geometry extraction.
* Room construction.
* Room validation.
* Input data collection.
* Airflow calculations.
* Heat loss calculations.
* Heating requirement calculations.
* Radiator selection.

Each calculation result must be traceable to its input data and calculation method.

Use explicit units and avoid ambiguous numeric values.

Use versioned calculation contracts so calculation results can be reproduced and compared later.

## 9. Updated development roadmap

Insert the following phases before radiator placement:

### Phase 2 – Geometry and room construction

* GEO-001 Source geometry normalization.
* GEO-002 Building element recognition.
* GEO-003 Room boundary detection.
* GEO-004 Room object construction.
* GEO-005 Room geometry validation.
* GEO-006 Area, height and volume calculation.

### Phase 3 – Room engineering calculations

* CALC-001 Engineering input data model.
* CALC-002 Room usage and classification.
* CALC-003 Ventilation design input collection.
* CALC-004 Room-specific airflow calculation.
* CALC-005 Building envelope thermal properties.
* CALC-006 Room-specific heat loss calculation.
* CALC-007 Heating requirement calculation.
* CALC-008 Calculation validation and audit.

### Phase 4 – Radiator planning

* ROOM-001 Radiator family registry.
* ROOM-002 Deterministic radiator placement rules.
* ROOM-003 AI-assisted placement proposal.
* ROOM-004 Visual preview.
* ROOM-005 Approved Revit model mutation.
* ROOM-006 User acceptance tests.

DXF ingestion and dataset development must integrate with the same room domain model.

## 10. Critical implementation rule

Do not implement radiator placement before room construction, room geometry validation and the required engineering calculation interfaces have been designed.

Do not implement regulatory compliance claims without documented and verified calculation methods and applicable requirements.

The system must distinguish:

* Geometry recognized.
* Room candidate identified.
* Room validated.
* Calculation inputs complete.
* Calculation completed.
* Calculation verified.
* Design proposal approved.
* Revit modification applied.
* Revit modification verified.
