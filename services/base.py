"""
Shared SSH helpers for all service installers.
"""


def run_script(client, password: str, script: str, label: str = "service"):
    """
    Upload a shell script to the remote host via SFTP and execute it with sudo.
    Falls back to a heredoc if SFTP is unavailable.
    Returns (stdout_str, stderr_str).
    """
    script_path = f"/tmp/_install_{label}.sh"

    try:
        sftp = client.open_sftp()
        with sftp.open(script_path, "w") as f:
            f.write(script)
        sftp.close()
    except Exception as e:
        print(f"  [{label}] SFTP unavailable ({e}), using heredoc fallback")
        stdin, stdout, stderr = client.exec_command(
            f"cat << 'INSTALL_EOF' > {script_path}\n{script}\nINSTALL_EOF"
        )
        stdout.read()

    stdin, stdout, stderr = client.exec_command(
        f"chmod +x {script_path} && sudo -S bash {script_path}"
    )
    stdin.write(password + "\n")
    stdin.flush()

    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err


def install_package(client, password: str, package: str):
    """
    Install a single package using the remote host's package manager.
    Auto-detects apt-get, dnf, or yum.
    """
    cmd = (
        f"if command -v apt-get > /dev/null; then "
        f"sudo -S DEBIAN_FRONTEND=noninteractive apt-get install -y {package}; "
        f"elif command -v dnf > /dev/null; then "
        f"sudo -S dnf install -y {package}; "
        f"elif command -v yum > /dev/null; then "
        f"sudo -S yum install -y {package}; "
        f"else echo 'No supported package manager found' >&2; exit 1; fi"
    )
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()

    out = stdout.read().decode()
    err = stderr.read().decode()
    if err:
        print(f"  [pkg:{package}] stderr: {err}")
    return out, err
