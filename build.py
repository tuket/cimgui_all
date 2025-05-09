import argparse
import os
import subprocess
import shutil

root_path = os.path.dirname(__file__)

vckpg_triplets = {
    "win-x64": "x64-windows-static",
    "win-arm64": "arm64-windows-static",
    "linux-x64": "x64-linux",
    "linux-arm64": "arm64-linux",
    "osx-arm64": "arm64-osx",
    "osx-x64": "x64-osx",
    "wasm": "wasm32-emscripten"
}

def rel_path(path):
    return os.path.join(root_path, path)

def build_path(platform):
    return os.path.join(rel_path("build"), platform)

def create_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def new_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    create_dir(path)

def common_cmake_args(target, buildMode, freetype = False):
    return [
        "-B", build_path(target),
        "-DIMGUI_WCHAR32=ON",
        "-DIMGUI_FREETYPE=ON" + "ON" if freetype else "OFF",
        f"-DCMAKE_BUILD_TYPE={buildMode}",
    ]

def setup_vcpkg(target):
    vcpkg_path = rel_path("vcpkg")
    bootstrap_vcpkg = os.path.join(vcpkg_path, "bootstrap-vcpkg.bat" if os.name == "nt" else "bootstrap-vcpkg.sh")
    vcpkg = os.path.join(vcpkg_path, "vcpkg.exe" if os.name == "nt" else "vcpkg")
    subprocess.call(bootstrap_vcpkg)
    subprocess.call([vcpkg, "install", "freetype", "--triplet", vckpg_triplets[target]])

def build_windows(target):
    triplet = vckpg_triplets[target]
    buildPath = build_path(target)
    cmake_cmd = ["cmake",
        "-A", "ARM64" if target == "win-arm64" else "x64",
        f'-DCMAKE_TOOLCHAIN_FILE={vckg_toolchain}',
        f"-DVCPKG_TARGET_TRIPLET={triplet}",
    ] + common_cmake_args(target, buildMode, True)
    subprocess.call(cmake_cmd)

    subprocess.call(["cmake", "--build", buildPath, "--config", buildMode])

    srcFolder = os.path.join(buildPath, buildMode, "cimgui.dll")
    dstFolder = os.path.join(outFolder, target, "cimgui.dll")
    new_dir(dstFolder)
    shutil.copy2(srcFolder, dstFolder)

def build_mac(target):
    triplet = vckpg_triplets[target]
    buildPath = build_path(target)
    cmake_cmd = ["cmake",
        "-A", "ARM64" if target == "osx-arm64" else "x64",
        f'-DCMAKE_TOOLCHAIN_FILE={vckg_toolchain}',
        f"-DVCPKG_TARGET_TRIPLET={triplet}",
    ] + common_cmake_args(target, buildMode, True)
    subprocess.call(cmake_cmd)

    subprocess.call(["cmake", "--build", buildPath, "--config", buildMode])

    srcFolder = os.path.join(buildPath, buildMode, "cimgui.dylib")
    dstFolder = os.path.join(outFolder, target, "cimgui.dylib")
    new_dir(dstFolder)
    shutil.copy2(srcFolder, dstFolder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        help = "Target platform to build for",
        nargs='?',
        default = "win-x64",
        choices = ["win-x64", "win-arm64", "linux-x64", "linux-arm64", "mac-arm64", "wasm"]
    )
    parser.add_argument(
        "--build_mode",
        type = str,
        help = "Debug or Release",
        default = "Release",
        choices = ["Debug", "Release"]
    )
    args = parser.parse_args()
    target = args.target
    triplet = vckpg_triplets[target]
    buildMode = args.build_mode

    setup_vcpkg(target)
    vckg_toolchain = os.path.join(rel_path("vcpkg"), "scripts", "buildsystems", "vcpkg.cmake")
    
    outFolder = build_path("OUT")
    new_dir(outFolder)

    # --- Windows x64 ---
    if target == "win-x64":
        build_windows(target)

    # --- Windows arm64 ---
    if args.target == "win-arm64":
        build_windows(target)
    
    # --- Mac arm64 ---
    if args.target == "win-arm64":
        build_mac_arm64()


    if args.linux_x64:
        build_linux_x64()


    if args.linux_arm64:
        build_linux_arm64()


    if args.wasm:
        build_wasm()


