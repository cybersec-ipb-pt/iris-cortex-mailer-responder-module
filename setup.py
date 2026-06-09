import pathlib
import setuptools

# The directory containing this file
CURR_DIR = pathlib.Path(__file__).parent

# The text of the README file
README = (CURR_DIR / "README.md").read_text()

setuptools.setup(
     name="iris_cortex_mailer_responder_module",
     version="1.0",
     packages=['iris_cortex_mailer_responder_module', 'iris_cortex_mailer_responder_module.cortex_mailer_responder_handler'],
     author="VLK14 & RaykoPT",
     author_email="jorge.loureiro@ipb.pt",
     description="iris_cortex_mailer_responder_module is an IRIS pipeline/processor module created with https://github.com/dfir-iris/iris-skeleton-module. This version of the module is based on https://github.com/socfortress/iris-cortexanalyzer-module, modified to execute Cortex Mailer Responder.",
     long_description=README,
     long_description_content_type="text/markdown",
     url="https://github.com/cybersec-ipb-pt/iris-cortex-mailer-responder-module",
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: LGLP 3.0 License",
         "Operating System :: OS Independent",
     ],
     install_requires=['cortex4py~=2.1', 'setuptools>=65.5.1', 'iris-interface==1.2.0']
 )