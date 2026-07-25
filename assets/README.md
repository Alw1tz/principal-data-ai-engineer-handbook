# Assets

Static files referenced from chapters/labs/projects via relative links (e.g. `![diagram](../../assets/diagrams/foo.png)` from a topic chapter).

| Folder | For |
|---|---|
| `images/` | Screenshots, photos, anything raster |
| `diagrams/` | Exported diagram images (draw.io, Excalidraw, etc. — export both the source and a `.png`/`.svg` here) |
| `architecture/` | Architecture diagrams specifically — kept separate from general `diagrams/` since these get referenced heavily from Production Architecture / Internal Architecture chapter sections |
| `mermaid/` | Mermaid `.mmd` source files (GitHub renders mermaid inline in markdown directly — these are for diagrams reused across multiple pages, or too complex to inline) |
| `pdfs/` | PDF exports (slide decks, printable checklists) |

Keep filenames scoped to their topic to avoid collisions, e.g. `spark-shuffle-architecture.png` rather than `architecture.png`.
