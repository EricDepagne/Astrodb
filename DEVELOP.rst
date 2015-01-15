.. _virtualenv: http://www.virtualenv.org/
.. _pip: http://www.pip-installer.org

How to develop on Astrodb
=========================

Installing the package on your system will not permit you to change it, this is why you will have to use virtual environment and install it from the repository sources.

You will use `virtualenv`_ to install the package with `pip`_ in `Editable installs <https://pip.pypa.io/en/latest/reference/pip_install.html#editable-installs>`_ mode (in fact a *Develop egg*).

#. Create a directory and make it a virtual environment: ::
    
    mkdir AstroDev
    cd AstroDev
    virtualenv --no-site-packages --setuptools .

#. Then install the editable package sources: ::

    bin/pip install -e git+https://github.com/EricDepagne/Astrodb#egg=Astrodb

#. Finally activate the virtual environment: ::

    source bin/activate

You should probably change the repository url if you don't have permissions to push on it.

You will find the package sources in ``AstroDev/src/astrodb/``, your virtualenv install use it directly so every changes on the source takes effect instantly.

When you have activated the virtual environment you can check that is rightly installed use the commandline script: ::

    astrodb

This should answer you something.
