from util.global_logger import GLOBAL_LOGGER as LOG


def shutdown():
    import os
    import platform

    current_os = platform.system()
    LOG.info(f"Shutting down {current_os}.")

    if current_os == "Windows":
        os.system("shutdown /s /t 1")
    elif current_os == "Linux" or current_os == "Darwin":
        os.system("sudo shutdown -h now")
    else:
        print(f"Unsupported operating system: {current_os}. Shutdown aborted.")
