import buildpackutil
import os
import subprocess
import time
from m2ee import logger


def start_mxbuild_server(dot_local_location, mx_version):
    cache = "/tmp/downloads"  # disable caching here, not in compile step
    mono_location = buildpackutil.ensure_and_get_mono(mx_version, cache)
    mono_env = buildpackutil._get_env_with_monolib(mono_location)
    path = os.path.join(os.getcwd(), "runtimes", str(mx_version))
    if not os.path.isdir(os.path.join(path, "modeler")):
        buildpackutil.ensure_mxbuild_in_directory(
            os.path.join(dot_local_location, "mxbuild"), mx_version, cache
        )
        path = os.path.join(dot_local_location, "mxbuild")

    jvm_location = buildpackutil.ensure_and_get_jvm(
        mx_version, cache, dot_local_location, package="jdk"
    )
    process = subprocess.Popen(
        [
            os.path.join(mono_location, "bin/mono"),
            "--config",
            os.path.join(mono_location, "etc/mono/config"),
            os.path.join(path, "modeler", "mxbuild.exe"),
            "--serve",
            "--port=6666",
            "--java-home=%s" % jvm_location,
            "--java-exe-path=%s/bin/java" % jvm_location,
        ],
        env=mono_env,
    )
    # give mxbuild a few seconds to init, then check if we are still running
    time.sleep(5)
    poll = process.poll()
    if poll is not None:
        raise Exception(
            "MxBuild did not start and returned code %d".format(poll)
        )
    logger.info("MxBuild is running and warming up")
