%if 0%{?fedora} || 0%{?rhel} > 7
# Enable python3 by default
%bcond_without python3
%else
%bcond_with python3
%endif

%if 0%{?rhel} > 7
# Disable python2 build by default
%bcond_with python2
%else
%bcond_without python2
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%endif

Name:           python-bugzilla
Version:        2.3.0
Release:        1%{?dist}
Summary:        Python library for interacting with Bugzilla

License:        GPLv2+
URL:            https://github.com/python-bugzilla/python-bugzilla
Source0:        https://github.com/python-bugzilla/python-bugzilla/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

%if %{with python2}
BuildRequires: python2-devel
BuildRequires: python2-requests
BuildRequires: python2-setuptools
BuildRequires: python2-pytest
%endif # with python2

%if %{with python3}
BuildRequires: python3-devel
BuildRequires: python3-requests
BuildRequires: python3-setuptools
BuildRequires: python3-pytest
%endif # if with_python3

%global _description\
python-bugzilla is a python library for interacting with bugzilla instances\
over XML-RPC.\

%description %_description


%if %{with python2}
%package -n python2-bugzilla
Summary: %summary
Requires: python2-requests
# This dep is for back compat, so that installing python-bugzilla continues
# to give the cli tool
Requires: python-bugzilla-cli
%{?python_provide:%python_provide python2-bugzilla}

%description -n python2-bugzilla %_description

%endif # with python2


%if %{with python3}
%package -n python3-bugzilla
Summary: %summary
Requires: python3-requests
%{?python_provide:%python_provide python3-bugzilla}

%if %{without python2}
Obsoletes:      python-bugzilla < %{version}-%{release}
Obsoletes:      python2-bugzilla < %{version}-%{release}
%endif # without python2

%description -n python3-bugzilla %_description
%endif # if with_python3


%package cli
Summary: Command line tool for interacting with Bugzilla
%if %{with python3}
Requires: python3-bugzilla = %{version}-%{release}
%else
Requires: python2-bugzilla = %{version}-%{release}
%endif

%description cli
This package includes the 'bugzilla' command-line tool for interacting with bugzilla. Uses the python-bugzilla API



%prep
%setup -q

%if %{with python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif # with_python3



%build
%if %{with python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif # with_python3

%if %{with python2}
%{__python2} setup.py build
%endif # with python2



%install
%if %{with python3}
pushd %{py3dir}
%{__python3} setup.py install -O1 --skip-build --root %{buildroot}

%if %{with python2}
rm %{buildroot}/usr/bin/bugzilla
%endif

popd
%endif # with_python3

%if %{with python2}
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}
%endif # with python2

# Replace '#!/usr/bin/env python' with '#!/usr/bin/python2'
# The format is ideal for upstream, but not a distro. See:
# https://fedoraproject.org/wiki/Features/SystemPythonExecutablesUseSystemPython
%if %{with python3}
%global python_env_path %{__python3}
%else
%global python_env_path %{__python2}
%endif
for f in $(find %{buildroot} -type f -executable -print); do
    sed -i "1 s|^#!/usr/bin/.*|#!%{python_env_path}|" $f || :
done



%check
%if %{with python2}
# py.test naming is needed for RHEL7 compat, works fine with Fedora
py.test
%endif # with python2
%if %{with python3}
pytest-3
%endif # with python3



%if %{with python2}
%files -n python2-bugzilla
%doc COPYING README.md NEWS.md
%{python2_sitelib}/*
%endif # with python2

%if %{with python3}
%files -n python3-bugzilla
%doc COPYING README.md NEWS.md
%{python3_sitelib}/*
%endif # with_python3

%files cli
%{_bindir}/bugzilla
%{_mandir}/man1/bugzilla.1.gz
