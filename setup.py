from setuptools import setup, find_packages

setup(name="logopipe",
      version="0.0.2",
      description="Creates, schedules, and pipes output for jobs in slurm. This Release is BETA 1.0",
      license="MIT",
      author="William Patterson",
      packages=find_packages(),
      package_data={'logopipe': ['*.yml', '*.txt', '*.sh']},
      install_requires=["Pyyaml"],
      long_description="long_description",
      entry_points={"console_scripts": ["logopipe=logopipe.__main__:main",]})
