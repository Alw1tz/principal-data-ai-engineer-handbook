# Assets

Static files referenced from chapters/labs/projects via relative links (e.g. `![diagram](../../assets/diagrams/foo.png)` from a topic chapter).

| Folder | For |
|---|---|
| `images/` | Screenshots, photos, anything raster |
| `diagrams/` | Exported diagram images (draw.io, Excalidraw, etc. — export both the source and a `.png`/`.svg` here) |
| `architecture/` | Architecture diagrams specifically — kept separate from general `diagrams/` since these get referenced heavily from Production Architecture / Internal Architecture chapter sections |
| `mermaid/` | Mermaid `.mmd` source files (GitHub renders mermaid inline in markdown directly — these are for diagrams reused across multiple pages, or too complex to inline) |
| `plantuml/` | PlantUML `.puml` source files. **Unlike Mermaid, GitHub does not render PlantUML inline** — write the diagram here, preview it in VS Code (`jebbs.plantuml` extension, configured to use the public PlantUML server, no local install needed), export it (`Export Current Diagram`) as PNG/SVG into `diagrams/` or `architecture/`, and embed *that* image in the page. |
| `pdfs/` | PDF exports (slide decks, printable checklists) |

Keep filenames scoped to their topic to avoid collisions, e.g. `spark-shuffle-architecture.png` rather than `architecture.png`.
