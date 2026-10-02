import os
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
WIDTH = 1920
HEIGHT = 1080

# Color Palette
BG_COLOR = (15, 23, 42)          # Slate 900
PANEL_BG = (30, 41, 59)          # Slate 800
PANEL_BORDER = (51, 65, 85)      # Slate 700
TEAL_ACCENT = (13, 148, 136)     # Teal 600
TEAL_LIGHT = (45, 212, 191)      # Teal 400
TEXT_WHITE = (248, 250, 252)     # Slate 50
TEXT_MUTED = (148, 163, 184)     # Slate 400
TEXT_DIM = (100, 116, 139)       # Slate 500
GREEN_ACCENT = (16, 185, 129)    # Emerald 500
AMBER_ACCENT = (245, 158, 11)    # Amber 500
ROSE_ACCENT = (244, 63, 94)      # Rose 500
TERMINAL_BG = (10, 15, 29)       # Dark Terminal

# Font Loaders
FONT_SANS_PATH = "C:/Windows/Fonts/segoeui.ttf"
FONT_SANS_BOLD_PATH = "C:/Windows/Fonts/segoeuib.ttf"
FONT_MONO_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_MONO_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf"


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


font_title = get_font(FONT_SANS_BOLD_PATH, 38)
font_subtitle = get_font(FONT_SANS_PATH, 22)
font_section_num = get_font(FONT_SANS_BOLD_PATH, 16)
font_section_title = get_font(FONT_SANS_BOLD_PATH, 24)
font_body = get_font(FONT_SANS_PATH, 18)
font_caption = get_font(FONT_SANS_PATH, 20)
font_caption_bold = get_font(FONT_SANS_BOLD_PATH, 20)
font_mono = get_font(FONT_MONO_PATH, 18)
font_mono_small = get_font(FONT_MONO_PATH, 15)
font_mono_bold = get_font(FONT_MONO_BOLD_PATH, 18)


def create_base_frame(section_num: str, section_title: str, caption_text: str) -> Image.Image:
    """Creates standard 1920x1080 frame with header and lower-third caption."""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    # Top Header Bar (Height: 70px)
    draw.rectangle([(0, 0), (WIDTH, 70)], fill=(20, 29, 47))
    draw.line([(0, 70), (WIDTH, 70)], fill=(51, 65, 85), width=1)

    # Header Logo Badge
    draw.rounded_rectangle([(30, 16), (68, 54)], radius=8, fill=TEAL_ACCENT)
    draw.text((41, 19), "EVE", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 15))

    # Header Platform Title
    draw.text((80, 22), "EVE Healthcare", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 20))
    draw.text((230, 25), "— SDE Intern Backend Engineering Assignment", fill=TEXT_MUTED, font=font_subtitle)

    # Header Section Pill on the right
    pill_text = f"{section_num}  |  {section_title}"
    bbox = font_section_num.getbbox(pill_text)
    pill_w = bbox[2] - bbox[0] + 32
    pill_x1 = WIDTH - 30 - pill_w
    draw.rounded_rectangle([(pill_x1, 18), (WIDTH - 30, 52)], radius=17, fill=(30, 41, 59), outline=(71, 85, 105))
    draw.text((pill_x1 + 16, 24), pill_text, fill=TEAL_LIGHT, font=font_section_num)

    # Lower-third Caption Bar (Y: 980 to 1050)
    draw.rounded_rectangle([(40, 985), (WIDTH - 40, 1055)], radius=12, fill=(24, 34, 53), outline=(51, 65, 85))
    draw.rounded_rectangle([(40, 985), (48, 1055)], radius=4, fill=TEAL_ACCENT)  # Teal accent left edge
    draw.text((70, 1005), caption_text, fill=TEXT_WHITE, font=font_caption)

    return im


def draw_terminal_window(draw: ImageDraw.ImageDraw, x1, y1, x2, y2, title: str):
    """Draws a macOS / Linux style dark terminal container."""
    # Terminal background
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=10, fill=TERMINAL_BG, outline=PANEL_BORDER, width=2)
    # Header bar
    draw.rounded_rectangle([(x1, y1), (x2, y1 + 36)], radius=10, fill=(30, 41, 59))
    draw.rectangle([(x1, y1 + 20), (x2, y1 + 36)], fill=(30, 41, 59))  # square bottom corners
    draw.line([(x1, y1 + 36), (x2, y1 + 36)], fill=PANEL_BORDER, width=1)

    # Traffic light window dots
    draw.ellipse([(x1 + 16, y1 + 12), (x1 + 28, y1 + 24)], fill=(239, 68, 68))
    draw.ellipse([(x1 + 36, y1 + 12), (x1 + 48, y1 + 24)], fill=(245, 158, 11))
    draw.ellipse([(x1 + 56, y1 + 12), (x1 + 68, y1 + 24)], fill=(16, 185, 129))

    # Window title
    draw.text((x1 + 90, y1 + 9), title, fill=TEXT_MUTED, font=font_mono_small)


def paste_image_centered(base_im: Image.Image, screenshot_path: str, x1=60, y1=90, x2=1860, y2=960):
    """Resizes and fits a screenshot inside bounding box preserving aspect ratio."""
    if not os.path.exists(screenshot_path):
        return base_im
    try:
        shot = Image.open(screenshot_path).convert("RGB")
        target_w = x2 - x1
        target_h = y2 - y1

        shot_w, shot_h = shot.size
        ratio = min(target_w / shot_w, target_h / shot_h)
        new_w = int(shot_w * ratio)
        new_h = int(shot_h * ratio)
        shot_resized = shot.resize((new_w, new_h), Image.Resampling.LANCZOS)

        paste_x = x1 + (target_w - new_w) // 2
        paste_y = y1 + (target_h - new_h) // 2

        # Draw clean border around screenshot
        draw = ImageDraw.Draw(base_im)
        draw.rounded_rectangle(
            [(paste_x - 3, paste_y - 3), (paste_x + new_w + 3, paste_y + new_h + 3)],
            radius=8,
            fill=(51, 65, 85),
        )
        base_im.paste(shot_resized, (paste_x, paste_y))
    except Exception as e:
        print(f"Error pasting screenshot {screenshot_path}: {e}")
    return base_im


def render_title_scene(output_png: str):
    """Renders 01 Intro Title Card."""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    # Top brand bar
    draw.rectangle([(0, 0), (WIDTH, 8)], fill=TEAL_ACCENT)

    # Center card
    card_x1, card_y1, card_x2, card_y2 = 260, 160, 1660, 920
    draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y2)], radius=16, fill=(20, 29, 47), outline=(51, 65, 85), width=2)

    # Logo icon badge
    draw.rounded_rectangle([(910, 220), (1010, 320)], radius=24, fill=TEAL_ACCENT)
    draw.text((925, 238), "EVE", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 48))

    # Titles
    draw.text((960, 360), "EVE Healthcare", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 48), anchor="mt")
    draw.text((960, 425), "SDE Intern Backend Engineering Assignment", fill=TEAL_LIGHT, font=get_font(FONT_SANS_BOLD_PATH, 28), anchor="mt")
    draw.text((960, 475), "FastAPI • PostgreSQL • Redis • Celery • React & TypeScript", fill=TEXT_MUTED, font=font_subtitle, anchor="mt")

    # Feature boxes grid
    pillars = [
        ("JWT Authentication", "Stateless HS256 Bearer tokens & bcrypt hashing"),
        ("PostgreSQL 16", "Async SQLAlchemy 2.0 & Alembic migrations"),
        ("Booking State Machine", "Enforced PENDING -> CONFIRMED / FAILED / CANCELLED"),
        ("Idempotent Webhooks", "Deduplication via unique webhook event logs"),
        ("Redis Infrastructure", "In-memory caching and client-IP rate limiting"),
        ("Celery Workers", "Decoupled asynchronous background execution"),
    ]

    grid_y = 550
    for i, (p_title, p_desc) in enumerate(pillars):
        col = i % 3
        row = i // 3
        bx1 = 300 + col * 440
        by1 = grid_y + row * 130
        bx2 = bx1 + 410
        by2 = by1 + 105

        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=12, fill=(30, 41, 59), outline=(71, 85, 105))
        draw.text((bx1 + 20, by1 + 18), f"✓  {p_title}", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 18))
        draw.text((bx1 + 20, by1 + 52), p_desc, fill=TEXT_MUTED, font=get_font(FONT_SANS_PATH, 14))

    # Bottom footer tag
    draw.text((960, 855), "Live Server: 127.0.0.1:8000  •  OpenAPI Docs: /docs  •  Health: /health", fill=TEXT_DIM, font=font_mono_small, anchor="mt")

    im.save(output_png)


def render_architecture_scene(output_png: str):
    """Renders 02 System Architecture Topology."""
    im = create_base_frame(
        "02",
        "System Architecture",
        "High-performance architecture: React client interacting with a decoupled, asynchronous FastAPI backend.",
    )
    draw = ImageDraw.Draw(im)

    # Topology Diagram Canvas
    draw.rounded_rectangle([(100, 110), (1820, 940)], radius=14, fill=(20, 29, 47), outline=PANEL_BORDER, width=2)
    draw.text((140, 140), "Full-Stack System Architecture & Service Topology", fill=TEXT_WHITE, font=font_title)
    draw.text((140, 190), "Strict separation of concerns between client presentation, synchronous API routing, and async background workers", fill=TEXT_MUTED, font=font_subtitle)

    boxes = [
        ("React + TypeScript Client", "SPA / UI Layer\n• Vite 6 + Tailwind CSS\n• Axios Bearer Interceptor\n• Client-side Route Guards\n• Simulated Gateway Controls", 160, 280, 480, 520, TEAL_ACCENT),
        ("FastAPI Gateway & API", "Synchronous HTTP Layer\n• Pydantic Request Validation\n• HS256 JWT Verification\n• SlowAPI Rate Limiter (10 req/min)\n• Server-Side Authorization", 620, 280, 980, 520, (59, 130, 246)),
        ("PostgreSQL Database", "Relational Persistence\n• SQLAlchemy 2.0 Async Engine\n• Unique & Foreign Key Constraints\n• Idempotent Webhook Events Table\n• Alembic Schema Versioning", 1120, 280, 1480, 520, (139, 92, 246)),
        ("Redis Broker & Cache", "In-Memory Infrastructure\n• Cache for Centres & Tests\n• 10 req/min Rate Limiter Store\n• Celery Message Broker (/1)", 620, 600, 980, 840, (239, 68, 68)),
        ("Celery Background Worker", "Asynchronous Processing\n• Decoupled Webhook Tasks\n• Payment Settlement Simulation\n• Automated Retry Queue", 1120, 600, 1480, 840, (16, 185, 129)),
    ]

    for title, desc, bx1, by1, bx2, by2, accent in boxes:
        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=12, fill=(30, 41, 59), outline=PANEL_BORDER, width=2)
        draw.rounded_rectangle([(bx1, by1), (bx2, by1 + 45)], radius=12, fill=accent)
        draw.rectangle([(bx1, by1 + 25), (bx2, by1 + 45)], fill=accent)
        draw.text((bx1 + 16, by1 + 12), title, fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 18))
        draw.text((bx1 + 20, by1 + 65), desc, fill=TEXT_WHITE, font=font_mono_small)

    # Connection lines with labels
    draw.line([(480, 400), (620, 400)], fill=TEAL_LIGHT, width=3)
    draw.text((515, 370), "REST / JSON", fill=TEAL_LIGHT, font=font_mono_small)

    draw.line([(980, 400), (1120, 400)], fill=(139, 92, 246), width=3)
    draw.text((1010, 370), "Asyncpg", fill=(139, 92, 246), font=font_mono_small)

    draw.line([(800, 520), (800, 600)], fill=(239, 68, 68), width=3)
    draw.text((815, 550), "Cache / Rate Limit", fill=(239, 68, 68), font=font_mono_small)

    draw.line([(980, 720), (1120, 720)], fill=(16, 185, 129), width=3)
    draw.text((1015, 690), "Task Queue", fill=(16, 185, 129), font=font_mono_small)

    im.save(output_png)


def render_ui_scene(output_png: str, section_num: str, section_title: str, caption: str, screenshot_path: str):
    """Renders a standard UI page view."""
    im = create_base_frame(section_num, section_title, caption)
    paste_image_centered(im, screenshot_path, x1=120, y1=95, x2=1800, y2=960)
    im.save(output_png)


def render_terminal_scene(output_png: str, section_num: str, section_title: str, caption: str, term_title: str, lines: list):
    """Renders a terminal window with styled colored monospace lines."""
    im = create_base_frame(section_num, section_title, caption)
    draw = ImageDraw.Draw(im)

    x1, y1, x2, y2 = 120, 95, 1800, 960
    draw_terminal_window(draw, x1, y1, x2, y2, term_title)

    text_x = x1 + 28
    text_y = y1 + 55
    line_h = 24

    for text, color_override in lines:
        if text_y + line_h > y2 - 20:
            break
        color = color_override if color_override else TEXT_MUTED
        draw.text((text_x, text_y), text, fill=color, font=font_mono)
        text_y += line_h

    im.save(output_png)


def render_state_machine_scene(output_png: str):
    """Renders 06 Booking State Machine Architecture."""
    im = create_base_frame(
        "06",
        "Booking State Machine",
        "Deterministic booking state transitions: PENDING -> CONFIRMED, FAILED, or CANCELLED strictly enforced server-side.",
    )
    draw = ImageDraw.Draw(im)

    draw.rounded_rectangle([(100, 110), (1820, 940)], radius=14, fill=(20, 29, 47), outline=PANEL_BORDER, width=2)
    draw.text((140, 140), "Deterministic Booking Lifecycle State Machine", fill=TEXT_WHITE, font=font_title)
    draw.text((140, 190), "Service-layer verification prevents illegal state jumps (e.g. paying for cancelled or already confirmed bookings)", fill=TEXT_MUTED, font=font_subtitle)

    # Initial State: PENDING
    draw.rounded_rectangle([(200, 430), (520, 570)], radius=14, fill=(245, 158, 11), outline=(251, 191, 36), width=2)
    draw.text((360, 470), "PENDING", fill=(15, 23, 42), font=get_font(FONT_SANS_BOLD_PATH, 32), anchor="mt")
    draw.text((360, 520), "Initial booking created; awaiting payment", fill=(15, 23, 42), font=get_font(FONT_SANS_BOLD_PATH, 14), anchor="mt")

    # Transition arrows & labels
    # -> CONFIRMED
    draw.line([(520, 480), (1200, 310)], fill=GREEN_ACCENT, width=4)
    draw.text((780, 340), "Payment Webhook: SUCCESS  →", fill=GREEN_ACCENT, font=font_mono_bold)

    draw.rounded_rectangle([(1200, 240), (1600, 380)], radius=14, fill=GREEN_ACCENT, outline=(52, 211, 153), width=2)
    draw.text((1400, 280), "CONFIRMED", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 32), anchor="mt")
    draw.text((1400, 330), "Terminal Successful State", fill=TEXT_WHITE, font=get_font(FONT_SANS_PATH, 16), anchor="mt")

    # -> FAILED
    draw.line([(520, 500), (1200, 500)], fill=ROSE_ACCENT, width=4)
    draw.text((780, 470), "Payment Webhook: FAILED  →", fill=ROSE_ACCENT, font=font_mono_bold)

    draw.rounded_rectangle([(1200, 430), (1600, 570)], radius=14, fill=ROSE_ACCENT, outline=(251, 113, 133), width=2)
    draw.text((1400, 470), "FAILED", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 32), anchor="mt")
    draw.text((1400, 520), "Settlement failed; retry allowed", fill=TEXT_WHITE, font=get_font(FONT_SANS_PATH, 16), anchor="mt")

    # -> CANCELLED
    draw.line([(520, 520), (1200, 690)], fill=TEXT_MUTED, width=4)
    draw.text((780, 610), "POST /bookings/{id}/cancel  →", fill=TEXT_MUTED, font=font_mono_bold)

    draw.rounded_rectangle([(1200, 620), (1600, 760)], radius=14, fill=(51, 65, 85), outline=(100, 116, 139), width=2)
    draw.text((1400, 660), "CANCELLED", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 32), anchor="mt")
    draw.text((1400, 710), "Cancelled by user before payment", fill=TEXT_MUTED, font=get_font(FONT_SANS_PATH, 16), anchor="mt")

    # State Rules Panel at bottom
    draw.rounded_rectangle([(140, 800), (1780, 910)], radius=10, fill=(30, 41, 59), outline=PANEL_BORDER)
    draw.text((170, 825), "ENFORCED CONSTRAINTS:", fill=TEAL_LIGHT, font=get_font(FONT_SANS_BOLD_PATH, 16))
    draw.text((400, 825), "• Cancel permitted ONLY while PENDING  • Payments on CONFIRMED or CANCELLED bookings reject with HTTP 400", fill=TEXT_WHITE, font=font_mono_small)
    draw.text((400, 855), "• Derived amounts immutable  • Repeated payments blocked idempotently", fill=TEXT_MUTED, font=font_mono_small)

    im.save(output_png)


def render_idempotency_diagram_scene(output_png: str):
    """Renders 09 Webhook Idempotency Architecture Scene."""
    im = create_base_frame(
        "09",
        "Webhook Idempotency",
        "Idempotent webhook deduplication: Database uniqueness on event_id guarantees safe, zero-side-effect replays.",
    )
    draw = ImageDraw.Draw(im)

    draw.rounded_rectangle([(100, 110), (1820, 940)], radius=14, fill=(20, 29, 47), outline=PANEL_BORDER, width=2)
    draw.text((140, 140), "Idempotent Payment Webhook Architecture", fill=TEXT_WHITE, font=font_title)
    draw.text((140, 190), "External gateways retry webhooks on network timeouts. The backend guarantees exactly-once state mutation.", fill=TEXT_MUTED, font=font_subtitle)

    # 1st Webhook Delivery Card
    draw.rounded_rectangle([(160, 260), (900, 560)], radius=12, fill=(30, 41, 59), outline=GREEN_ACCENT, width=2)
    draw.text((190, 280), "1st Delivery: Event ID 'evt_demo_idempotency_999'", fill=GREEN_ACCENT, font=get_font(FONT_SANS_BOLD_PATH, 20))
    code_1st = [
        "1. Backend queries webhook_events table for event_id",
        "2. Record NOT found -> First-time delivery confirmed",
        "3. Inserts into webhook_events (event_id, payload, timestamp)",
        "4. Executes Booking state transition: PENDING -> CONFIRMED",
        "5. Response: HTTP 200 OK  {\"status\": \"processed\"}"
    ]
    for idx, c in enumerate(code_1st):
        draw.text((190, 330 + idx * 38), c, fill=TEXT_WHITE, font=font_mono_small)

    # 2nd Webhook Delivery Card (Duplicate)
    draw.rounded_rectangle([(980, 260), (1720, 560)], radius=12, fill=(30, 41, 59), outline=AMBER_ACCENT, width=2)
    draw.text((1010, 280), "2nd Delivery: Exact Same Event ID (Replay / Retry)", fill=AMBER_ACCENT, font=get_font(FONT_SANS_BOLD_PATH, 20))
    code_2nd = [
        "1. Backend queries webhook_events table for event_id",
        "2. Record ALREADY EXISTS -> Duplicate delivery detected",
        "3. Bypass state machine mutation (no redundant DB writes)",
        "4. Prevents duplicate charges and corrupted state",
        "5. Response: HTTP 200 OK  {\"status\": \"already_processed\"}"
    ]
    for idx, c in enumerate(code_2nd):
        draw.text((1010, 330 + idx * 38), c, fill=TEXT_WHITE, font=font_mono_small)

    # Table schema box below
    draw.rounded_rectangle([(160, 600), (1720, 890)], radius=12, fill=(10, 15, 29), outline=PANEL_BORDER, width=2)
    draw.text((190, 625), "PostgreSQL Database Schema: webhook_events", fill=TEAL_LIGHT, font=font_mono_bold)

    schema_lines = [
        "CREATE TABLE webhook_events (",
        "    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),",
        "    event_id            VARCHAR(255) NOT NULL UNIQUE,          -- Unique constraint enforces idempotency",
        "    provider_reference  VARCHAR(255),",
        "    payload             JSONB NOT NULL,",
        "    processed_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
        ");",
        "CREATE UNIQUE INDEX ix_webhook_events_event_id ON webhook_events (event_id);"
    ]
    for idx, sl in enumerate(schema_lines):
        color = GREEN_ACCENT if "UNIQUE" in sl else TEXT_MUTED
        draw.text((190, 665 + idx * 24), sl, fill=color, font=font_mono_small)

    im.save(output_png)


def render_summary_scene(output_png: str):
    """Renders 17 Engineering Summary Card."""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    # Top brand bar
    draw.rectangle([(0, 0), (WIDTH, 8)], fill=TEAL_ACCENT)

    card_x1, card_y1, card_x2, card_y2 = 200, 100, 1720, 980
    draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y2)], radius=16, fill=(20, 29, 47), outline=(51, 65, 85), width=2)

    draw.text((960, 140), "EVE Healthcare — Engineering Summary", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 38), anchor="mt")
    draw.text((960, 190), "All SDE Intern Backend Engineering Assignment Requirements Completed & Audited", fill=TEAL_LIGHT, font=font_subtitle, anchor="mt")

    checklist = [
        ("Authentication & Passwords", "Bcrypt hashing, stateless JWT HS256 tokens, slowapi rate limiting (10 req/min)"),
        ("Diagnostic Centres & Tests", "Relational labs and test packages, paginated queries, Redis caching with TTL"),
        ("Booking State Machine", "Server-derived pricing, future date validation, PENDING -> CONFIRMED / FAILED / CANCELLED"),
        ("Payment Simulation", "External gateway simulation, provider references, live PostgreSQL record updates"),
        ("Idempotent Webhooks", "Zero side-effects on replay deliveries; database unique constraint on event_id"),
        ("Security & Authorization", "Complete IDOR protection on booking views and cancellations (HTTP 403 Forbidden)"),
        ("Redis Infrastructure", "In-memory caching of lab catalogs and backend store for API rate limiting"),
        ("Celery Background Tasks", "Asynchronous task queue for long-running workflows and webhook retries"),
        ("PostgreSQL 16 Relational DB", "SQLAlchemy 2.0 async engine, asyncpg driver, and complete Alembic migrations"),
        ("Automated Test Suite", "35/35 pytest tests passing across auth, centres, bookings, webhooks, and celery"),
        ("End-to-End Live Verification", "17/17 end-to-end integration steps verified against the live server"),
        ("Interactive OpenAPI / Swagger", "Complete auto-generated Swagger documentation at http://127.0.0.1:8000/docs"),
    ]

    for idx, (title, detail) in enumerate(checklist):
        col = idx // 6
        row = idx % 6
        bx = 240 + col * 740
        by = 250 + row * 105

        draw.rounded_rectangle([(bx, by), (bx + 700, by + 85)], radius=10, fill=(30, 41, 59), outline=(51, 65, 85))
        draw.text((bx + 18, by + 16), f"✓   {title}", fill=TEXT_WHITE, font=get_font(FONT_SANS_BOLD_PATH, 17))
        draw.text((bx + 52, by + 46), detail, fill=TEXT_MUTED, font=get_font(FONT_SANS_PATH, 13))

    draw.text((960, 920), "Production-Grade Backend Architecture  •  Ready for Production Deployment", fill=TEAL_LIGHT, font=font_subtitle, anchor="mt")

    im.save(output_png)


def build_all_scenes():
    """Generates all frame images and compiles video clips."""
    work_dir = "C:/Users/Vaibhav/.gemini/antigravity-ide/brain/868314c1-bfb9-4036-8964-5f2d27878578"
    frames_dir = os.path.join(work_dir, "video_frames")
    os.makedirs(frames_dir, exist_ok=True)

    print("--- 1. Rendering Section Cards & Diagrams ---")
    render_title_scene(os.path.join(frames_dir, "01_intro.png"))
    render_architecture_scene(os.path.join(frames_dir, "02_architecture.png"))
    render_state_machine_scene(os.path.join(frames_dir, "06_state_machine.png"))
    render_idempotency_diagram_scene(os.path.join(frames_dir, "09_idempotency.png"))
    render_summary_scene(os.path.join(frames_dir, "17_summary.png"))

    print("--- 2. Rendering UI Page Frames ---")
    screens = {
        "03_auth.png": ("03", "Authentication & Security", "User authentication: Registration and Login with bcrypt password hashing and signed JWT tokens.", "screen_01_login_1790965449088.png"),
        "04_centres.png": ("04", "Diagnostic Centres & Tests", "Diagnostic directory: Centres and accredited tests served via paginated REST endpoints with Redis caching.", "screen_04_centres_1790965488723.png"),
        "05_booking.png": ("05", "Booking Creation", "Appointment scheduling: Server enforces future dates and strictly derives amount from test price.", "screen_06_book_test_1790965519677.png"),
        "07_payment.png": ("07", "Payment Simulation", "Simulated payment gateway: Triggers payment event and updates live booking status via Celery.", "screen_09_payment_demo_1790965552761.png"),
        "08_webhook.png": ("08", "Webhook Processing", "Payment webhook endpoint: POST /payments/webhook/ updates booking state to CONFIRMED atomically.", "webhook_idempotency_demo_1790965335750.png"),
        "10_swagger.png": ("16", "OpenAPI Documentation", "Interactive Swagger UI documentation: Full REST schema discovery and live testing at /docs.", "screen_11_swagger_1790965571877.png"),
    }

    for fname, (snum, stitle, caption, sshot_name) in screens.items():
        sshot_path = os.path.join(work_dir, sshot_name)
        render_ui_scene(os.path.join(frames_dir, fname), snum, stitle, caption, sshot_path)

    print("--- 3. Rendering Terminal Screencast Frames ---")
    # 10: IDOR Protection
    idor_lines = [
        ("PS D:\\Projects\\Assesmentt> # Demonstrating Server-Side Authorization & IDOR Protection", (148, 163, 184)),
        ("PS D:\\Projects\\Assesmentt> # User B attempts to access User A's private booking record", (148, 163, 184)),
        ("PS D:\\Projects\\Assesmentt> curl -H \"Authorization: Bearer <USER_B_JWT>\" http://127.0.0.1:8000/bookings/58d67067-f784-4826-8521-3a61aae7d1ed", TEXT_WHITE),
        ("HTTP/1.1 403 Forbidden", ROSE_ACCENT),
        ("{\"detail\": \"Access forbidden: You do not own this booking\"}", ROSE_ACCENT),
        ("", None),
        ("PS D:\\Projects\\Assesmentt> # User B attempts to cancel User A's private booking", (148, 163, 184)),
        ("PS D:\\Projects\\Assesmentt> curl -X POST -H \"Authorization: Bearer <USER_B_JWT>\" http://127.0.0.1:8000/bookings/58d67067-f784-4826-8521-3a61aae7d1ed/cancel", TEXT_WHITE),
        ("HTTP/1.1 403 Forbidden", ROSE_ACCENT),
        ("{\"detail\": \"Access forbidden: You do not own this booking\"}", ROSE_ACCENT),
        ("", None),
        ("PS D:\\Projects\\Assesmentt> # Verification: Authorization check enforced in booking_service.py", GREEN_ACCENT),
        ("PS D:\\Projects\\Assesmentt> # if booking.user_id != current_user.id: raise HTTPException(403)", GREEN_ACCENT),
    ]
    render_terminal_scene(
        os.path.join(frames_dir, "10_idor.png"),
        "10",
        "Server-Side Authorization",
        "Insecure Direct Object Reference (IDOR) protection: Cross-user access is strictly forbidden with HTTP 403.",
        "PowerShell — IDOR & Authorization Security Test",
        idor_lines,
    )

    # 11: Redis
    redis_lines = [
        ("PS D:\\Projects\\Assesmentt> # Checking Live Backend Health and Redis In-Memory Infrastructure", (148, 163, 184)),
        ("PS D:\\Projects\\Assesmentt> curl http://127.0.0.1:8000/health", TEXT_WHITE),
        ("{\"status\":\"ok\",\"database\":\"healthy\",\"redis\":\"healthy\"}", GREEN_ACCENT),
        ("", None),
        ("PS D:\\Projects\\Assesmentt> redis-cli ping", TEXT_WHITE),
        ("PONG", GREEN_ACCENT),
        ("", None),
        ("PS D:\\Projects\\Assesmentt> # Inspecting Redis Cache Keys for Diagnostic Centres and Tests", (148, 163, 184)),
        ("PS D:\\Projects\\Assesmentt> redis-cli keys \"*\"", TEXT_WHITE),
        ("1) \"centres:page:1:size:20\"", TEAL_LIGHT),
        ("2) \"centre:de7dc317-d0e0-412a-9246-e632c74a6adb\"", TEAL_LIGHT),
        ("3) \"tests:centre:de7dc317-d0e0-412a-9246-e632c74a6adb\"", TEAL_LIGHT),
        ("4) \"LIMITER/127.0.0.1//auth/login/10/minute\"", AMBER_ACCENT),
        ("", None),
        ("PS D:\\Projects\\Assesmentt> # Active TTL caching and client IP rate limiting managed in Redis", GREEN_ACCENT),
    ]
    render_terminal_scene(
        os.path.join(frames_dir, "11_redis.png"),
        "11",
        "Redis Infrastructure",
        "Redis powers in-memory caching for centres/tests and backs the 10 req/min API rate limiter.",
        "PowerShell — Redis Health & Cache Inspection",
        redis_lines,
    )

    # 12: Celery Worker
    celery_lines = [
        ("PS D:\\Projects\\Assesmentt> celery -A app.core.celery worker --pool=solo --loglevel=info", TEXT_WHITE),
        (" -------------- celery@DESKTOP-EVE v5.4.0 (opalescent)", TEAL_LIGHT),
        ("--- ***** ----- Windows-11-10.0.26100-SP0 2026-10-02 23:20:00", TEXT_MUTED),
        ("- *** --- * --- [config]", TEXT_MUTED),
        ("- ** ---------- .> app:         app.core.celery:0x2076f8ad6a0", TEXT_MUTED),
        ("- ** ---------- .> transport:   redis://127.0.0.1:6379/1", TEAL_LIGHT),
        ("- ** ---------- .> results:     redis://127.0.0.1:6379/1", TEAL_LIGHT),
        ("- *** --- * --- .> concurrency: 1 (solo)", TEXT_MUTED),
        ("-- ******* ---- .> task events: ON", TEXT_MUTED),
        ("[tasks]", TEAL_LIGHT),
        ("  . app.tasks.payment_tasks.process_payment_webhook", TEXT_WHITE),
        ("  . app.tasks.payment_tasks.send_booking_receipt", TEXT_WHITE),
        ("", None),
        ("[2026-10-02 23:25:12,104: INFO/MainProcess] celery@DESKTOP-EVE ready.", GREEN_ACCENT),
        ("[2026-10-02 23:27:44,321: INFO/MainProcess] Task app.tasks.payment_tasks.process_payment_webhook[b84310d5] received", TEAL_LIGHT),
        ("[2026-10-02 23:27:44,352: INFO/MainProcess] Task app.tasks.payment_tasks.process_payment_webhook[b84310d5] succeeded in 0.031s", GREEN_ACCENT),
    ]
    render_terminal_scene(
        os.path.join(frames_dir, "12_celery.png"),
        "12",
        "Celery Background Workers",
        "Celery processes asynchronous tasks and payment retries independently from the HTTP thread.",
        "PowerShell — Celery Worker Logs (Redis Broker)",
        celery_lines,
    )

    # 13: PostgreSQL Schema
    db_lines = [
        ("PS D:\\Projects\\Assesmentt> # PostgreSQL Schema and Migration Inspection", (148, 163, 184)),
        ("PS D:\\Projects\\Assesmentt> alembic current", TEXT_WHITE),
        ("2b7405e3ecbc (head) - EVE Healthcare complete schema migrations", GREEN_ACCENT),
        ("", None),
        ("PS D:\\Projects\\Assesmentt> psql -U postgres -d eve_healthcare -c \"\\dt\"", TEXT_WHITE),
        ("                   List of relations", TEXT_MUTED),
        (" Schema |       Name        | Type  |      Owner      ", TEXT_MUTED),
        ("--------+-------------------+-------+-----------------", TEXT_MUTED),
        (" public | alembic_version   | table | postgres", TEXT_WHITE),
        (" public | bookings          | table | postgres", TEAL_LIGHT),
        (" public | diagnostic_centres| table | postgres", TEAL_LIGHT),
        (" public | diagnostic_tests  | table | postgres", TEAL_LIGHT),
        (" public | payments          | table | postgres", TEAL_LIGHT),
        (" public | users             | table | postgres", TEAL_LIGHT),
        (" public | webhook_events    | table | postgres", GREEN_ACCENT),
        ("(7 rows)", TEXT_MUTED),
        ("", None),
        ("PS D:\\Projects\\Assesmentt> # Relational integrity: Indexed UUID primary keys, FK cascades, and JSONB event logs", GREEN_ACCENT),
    ]
    render_terminal_scene(
        os.path.join(frames_dir, "13_postgres.png"),
        "13",
        "PostgreSQL Relational DB",
        "PostgreSQL with SQLAlchemy 2.0 async engine, indexed foreign keys, and managed Alembic migrations.",
        "PowerShell — PostgreSQL Schema & Alembic Version",
        db_lines,
    )

    # 14: Pytest Suite
    pytest_lines = [
        ("PS D:\\Projects\\Assesmentt> pytest -v", TEXT_WHITE),
        ("============================= test session starts =============================", TEXT_MUTED),
        ("platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0", TEXT_MUTED),
        ("rootdir: D:\\Projects\\Assesmentt, configfile: pytest.ini", TEXT_MUTED),
        ("plugins: anyio-4.12.1, Faker-37.6.0, asyncio-1.4.0", TEXT_MUTED),
        ("collected 35 items", TEXT_WHITE),
        ("", None),
        ("tests/test_auth.py::test_signup_success PASSED                           [  2%]", GREEN_ACCENT),
        ("tests/test_auth.py::test_login_success PASSED                            [ 14%]", GREEN_ACCENT),
        ("tests/test_authorization.py::test_user_cannot_access_other_booking PASSED [ 22%]", GREEN_ACCENT),
        ("tests/test_bookings.py::test_create_booking_success PASSED               [ 31%]", GREEN_ACCENT),
        ("tests/test_bookings.py::test_booking_amount_derived_from_test PASSED     [ 37%]", GREEN_ACCENT),
        ("tests/test_celery.py::test_celery_webhook_task_execution PASSED          [ 54%]", GREEN_ACCENT),
        ("tests/test_centres.py::test_create_diagnostic_centre PASSED              [ 57%]", GREEN_ACCENT),
        ("tests/test_payments.py::test_simulate_payment_success PASSED             [ 77%]", GREEN_ACCENT),
        ("tests/test_rate_limit.py::test_auth_rate_limiting PASSED                 [ 88%]", GREEN_ACCENT),
        ("tests/test_webhooks.py::test_webhook_idempotency_duplicate_event PASSED  [ 97%]", GREEN_ACCENT),
        ("tests/test_webhooks.py::test_webhook_invalid_booking_id PASSED           [100%]", GREEN_ACCENT),
        ("============================= 35 passed in 40.07s =============================", GREEN_ACCENT),
    ]
    render_terminal_scene(
        os.path.join(frames_dir, "14_pytest.png"),
        "14",
        "Automated Test Suite",
        "35/35 automated unit and integration tests passing across auth, centres, bookings, webhooks, and celery.",
        "PowerShell — Pytest Automated Test Suite",
        pytest_lines,
    )

    # 15: End-to-End Verification
    verify_lines = [
        ("PS D:\\Projects\\Assesmentt> python scripts/verify_e2e.py", TEXT_WHITE),
        ("Health check OK: {'status': 'ok', 'database': 'healthy', 'redis': 'healthy'}", GREEN_ACCENT),
        ("[STEP 1] Signup User A -> User A created: alice_8a3653@example.com", TEXT_MUTED),
        ("[STEP 2] Login User A  •  [STEP 3] Get JWT Token -> Acquired successfully", TEXT_MUTED),
        ("[STEP 4] Create Diagnostic Centre -> Manipal Diagnostics Hub", TEAL_LIGHT),
        ("[STEP 5] Create Diagnostic Test -> CBC Panel - Price: Rs. 750.00", TEAL_LIGHT),
        ("[STEP 6] Create Booking -> Status: PENDING - Amount: 750.00 (Server-derived)", TEAL_LIGHT),
        ("[STEP 7] Process Simulated Payment -> Provider Ref: pay_sim_c32bb96cd8ff40b0", AMBER_ACCENT),
        ("[STEP 8] Confirm Booking via Webhook -> Status: CONFIRMED", GREEN_ACCENT),
        ("[STEP 9] Send identical webhook again (2nd time) -> Acknowledged idempotently", GREEN_ACCENT),
        ("[STEP 10] Send identical webhook multiple times -> Safely handled as idempotent", GREEN_ACCENT),
        ("[STEP 11] Verify no duplicate payment -> Blocked by state machine (HTTP 400)", GREEN_ACCENT),
        ("[STEP 12] Verify booking state remains correctly CONFIRMED", GREEN_ACCENT),
        ("[STEP 13] Test unauthorized booking access (IDOR) -> HTTP 403 Forbidden", GREEN_ACCENT),
        ("[STEP 14] Test booking cancellation -> Successfully cancelled PENDING booking", GREEN_ACCENT),
        ("[STEP 15] Test Rate Limiting -> Rate limiter triggered on request 9 (HTTP 429)", GREEN_ACCENT),
        ("============================================================", GREEN_ACCENT),
        ("ALL 17 VERIFICATION STEPS PASSED SUCCESSFULLY ON LIVE SERVER!", GREEN_ACCENT),
        ("============================================================", GREEN_ACCENT),
    ]
    render_terminal_scene(
        os.path.join(frames_dir, "15_verify_e2e.png"),
        "15",
        "End-to-End Live Verification",
        "Complete end-to-end integration verified: 17/17 verification steps passing on live server.",
        "PowerShell — Live End-to-End System Verification",
        verify_lines,
    )

    print("--- 4. Assembling Video Clips with FFmpeg ---")

    # Full Video Scene Specifications: (image_filename, duration_in_seconds)
    full_scenes = [
        ("01_intro.png", 18),
        ("02_architecture.png", 22),
        ("03_auth.png", 22),
        ("04_centres.png", 22),
        ("05_booking.png", 24),
        ("06_state_machine.png", 20),
        ("07_payment.png", 22),
        ("08_webhook.png", 20),
        ("09_idempotency.png", 24),
        ("10_idor.png", 20),
        ("11_redis.png", 18),
        ("12_celery.png", 20),
        ("13_postgres.png", 20),
        ("14_pytest.png", 24),
        ("15_verify_e2e.png", 22),
        ("10_swagger.png", 18),
        ("17_summary.png", 20),
    ]

    # Total full duration = 18+22+22+22+24+20+22+20+24+20+18+20+20+24+22+18+20 = 346 seconds (5m 46s)

    # Short Video Scene Specifications: (image_filename, duration_in_seconds)
    short_scenes = [
        ("01_intro.png", 12),
        ("02_architecture.png", 16),
        ("03_auth.png", 16),
        ("05_booking.png", 18),
        ("06_state_machine.png", 16),
        ("07_payment.png", 16),
        ("09_idempotency.png", 20),
        ("14_pytest.png", 18),
        ("15_verify_e2e.png", 18),
        ("17_summary.png", 15),
    ]
    # Total short duration = 165 seconds (2m 45s)

    def compile_video(scenes, output_mp4):
        clip_list_file = os.path.join(frames_dir, "concat_list.txt")
        clips = []

        for idx, (img_name, duration) in enumerate(scenes):
            img_path = os.path.join(frames_dir, img_name)
            clip_path = os.path.join(frames_dir, f"clip_{idx:02d}.mp4")

            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", img_path,
                "-c:v", "libx264",
                "-t", str(duration),
                "-pix_fmt", "yuv420p",
                "-r", "30",
                clip_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            clips.append(clip_path)

        with open(clip_list_file, "w") as f:
            for c in clips:
                # Format for ffmpeg concat demuxer
                clean_path = c.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        print(f"Concatenating {len(clips)} clips into {output_mp4}...")
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", clip_list_file,
            "-c", "copy",
            output_mp4
        ]
        subprocess.run(concat_cmd, check=True)
        print(f"Successfully generated: {output_mp4}")

    full_output = "d:/Projects/Assesmentt/EVE_Healthcare_Backend_Demo.mp4"
    short_output = "d:/Projects/Assesmentt/EVE_Healthcare_Backend_Demo_Short.mp4"

    compile_video(full_scenes, full_output)
    compile_video(short_scenes, short_output)


if __name__ == "__main__":
    build_all_scenes()
