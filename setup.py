from setuptools import setup, find_packages

setup(name="logopipe",
      version="0.0.0",
      description="Creates, schedules, and pipes output for jobs in slurm.",
      license="MIT",
      author="William Patterson",
      packages=find_packages(),
      package_data={'logopipe': ['*.yml', '*.txt', '*.sh']},
      install_requires=["PyYaml", "paramiko"],
      long_description="long_description",
      entry_points={"console_scripts": ["logopipe=logopipe.__main__:main",]})
