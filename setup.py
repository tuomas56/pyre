from setuptools import setup, find_packages
setup(name="pyre", 
	package_dir={'':'src'},
	version="0.1.0",
	packages=find_packages('src'),
	install_requires= [
		'funcparserlib'
	],
	scripts=['src/ipyre'])
