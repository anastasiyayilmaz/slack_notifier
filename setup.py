from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="slack-sender",
    version="0.1.0",
    author="Anastasiya Yilmaz",
    author_email="anastasiya.yilmaz@inaf.it",
    description="Send Slack notifications from Jupyter notebooks for cell execution monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anastasiyayilmaz/slack_sender",
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
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.20.0",
        "ipython>=7.0.0",
    ],
    keywords="slack notifications jupyter notebook monitoring",
)
