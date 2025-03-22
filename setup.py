from setuptools import setup, find_packages
import platform

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define base dependencies
install_requires = [
    "psutil>=5.8.0",
    "setuptools>=65.5.1",
    "pygame>=2.1.0",
]

# Add platform-specific dependencies
if platform.system() == "Windows":
    install_requires.append("pywin32>=305")

setup(
    name="stealthmon",
    version="0.1.0",
    author="dkydivyansh.com",
    author_email="support@dkydivyansh.com",
    description="A Python module for detecting Incognito mode and monitoring browser search queries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dkydivyansh/stealthmon",
    project_urls={
        "Bug Tracker": "https://github.com/dkydivyansh/stealthmon/issues",
        "Documentation": "https://github.com/dkydivyansh/stealthmon",
        "Source Code": "https://github.com/dkydivyansh/stealthmon",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="incognito, privacy, monitoring, browser, detection, parental-control",
    python_requires=">=3.7",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "stealthmon=stealthmon.cli:main",
        ],
    },
    include_package_data=True,
) 