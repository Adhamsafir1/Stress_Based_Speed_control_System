from setuptools import setup, find_packages

setup(
    name="stress-speed-control",
    version="1.0.0",
    description="Real-time driver stress monitoring and speed control system",
    author="Adham Safir",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0",
        "flask-socketio>=5.3",
        "scikit-learn>=1.4",
        "numpy>=1.26",
        "pandas>=2.2",
        "scipy>=1.13",
        "PyYAML>=6.0",
        "pyserial>=3.5",
        "eventlet>=0.36",
        "joblib>=1.4",
    ],
    entry_points={
        "console_scripts": [
            "stress-monitor=main:main",
        ],
    },
)
