from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import io

# ── Colors ────────────────────────────────────────────────
BLACK      = colors.HexColor('#000000')
DARK_NAVY  = colors.HexColor('#0a0e1a')
NAVY       = colors.HexColor('#1a2035')
GREEN      = colors.HexColor('#007a3d')
RED        = colors.HexColor('#cc0000')
ORANGE     = colors.HexColor('#cc6600')
BLUE       = colors.HexColor('#003399')
LIGHT_GRAY = colors.HexColor('#f5f5f5')
MID_GRAY   = colors.HexColor('#cccccc')
DARK_GRAY  = colors.HexColor('#333333')
WHITE      = colors.white

GRADE_COLORS = {
    'A': colors.HexColor('#007a3d'),
    'B': colors.HexColor('#003399'),
    'C': colors.HexColor('#cc6600'),
    'D': colors.HexColor('#cc0000'),
}

GRADE_LABELS = {
    'A': 'SECURE — No critical issues found.',
    'B': 'MODERATE — Minor security improvements recommended.',
    'C': 'AT RISK — Several security issues need attention.',
    'D': 'VULNERABLE — Immediate action required.',
}

# ── Styles ────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()

    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        'cover_tag':   s('ct',  fontName='Times-Roman',   fontSize=11, textColor=DARK_GRAY,
                         alignment=TA_CENTER, spaceAfter=6),
        'cover_title': s('cti', fontName='Times-Bold',    fontSize=28, textColor=BLACK,
                         alignment=TA_CENTER, spaceAfter=8, leading=34),
        'cover_sub':   s('cs',  fontName='Times-Roman',   fontSize=13, textColor=DARK_GRAY,
                         alignment=TA_CENTER, spaceAfter=4),
        'cover_meta':  s('cm',  fontName='Times-Roman',   fontSize=11, textColor=DARK_GRAY,
                         alignment=TA_CENTER, spaceAfter=4),
        'cover_grade': s('cg',  fontName='Times-Bold',    fontSize=48, textColor=BLACK,
                         alignment=TA_CENTER, spaceAfter=4),
        'cover_glabel':s('cgl', fontName='Times-Italic',  fontSize=13, textColor=DARK_GRAY,
                         alignment=TA_CENTER, spaceAfter=4),

        'section':     s('sec', fontName='Times-Bold',    fontSize=15, textColor=BLACK,
                         spaceBefore=14, spaceAfter=6, borderPad=2,
                         borderWidth=0, leftIndent=0),
        'subsection':  s('ss',  fontName='Times-Bold',    fontSize=13, textColor=DARK_GRAY,
                         spaceBefore=10, spaceAfter=4),
        'body':        s('bd',  fontName='Times-Roman',   fontSize=12, textColor=DARK_GRAY,
                         spaceAfter=5, leading=18, alignment=TA_JUSTIFY),
        'body_bold':   s('bdb', fontName='Times-Bold',    fontSize=12, textColor=BLACK,
                         spaceAfter=4, leading=18),
        'bullet':      s('bul', fontName='Times-Roman',   fontSize=12, textColor=DARK_GRAY,
                         spaceAfter=4, leading=18, leftIndent=16, firstLineIndent=-10),
        'code':        s('cod', fontName='Courier',       fontSize=10, textColor=DARK_GRAY,
                         spaceAfter=3, leading=14, leftIndent=12,
                         backColor=LIGHT_GRAY),
        'pass_label':  s('pl',  fontName='Times-Bold',    fontSize=12, textColor=GREEN,
                         spaceAfter=3),
        'fail_label':  s('fl',  fontName='Times-Bold',    fontSize=12, textColor=RED,
                         spaceAfter=3),
        'warn_label':  s('wl',  fontName='Times-Bold',    fontSize=12, textColor=ORANGE,
                         spaceAfter=3),
        'footer':      s('ft',  fontName='Times-Italic',  fontSize=9,  textColor=MID_GRAY,
                         alignment=TA_CENTER),
        'toc_item':    s('toc', fontName='Times-Roman',   fontSize=12, textColor=DARK_GRAY,
                         spaceAfter=5, leading=18),
    }


# ── Remediation details ───────────────────────────────────
REMEDIATION = {
    'Content-Security-Policy': {
        'what': (
            "Content-Security-Policy (CSP) is a security rule that tells the browser "
            "which sources of content — such as scripts, images, and styles — are "
            "allowed to load on your webpage. Without this rule, a malicious user "
            "could inject harmful scripts into your site (this is called a Cross-Site "
            "Scripting or XSS attack), potentially stealing user data or hijacking accounts."
        ),
        'impact': (
            "If this header is missing, attackers can inject malicious JavaScript code "
            "into your website. This can lead to stolen login credentials, session "
            "hijacking, redirecting users to fake sites, or defacing your website."
        ),
        'steps': [
            "Step 1 — Identify your web server. Common options are Nginx, Apache, or a cloud "
            "platform like Netlify, Vercel, or Cloudflare.",
            "Step 2 — Access your server configuration file. For Nginx this is usually located "
            "at /etc/nginx/nginx.conf or /etc/nginx/sites-available/your-site. For Apache, "
            "look for .htaccess or httpd.conf.",
            "Step 3 — Add the following line inside your server block (Nginx) or your "
            ".htaccess file (Apache). This is a starter policy that only allows content "
            "from your own domain:",
            "Step 4 — Save the file and restart your web server using the command: "
            "sudo systemctl restart nginx  (or apache2 for Apache).",
            "Step 5 — Verify the fix by re-scanning your website on VulnScan Lite. "
            "The Content-Security-Policy check should now show as PASSED.",
        ],
        'nginx':  "add_header Content-Security-Policy \"default-src 'self'\" always;",
        'apache': "Header always set Content-Security-Policy \"default-src 'self'\"",
        'note': (
            "Note: If your website loads content from external sources such as Google "
            "Fonts, YouTube embeds, or CDN scripts, you will need to add those domains "
            "to the policy. For example: default-src 'self' https://fonts.googleapis.com"
        ),
    },

    'X-Frame-Options': {
        'what': (
            "X-Frame-Options is a security header that prevents your website from being "
            "embedded inside another website using an HTML iframe. Without this protection, "
            "attackers can place an invisible copy of your website on top of a fake page "
            "and trick users into clicking on hidden buttons — this attack is called "
            "Clickjacking."
        ),
        'impact': (
            "Clickjacking attacks can trick your users into unknowingly transferring money, "
            "changing account settings, liking malicious social media posts, or clicking "
            "hidden links on your website. The user sees a harmless-looking page but is "
            "actually interacting with your site in the background."
        ),
        'steps': [
            "Step 1 — Access your server configuration file as described above.",
            "Step 2 — Add the following line to your configuration. SAMEORIGIN means your "
            "website can only be framed by pages from the same domain, which is the "
            "recommended and safest setting for most websites.",
            "Step 3 — Save and restart your server.",
            "Step 4 — Re-scan your website to confirm the fix.",
        ],
        'nginx':  "add_header X-Frame-Options \"SAMEORIGIN\" always;",
        'apache': "Header always set X-Frame-Options \"SAMEORIGIN\"",
        'note': (
            "Note: If your website is intentionally embedded in other websites (for example "
            "a widget), you may want to use ALLOWFROM https://trusted-site.com instead of "
            "SAMEORIGIN. Otherwise SAMEORIGIN is the right choice for almost all websites."
        ),
    },

    'Strict-Transport-Security': {
        'what': (
            "Strict-Transport-Security (HSTS) is a header that instructs the browser to "
            "always connect to your website using HTTPS (the secure, encrypted version) "
            "and never fall back to HTTP (the unencrypted version). Without this header, "
            "an attacker on the same network — for example on a public Wi-Fi — could "
            "intercept the connection before it becomes secure."
        ),
        'impact': (
            "Without HSTS, attackers can perform what is called an SSL Stripping attack. "
            "They intercept your visitor's first request to your website (which may be "
            "plain HTTP) before the browser is redirected to HTTPS, allowing them to read "
            "or modify everything the user sends and receives, including passwords and "
            "personal information."
        ),
        'steps': [
            "Step 1 — Make sure your website already has a valid SSL certificate and "
            "runs entirely over HTTPS before adding this header. If your site still has "
            "HTTP pages, fix those first.",
            "Step 2 — Access your server configuration file.",
            "Step 3 — Add the following header. The max-age value (31536000) means the "
            "browser will remember to always use HTTPS for one full year.",
            "Step 4 — Save and restart your server.",
            "Step 5 — Re-scan to confirm the fix is working.",
        ],
        'nginx':  "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
        'apache': "Header always set Strict-Transport-Security \"max-age=31536000; includeSubDomains\"",
        'note': (
            "Note: The includeSubDomains directive also applies this rule to all subdomains "
            "of your website (e.g. mail.yoursite.com, shop.yoursite.com). This is recommended "
            "if all your subdomains also use HTTPS. Remove includeSubDomains if some "
            "subdomains still use plain HTTP."
        ),
    },
}


def generate_pdf(report: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=22*mm,
        rightMargin=22*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
        title="VulnScan Lite — Security Report",
        author="VulnScan Lite",
    )

    ST = make_styles()
    story = []

    grade     = report.get('grade', 'N/A')
    score     = report.get('total_score', 0)
    url       = report.get('url', 'N/A')
    ssl       = report.get('ssl', {})
    cms       = report.get('cms', {})
    headers   = report.get('headers', {})
    passed    = headers.get('passed', [])
    failed    = headers.get('failed', [])
    grade_col = GRADE_COLORS.get(grade, DARK_GRAY)
    now       = datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')

    # ══════════════════════════════════════════════════════
    # PAGE 1 — COVER PAGE
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 18*mm))

    # Top line
    story.append(HRFlowable(width='100%', thickness=2, color=BLACK, spaceAfter=8))

    story.append(Paragraph('WEBSITE SECURITY ASSESSMENT REPORT', ST['cover_tag']))
    story.append(Paragraph('VulnScan Lite', ST['cover_title']))
    story.append(HRFlowable(width='100%', thickness=1, color=MID_GRAY, spaceAfter=14))

    story.append(Spacer(1, 10*mm))

    # Target info box
    info_data = [
        ['Target Website', url],
        ['Report Generated', now],
        ['Analysis Type', 'Passive Security Analysis (No exploitation performed)'],
        ['Checks Performed', 'HTTP Security Headers, SSL/TLS Certificate, CMS Detection'],
    ]
    info_table = Table(info_data, colWidths=[55*mm, 105*mm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), LIGHT_GRAY),
        ('BACKGROUND',    (1,0), (1,-1), WHITE),
        ('BOX',           (0,0), (-1,-1), 1, MID_GRAY),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, MID_GRAY),
        ('FONTNAME',      (0,0), (0,-1), 'Times-Bold'),
        ('FONTNAME',      (1,0), (1,-1), 'Times-Roman'),
        ('FONTSIZE',      (0,0), (-1,-1), 12),
        ('TEXTCOLOR',     (0,0), (-1,-1), DARK_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(info_table)

    story.append(Spacer(1, 14*mm))

    # Grade box
    grade_data = [[
        Paragraph('OVERALL SECURITY GRADE', ParagraphStyle('gl',
            fontName='Times-Bold', fontSize=13, textColor=DARK_GRAY, alignment=TA_CENTER)),
        Paragraph(grade, ParagraphStyle('gv',
            fontName='Times-Bold', fontSize=52, textColor=grade_col, alignment=TA_CENTER)),
        Paragraph(GRADE_LABELS.get(grade, ''), ParagraphStyle('gd',
            fontName='Times-Italic', fontSize=12, textColor=DARK_GRAY, alignment=TA_CENTER)),
    ]]
    grade_table = Table([[grade_data[0][0]], [grade_data[0][1]], [grade_data[0][2]]],
                        colWidths=[160*mm])
    grade_table.setStyle(TableStyle([
        ('BOX',           (0,0), (-1,-1), 1.5, BLACK),
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(grade_table)

    story.append(Spacer(1, 10*mm))

    # Score summary
    score_data = [
        ['Security Score', f'{score} points',
         'SSL Certificate', 'Valid ✓' if ssl.get('is_valid') else 'Invalid ✗'],
        ['Checks Passed', str(len(passed)),
         'Checks Failed', str(len(failed))],
    ]
    score_table = Table(score_data, colWidths=[45*mm, 35*mm, 45*mm, 35*mm])
    score_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), LIGHT_GRAY),
        ('BACKGROUND',    (2,0), (2,-1), LIGHT_GRAY),
        ('BOX',           (0,0), (-1,-1), 1, MID_GRAY),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, MID_GRAY),
        ('FONTNAME',      (0,0), (0,-1), 'Times-Bold'),
        ('FONTNAME',      (2,0), (2,-1), 'Times-Bold'),
        ('FONTNAME',      (1,0), (1,-1), 'Times-Roman'),
        ('FONTNAME',      (3,0), (3,-1), 'Times-Roman'),
        ('FONTSIZE',      (0,0), (-1,-1), 12),
        ('TEXTCOLOR',     (0,0), (-1,-1), DARK_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('ALIGN',         (1,0), (1,-1), 'CENTER'),
        ('ALIGN',         (3,0), (3,-1), 'CENTER'),
    ]))
    story.append(score_table)

    story.append(Spacer(1, 16*mm))
    story.append(HRFlowable(width='100%', thickness=1, color=MID_GRAY, spaceAfter=6))
    story.append(Paragraph(
        'This report was generated automatically by VulnScan Lite. '
        'It is intended for the website owner or authorized security personnel only. '
        'All findings are based on passive analysis and no exploitation was performed.',
        ParagraphStyle('disc', fontName='Times-Italic', fontSize=10,
                       textColor=DARK_GRAY, alignment=TA_CENTER, leading=14)
    ))

    # ══════════════════════════════════════════════════════
    # PAGE 2 — SSL + HEADER FINDINGS
    # ══════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph('1.  SSL / TLS CERTIFICATE ANALYSIS', ST['section']))
    story.append(HRFlowable(width='100%', thickness=1, color=BLACK, spaceAfter=8))

    story.append(Paragraph(
        "SSL (Secure Sockets Layer) and its modern replacement TLS (Transport Layer Security) "
        "encrypt the connection between your website and your visitors. This means that "
        "passwords, personal information, and payment details cannot be read by anyone "
        "intercepting the traffic. A valid certificate is essential for any website today.",
        ST['body']
    ))

    story.append(Spacer(1, 4*mm))

    ssl_status = 'VALID — Certificate is active and trusted.' if ssl.get('is_valid') \
        else 'INVALID — Certificate is missing, expired, or untrusted.'
    ssl_color  = GREEN if ssl.get('is_valid') else RED

    ssl_rows = [
        ['Certificate Status',
         Paragraph(ssl_status, ParagraphStyle('ss', fontName='Times-Bold',
                   fontSize=12, textColor=ssl_color))],
        ['Expiry Date',        ssl.get('expires_on', 'Not available')],
        ['Days Remaining',     f"{ssl.get('days_left', 'N/A')} days"],
    ]
    ssl_table = Table(ssl_rows, colWidths=[55*mm, 105*mm])
    ssl_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), LIGHT_GRAY),
        ('BOX',           (0,0), (-1,-1), 1, MID_GRAY),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, MID_GRAY),
        ('FONTNAME',      (0,0), (0,-1), 'Times-Bold'),
        ('FONTNAME',      (1,0), (1,-1), 'Times-Roman'),
        ('FONTSIZE',      (0,0), (-1,-1), 12),
        ('TEXTCOLOR',     (0,0), (0,-1), DARK_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(ssl_table)

    if ssl.get('days_left') and ssl['days_left'] < 30:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(
            f"⚠  Warning: Your SSL certificate expires in only {ssl['days_left']} days. "
            "You should renew it immediately to avoid your website showing a security "
            "warning to visitors. Contact your hosting provider or use a free certificate "
            "from Let's Encrypt (https://letsencrypt.org).",
            ParagraphStyle('warn', fontName='Times-Bold', fontSize=12,
                           textColor=ORANGE, spaceAfter=4, leading=18)
        ))

    story.append(Spacer(1, 8*mm))

    # CMS Section
    if cms.get('cms_name'):
        story.append(Paragraph('2.  CMS DETECTION', ST['section']))
        story.append(HRFlowable(width='100%', thickness=1, color=BLACK, spaceAfter=8))

        story.append(Paragraph(
            f"Your website is running {cms.get('cms_name', 'an unknown CMS')}"
            f"{', version ' + cms['cms_version'] if cms.get('cms_version') else ''}. "
            "A Content Management System (CMS) is the software platform used to build "
            "and manage your website content. While CMS platforms are convenient, "
            "they must be kept up to date to avoid known security vulnerabilities.",
            ST['body']
        ))
        for w in cms.get('warnings', []):
            story.append(Paragraph(f"•  {w}", ST['bullet']))

        story.append(Paragraph(
            "Recommendation: Always keep your CMS and all installed plugins or themes "
            "updated to the latest version. Enable automatic security updates if available. "
            "Remove any plugins or themes that are no longer in use.",
            ParagraphStyle('rec', fontName='Times-Italic', fontSize=12,
                           textColor=DARK_GRAY, leftIndent=10, spaceAfter=4, leading=18)
        ))
        story.append(Spacer(1, 6*mm))

    # Header Checks
    sec_num = 3 if cms.get('cms_name') else 2
    story.append(Paragraph(f'{sec_num}.  HTTP SECURITY HEADER CHECKS', ST['section']))
    story.append(HRFlowable(width='100%', thickness=1, color=BLACK, spaceAfter=8))

    story.append(Paragraph(
        "HTTP security headers are instructions sent by your web server to the visitor's "
        "browser. They tell the browser how to behave when handling your website's content "
        "and provide protection against many common web attacks. The following checks were "
        "performed on your website:",
        ST['body']
    ))
    story.append(Spacer(1, 4*mm))

    check_rows = [
        [Paragraph('HEADER NAME', ParagraphStyle('th', fontName='Times-Bold',
                   fontSize=12, textColor=BLACK)),
         Paragraph('RESULT', ParagraphStyle('th2', fontName='Times-Bold',
                   fontSize=12, textColor=BLACK)),
         Paragraph('IMPACT IF MISSING', ParagraphStyle('th3', fontName='Times-Bold',
                   fontSize=12, textColor=BLACK))],
    ]

    impact_map = {
        'Content-Security-Policy':    'Cross-Site Scripting (XSS) attacks possible',
        'X-Frame-Options':            'Clickjacking attacks possible',
        'Strict-Transport-Security':  'SSL stripping and traffic interception possible',
    }

    all_checks = [(h, True) for h in passed] + [(h, False) for h in failed]
    for h, is_passed in all_checks:
        result_text = 'PASSED ✓' if is_passed else 'FAILED ✗'
        result_color = GREEN if is_passed else RED
        check_rows.append([
            Paragraph(h, ParagraphStyle('cn', fontName='Times-Roman', fontSize=11,
                      textColor=DARK_GRAY)),
            Paragraph(result_text, ParagraphStyle('cr', fontName='Times-Bold',
                      fontSize=11, textColor=result_color)),
            Paragraph(impact_map.get(h, 'Security risk'), ParagraphStyle('ci',
                      fontName='Times-Roman', fontSize=11, textColor=DARK_GRAY)),
        ])

    check_table = Table(check_rows, colWidths=[65*mm, 28*mm, 67*mm])
    check_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), DARK_NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [WHITE, LIGHT_GRAY]),
        ('BOX',           (0,0), (-1,-1), 1, MID_GRAY),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, MID_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(check_table)

    # ══════════════════════════════════════════════════════
    # PAGE 3+ — REMEDIATION GUIDE
    # ══════════════════════════════════════════════════════
    if failed:
        story.append(PageBreak())
        story.append(Paragraph('REMEDIATION GUIDE', ST['section']))
        story.append(HRFlowable(width='100%', thickness=2, color=BLACK, spaceAfter=6))
        story.append(Paragraph(
            "This section explains each failed check in plain language and provides "
            "step-by-step instructions to fix the issue. You do not need advanced "
            "technical knowledge to follow these steps. If you are unsure, share "
            "this report with your web developer or hosting provider.",
            ST['body']
        ))
        story.append(Spacer(1, 6*mm))

        for i, header in enumerate(failed):
            if header not in REMEDIATION:
                continue
            rem = REMEDIATION[header]

            block = []
            block.append(Paragraph(
                f'Fix {i+1} of {len(failed)}: {header}',
                ParagraphStyle('fh', fontName='Times-Bold', fontSize=14,
                               textColor=BLACK, spaceBefore=8, spaceAfter=4,
                               borderWidth=0, leftIndent=0)
            ))
            block.append(HRFlowable(width='100%', thickness=0.8, color=MID_GRAY, spaceAfter=6))

            block.append(Paragraph('What is this?', ST['subsection']))
            block.append(Paragraph(rem['what'], ST['body']))

            block.append(Paragraph('Why does it matter?', ST['subsection']))
            block.append(Paragraph(rem['impact'], ST['body']))

            block.append(Paragraph('How to fix it — Step by step:', ST['subsection']))
            for step in rem['steps']:
                block.append(Paragraph(f'•   {step}', ST['bullet']))

            block.append(Spacer(1, 3*mm))
            block.append(Paragraph('Configuration code to add:', ST['subsection']))

            code_data = [
                [Paragraph('For Nginx web server:', ParagraphStyle('cl', fontName='Times-Bold',
                           fontSize=11, textColor=DARK_GRAY))],
                [Paragraph(rem['nginx'], ParagraphStyle('cc', fontName='Courier',
                           fontSize=10, textColor=DARK_GRAY, backColor=LIGHT_GRAY))],
                [Paragraph('For Apache web server:', ParagraphStyle('cl2', fontName='Times-Bold',
                           fontSize=11, textColor=DARK_GRAY, spaceBefore=4))],
                [Paragraph(rem['apache'], ParagraphStyle('cc2', fontName='Courier',
                           fontSize=10, textColor=DARK_GRAY, backColor=LIGHT_GRAY))],
            ]
            code_table = Table(code_data, colWidths=[160*mm])
            code_table.setStyle(TableStyle([
                ('BOX',           (0,0), (-1,-1), 1, MID_GRAY),
                ('BACKGROUND',    (0,1), (-1,1), LIGHT_GRAY),
                ('BACKGROUND',    (0,3), (-1,3), LIGHT_GRAY),
                ('TOPPADDING',    (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ]))
            block.append(code_table)

            block.append(Spacer(1, 3*mm))
            block.append(Paragraph(rem['note'], ParagraphStyle('nt', fontName='Times-Italic',
                         fontSize=11, textColor=DARK_GRAY, leftIndent=10,
                         spaceAfter=6, leading=16)))

            if i < len(failed) - 1:
                block.append(HRFlowable(width='100%', thickness=0.5,
                                        color=MID_GRAY, spaceBefore=10, spaceAfter=4))

            story.append(KeepTogether(block[:4]))
            story.extend(block[4:])

    # ══════════════════════════════════════════════════════
    # FINAL PAGE — SUMMARY
    # ══════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph('SUMMARY AND NEXT STEPS', ST['section']))
    story.append(HRFlowable(width='100%', thickness=2, color=BLACK, spaceAfter=8))

    story.append(Paragraph(
        f"The security scan of {url} has been completed. "
        f"The overall security grade assigned is {grade} — {GRADE_LABELS.get(grade, '')} "
        f"A total security score of {score} points was calculated based on the results "
        "of all checks performed.",
        ST['body']
    ))
    story.append(Spacer(1, 4*mm))

    if failed:
        story.append(Paragraph('Issues that require your attention:', ST['subsection']))
        for h in failed:
            story.append(Paragraph(f'•   {h} — see the Remediation Guide section for fix instructions.', ST['bullet']))
        story.append(Spacer(1, 4*mm))

    if passed:
        story.append(Paragraph('Checks that are already correctly configured:', ST['subsection']))
        for h in passed:
            story.append(Paragraph(f'•   {h} — no action required.', ST['bullet']))
        story.append(Spacer(1, 4*mm))

    story.append(Paragraph('General security recommendations:', ST['subsection']))
    general_recs = [
        "Keep all software, plugins, and themes updated to the latest version at all times.",
        "Renew your SSL certificate before it expires to avoid security warnings for visitors.",
        "Use a strong and unique password for your website admin panel and hosting account.",
        "Enable two-factor authentication (2FA) on all admin accounts where possible.",
        "Perform a security scan regularly — at least once every month — to catch new issues early.",
        "Consider using a Web Application Firewall (WAF) such as Cloudflare for additional protection.",
        "Take regular backups of your website and store them securely in a separate location.",
    ]
    for rec in general_recs:
        story.append(Paragraph(f'•   {rec}', ST['bullet']))

    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width='100%', thickness=1, color=MID_GRAY, spaceAfter=6))
    story.append(Paragraph(
        f'Report generated by VulnScan Lite  |  {now}  |  '
        'This report is for authorized use only. '
        'VulnScan Lite performs passive analysis only and does not exploit vulnerabilities.',
        ST['footer']
    ))

    doc.build(story)
    return buffer.getvalue()