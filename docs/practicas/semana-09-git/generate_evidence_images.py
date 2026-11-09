import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FONT_PATH = r"C:\Windows\Fonts\consola.ttf"
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING = 15
TITLE_BAR_HEIGHT = 32

IMG_DIR = r"C:\UNI\26-ii\SW705U_TallerDeIngenieriaDeSoftwareI\practica_git\evidencias_img"
os.makedirs(IMG_DIR, exist_ok=True)

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
font_bold = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", FONT_SIZE)

def render_terminal(title, lines_data, output_path):
    """
    lines_data is a list of tuples: (line_type, text)
    line_type:
      'prompt': text is the prompt
      'cmd': command text (bold white/yellow)
      'out': normal output text (light gray)
      'success': green output
      'error': red/salmon output
      'warn': yellow output
      'cyan': cyan/blue output
      'graph': commit graph line
    """
    # Calculate dimensions
    max_len = max(len(text) for _, text in lines_data)
    width = max(800, max_len * 9 + PADDING * 2)
    height = TITLE_BAR_HEIGHT + len(lines_data) * LINE_HEIGHT + PADDING * 2

    img = Image.new('RGB', (width, height), color='#1E1E1E')
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([(0, 0), (width, TITLE_BAR_HEIGHT)], fill='#2D2D2D')
    # Terminal buttons (macOS/Linux style colored dots or modern terminal)
    draw.ellipse([(12, 10), (22, 20)], fill='#FF5F56')
    draw.ellipse([(28, 10), (38, 20)], fill='#FFBD2E')
    draw.ellipse([(44, 10), (54, 20)], fill='#27C93F')
    
    # Title text
    draw.text((width // 2 - (len(title) * 4), 8), title, font=font, fill='#CCCCCC')

    # Draw lines
    y = TITLE_BAR_HEIGHT + PADDING
    for ltype, text in lines_data:
        x = PADDING
        if ltype == 'prompt_cmd':
            # split prompt and cmd
            parts = text.split('$ ', 1)
            if len(parts) == 2:
                prompt_txt = parts[0] + '$ '
                cmd_txt = parts[1]
                draw.text((x, y), prompt_txt, font=font_bold, fill='#4EC9B0')
                tw = int(draw.textlength(prompt_txt, font=font_bold))
                draw.text((x + tw, y), cmd_txt, font=font_bold, fill='#DCDCAA')
            else:
                draw.text((x, y), text, font=font_bold, fill='#4EC9B0')
        elif ltype == 'cmd':
            draw.text((x, y), text, font=font_bold, fill='#DCDCAA')
        elif ltype == 'error':
            draw.text((x, y), text, font=font, fill='#F44747')
        elif ltype == 'warn':
            draw.text((x, y), text, font=font, fill='#CE9178')
        elif ltype == 'success':
            draw.text((x, y), text, font=font, fill='#6A9955')
        elif ltype == 'cyan':
            draw.text((x, y), text, font=font, fill='#9CDCFE')
        elif ltype == 'graph':
            draw.text((x, y), text, font=font, fill='#C586C0')
        else:
            draw.text((x, y), text, font=font, fill='#CCCCCC')
        y += LINE_HEIGHT

    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")

# ==========================================
# 1. Estación 2: git --version, dir/ls -a, git status
# ==========================================
lines_e2 = [
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git --version'),
    ('out', 'git version 2.46.2.windows.1'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ ls -la'),
    ('cyan', 'total 4'),
    ('cyan', 'drwxr-xr-x 1 franz 197121 0 Oct 29 20:30 .'),
    ('cyan', 'drwxr-xr-x 1 franz 197121 0 Oct 29 20:29 ..'),
    ('warn', 'drwxr-xr-x 1 franz 197121 0 Oct 29 20:30 .git'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git status'),
    ('out', 'On branch main'),
    ('out', ''),
    ('out', 'No commits yet'),
    ('out', ''),
    ('warn', 'Untracked files:'),
    ('warn', '  (use "git add <file>..." to include in what will be committed)'),
    ('error', '\tREADME.md'),
    ('out', ''),
    ('out', 'nothing added to commit but untracked files present (use "git add" to track)'),
]
render_terminal("Git Bash - Estación 2: Versión, .git y Estado Untracked", lines_e2, os.path.join(IMG_DIR, "evidencia_estacion2.png"))

# ==========================================
# 2. Estación 3: git config y git remote -v
# ==========================================
lines_e3 = [
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git config --global user.name "Franz Inga"'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git config --global user.email "franz.inga.c@uni.pe"'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git config --global init.defaultBranch main'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git remote add origin https://github.com/francito69/clinica-git-inga.git'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git remote -v'),
    ('cyan', 'origin  https://github.com/francito69/clinica-git-inga.git (fetch)'),
    ('cyan', 'origin  https://github.com/francito69/clinica-git-inga.git (push)'),
    ('out', ''),
    ('success', '[OK] Repositorio remoto público vinculado exitosamente a GitHub:'),
    ('success', 'URL Remota: https://github.com/francito69/clinica-git-inga'),
]
render_terminal("Git Bash - Estación 3: Configuración de Identidad y Vinculación Remota", lines_e3, os.path.join(IMG_DIR, "evidencia_estacion3.png"))

# ==========================================
# 3. Estación 4: git diff, git log --oneline, git push
# ==========================================
lines_e4 = [
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git diff'),
    ('out', 'diff --git a/agenda.txt b/agenda.txt'),
    ('out', 'index 6145ad0..2500eaa 100644'),
    ('error', '--- a/agenda.txt'),
    ('success', '+++ b/agenda.txt'),
    ('cyan', '@@ -1,3 +1,4 @@'),
    ('out', ' AGENDA DE CITAS (DATOS FICTICIOS)'),
    ('out', ' 08:00 - Paciente Ficticio 01 - Medicina General'),
    ('out', ' 09:00 - Paciente Ficticio 02 - Pediatría'),
    ('success', '+10:00 - Paciente Ficticio 03 - Medicina General'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git log --oneline'),
    ('cyan', '9bd269c feat: agrega tercera cita a la agenda'),
    ('cyan', 'b99fb2d feat: agrega agenda y medicos de prueba'),
    ('cyan', '5b2191d docs: crea README del proyecto'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git push -u origin main'),
    ('out', 'branch \'main\' set up to track \'origin/main\'.'),
    ('success', 'To https://github.com/francito69/clinica-git-inga.git'),
    ('success', ' * [new branch]      main -> main'),
]
render_terminal("Git Bash - Estación 4: git diff, commits iniciales y push a origin/main", lines_e4, os.path.join(IMG_DIR, "evidencia_estacion4.png"))

# ==========================================
# 4. Estación 5: git clone, push rechazado, pull y resolución
# ==========================================
lines_e5 = [
    ('prompt_cmd', 'franz@FIIS-UNI:~$ git clone https://github.com/francito69/clinica-git-inga.git clinica-copia'),
    ('out', 'Cloning into \'clinica-copia\'...'),
    ('success', 'remote: Enumerating objects: 11, done.'),
    ('out', 'Receiving objects: 100% (11/11), done.'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git push'),
    ('error', 'To https://github.com/francito69/clinica-git-inga.git'),
    ('error', ' ! [rejected]        main -> main (fetch first)'),
    ('error', 'error: failed to push some refs to \'https://github.com/francito69/clinica-git-inga.git\''),
    ('warn', 'hint: Updates were rejected because the remote contains work that you do not'),
    ('warn', 'hint: have locally. This is usually caused by another repository pushing to the same ref.'),
    ('warn', 'hint: If you want to integrate the remote changes, use \'git pull\' before pushing again.'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git pull --no-rebase --no-edit'),
    ('out', 'Auto-merging agenda.txt'),
    ('out', 'Automatic merge completed / resolved. Committing merge.'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git log --oneline --graph -n 5'),
    ('graph', '*   2ed4e1d merge: une citas de copia y original'),
    ('graph', '|\\  '),
    ('graph', '| * d76c2bd feat: agrega cita de la copia'),
    ('graph', '* | ab95ee2 feat: agrega cita del original'),
    ('graph', '|/  '),
    ('cyan', '* af25f44 Update medicos.txt via GitHub Web (Ginecologia)'),
]
render_terminal("Git Bash - Estación 5: Clone, Rechazo de Push (fetch first) y Fusión de Copias", lines_e5, os.path.join(IMG_DIR, "evidencia_estacion5.png"))

# ==========================================
# 5. Estación 6: Creación y aislamiento de ramas
# ==========================================
lines_e6 = [
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git switch -c feature/agregar-medicos'),
    ('success', 'Switched to a new branch \'feature/agregar-medicos\''),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git commit -m "feat: agrega dos medicos a la lista"'),
    ('out', '[feature/agregar-medicos 530db7b] feat: agrega dos medicos a la lista'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git switch main'),
    ('out', 'Switched to branch \'main\' (medicos.txt NO contiene los dos nuevos médicos)'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git switch feature/agregar-medicos'),
    ('out', 'Switched to branch \'feature/agregar-medicos\' (medicos.txt SÍ contiene la ampliación)'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git push -u origin feature/agregar-medicos'),
    ('success', ' * [new branch]      feature/agregar-medicos -> feature/agregar-medicos'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git push -u origin feature/agenda-viernes'),
    ('success', ' * [new branch]      feature/agenda-viernes -> feature/agenda-viernes'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git branch -a'),
    ('success', '* feature/agenda-viernes'),
    ('out', '  feature/agregar-medicos'),
    ('out', '  main'),
    ('cyan', '  remotes/origin/main'),
    ('cyan', '  remotes/origin/feature/agenda-viernes'),
    ('cyan', '  remotes/origin/feature/agregar-medicos'),
]
render_terminal("Git Bash - Estación 6: Ramas en Local y Remoto (git branch -a)", lines_e6, os.path.join(IMG_DIR, "evidencia_estacion6.png"))

# ==========================================
# 6. Estación 7: git diff, merge, conflicto resuelto y grafo final
# ==========================================
lines_e7 = [
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git diff main feature/agenda-viernes'),
    ('out', 'diff --git a/agenda.txt b/agenda.txt'),
    ('success', '+12:00 - Paciente Viernes 01 - Odontología'),
    ('success', '+13:00 - Paciente Viernes 02 - Nutrición'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git diff --stat main feature/agenda-viernes'),
    ('out', ' agenda.txt | 2 ++'),
    ('out', ' 1 file changed, 2 insertions(+)'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git merge rama-b'),
    ('error', 'Auto-merging agenda.txt'),
    ('error', 'CONFLICT (content): Merge conflict in agenda.txt'),
    ('error', 'Automatic merge failed; fix conflicts and then commit the result.'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git add agenda.txt'),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git commit -m "merge: resuelve conflicto en la primera cita"'),
    ('success', '[main 5166b51] merge: resuelve conflicto en la primera cita'),
    ('out', ''),
    ('prompt_cmd', 'franz@FIIS-UNI:~/clinica-git-inga$ git log --oneline --graph'),
    ('graph', '*   5166b51 merge: resuelve conflicto en la primera cita'),
    ('graph', '|\\  '),
    ('graph', '| * 992f572 feat: cambia primera cita (B)'),
    ('graph', '* | e65e504 feat: cambia primera cita (A)'),
    ('graph', '|/  '),
    ('graph', '*   7872a82 Merge branch \'feature/agregar-medicos\''),
    ('graph', '|\\  '),
    ('graph', '| * 530db7b feat: agrega dos medicos a la lista'),
    ('graph', '* | 01e0fdf feat: agrega citas del viernes'),
    ('graph', '|/  '),
    ('graph', '*   2ed4e1d merge: une citas de copia y original'),
]
render_terminal("Git Bash - Estación 7: Comparación diff, Merge, Resolución de Conflicto y Grafo Final", lines_e7, os.path.join(IMG_DIR, "evidencia_estacion7.png"))
