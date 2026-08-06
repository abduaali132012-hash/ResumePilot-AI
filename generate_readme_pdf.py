#!/usr/bin/env python3
"""Generate README.pdf for ResumePilot AI."""
from fpdf import FPDF
import os, base64, shutil

class RPDF(FPDF):
    def sec(self, title):
        self.set_font('S', 'B', 18)
        self.set_text_color(30, 64, 175)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 64, 175)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def bul(self, text):
        self.set_font('S', '', 10)
        self.set_text_color(50, 50, 50)
        self.set_x(14)
        self.cell(5, 5.5, '>')
        self.multi_cell(0, 5.5, text)
        self.ln(0.5)

    def txt(self, text):
        self.set_font('S', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def code(self, lines):
        self.set_font('M', '', 9)
        self.set_fill_color(245, 245, 250)
        self.set_text_color(40, 40, 40)
        self.ln(2)
        for line in lines:
            self.cell(0, 5, '  ' + line, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

    def tbl(self, rows, hdr=True):
        for i, row in enumerate(rows):
            if hdr and i == 0:
                self.set_font('S', 'B', 10)
                self.set_fill_color(30, 64, 175)
                self.set_text_color(255, 255, 255)
            else:
                self.set_font('S', '', 10)
                self.set_text_color(50, 50, 50)
                self.set_fill_color(245, 247, 255) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.cell(50, 7, ' ' + row[0], 1, 0, 'L', True)
            self.cell(130, 7, ' ' + row[1], 1, 0, 'L', True)
            self.ln()


pdf = RPDF()
pdf.add_font('S', '', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
pdf.add_font('S', 'B', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
pdf.add_font('S', 'I', '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf')
pdf.add_font('M', '', '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf')
pdf.set_auto_page_break(auto=True, margin=20)

# --- Page 1: Title ---
pdf.add_page()
pdf.ln(40)
pdf.set_fill_color(30, 64, 175)
pdf.rect(10, 50, 190, 3, 'F')
pdf.ln(15)
pdf.set_font('S', 'B', 32)
pdf.set_text_color(30, 64, 175)
pdf.cell(0, 15, 'ResumePilot AI', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.set_font('S', '', 14)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 10, 'AI-Powered Resume Builder & Tailoring Tool', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(8)
pdf.set_draw_color(30, 64, 175)
pdf.set_line_width(0.5)
pdf.line(70, pdf.get_y(), 140, pdf.get_y())
pdf.ln(10)
pdf.set_font('S', '', 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, 'Built with React + TypeScript + Tailwind CSS', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.cell(0, 8, 'NativelyAI Hackathon 2025', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(5)
pdf.set_font('S', 'I', 10)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 8, 'Author: Abdu Ali Adem', new_x="LMARGIN", new_y="NEXT", align='C')

# --- Page 2: Features + Quick Start + Tech Stack ---
pdf.add_page()
pdf.sec('Features')
pdf.bul('AI Resume Tailoring - Tailor your resume to match job descriptions')
pdf.bul('Smart Suggestions - AI-powered recommendations for bullet points')
pdf.bul('ATS-Optimized - Templates that pass Applicant Tracking Systems')
pdf.bul('Modern Templates - Professionally designed resume templates')
pdf.bul('Real-time Preview - See changes instantly as you edit')
pdf.bul('Export Options - Download as PDF or export to other formats')
pdf.bul('Privacy First - Your data stays on your device')

pdf.sec('Quick Start')
pdf.bul('Prerequisites: Node.js v18+ and npm v9+')
pdf.code(['git clone <repo-url>', 'cd ResumePilot-AI', 'npm install', 'npm run dev'])
pdf.txt('The app will be available at http://localhost:5173')

pdf.sec('Tech Stack')
pdf.tbl([
    ['Layer', 'Technology'],
    ['Framework', 'React 18 with TypeScript'],
    ['Build Tool', 'Vite 5'],
    ['Styling', 'Tailwind CSS v4'],
    ['Icons', 'Lucide React'],
    ['Animations', 'Framer Motion'],
    ['PDF', '@react-pdf/renderer'],
])

# --- Page 3: Hackathon + Author ---
pdf.add_page()
pdf.sec('Hackathon Submission')
pdf.txt('This project was created as part of the NativelyAI Hackathon.')
pdf.bul('Project: ResumePilot AI - AI-Powered Resume Builder')
pdf.bul('Category: Productivity / Career Tools')
pdf.bul('Tech: React, TypeScript, Tailwind CSS, Vite')

pdf.sec('Author')
pdf.bul('Abdu Ali Adem')
pdf.bul('GitHub: @abduali-adem')
pdf.bul('LinkedIn: /in/abdu-ali-adem')

pdf.ln(8)
pdf.set_draw_color(30, 64, 175)
pdf.set_line_width(0.3)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(5)
pdf.set_font('S', 'I', 10)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 8, 'Made with love for the NativelyAI Hackathon', new_x="LMARGIN", new_y="NEXT", align='C')

# --- Output ---
pdf.output('README.pdf')
size = os.path.getsize('README.pdf')
print(f'PDF created: README.pdf ({size} bytes)')

# Base64 encode for persistence
with open('README.pdf', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
with open('README.pdf.b64', 'w') as f:
    f.write(b64)
print(f'Base64 saved: README.pdf.b64 ({len(b64)} chars)')

# Copy to public/ for web serving
shutil.copy('README.pdf', 'public/README.pdf')
print(f'Copied to public/README.pdf')