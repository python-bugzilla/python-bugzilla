Name:           python-bugzilla
Version:        3.2.0
Release:        1%{?dist}
Summary:        Python library for interacting with Bugzilla

License:        GPLv2+
URL:            https://github.com/python-bugzilla/python-bugzilla
Source0:        https://github.com/python-bugzilla/python-bugzilla/archive/v%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires: python3-devel
BuildRequires: python3-requests
BuildRequires: python3-setuptools
BuildRequires: python3-pytest

%global _description\
python-bugzilla is a python library for interacting with bugzilla instances\
over XMLRPC or REST.\

%description %_description


%package -n python3-bugzilla
Summary: %summary
Requires: python3-requests
%{?python_provide:%python_provide python3-bugzilla}

Obsoletes:      python-bugzilla < %{version}-%{release}
Obsoletes:      python2-bugzilla < %{version}-%{release}

%description -n python3-bugzilla %_description


%package cli
Summary: Command line tool for interacting with Bugzilla
Requires: python3-bugzilla = %{version}-%{release}

%description cli
This package includes the 'bugzilla' command-line tool for interacting with bugzilla. Uses the python-bugzilla API



%prep
%setup -q



%install
%{__python3} setup.py install -O1 --root %{buildroot}



%check
pytest-3



%files -n python3-bugzilla
%doc COPYING README.md NEWS.md
%{python3_sitelib}/*

%files cli
%{_bindir}/bugzilla
%{_mandir}/man1/bugzilla.1.gz
