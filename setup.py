from setuptools import setup, find_packages

setup(
    name="MinecraftBotClient",
    version="1.0.0",
    description="MBC - Minecraft Bot Client supporting versions 1.8 to 26.2",
    author="Creaddinscart",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "mbc=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
