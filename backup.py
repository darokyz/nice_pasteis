import os
import shutil
import glob
from datetime import datetime


DB_PATH      = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
BACKUP_DIR   = os.path.join(os.path.dirname(__file__), 'backups')
MAX_BACKUPS  = 10  # quantos backups manter



def fazer_backup():
    if not os.path.exists(DB_PATH):
        print("[backup] db.sqlite3 não encontrado, pulando.")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(BACKUP_DIR, f"db_{timestamp}.sqlite3")

    shutil.copy2(DB_PATH, destino)
    print(f"[backup] Salvo: {destino}")

    # Remove backups antigos, mantém só os MAX_BACKUPS mais recentes
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "db_*.sqlite3")))
    excedentes = backups[:-MAX_BACKUPS]
    for antigo in excedentes:
        os.remove(antigo)
        print(f"[backup] Removido antigo: {os.path.basename(antigo)}")


if __name__ == "__main__":
    fazer_backup()