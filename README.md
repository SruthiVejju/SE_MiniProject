# Software Engineering Mini-Project

## TEAM H15 - Hostel Management System
- Shashank Vinayak - PES1UG24CS435
- Shubashtiha Gowtham - PES1UG24CS450
- Simran Joshi - PES1UG24CS455
- Sruthi Vejju - PES1UG24CS472

A web-based system to digitize hostel administration: student registration, room/bed allocation, fee collection, complaint handling, leave/outpass management, visitor logging, notices, and occupancy reporting.

## Part-1 Deliverables

| # | Deliverable | Document |
|---|---|---|
| 1 | Software Requirements Specification (IEEE 830) | [`docs/SRS.md`](docs/SRS.md) |
| 2 | Test Plan (IEEE 829), incl. 10 test cases and security validation | [`docs/Test_Plan.md`](docs/Test_Plan.md) |
| 3 | Software Architecture & Design Specification (IEEE 1016) | [`docs/Architecture_Design.md`](docs/Architecture_Design.md) |

## Diagrams

Rendered UML diagrams live in [`docs/diagrams/`](docs/diagrams/); their editable PlantUML sources are in [`docs/diagrams/src/`](docs/diagrams/src/).

- Use Case Diagram — `use-case-diagram.png`
- Component Diagram — `component-diagram.png`
- Sequence Diagrams — `sequence-login.png`, `sequence-room-allocation.png`, `sequence-fee-payment.png`

To regenerate diagrams after editing a `.puml` file:

```bash
java -jar plantuml.jar -o .. docs/diagrams/src/*.puml
```

(requires Java and Graphviz's `dot` on `PATH`)
