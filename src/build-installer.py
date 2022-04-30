#!/usr/bin/python3

import os
import sys
from re import match
from os.path import join, dirname
import shutil
import subprocess

from pkg_resources import Distribution

def is_numeric_version(version):
    return True

if len(sys.argv) < 3:
    print("\nUSAGE: src/build-installer.py AppName 1.0.0\n")
    exit(1)

app_name = sys.argv[1] if not len(sys.argv[1]) == 0 else "UnknownApp"
app_version = sys.argv[2]
app_numeric_version = app_version if match(r"[0-9]\.[0-9]\.[0-9]", app_version) else "0.0.0"
where = dirname(__file__)
devnull = open(os.devnull, "w")

# Input
stage_dir = join(where, "../stage")
src_installer_dir = join(stage_dir, "installer")
src_application_dir = join(stage_dir, "application")

# Temporary
tmp_dir = join(where, "../tmp")
darwin_dir = join(tmp_dir, "darwin")
resources_dir = join(darwin_dir, "Resources")
scripts_dir = join(darwin_dir, "scripts")
darwinpkg_dir = join(tmp_dir, "darwinpkg")
installation_dir = join(darwinpkg_dir, "Library", app_name, app_version)
package_dir = join(tmp_dir, "package")
pkg_dir = join(tmp_dir, "pkg")

# Output
build_dir = join(where, "../build")

def main():
    print(f"Creating installer for '{app_name} {app_version}'")

    prepare()
    arrange()
    create_uninstaller()
    create_installer()
    cleanup()

    print("Successfully packaged!")

def prepare():
    # Clean output folder
    shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_dir, exist_ok=True)

    # Clean temporary folder
    shutil.rmtree(tmp_dir, ignore_errors=True)

    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(darwin_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

def arrange():
    # Resources
    shutil.copy(join(src_installer_dir, "banner.png"), join(resources_dir, "banner.png"))
    shutil.copy(join(src_installer_dir, "conclusion.html"), join(resources_dir, "conclusion.html"))
    shutil.copy(join(src_installer_dir, "index.css"), join(resources_dir, "index.css"))
    shutil.copy(join(src_installer_dir, "uninstall.sh"), join(resources_dir, "uninstall.sh"))
    shutil.copy(join(src_installer_dir, "welcome.html"), join(resources_dir, "welcome.html"))

    # Scripts
    shutil.copy(join(src_installer_dir, "postinstall"), join(scripts_dir, "postinstall"))

    # Distribution
    shutil.copy(join(src_installer_dir, "Distribution"), join(darwin_dir, "Distribution"))

    # Give permissions
    subprocess.call(['chmod', '-R', '755', scripts_dir])
    subprocess.call(['chmod', '-R', '755', resources_dir])
    os.chmod(join(darwin_dir, "Distribution"), 0o755)

    emplace_files()

def substitute_values(filename):
    subprocess.call(['sed', '-i', '', '-e', f's/__VERSION__/{app_version}/g', filename])
    subprocess.call(['sed', '-i', '', '-e', f's/__PRODUCT__/{app_name}/g', filename])
    subprocess.call(['chmod', '-R', '755', filename])

def emplace_files():
    substitute_values(join(scripts_dir, "postinstall"))
    substitute_values(join(darwin_dir, "Distribution"))
    substitute_values(join(resources_dir, "welcome.html"))
    substitute_values(join(resources_dir, "conclusion.html"))
    
    os.chmod(join(resources_dir, "uninstall.sh"), 0o755)

    os.makedirs(darwinpkg_dir, exist_ok=True)

    os.makedirs(installation_dir, exist_ok=True)
    subprocess.call(['cp', '-a', join(stage_dir, "application"), installation_dir])
    subprocess.call(['chmod', '-R', '755', installation_dir])

    os.makedirs(package_dir, exist_ok=True)
    subprocess.call(['chmod', '-R', '755', package_dir])

    os.makedirs(pkg_dir, exist_ok=True)
    subprocess.call(['chmod', '-R', '755', pkg_dir])

def create_uninstaller():
    uninstaller_file = join(installation_dir, "uninstall.sh")
    shutil.copy(join(src_installer_dir, "uninstall.sh"), uninstaller_file)
    subprocess.call(['sed', '-i', '', '-e', f's/__VERSION__/{app_version}/g', uninstaller_file])
    subprocess.call(['sed', '-i', '', '-e', f's/__PRODUCT__/{app_name}/g', uninstaller_file])

def create_installer():
    output_name = f'{app_name}-{app_version}-installer.pkg'
    build_package()
    build_product(output_name)
    present(output_name)

def build_package():
    subprocess.call(
        [
            'pkgbuild',
            '--identifier', f'org.{app_name}.{app_version}',
            '--version', app_numeric_version,
            '--scripts', scripts_dir,
            '--root', darwinpkg_dir,
            join(package_dir, app_name + ".pkg"),
        ],
        stdout=devnull,
        stderr=devnull
    )

def build_product(output_name):
    subprocess.call([
            'productbuild',
            '--distribution', join(darwin_dir, 'Distribution'),
            '--resources', resources_dir,
            '--package-path', package_dir,
            join(pkg_dir, output_name),
        ],
        stdout=devnull,
        stderr=devnull
    )

def present(output_name):
    shutil.move(join(pkg_dir, output_name), join(build_dir, output_name))

def cleanup():
    shutil.rmtree(tmp_dir, ignore_errors=True)
    devnull.close()

main()
