#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='news_agent',
    author='Pinperepette',
    author_email='pinperepette@gmail.com',
    description='Terminal news agent: fetches Google News, launches LLM agents, works with Ollama, terminal UI.',
    packages=find_packages(include=["news_agent", "news_agent.*"]),
    install_requires=[
        'requests',
        'rich',
    ],
    include_package_data=True,
    package_data={'': ['settings.ini']},
    entry_points={
        'console_scripts': [
            'news-agent=news_agent.main:main',
        ],
    },
)
