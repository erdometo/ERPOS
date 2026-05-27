import os
import sys
import subprocess
import threading
import signal
import time

# Flag to signal threads to stop
shutdown_event = threading.Event()

def read_output(process, prefix, color_code):
    """
    Reads stdout/stderr (combined) from a process and outputs it to console with prefix and colors.
    """
    reset_code = "\033[0m"
    try:
        # Read line by line from the combined stdout/stderr stream
        for line in iter(process.stdout.readline, ''):
            if shutdown_event.is_set():
                break
            if line:
                # Strip and print with prefix
                try:
                    print(f"{color_code}{prefix}{reset_code} {line.strip()}", flush=True)
                except UnicodeEncodeError:
                    # Fallback for terminals that cannot print unicode characters
                    encoding = sys.stdout.encoding or 'ascii'
                    safe_line = line.encode(encoding, errors='replace').decode(encoding)
                    print(f"{color_code}{prefix}{reset_code} {safe_line.strip()}", flush=True)
    except Exception as e:
        if not shutdown_event.is_set():
            try:
                print(f"{color_code}{prefix}{reset_code} Error reading stream: {e}", flush=True)
            except Exception:
                pass
    finally:
        try:
            process.stdout.close()
        except:
            pass

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    print("==================================================================", flush=True)
    print("OmniGate ERP OS: Local Application Launcher Orchestrator", flush=True)
    print("==================================================================", flush=True)

    workspace_root = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Resolve virtual environment python executable
    python_exe = os.path.join(workspace_root, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable
        print(f"[*] Warning: Virtual env python not found at {python_exe}.", flush=True)
        print(f"[*] Falling back to global/current interpreter: {python_exe}", flush=True)
    else:
        print(f"[*] Found virtual environment Python: {python_exe}", flush=True)

    # Define backend configuration
    backend_cwd = os.path.join(workspace_root, "backend")
    backend_args = [python_exe, "-m", "uvicorn", "main:app", "--port", "8000", "--reload"]

    # Define frontend configuration
    frontend_cwd = os.path.join(workspace_root, "frontend")
    frontend_args = ["npm", "run", "dev"]

    # Console colors
    cyan = "\033[96m"
    magenta = "\033[95m"
    yellow = "\033[93m"
    red = "\033[91m"
    reset = "\033[0m"

    print(f"[*] Launching Python Backend in: {backend_cwd}", flush=True)
    backend_proc = None
    frontend_proc = None

    try:
        backend_proc = subprocess.Popen(
            backend_args,
            cwd=backend_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1
        )
    except Exception as e:
        print(f"{red}[Error]{reset} Failed to launch backend: {e}", flush=True)
        sys.exit(1)

    print(f"[*] Launching React Frontend in: {frontend_cwd}", flush=True)
    try:
        frontend_proc = subprocess.Popen(
            frontend_args,
            cwd=frontend_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,
            shell=True
        )
    except Exception as e:
        print(f"{red}[Error]{reset} Failed to launch frontend: {e}", flush=True)
        # Terminate backend if it was running
        if backend_proc:
            backend_proc.terminate()
        sys.exit(1)

    # 3. Spawn reader threads
    backend_thread = threading.Thread(
        target=read_output,
        args=(backend_proc, "[Backend]", cyan),
        daemon=True
    )
    frontend_thread = threading.Thread(
        target=read_output,
        args=(frontend_proc, "[Frontend]", magenta),
        daemon=True
    )

    backend_thread.start()
    frontend_thread.start()

    print("[*] Both services started successfully.", flush=True)
    print("[*] Monitoring logs concurrently... Press Ctrl+C to terminate.", flush=True)
    print("------------------------------------------------------------------", flush=True)

    try:
        while True:
            # Monitor processes status
            backend_status = backend_proc.poll()
            frontend_status = frontend_proc.poll()

            if backend_status is not None:
                print(f"\n{red}[Backend]{reset} Process exited unexpectedly with code {backend_status}", flush=True)
                break
            if frontend_status is not None:
                print(f"\n{magenta}[Frontend]{reset} Process exited unexpectedly with code {frontend_status}", flush=True)
                break

            time.sleep(0.5)

    except KeyboardInterrupt:
        print(f"\n{yellow}[*] Ctrl+C intercepted. Cleaning up active processes...{reset}", flush=True)
    finally:
        # Set shutdown flag to exit reader threads
        shutdown_event.set()

        # Clean up backend and frontend process trees
        for proc, name in [(backend_proc, "Backend"), (frontend_proc, "Frontend")]:
            if proc and proc.poll() is None:
                print(f"[*] Terminating {name} (PID: {proc.pid}) and its descendants...", flush=True)
                try:
                    if os.name == 'nt':
                        # Use taskkill /F /T on Windows to clean up process trees
                        subprocess.run(
                            f"taskkill /F /T /PID {proc.pid}",
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    else:
                        proc.terminate()
                        proc.wait(timeout=3)
                except Exception as ex:
                    print(f"[*] Error terminating {name}: {ex}", flush=True)
                    try:
                        proc.kill()
                    except:
                        pass

        print("[*] Cleanup complete. ERP Local Launcher has terminated.", flush=True)

if __name__ == "__main__":
    main()
