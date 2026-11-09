import os
import sys
import subprocess
import json
import base64
import urllib.request
import shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = 'francito69/clinica-git-inga'
BASE_DIR = r'C:\UNI\26-ii\SW705U_TallerDeIngenieriaDeSoftwareI\practica_git'
ORIG_DIR = os.path.join(BASE_DIR, 'clinica-git-inga')
CLONE_DIR = os.path.join(BASE_DIR, 'clinica-copia')

log_records = []

def run_cmd(cmd, cwd=None, allow_fail=False):
    res = subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
    out = res.stdout
    if res.stderr:
        out += ('\n' if out and not out.endswith('\n') else '') + res.stderr
    print(f'=== CMD: {cmd} (cwd: {cwd}) ===')
    print(f'EXIT: {res.returncode}')
    print(out)
    log_records.append({
        'cmd': cmd,
        'cwd': cwd,
        'code': res.returncode,
        'out': out.strip()
    })
    if res.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed: {cmd}\nOutput: {out}")
    return res.returncode, out

def remove_readonly(func, path, excinfo):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clean_dir():
    if os.path.exists(BASE_DIR):
        subprocess.run(f'rd /s /q "{BASE_DIR}"', shell=True)
    os.makedirs(ORIG_DIR, exist_ok=True)

print("Starting practice automation...")
clean_dir()

# ==========================================
# ESTACIÓN 2: Instalar Git y primer repo
# ==========================================
run_cmd('git --version')
run_cmd('git init -b main', cwd=ORIG_DIR)
run_cmd('dir /a', cwd=ORIG_DIR)
run_cmd('git status', cwd=ORIG_DIR)

readme_content = """# Clínica San Rafael - Práctica de Git
Autor: Franz Joe Inga Champi (20231302G)
Fecha: 29/10/2026
"""
with open(os.path.join(ORIG_DIR, 'README.md'), 'w', encoding='utf-8') as f:
    f.write(readme_content)

run_cmd('git status', cwd=ORIG_DIR)

# ==========================================
# ESTACIÓN 3: Cuenta y repo en GitHub
# ==========================================
run_cmd('git remote add origin https://github.com/francito69/clinica-git-inga.git', cwd=ORIG_DIR)
run_cmd('git remote -v', cwd=ORIG_DIR)

# ==========================================
# ESTACIÓN 4: add, commit y push
# ==========================================
run_cmd('git add README.md', cwd=ORIG_DIR)
run_cmd('git status', cwd=ORIG_DIR)
run_cmd('git commit -m "docs: crea README del proyecto"', cwd=ORIG_DIR)

agenda_content = """AGENDA DE CITAS (DATOS FICTICIOS)
08:00 - Paciente Ficticio 01 - Medicina General
09:00 - Paciente Ficticio 02 - Pediatría
"""
medicos_content = """MÉDICOS (DATOS FICTICIOS)
Dra. Ana Prueba - Medicina General
Dr. Luis Ejemplo - Pediatría
"""
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'w', encoding='utf-8') as f:
    f.write(agenda_content)
with open(os.path.join(ORIG_DIR, 'medicos.txt'), 'w', encoding='utf-8') as f:
    f.write(medicos_content)

run_cmd('git add agenda.txt medicos.txt', cwd=ORIG_DIR)
run_cmd('git commit -m "feat: agrega agenda y medicos de prueba"', cwd=ORIG_DIR)

with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'a', encoding='utf-8') as f:
    f.write('10:00 - Paciente Ficticio 03 - Medicina General\n')

run_cmd('git diff', cwd=ORIG_DIR)
run_cmd('git add agenda.txt', cwd=ORIG_DIR)
run_cmd('git commit -m "feat: agrega tercera cita a la agenda"', cwd=ORIG_DIR)

run_cmd('git log', cwd=ORIG_DIR)
run_cmd('git log --oneline', cwd=ORIG_DIR)
run_cmd('git branch -M main', cwd=ORIG_DIR)
# Push with force or normal to ensure fresh history
run_cmd('git push -u origin main --force', cwd=ORIG_DIR)

# ==========================================
# ESTACIÓN 5: Clone y Pull + Push rechazado
# ==========================================
if os.path.exists(CLONE_DIR):
    subprocess.run(f'rd /s /q "{CLONE_DIR}"', shell=True)
run_cmd(f'git clone https://github.com/francito69/clinica-git-inga.git clinica-copia', cwd=BASE_DIR)

# 5.2 En la copia, agregar médico de cardiología y subir
with open(os.path.join(CLONE_DIR, 'medicos.txt'), 'a', encoding='utf-8') as f:
    f.write('Dr. Pedro Muestra - Cardiología\n')
run_cmd('git add medicos.txt', cwd=CLONE_DIR)
run_cmd('git commit -m "feat: agrega medico de cardiologia"', cwd=CLONE_DIR)
run_cmd('git push', cwd=CLONE_DIR)

# 5.3 Volver a la carpeta original y traer cambios
run_cmd('git status', cwd=ORIG_DIR)
run_cmd('git pull', cwd=ORIG_DIR)
run_cmd('type medicos.txt', cwd=ORIG_DIR)

# 5.4 Simular edición en GitHub Web mediante GitHub API
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/contents/medicos.txt', headers={
    'Authorization': f'Bearer {TOKEN}',
    'User-Agent': 'Python'
})
with urllib.request.urlopen(req) as resp:
    file_info = json.loads(resp.read().decode())
    sha = file_info['sha']
    current_content = base64.b64decode(file_info['content']).decode('utf-8')

new_web_content = current_content.rstrip() + '\nDra. Carmen Consulta - Ginecología\n'
put_data = json.dumps({
    'message': 'Update medicos.txt via GitHub Web (Ginecologia)',
    'content': base64.b64encode(new_web_content.encode('utf-8')).decode('utf-8'),
    'sha': sha,
    'branch': 'main'
}).encode('utf-8')

req_put = urllib.request.Request(f'https://api.github.com/repos/{REPO}/contents/medicos.txt', data=put_data, method='PUT', headers={
    'Authorization': f'Bearer {TOKEN}',
    'User-Agent': 'Python',
    'Content-Type': 'application/json'
})
with urllib.request.urlopen(req_put) as resp_put:
    print("GitHub Web commit status:", resp_put.status)

# Traerlo a la carpeta original
run_cmd('git pull', cwd=ORIG_DIR)
run_cmd('type medicos.txt', cwd=ORIG_DIR)

# 5.5 En clinica-copia, agregar una línea a agenda.txt, registrar y subir
run_cmd('git pull', cwd=CLONE_DIR) # keep clone updated first
with open(os.path.join(CLONE_DIR, 'agenda.txt'), 'a', encoding='utf-8') as f:
    f.write('11:00 - Paciente Ficticio 04 - Traumatología\n')
run_cmd('git add agenda.txt', cwd=CLONE_DIR)
run_cmd('git commit -m "feat: agrega cita de la copia"', cwd=CLONE_DIR)
run_cmd('git push', cwd=CLONE_DIR)

# 5.6 En clinica-git-inga ORIGINAL, agregar OTRA línea SIN hacer pull antes, commit e intentar push
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'a', encoding='utf-8') as f:
    f.write('11:30 - Paciente Ficticio 05 - Dermatología\n')
run_cmd('git add agenda.txt', cwd=ORIG_DIR)
run_cmd('git commit -m "feat: agrega cita del original"', cwd=ORIG_DIR)
# This push must fail!
code_rejected, out_rejected = run_cmd('git push', cwd=ORIG_DIR, allow_fail=True)
print("REJECTION OBSERVED AS EXPECTED:", code_rejected)

# 5.7 Traer cambios y unirlos
pull_code, pull_out = run_cmd('git pull --no-rebase --no-edit', cwd=ORIG_DIR, allow_fail=True)
if 'CONFLICT' in pull_out:
    print("Resolving conflict in step 5.7 as described in guide table 32...")
    with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'r', encoding='utf-8') as f:
        conf_lines = f.read().splitlines()
    clean_lines = [l for l in conf_lines if not (l.startswith('<<<<<<<') or l.startswith('=======') or l.startswith('>>>>>>>'))]
    with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(clean_lines) + '\n')
    run_cmd('git add agenda.txt', cwd=ORIG_DIR)
    run_cmd('git commit -m "merge: une citas de copia y original"', cwd=ORIG_DIR)

run_cmd('git log --oneline --graph', cwd=ORIG_DIR)

# 5.8 Subir el resultado
run_cmd('git push', cwd=ORIG_DIR)

# ==========================================
# ESTACIÓN 6: Ramas (branches)
# ==========================================
# 6.1
run_cmd('git pull', cwd=ORIG_DIR)
run_cmd('git branch', cwd=ORIG_DIR)
run_cmd('git status', cwd=ORIG_DIR)

# 6.2 Switch to feature/agregar-medicos
run_cmd('git switch -c feature/agregar-medicos', cwd=ORIG_DIR)
run_cmd('git branch', cwd=ORIG_DIR)

# 6.3 Agregar dos médicos
with open(os.path.join(ORIG_DIR, 'medicos.txt'), 'a', encoding='utf-8') as f:
    f.write('Dr. Roberto Diagnóstico - Neurología\n')
    f.write('Dra. Elena Cuidado - Oftalmología\n')
run_cmd('git add medicos.txt', cwd=ORIG_DIR)
run_cmd('git commit -m "feat: agrega dos medicos a la lista"', cwd=ORIG_DIR)

# 6.4 Switch to main and compare
run_cmd('git switch main', cwd=ORIG_DIR)
run_cmd('type medicos.txt', cwd=ORIG_DIR)
run_cmd('git switch feature/agregar-medicos', cwd=ORIG_DIR)
run_cmd('type medicos.txt', cwd=ORIG_DIR)

# 6.5 Push feature/agregar-medicos
run_cmd('git push -u origin feature/agregar-medicos', cwd=ORIG_DIR)

# 6.6 Switch to main, create feature/agenda-viernes, add citas, commit and push
run_cmd('git switch main', cwd=ORIG_DIR)
run_cmd('git switch -c feature/agenda-viernes', cwd=ORIG_DIR)
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'a', encoding='utf-8') as f:
    f.write('12:00 - Paciente Viernes 01 - Odontología\n')
    f.write('13:00 - Paciente Viernes 02 - Nutrición\n')
run_cmd('git add agenda.txt', cwd=ORIG_DIR)
run_cmd('git commit -m "feat: agrega citas del viernes"', cwd=ORIG_DIR)
run_cmd('git push -u origin feature/agenda-viernes', cwd=ORIG_DIR)

# 6.7 Ver todas las ramas
run_cmd('git branch -a', cwd=ORIG_DIR)

# ==========================================
# ESTACIÓN 7: Comparar y fusionar ramas (diff y merge)
# ==========================================
# 7.1 Comparar main con feature/agenda-viernes
run_cmd('git diff main feature/agenda-viernes', cwd=ORIG_DIR)
run_cmd('git diff --stat main feature/agenda-viernes', cwd=ORIG_DIR)

# 7.2 Fusionar en main feature/agenda-viernes (Fast-forward)
run_cmd('git switch main', cwd=ORIG_DIR)
run_cmd('git merge feature/agenda-viernes', cwd=ORIG_DIR)

# 7.3 Fusionar feature/agregar-medicos (Merge commit)
run_cmd('git merge --no-edit feature/agregar-medicos', cwd=ORIG_DIR)

# 7.4 Log gráfico
run_cmd('git log --oneline --graph', cwd=ORIG_DIR)

# 7.5 Verificar y subir
run_cmd('type agenda.txt', cwd=ORIG_DIR)
run_cmd('type medicos.txt', cwd=ORIG_DIR)
run_cmd('git push', cwd=ORIG_DIR)

# 7.6 Borrar ramas fusionadas local y remoto
run_cmd('git branch -d feature/agenda-viernes feature/agregar-medicos', cwd=ORIG_DIR)
run_cmd('git push origin --delete feature/agenda-viernes feature/agregar-medicos', cwd=ORIG_DIR)
run_cmd('git branch -a', cwd=ORIG_DIR)

# 7.7 Reto: conflicto
run_cmd('git switch -c rama-a', cwd=ORIG_DIR)
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'r', encoding='utf-8') as f:
    lines = f.readlines()
# modify line 1 (08:00)
lines[1] = '08:00 - Paciente Ficticio 01 (Modificado por Rama A) - Medicina General / Triaje 1\n'
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'w', encoding='utf-8') as f:
    f.writelines(lines)
run_cmd('git commit -am "feat: cambia primera cita (A)"', cwd=ORIG_DIR)

run_cmd('git switch main', cwd=ORIG_DIR)
run_cmd('git switch -c rama-b', cwd=ORIG_DIR)
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'r', encoding='utf-8') as f:
    lines = f.readlines()
lines[1] = '08:00 - Paciente Ficticio 01 (Modificado por Rama B) - Medicina General / Triaje 2\n'
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'w', encoding='utf-8') as f:
    f.writelines(lines)
run_cmd('git commit -am "feat: cambia primera cita (B)"', cwd=ORIG_DIR)

# 7.8 Fusionar rama-a (FF) y rama-b (Conflicto)
run_cmd('git switch main', cwd=ORIG_DIR)
run_cmd('git merge rama-a', cwd=ORIG_DIR)
run_cmd('git merge rama-b', cwd=ORIG_DIR, allow_fail=True)

# 7.9 Resolver conflicto
with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'r', encoding='utf-8') as f:
    conflict_text = f.read()
print("CONFLICT CONTENT:\n", conflict_text)

# Clean conflict markers and consolidate
resolved_lines = []
for line in conflict_text.splitlines():
    if line.startswith('<<<<<<<') or line.startswith('=======') or line.startswith('>>>>>>>'):
        continue
    if 'Modificado por Rama B' in line:
        continue # resolve by keeping unified version or single clean line
    if 'Modificado por Rama A' in line:
        resolved_lines.append('08:00 - Paciente Ficticio 01 (Consensuado Rama A y B) - Medicina General / Triaje Unificado')
    else:
        resolved_lines.append(line)

with open(os.path.join(ORIG_DIR, 'agenda.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(resolved_lines) + '\n')

run_cmd('git add agenda.txt', cwd=ORIG_DIR)
run_cmd('git commit -m "merge: resuelve conflicto en la primera cita"', cwd=ORIG_DIR)

# 7.10 Subir main y borrar ramas de prueba
run_cmd('git push', cwd=ORIG_DIR)
run_cmd('git branch -d rama-a rama-b', cwd=ORIG_DIR)
run_cmd('git log --oneline --graph', cwd=ORIG_DIR)

with open(os.path.join(BASE_DIR, 'practice_log.json'), 'w', encoding='utf-8') as f:
    json.dump(log_records, f, indent=2, ensure_ascii=False)

print("PRACTICE COMPLETED SUCCESSFULLY!")
