"""
Multi-Bot Launcher for Shinjuku Protect
Démarre plusieurs instances du bot avec différents tokens.

Utilisation:
  1. Ajoutez vos tokens dans le fichier .env :
       BOT_TOKEN_1=premier_token
       BOT_TOKEN_2=deuxieme_token
       BOT_TOKEN_3=troisieme_token
     (Le BOT_TOKEN simple fonctionne aussi)

  2. Lancez ce script :
       python launcher.py
"""

import os
import sys
import subprocess
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


def get_all_tokens():
    tokens = []

    token = os.environ.get("BOT_TOKEN")
    if token:
        tokens.append(("BOT_TOKEN", token))

    i = 1
    while True:
        key = f"BOT_TOKEN_{i}"
        token = os.environ.get(key)
        if token:
            tokens.append((key, token))
            i += 1
        else:
            break

    return tokens


def main():
    print("=" * 56)
    print("  [+] EMPIRE-X | PROTECT - Multi-Bot Launcher")
    print("=" * 56)

    tokens = get_all_tokens()

    if not tokens:
        print("  Aucun token trouvé dans .env")
        print("  Ajoutez BOT_TOKEN=xxx ou BOT_TOKEN_1=xxx, BOT_TOKEN_2=xxx, etc.")
        sys.exit(1)

    print(f"  {len(tokens)} bot(s) à démarrer :")
    for name, t in tokens:
        print(f"    {name}: {t[:20]}...{t[-5:]}")
    print("─" * 56)

    processes = []

    try:
        for name, token in tokens:
            env = os.environ.copy()
            env["BOT_TOKEN"] = token
            env["BOT_INSTANCE"] = name

            proc = subprocess.Popen(
                [sys.executable, "main.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            processes.append((name, proc))
            print(f"  [+] {name} démarré (PID: {proc.pid})")
            time.sleep(2)

        print("=" * 56)
        print(f"  {len(processes)} bot(s) en cours d'exécution")
        print("  Ctrl+C pour tout arrêter")
        print("=" * 56)

        for name, proc in processes:
            for line in proc.stdout:
                print(f"[{name}] {line}", end="")

    except KeyboardInterrupt:
        print("\n  Arrêt des bots...")
        for name, proc in processes:
            proc.terminate()
        for name, proc in processes:
            proc.wait()
        print("  Tous les bots arrêtés.")

    except Exception as e:
        print(f"  Erreur: {e}")
        for name, proc in processes:
            proc.terminate()


if __name__ == "__main__":
    main()
