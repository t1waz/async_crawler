import setuptools


setuptools.setup(name='rest_utils',
                 version='0.0.1',
                 author='t1waz',
                 author_email='milewiczmichal87@gmail.com',
                 description='REST tools for building backends '
                             'with TorToiseORM and Starlette framework',
                 url='github.com/t1waz/rest_utils',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 classifiers=[
                       "Programming Language :: Python :: 3",
                       "License :: OSI Approved :: MIT License",
                       "Operating System :: OS Independent",
                 ],
                 python_requires='>=3.6',
                 zip_safe=False)
