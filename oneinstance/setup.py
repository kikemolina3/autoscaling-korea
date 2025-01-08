from setuptools import setup, find_packages

setup(
    name='autoscaling-korea',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "flask",
        "psutil",
        "requests",
        "gunicorn",
        "boto3",
        "botocore",
        "argparse"
    ],
    python_requires='>=3.6',
)