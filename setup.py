from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()



setup(
    name='apexomni',
    version='3.1.7',
    packages=find_packages(),
    description='Python3 Apexpro omni HTTP/WebSocket API Connector',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ApeX-Protocol/apexpro-openapi',
    license='MIT License',
    author='Dexter Dickinson',
    author_email='xxx@apexomni.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='apexomni apexpro api connector',
    package_data={'': ['*.json','*.dylib','*.dll','*.so']},
    # packages=['apexpro'],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'websocket-client',
        'websockets',
        'dateparser==1.0.0',
        'ecdsa==0.16.0',
        'eth_keys',
        'eth-account==0.13.7',
        'mpmath==1.0.0',
        'pytest>=4.4.0,<5.0.0',
        'requests-mock==1.6.0',
        'requests>=2.32.3,<3.0.0',
        'setuptools>=50.3.2',
        'sympy==1.6',
        'tox==3.13.2',
        'web3==6.0.0',
    ],
)
