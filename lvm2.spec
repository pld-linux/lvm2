#
# Conditional build:
%bcond_without	initrd	# don't build initrd version
%bcond_without	uClibc	# link initrd version with static glibc instead of uClibc
%bcond_without	clvmd	# build clvmd
%bcond_with	cman	# use cman+dlm instead of gulm+ccs
%bcond_without	selinux	# disable SELinux
#
%ifarch sparc64 sparc
%undefine	with_uClibc
%endif
#
%define	devmapper_ver	1.02.13
Summary:	The new version of Logical Volume Manager for Linux
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.02.16
Release:	0.1
License:	GPL
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	fb711403e1b763e135686aaa800b3d6a
Patch0:		%{name}-as-needed.patch
URL:		http://sources.redhat.com/lvm2/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	device-mapper-devel >= %{devmapper_ver}
%{?with_selinux:BuildRequires:	libselinux-devel >= 1.10}
BuildRequires:	rpmbuild(macros) >= 1.213
%if %{with initrd}
	%if %{with uClibc}
BuildRequires:	device-mapper-initrd-devel >= %{devmapper_ver}
		%ifarch ppc
BuildRequires:	uClibc-static >= 2:0.9.29
		%else
BuildRequires:	uClibc-static >= 2:0.9.26
		%endif
	%else
BuildRequires:	device-mapper-static >= %{devmapper_ver}
BuildRequires:	glibc-static
	%endif
%endif
%if %{with clvmd}
BuildRequires:	dlm-devel >= 1.0-0.pre21.2
%if %{with cman}
BuildRequires:	cman-devel >= 1.0
%else
BuildRequires:	ccs-devel >= 1.0
BuildRequires:	gulm-devel >= 1.0-0.pre26.2
%endif
%endif
BuildRequires:	readline-devel
Requires:	device-mapper >= %{devmapper_ver}
%if %{with clvmd}
%if %{with cman}
Requires:	cman >= 1.0
Requires:	dlm >= 1.0-0.pre21.2
%else
Requires:	gulm >= 1.0-0.pre26.2
%endif
%endif
%{?with_selinux:Requires:	libselinux >= 1.10}
Obsoletes:	lvm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_exec_prefix	/
%define		_sbindir	/sbin
%define		_libdir		/%{_lib}

# changing CFLAGS in the middle confuses confcache
%undefine	configure_cache

%description
This package includes a number of utilities for creating, checking,
and repairing logical volumes.

%description -l pl
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2).

%package initrd
Summary:	The new version of Logical Volume Manager for Linux - initrd version
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa - wersja dla initrd
Group:		Base

%description initrd
This package includes a number of utilities for creating, checking,
and repairing logical volumes - staticaly linked for initrd.

%description initrd -l pl
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2) - statycznie skonsolidowane na
potrzeby initrd.

%prep
%setup -q -n LVM2.%{version}
%patch0 -p1

%build
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}

%if %{with initrd}
%configure \
	%{?with_uClibc:CC="%{_target_cpu}-uclibc-gcc"} \
	ac_cv_lib_dl_dlopen=no \
	--with-optimisation="-Os" \
	--enable-static_link \
	--with-lvm1=internal \
	--disable-selinux \
	--disable-nls
sed -i -e 's#rpl_malloc#malloc#g' lib/misc/configure.h

%{__make}
mv -f tools/lvm.static initrd-lvm
%{__make} clean
%endif

%configure \
	CFLAGS="%{rpmcflags}" \
	--with-optimisation="" \
	--enable-readline \
	--enable-fsadm \
	%{?with_clvmd:--with-clvmd=%{?with_cman:cman}%{!?with_cman:gulm}} \
	--with-lvm1=internal \
	--with-pool=internal \
	--with-cluster=internal \
	--with-snapshots=internal \
	--with-mirrors=internal \
	%{!?with_selinux:--disable-selinux}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/lvm

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER="" \
	GROUP=""

touch $RPM_BUILD_ROOT%{_sysconfdir}/lvm/lvm.conf

%{?with_initrd:install initrd-lvm $RPM_BUILD_ROOT%{_sbindir}/initrd-lvm}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/*
%{?with_initrd:%exclude %{_sbindir}/initrd-lvm}
%{_mandir}/man?/*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/lvm.conf

%if %{with initrd}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/initrd-lvm
%endif
