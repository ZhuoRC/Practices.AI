import subprocess
import sys
import time
import requests
import os

def kill_windows_process_on_port(port):
    """Kill processes on Windows using netstat and taskkill."""
    try:
        result = subprocess.run(f'netstat -aon | findstr :{port}',
                              shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            pids = set()
            for line in result.stdout.strip().split('\n'):
                if line.strip() and f':{port}' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        pids.add(pid)

            for pid in pids:
                try:
                    print(f"Stopping process {pid} using port {port}")
                    subprocess.run(f'taskkill /f /pid {pid}', shell=True, capture_output=True)
                    time.sleep(1)
                except:
                    pass

            return len(pids) > 0
        return False
    except Exception as e:
        print(f"Error stopping process on port {port}: {e}")
        return False

def check_service_running(url):
    """Check if a service is running."""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server."""
    print("Starting backend...")

    # Kill existing backend process
    if kill_windows_process_on_port(8000):
        print("Waiting for port 8000 to be free...")
        time.sleep(3)

    # Change to backend directory
    os.chdir("backend")

    try:
        # Create virtual environment if not exists
        if not os.path.exists("venv"):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

        # Get virtual environment python path
        if os.name == "nt":
            venv_python = os.path.join("venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join("venv", "bin", "python")

        # Install dependencies
        print("Installing dependencies...")
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
                      capture_output=True)

        # Start backend
        print("Starting backend server...")
        backend_process = subprocess.Popen([venv_python, "main.py"])

        # Wait for backend to start
        for i in range(15):
            time.sleep(1)
            if check_service_running("http://localhost:8000/health"):
                print("Backend started successfully!")
                return backend_process

        print("Backend failed to start")
        backend_process.terminate()
        return None

    except Exception as e:
        print(f"Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server."""
    print("Starting frontend...")

    # Kill existing frontend process
    if kill_windows_process_on_port(3000):
        print("Waiting for port 3000 to be free...")
        time.sleep(3)

    # Change to frontend directory (from project root)
    if os.getcwd().endswith("backend"):
        os.chdir("..")
    os.chdir("frontend")

    try:
        # Check if node_modules exists
        if not os.path.exists("node_modules"):
            print("Installing frontend dependencies...")
            subprocess.run(["npm", "install"], capture_output=True)

        # Check if npm is available
        try:
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: npm not found! Please install Node.js from https://nodejs.org/")
            return None

        # Start frontend
        print("Starting frontend server...")
        frontend_process = subprocess.Popen(["npm", "start"])

        # Wait for frontend to start
        for i in range(30):
            time.sleep(2)
            if check_service_running("http://localhost:3000"):
                print("Frontend started successfully!")
                return frontend_process

        print("Frontend is still starting (this may take a minute)...")
        return frontend_process

    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return None

def main():
    """Main function to start both services."""
    print("=== AI Rewriter Application Starter ===")
    print()

    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("Failed to start backend")
            return

        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("Failed to start frontend")
            backend_process.terminate()
            return

        print("\n" + "="*60)
        print("Application Started Successfully!")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:3000")
        print("API Docs: http://localhost:8000/docs")
        print("="*60)
        print("\nPress Ctrl+C to stop both services")

        # Monitor processes
        try:
            while True:
                time.sleep(5)
                if not check_service_running("http://localhost:8000/health"):
                    print("Backend stopped unexpectedly")
                    break
                if not check_service_running("http://localhost:3000"):
                    print("Frontend stopped unexpectedly")
                    break
        except KeyboardInterrupt:
            print("\nStopping services...")
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
            print("Services stopped")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()