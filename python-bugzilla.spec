%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-bugzilla
Version:        0.8.0
Release:        1%{?dist}
Summary:        A python library for interacting with Bugzilla

Group:          Development/Languages
License:        GPLv2+
URL:            https://fedorahosted.org/python-bugzilla
Source0:        https://fedorahosted.org/releases/p/y/%{name}/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel
%if 0%{?rhel} == 5
BuildRequires:  python-setuptools
%else
BuildRequires:  python-setuptools-devel
%endif

Requires: python-pycurl
Requires: python-magic

%description
python-bugzilla is a python library for interacting with bugzilla instances
over XML-RPC. This package also includes the 'bugzilla' command-line tool
for interacting with bugzilla from shell scripts.

%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root=$RPM_BUILD_ROOT


%check
python setup.py test


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING README PKG-INFO
%{python_sitelib}/*
%{_bindir}/bugzilla
%{_mandir}/man1/bugzilla.1.gz
