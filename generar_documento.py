"""Genera la documentación Scrum del proyecto en formato Word.

Uso: ``./.venv/bin/python generar_documento.py``.
El archivo resultante se guarda en la raíz del repositorio y está ignorado por Git.
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUTPUT = Path(__file__).resolve().parent / "Documentacion_Scrum_SupervisorIA.docx"

TITULO = (
    "Software de Supervisión Inteligente de Obras y Seguridad Laboral "
    "mediante Visión Artificial"
)

PORTADA = [
    ("Universidad", "Universidad Autónoma Gabriel René Moreno"),
    ("Facultad", "Facultad de Ingeniería en Ciencias de la Computación y Telecomunicaciones"),
    ("Materia", "Ingeniería de Software I"),
    ("Docente", "Ing. Rolando Martínez"),
    ("Grupo", "14"),
    ("Integrante", "Rolando Velasco Soliz"),
    ("Fecha", "Noviembre 2026"),
]

SPRINT_0 = [
    (
        "Equipo Scrum",
        "Grupo 14: Rolando Velasco Soliz (Product Owner, Scrum Master y desarrollo). "
        "Equipo multidisciplinar a cargo del backend, frontend, aplicación móvil y pruebas.",
    ),
    (
        "Objetivo del Producto",
        "Supervisar obras y seguridad laboral mediante visión artificial: detectar "
        "personas, EPI, caídas y materiales en fotografías, emitir alertas en tiempo "
        "real, mantener trazabilidad por obra y generar reportes PDF.",
    ),
    (
        "Duración del Sprint",
        "Sprints de dos (2) semanas. Sprint 0 de definiciones iniciales y Sprints 1 a 3 "
        "de ejecución incremental, con revisión y retrospectiva al final de cada uno.",
    ),
    (
        "Infraestructura Tecnológica",
        "Python 3.12 + FastAPI/Uvicorn; React 19 + Vite + TailwindCSS; Flutter; "
        "Supabase (PostgreSQL y Auth); Cloudinary; YOLOv8 y MediaPipe; "
        "despliegue en Render y Cloudflare Pages.",
    ),
    (
        "Prácticas de Ingeniería",
        "Product backlog priorizado, sprint backlog por iteración, daily meetings, "
        "revisión de código, control de versiones con Git/GitHub, ramas por historia "
        "y automatización de pruebas y compilación.",
    ),
    (
        "Criterios de Calidad",
        "Suite de 69 pruebas pytest en verde, npm run build sin errores, endpoints "
        "protegidos con JWT, fallos de los modelos de IA no interrumpen el pipeline, "
        "cobertura de autenticación, obras, carga, detecciones, alertas, reportes y overlay.",
    ),
]

PRODUCT_BACKLOG = [
    ("R-1", "Login", "Registro e inicio de sesión de supervisores con Supabase Auth y JWT.", "Alta"),
    ("R-2", "Obras", "Crear, listar y consultar obras con ubicación y fechas de inicio y fin.", "Alta"),
    ("R-3", "Subida de fotos", "Cargar imágenes al backend, guardarlas en Cloudinary y registrarlas por obra.", "Alta"),
    ("R-4", "IA de personas", "Detectar personas con YOLOv8 y contarlas en cada imagen analizada.", "Alta"),
    ("R-5", "IA de EPI", "Detectar casco y chaleco con el modelo PPE y alertar si faltan.", "Alta"),
    ("R-6", "IA de caídas", "Detectar posturas de caída con MediaPipe Pose y emitir alerta de nivel alto.", "Alta"),
    ("R-7", "Conteo de materiales", "Detectar camiones, mochilas, maletines y botellas como materiales.", "Media"),
    ("R-8", "Plano y overlay", "Subir el plano de cada obra y superponer la foto analizada con cv2.addWeighted.", "Media"),
    ("R-9", "Alertas en vivo", "Difundir alertas por WebSocket con icono rojo para caídas.", "Alta"),
    ("R-10", "Reportes PDF", "Generar un reporte PDF por obra con resumen y tabla de alertas.", "Media"),
    ("R-11", "App móvil offline", "Capturar fotos en Flutter, guardarlas en SQLite y sincronizar al recuperar conexión.", "Media"),
    ("R-12", "Cámara en vivo", "Capturar desde la cámara del navegador con selección y volteo frontal/trasera.", "Media"),
    ("R-13", "Panel de métricas", "Mostrar obras, alertas pendientes, imágenes y materiales detectados.", "Baja"),
    ("R-14", "Resolver alertas", "Marcar alertas como resueltas y filtrarlas por obra y estado.", "Baja"),
]

SPRINTS = [
    (
        "Sprint 1 — Fundamentos, autenticación y análisis básico",
        "Entregar el núcleo funcional: acceso seguro, gestión de obras, carga de imágenes "
        "y detección de personas con alertas en tiempo real.",
        [
            ("S1-1", "Configurar proyecto FastAPI, settings y esquemas Pydantic", "5", "Rolando Velasco Soliz", "Completado"),
            ("S1-2", "Diseñar el esquema de base de datos y el script init_db.py", "5", "Rolando Velasco Soliz", "Completado"),
            ("S1-3", "Autenticación Supabase: /register, /login y validación JWT", "5", "Rolando Velasco Soliz", "Completado"),
            ("S1-4", "Endpoints de obras: crear, listar y consultar por id", "3", "Rolando Velasco Soliz", "Completado"),
            ("S1-5", "Subida de imágenes, archivos temporales y Cloudinary", "5", "Rolando Velasco Soliz", "Completado"),
            ("S1-6", "Detección de personas con YOLOv8 y persistencia del análisis", "8", "Rolando Velasco Soliz", "Completado"),
            ("S1-7", "Creación de alertas y canal WebSocket /ws/alertas", "5", "Rolando Velasco Soliz", "Completado"),
            ("S1-8", "Dashboard: login, métricas y feed de alertas en React", "8", "Rolando Velasco Soliz", "Completado"),
        ],
    ),
    (
        "Sprint 2 — Seguridad laboral, reportes y móvil",
        "Ampliar el análisis con EPI, caídas y materiales; incorporar cámaras, reportes "
        "PDF y la aplicación móvil con trabajo offline.",
        [
            ("S2-1", "Modelo PPE de seis clases y detección de casco/chaleco", "8", "Rolando Velasco Soliz", "Completado"),
            ("S2-2", "Alertas de falta de EPI por proporción persona/EPI", "3", "Rolando Velasco Soliz", "Completado"),
            ("S2-3", "Detección de caídas con MediaPipe Pose y regla heurística", "8", "Rolando Velasco Soliz", "Completado"),
            ("S2-4", "Icono rojo de caída en AlertCard y tabla de Alertas", "2", "Rolando Velasco Soliz", "Completado"),
            ("S2-5", "Conteo de materiales y métrica 'Materiales Detectados'", "3", "Rolando Velasco Soliz", "Completado"),
            ("S2-6", "Reportes PDF por obra con tabla de alertas", "5", "Rolando Velasco Soliz", "Completado"),
            ("S2-7", "Cámara en vivo, captura y volteo frontal/trasera", "8", "Rolando Velasco Soliz", "Completado"),
            ("S2-8", "App Flutter con SQLite offline y sincronización al reconectar", "8", "Rolando Velasco Soliz", "Completado"),
        ],
    ),
    (
        "Sprint 3 — Overlay sobre plano, calidad y despliegue",
        "Cerrar la trazabilidad visual sobre el plano de la obra, consolidar pruebas "
        "automáticas y publicar el sistema.",
        [
            ("S3-1", "Columnas plano_url y overlay_url con migración idempotente", "3", "Rolando Velasco Soliz", "Completado"),
            ("S3-2", "Endpoint POST /obras/{id}/plano y botón 'Subir Plano' en Obras", "5", "Rolando Velasco Soliz", "Completado"),
            ("S3-3", "generar_overlay con cv2.addWeighted y subida del resultado", "5", "Rolando Velasco Soliz", "Completado"),
            ("S3-4", "Persistencia de overlay_url y payload de /results", "3", "Rolando Velasco Soliz", "Completado"),
            ("S3-5", "Miniatura y modal de overlay en el Dashboard", "5", "Rolando Velasco Soliz", "Completado"),
            ("S3-6", "Suite de 69 pruebas pytest y compilación frontend limpia", "5", "Rolando Velasco Soliz", "Completado"),
            ("S3-7", "Despliegue en Render/Cloudflare Pages y documentación Scrum", "3", "Rolando Velasco Soliz", "Completado"),
        ],
    ),
]

FORMATO_HU = [
    ("Id", "Identificador único de la historia (HU-01, HU-02, …)."),
    ("Nombre corto", "Título breve y reconocible de la funcionalidad."),
    ("Prioridad", "Valor negocial: Alta, Media o Baja."),
    ("PHU", "Puntos de historia de usuario estimados con la escala de Fibonacci."),
    ("Como", "Rol que ejecuta la acción."),
    ("Quiero", "Acción o funcionalidad esperada."),
    ("Para", "Beneficio o valor que se obtiene."),
    ("Criterios de aceptación", "Lista verificable de condiciones de cumplimiento."),
]

HISTORIAS = [
    [
        ("Id", "HU-01"),
        ("Nombre corto", "Detección de caídas"),
        ("Prioridad", "Alta"),
        ("PHU", "8"),
        ("Como", "supervisor de seguridad laboral"),
        ("Quiero", "recibir una alerta automática cuando una persona esté caída en la zona vigilada"),
        ("Para", "atender de inmediato un posible accidente y reducir el tiempo de respuesta"),
        (
            "Criterios de aceptación",
            "1) Una imagen con una persona en posición horizontal marca caida_detectada=true. "
            "2) Se crea una alerta tipo 'caida', nivel 'alta' y descripción "
            "'Posible caída de personal detectada'. "
            "3) La alerta se transmite por WebSocket y muestra un icono rojo en el dashboard. "
            "4) Si MediaPipe falla, el análisis continúa sin generar la alerta.",
        ),
    ],
    [
        ("Id", "HU-02"),
        ("Nombre corto", "Gestión de obras"),
        ("Prioridad", "Alta"),
        ("PHU", "5"),
        ("Como", "supervisor de obra"),
        ("Quiero", "registrar y consultar obras con su ubicación y período de ejecución"),
        ("Para", "organizar las inspecciones y asociar cada análisis a una obra concreta"),
        (
            "Criterios de aceptación",
            "1) POST /obras crea la obra con fechas convertidas a ISO. "
            "2) GET /obras devuelve el listado y GET /obras/{id} el detalle. "
            "3) Una obra inexistente responde 404. "
            "4) Todos los endpoints requieren token JWT válido.",
        ),
    ],
    [
        ("Id", "HU-03"),
        ("Nombre corto", "Overlay sobre el plano"),
        ("Prioridad", "Media"),
        ("PHU", "5"),
        ("Como", "supervisor de obra"),
        ("Quiero", "subir el plano de la obra y ver la fotografía analizada superpuesta"),
        ("Para", "ubicar visualmente las incidencias dentro de la planta de la construcción"),
        (
            "Criterios de aceptación",
            "1) POST /obras/{id}/plano guarda la URL de Cloudinary en plano_url. "
            "2) generar_overlay fusiona plano y foto al 50 %/50 % con cv2.addWeighted. "
            "3) Sin plano o ante un error, se devuelve la URL de la foto original. "
            "4) El Dashboard muestra una miniatura y permite ampliarla en un modal.",
        ),
    ],
]

DIAGRAMAS = [
    ("Diagrama de Casos de Uso", "Casos de uso: autenticarse, gestionar obras, subir plano, capturar/subir foto, analizar imagen, recibir alertas, resolver alertas, descargar reporte y sincronizar fotos offline."),
    ("Diagrama de Clases", "Clases principales: Usuario, Obra, Imagen, Analisis, Alerta, ObraResponse, UploadResponse y servicios storage/analysis/database."),
    ("Diagrama de Despliegue", "Cliente web (Cloudflare Pages) y app Flutter → API FastAPI (Render) → Supabase (Auth/PostgreSQL) y Cloudinary (imágenes), con modelos YOLOv8, PPE y MediaPipe en el servidor."),
]


_STATE = {"document": None}


def _centered(text: str, size: int = 12, bold: bool = False) -> None:
    paragraph = _STATE["document"].add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold


def _shade(cell, color: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), color)
    properties.append(shading)


def _repeat_header(row) -> None:
    properties = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    properties.append(header)


def add_table(headers, rows, widths=None) -> None:
    """Insert a grid table with a shaded, repeating header row."""
    table = _STATE["document"].add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    for index, text in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = text
        _shade(cell, "1F4E79")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    _repeat_header(table.rows[0])

    for values in rows:
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cells[index].text = str(value)
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for run in cells[index].paragraphs[0].runs:
                run.font.size = Pt(9)

    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Cm(width)
    _STATE["document"].add_paragraph()


def build_cover() -> None:
    document = _STATE["document"]
    for _ in range(3):
        document.add_paragraph()
    _centered(PORTADA[0][1], size=14, bold=True)
    _centered(PORTADA[1][1], size=12, bold=True)
    for _ in range(4):
        document.add_paragraph()
    _centered(TITULO, size=18, bold=True)
    for _ in range(4):
        document.add_paragraph()
    for label, value in PORTADA[2:]:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(f"{label}: {value}")
        run.font.size = Pt(12)
    document.add_page_break()


def build_sprint_zero() -> None:
    document = _STATE["document"]
    document.add_heading("Sprint 0 — Definiciones Iniciales (R-1)", level=1)
    document.add_paragraph(
        "Esta sección consolida los acuerdos iniciales del equipo antes de iniciar "
        "la planificación de los sprints de ejecución."
    )
    add_table(["Concepto", "Definición"], SPRINT_0, widths=[4.5, 12])


def build_product_backlog() -> None:
    document = _STATE["document"]
    document.add_heading("Product Backlog (F3)", level=1)
    document.add_paragraph(
        "Listado priorizado de requerimientos del producto. La prioridad refleja el "
        "valor para el supervisor y la dependencia entre funcionalidades."
    )
    add_table(
        ["ID", "Nombre corto", "Descripción del requerimiento", "Prioridad"],
        PRODUCT_BACKLOG,
        widths=[1.8, 3, 9, 2.2],
    )


def build_sprints() -> None:
    document = _STATE["document"]
    for title, goal, tasks in SPRINTS:
        document.add_heading(title, level=1)
        document.add_paragraph(f"Objetivo del sprint: {goal}")
        document.add_heading("Sprint Backlog (F5)", level=2)
        add_table(
            ["Id", "Tarea", "Estimación", "Responsable", "Estado"],
            tasks,
            widths=[1.8, 8, 2, 3.2, 2],
        )


def build_user_stories() -> None:
    document = _STATE["document"]
    document.add_heading("Historias de Usuario (F4)", level=1)
    document.add_paragraph(
        "Formato adoptado por el equipo para documentar cada historia. Los puntos de "
        "historia (PHU) se estiman con la escala de Fibonacci."
    )
    add_table(["Campo", "Descripción"], FORMATO_HU, widths=[4.5, 12])
    document.add_heading("Ejemplos de historias de usuario", level=2)
    for story in HISTORIAS:
        document.add_heading(f"{story[0][1]} — {story[1][1]}", level=3)
        add_table(["Campo", "Contenido"], story, widths=[4.5, 12])


def build_diagrams() -> None:
    document = _STATE["document"]
    document.add_heading("Diagramas UML", level=1)
    for title, note in DIAGRAMAS:
        document.add_heading(title, level=2)
        document.add_paragraph(note)
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run("[Insertar Diagrama UML aquí]")
        run.italic = True
        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
        for _ in range(4):
            document.add_paragraph()


def main() -> None:
    document = Document()
    _STATE["document"] = document

    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    document.core_properties.title = TITULO
    document.core_properties.author = "Rolando Velasco Soliz"
    document.core_properties.subject = "Documentación Scrum — Ingeniería de Software I"

    build_cover()
    build_sprint_zero()
    build_product_backlog()
    build_sprints()
    build_user_stories()
    build_diagrams()

    document.save(OUTPUT)
    print(f"Documento generado: {OUTPUT}")


if __name__ == "__main__":
    main()
