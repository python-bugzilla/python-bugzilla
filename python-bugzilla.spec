%if 0%{?fedora} || 0%{?rhel} >= 8
%global with_python3 1
%else
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib2: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%endif

Name:           python-bugzilla
Version:        2.1.0
Release:        1%{?dist}
Summary:        python2 library for interacting with Bugzilla

License:        GPLv2+
URL:            https://github.com/python-bugzilla/python-bugzilla
Source0:        https://github.com/python-bugzilla/python-bugzilla/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires: python2-devel
BuildRequires: python-requests
BuildRequires: python-setuptools
%if 0%{?el6}
BuildRequires: python-argparse
%endif

%if 0%{?with_python3}
BuildRequires: python3-devel
BuildRequires: python3-requests
BuildRequires: python3-setuptools
%endif # if with_python3

Requires: python-requests
Requires: python-magic
%if 0%{?el6}
Requires: python-argparse
%endif
# This dep is for back compat, so that installing python-bugzilla continues
# to give the cli tool
Requires: python-bugzilla-cli


%description
python-bugzilla is a python 2 library for interacting with bugzilla instances
over XML-RPC.


%if 0%{?with_python3}
%package -n python3-bugzilla
Summary: python 3 library for interacting with Bugzilla
Requires: python3-requests
Requires: python3-magic

%description -n python3-bugzilla
python3-bugzilla is a python 3 library for interacting with bugzilla instances
over XML-RPC.
%endif # if with_python3


%package cli
Summary: Command line tool for interacting with Bugzilla
%if 0%{?with_python3}
Requires: python3-bugzilla = %{version}-%{release}
%else
Requires: python-bugzilla = %{version}-%{release}
%endif

%description cli
This package includes the 'bugzilla' command-line tool for interacting with bugzilla. Uses the python-bugzilla API



%prep
%setup -q

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif # with_python3



%build
%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif # with_python3

%{__python2} setup.py build



%install
%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install -O1 --skip-build --root %{buildroot}
rm %{buildroot}/usr/bin/bugzilla
popd
%endif # with_python3

%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Replace '#!/usr/bin/env python' with '#!/usr/bin/python2'
# The format is ideal for upstream, but not a distro. See:
# https://fedoraproject.org/wiki/Features/SystemPythonExecutablesUseSystemPython
%if 0%{?with_python3}
%global python_env_path %{__python3}
%else
%global python_env_path %{__python2}
%endif
for f in $(find %{buildroot} -type f -executable -print); do
    sed -i "1 s|^#!/usr/bin/.*|#!%{python_env_path}|" $f || :
done



%check
%{__python2} setup.py test



%files
%doc COPYING README.md NEWS.md
%{python2_sitelib}/*

%if 0%{?with_python3}
%files -n python3-bugzilla
%doc COPYING README.md NEWS.md
%{python3_sitelib}/*
%endif # with_python3

%files cli
%{_bindir}/bugzilla
%{_mandir}/man1/bugzilla.1.gz
